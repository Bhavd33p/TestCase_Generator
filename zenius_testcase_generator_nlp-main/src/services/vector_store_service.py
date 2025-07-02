import chromadb
from typing import List, Dict, Any, Optional
from uuid import uuid4
import hashlib
import logging
import os
from chromadb.config import Settings
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from src.services.embedding_service import EmbeddingService

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self, collection_name: str = "documents", config: Dict = None):
        """
        Initialize the vector store service.
        
        Args:
            collection_name (str): Name of the collection to use
            config (Dict): Configuration dictionary containing OpenAI API key
        """
        self.logger = logging.getLogger(__name__)
        try:
            # Initialize ChromaDB client with new configuration
            self.client = chromadb.PersistentClient(path="./chroma_db")
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            self.embedding_service = EmbeddingService(config=config)
            self.logger.info(f"Vector store initialized with collection: {collection_name}")
        except Exception as e:
            self.logger.error(f"Error initializing vector store: {str(e)}")
            raise

    def add_documents(
        self,
        documents: List[Document],
        embeddings: Optional[List[List[float]]] = None
    ) -> Dict[str, Any]:
        """
        Add documents to the vector store.
        
        Args:
            documents (List[Document]): List of documents to add
            embeddings (Optional[List[List[float]]]): Pre-computed embeddings
            
        Returns:
            Dict[str, Any]: Processing results
        """
        try:
            if not documents:
                return {"status": "error", "message": "No documents provided"}

            # Generate embeddings if not provided
            if embeddings is None:
                embeddings = self.embedding_service.embed_documents(documents)

            # Prepare documents for ChromaDB
            ids = [f"doc_{i}" for i in range(len(documents))]
            texts = [doc.page_content for doc in documents]
            metadatas = [doc.metadata for doc in documents]
               
            # Add to collection
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas
            )

            return {
                "status": "success",
                "num_documents": len(documents)
            }

        except Exception as e:
            self.logger.error(f"Error adding documents: {str(e)}")
            raise Exception(f"Failed to add documents: {str(e)}")

    def search(
        self,
        query: List[float],
        n_results: int = 3,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents.
        
        Args:
            query (str): Search query
            n_results (int): Number of results to return
            filter_metadata (Optional[Dict[str, Any]]): Metadata filters
            
        Returns:
            List[Dict[str, Any]]: Search results
        """
        try:
            self.logger.info(f"Starting vector search with n_results={n_results}, filter_metadata={filter_metadata}")
            self.logger.debug(f"Query embedding: {query}")

            # Search collection
            results = self.collection.query(
                query_embeddings=[query],
                n_results=n_results,
                where=filter_metadata
            )

            # Format results
            formatted_results = []
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    'text': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else None
                })

            self.logger.info(f"Vector search returned {len(formatted_results)} results.")
            self.logger.debug(f"Formatted search results: {formatted_results}")

            return formatted_results

        except Exception as e:
            self.logger.error(f"Error searching documents: {str(e)}")
            raise Exception(f"Search failed: {str(e)}")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get collection statistics.
        
        Returns:
            Dict[str, Any]: Collection statistics
        """
        try:
            count = self.collection.count()
            return {
                "total_documents": count
            }
        except Exception as e:
            self.logger.error(f"Error getting collection stats: {str(e)}")
            raise Exception(f"Failed to get collection stats: {str(e)}")

    def _generate_hash(self, text: str) -> str:
        """Generate SHA256 hash of text content"""
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def _check_duplicates(self, content_hashes: List[str]) -> List[str]:
        """Check for existing content hashes to avoid duplicates"""
        if not content_hashes:
            return []
        
        try:
            # Query for existing hashes in batches to avoid query size limits
            existing_hashes = []
            batch_size = 100
            
            for i in range(0, len(content_hashes), batch_size):
                batch = content_hashes[i:i + batch_size]
                
                # ChromaDB where clause for multiple values
                where_clause = {"content_hash": {"$in": batch}}
                
                results = self.collection.query(
                    where=where_clause,
                    include=["metadatas"]
                )
                
                # Extract existing hashes from results
                if results.get("metadatas"):
                    for metadata_list in results["metadatas"]:
                        for metadata in metadata_list:
                            if metadata and "content_hash" in metadata:
                                existing_hashes.append(metadata["content_hash"])
            
            return existing_hashes
            
        except Exception as e:
            self.logger.warning(f"Failed to check duplicates: {e}")
            return []

    def store_embeddings(self, embeddings: List[List[float]], chunks: List[str], metadata_info: Dict[str, str]) -> int:
        """Store embeddings with metadata and deduplication"""
        if len(embeddings) != len(chunks):
            raise ValueError(f"Embeddings count ({len(embeddings)}) and chunks count ({len(chunks)}) mismatch.")

        # Generate content hashes
        content_hashes = [self._generate_hash(chunk) for chunk in chunks]
        
        # Check for duplicates
        existing_hashes = self._check_duplicates(content_hashes)
        
        # Filter out duplicates
        new_data = []
        for i, (embedding, chunk, content_hash) in enumerate(zip(embeddings, chunks, content_hashes)):
            if content_hash not in existing_hashes:
                new_data.append((embedding, chunk, content_hash))
        
        if not new_data:
            self.logger.info("No new data to insert (all duplicates)")
            return 0

        # Prepare data for insertion
        ids = []
        metadatas = []
        documents = []
        new_embeddings = []

        for embedding, chunk, content_hash in new_data:
            unique_id = str(uuid4())
            ids.append(unique_id)
            documents.append(chunk)
            new_embeddings.append(embedding)
            metadatas.append({
                "project_name": metadata_info.get("project_name", ""),
                "model_name": metadata_info.get("model_name", ""),
                "source": metadata_info.get("source", ""),
                "source_id": metadata_info.get("source_id", ""),
                "content_hash": content_hash
            })

        try:
            self.collection.add(
                documents=documents,
                embeddings=new_embeddings,
                metadatas=metadatas,
                ids=ids
            )
            
            inserted_count = len(ids)
            self.logger.info(f"Inserted {inserted_count} new records (skipped {len(chunks) - inserted_count} duplicates)")
            return inserted_count
            
        except Exception as e:
            self.logger.error(f"Failed to insert data: {e}")
            raise

    def delete_by_project(self, project_name: str) -> int:
        """Delete records by project name"""
        try:
            # Get all records with the given project_name
            results = self.collection.query(
                where={"project_name": project_name},
                include=["ids"]
            )
            
            # ChromaDB returns nested lists, so we need to flatten
            ids_to_delete = []
            if results.get("ids"):
                for id_list in results["ids"]:
                    if isinstance(id_list, list):
                        ids_to_delete.extend(id_list)
                    else:
                        ids_to_delete.append(id_list)
            
            if ids_to_delete:
                self.collection.delete(ids=ids_to_delete)
                deleted_count = len(ids_to_delete)
                self.logger.info(f"Deleted {deleted_count} records for project: {project_name}")
                return deleted_count
            else:
                self.logger.info(f"No records found for project: {project_name}")
                return 0
                
        except Exception as e:
            self.logger.error(f"Failed to delete records: {e}")
            raise

    def delete_by_source(self, source: str, project_name: Optional[str] = None) -> int:
        """Delete records by source, optionally filtered by project"""
        try:
            # Build where clause
            if project_name:
                where_clause = {"$and": [{"source": source}, {"project_name": project_name}]}
            else:
                where_clause = {"source": source}
            
            # Get all records matching the criteria
            results = self.collection.query(
                where=where_clause,
                include=["ids"]
            )
            
            # Flatten the nested ids list
            ids_to_delete = []
            if results.get("ids"):
                for id_list in results["ids"]:
                    if isinstance(id_list, list):
                        ids_to_delete.extend(id_list)
                    else:
                        ids_to_delete.append(id_list)
            
            if ids_to_delete:
                self.collection.delete(ids=ids_to_delete)
                deleted_count = len(ids_to_delete)
                self.logger.info(f"Deleted {deleted_count} records for source: {source}")
                return deleted_count
            else:
                self.logger.info(f"No records found for source: {source}")
                return 0
                
        except Exception as e:
            self.logger.error(f"Failed to delete records: {e}")
            raise

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics"""
        try:
            # Get collection info
            collection_info = self.collection.get()
            
            return {
                "collection_name": self.collection.name,
                "total_documents": len(collection_info.get("ids", [])),
                "persist_directory": self.client.persist_directory
            }
        except Exception as e:
            self.logger.error(f"Failed to get stats: {e}")
            return {}

    def list_projects(self) -> List[str]:
        """List all unique project names"""
        try:
            # Get all records with project_name metadata
            results = self.collection.get(include=["metadatas"])
            
            projects = set()
            if results.get("metadatas"):
                for metadata in results["metadatas"]:
                    if metadata and "project_name" in metadata and metadata["project_name"]:
                        projects.add(metadata["project_name"])
            
            return sorted(list(projects))
        except Exception as e:
            self.logger.error(f"Failed to list projects: {e}")
            return []

    def reset_collection(self):
        """Delete all data in the collection"""
        try:
            self.client.delete_collection(name=self.collection.name)
            self.collection = self.client.get_or_create_collection(
                name=self.collection.name,
                metadata={"hnsw:space": "cosine"}
            )
            self.logger.info(f"Reset collection: {self.collection.name}")
        except Exception as e:
            self.logger.error(f"Failed to reset collection: {e}")
            raise