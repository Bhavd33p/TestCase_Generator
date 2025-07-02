import chromadb
from typing import List, Dict, Any, Optional, Tuple
from uuid import uuid4
import hashlib
import logging
import os
import json
from chromadb.config import Settings
from chromadb.utils import embedding_functions

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorStore:
    """
    ChromaDB vector store with proper nested list handling,
    duplicate prevention, and comprehensive search functionality.
    """
    
    def __init__(
        self,
        collection_name: str = "test_case_documents",
        persist_directory: str = ".chromadb",
        embedding_function: Optional[Any] = None
    ):
        """
        Initialize ChromaDB vector store.
        
        Args:
            collection_name: Name of the collection
            persist_directory: Directory to persist the database
            embedding_function: Custom embedding function (optional)
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self.client = None
        self.collection = None
        self.embedding_function = embedding_function
        
        # Create persist directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize client and collection
        self._initialize_client()
        self._initialize_collection()
        
        logger.info(f"VectorStore initialized with collection: {collection_name}")
    
    def _initialize_client(self):
        """Initialize ChromaDB client with proper configuration."""
        try:
            # Use PersistentClient for modern ChromaDB versions
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            logger.info("ChromaDB client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB client: {e}")
            raise RuntimeError(f"Could not initialize ChromaDB client: {e}")
    
    def _initialize_collection(self):
        """Initialize or get the collection."""
        try:
            # Try to get existing collection first
            try:
                self.collection = self.client.get_collection(
                    name=self.collection_name,
                    embedding_function=self.embedding_function
                )
                logger.info(f"Retrieved existing collection: {self.collection_name}")
                
            except Exception:
                # Create new collection if it doesn't exist
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    embedding_function=self.embedding_function,
                    metadata={"hnsw:space": "cosine"}
                )
                logger.info(f"Created new collection: {self.collection_name}")
                
        except Exception as e:
            logger.error(f"Failed to initialize collection: {e}")
            raise RuntimeError(f"Could not initialize collection: {e}")
    
    def _generate_content_hash(self, content: str) -> str:
        """Generate hash for content to prevent duplicates."""
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def _prepare_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare metadata for ChromaDB (ensure all values are strings)."""
        prepared = {}
        for key, value in metadata.items():
            if isinstance(value, (dict, list)):
                prepared[key] = json.dumps(value)
            elif value is None:
                prepared[key] = ""
            else:
                prepared[key] = str(value)
        return prepared
    
    def add_documents(
        self,
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Add documents to the vector store with duplicate prevention.
        
        Args:
            documents: List of document texts
            embeddings: List of embedding vectors
            metadatas: Optional list of metadata dictionaries
            ids: Optional list of document IDs
            
        Returns:
            Dictionary with operation results
        """
        if not documents or not embeddings:
            logger.warning("Empty documents or embeddings provided")
            return {"added": 0, "skipped": 0, "errors": 0}
        
        if len(documents) != len(embeddings):
            logger.error("Mismatch between documents and embeddings length")
            return {"added": 0, "skipped": 0, "errors": len(documents)}
        
        # Prepare data
        if metadatas is None:
            metadatas = [{}] * len(documents)
        
        if ids is None:
            ids = [self._generate_content_hash(doc) for doc in documents]
        
        # Ensure all lists have same length
        min_length = min(len(documents), len(embeddings), len(metadatas), len(ids))
        documents = documents[:min_length]
        embeddings = embeddings[:min_length]
        metadatas = metadatas[:min_length]
        ids = ids[:min_length]
        
        added_count = 0
        skipped_count = 0
        error_count = 0
        
        try:
            # Check for existing documents to prevent duplicates
            existing_ids = set()
            try:
                existing_data = self.collection.get(ids=ids)
                if existing_data and existing_data.get('ids'):
                    existing_ids = set(existing_data['ids'])
            except Exception as e:
                logger.warning(f"Could not check for existing documents: {e}")
            
            # Prepare data for insertion
            docs_to_add = []
            embeddings_to_add = []
            metadatas_to_add = []
            ids_to_add = []
            
            for i, (doc, embedding, metadata, doc_id) in enumerate(zip(documents, embeddings, metadatas, ids)):
                try:
                    if doc_id in existing_ids:
                        logger.debug(f"Skipping duplicate document with ID: {doc_id}")
                        skipped_count += 1
                        continue
                    
                    # Validate embedding
                    if not isinstance(embedding, list) or not embedding:
                        logger.error(f"Invalid embedding for document {i}")
                        error_count += 1
                        continue
                    
                    # Prepare metadata
                    prepared_metadata = self._prepare_metadata(metadata)
                    prepared_metadata['content_hash'] = self._generate_content_hash(doc)
                    prepared_metadata['document_length'] = str(len(doc))
                    
                    docs_to_add.append(doc)
                    embeddings_to_add.append(embedding)
                    metadatas_to_add.append(prepared_metadata)
                    ids_to_add.append(doc_id)
                    
                except Exception as e:
                    logger.error(f"Error preparing document {i}: {e}")
                    error_count += 1
            
            # Add documents in batches
            if docs_to_add:
                batch_size = 100
                for i in range(0, len(docs_to_add), batch_size):
                    batch_end = min(i + batch_size, len(docs_to_add))
                    
                    try:
                        self.collection.add(
                            documents=docs_to_add[i:batch_end],
                            embeddings=embeddings_to_add[i:batch_end],
                            metadatas=metadatas_to_add[i:batch_end],
                            ids=ids_to_add[i:batch_end]
                        )
                        added_count += (batch_end - i)
                        logger.info(f"Added batch {i//batch_size + 1}: {batch_end - i} documents")
                        
                    except Exception as e:
                        logger.error(f"Error adding batch {i//batch_size + 1}: {e}")
                        error_count += (batch_end - i)
            
            result = {
                "added": added_count,
                "skipped": skipped_count,
                "errors": error_count,
                "total_processed": len(documents)
            }
            
            logger.info(f"Document addition complete: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            return {
                "added": 0,
                "skipped": 0,
                "errors": len(documents),
                "error_message": str(e)
            }
    
    def search(
        self,
        query_embedding: List[float],
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
        include: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Search for similar documents.
        
        Args:
            query_embedding: Query embedding vector
            n_results: Number of results to return
            where: Optional metadata filter
            include: Optional list of fields to include
            
        Returns:
            Search results with proper nested list handling
        """
        if not query_embedding:
            logger.warning("Empty query embedding provided")
            return {"documents": [], "metadatas": [], "distances": [], "ids": []}
        
        try:
            # Set default include fields
            if include is None:
                include = ["documents", "metadatas", "distances"]
            
            # Perform search
            results = self.collection.query(
                query_embeddings=[query_embedding],  # ChromaDB expects nested list
                n_results=n_results,
                where=where,
                include=include
            )
            
            # Handle nested list structure properly
            processed_results = {
                "documents": [],
                "metadatas": [],
                "distances": [],
                "ids": []
            }
            
            # ChromaDB returns nested lists, so we need to extract the first (and only) query result
            if results:
                if "documents" in results and results["documents"]:
                    processed_results["documents"] = results["documents"][0] if results["documents"][0] else []
                
                if "metadatas" in results and results["metadatas"]:
                    processed_results["metadatas"] = results["metadatas"][0] if results["metadatas"][0] else []
                
                if "distances" in results and results["distances"]:
                    processed_results["distances"] = results["distances"][0] if results["distances"][0] else []
                
                if "ids" in results and results["ids"]:
                    processed_results["ids"] = results["ids"][0] if results["ids"][0] else []
            
            # Post-process metadata (convert JSON strings back to objects)
            if processed_results["metadatas"]:
                for metadata in processed_results["metadatas"]:
                    if metadata:
                        for key, value in metadata.items():
                            if isinstance(value, str) and value.startswith(('[', '{')):
                                try:
                                    metadata[key] = json.loads(value)
                                except json.JSONDecodeError:
                                    pass  # Keep as string if not valid JSON
            
            logger.info(f"Search completed: found {len(processed_results['documents'])} results")
            return processed_results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return {
                "documents": [],
                "metadatas": [],
                "distances": [],
                "ids": [],
                "error": str(e)
            }
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection."""
        try:
            count = self.collection.count()
            
            # Get sample of documents to analyze
            sample_size = min(10, count)
            sample_data = self.collection.get(limit=sample_size) if count > 0 else None
            
            stats = {
                "collection_name": self.collection_name,
                "document_count": count,
                "persist_directory": self.persist_directory
            }
            
            if sample_data and sample_data.get('metadatas'):
                # Analyze metadata fields
                metadata_fields = set()
                for metadata in sample_data['metadatas']:
                    if metadata:
                        metadata_fields.update(metadata.keys())
                
                stats["metadata_fields"] = list(metadata_fields)
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {
                "collection_name": self.collection_name,
                "error": str(e)
            }
    
    def delete_documents(self, ids: List[str]) -> Dict[str, Any]:
        """
        Delete documents by IDs.
        
        Args:
            ids: List of document IDs to delete
            
        Returns:
            Deletion results
        """
        if not ids:
            logger.warning("No IDs provided for deletion")
            return {"deleted": 0, "errors": 0}
        
        try:
            # Check which IDs exist
            existing_data = self.collection.get(ids=ids)
            existing_ids = set(existing_data.get('ids', []))
            
            ids_to_delete = [id for id in ids if id in existing_ids]
            
            if ids_to_delete:
                self.collection.delete(ids=ids_to_delete)
                deleted_count = len(ids_to_delete)
            else:
                deleted_count = 0
            
            result = {
                "deleted": deleted_count,
                "not_found": len(ids) - deleted_count,
                "errors": 0
            }
            
            logger.info(f"Deletion complete: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to delete documents: {e}")
            return {
                "deleted": 0,
                "errors": len(ids),
                "error_message": str(e)
            }
    
    def reset_collection(self) -> bool:
        """
        Reset (clear) the entire collection.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Delete the collection
            self.client.delete_collection(name=self.collection_name)
            
            # Recreate the collection
            self._initialize_collection()
            
            logger.info(f"Collection {self.collection_name} reset successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to reset collection: {e}")
            return False
    
    def get_documents_by_metadata(
        self,
        where: Dict[str, Any],
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get documents by metadata filter.
        
        Args:
            where: Metadata filter
            limit: Optional limit on number of results
            
        Returns:
            Filtered documents
        """
        try:
            results = self.collection.get(
                where=where,
                limit=limit,
                include=["documents", "metadatas", "ids"]
            )
            
            # Post-process metadata
            if results.get("metadatas"):
                for metadata in results["metadatas"]:
                    if metadata:
                        for key, value in metadata.items():
                            if isinstance(value, str) and value.startswith(('[', '{')):
                                try:
                                    metadata[key] = json.loads(value)
                                except json.JSONDecodeError:
                                    pass
            
            logger.info(f"Retrieved {len(results.get('documents', []))} documents by metadata")
            return results
            
        except Exception as e:
            logger.error(f"Failed to get documents by metadata: {e}")
            return {"documents": [], "metadatas": [], "ids": [], "error": str(e)}
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on the vector store.
        
        Returns:
            Health status information
        """
        try:
            # Test basic operations
            count = self.collection.count()
            
            # Test a simple query if there are documents
            if count > 0:
                test_embedding = [0.1] * 384  # Default embedding dimension
                test_results = self.collection.query(
                    query_embeddings=[test_embedding],
                    n_results=1
                )
                query_success = bool(test_results)
            else:
                query_success = True  # No documents to query
            
            return {
                "status": "healthy",
                "collection_name": self.collection_name,
                "document_count": count,
                "query_test": "passed" if query_success else "failed",
                "persist_directory": self.persist_directory
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "collection_name": self.collection_name
            }
    
    def __del__(self):
        """Cleanup resources."""
        try:
            if hasattr(self, 'client') and self.client:
                # ChromaDB client cleanup is handled automatically
                pass
        except Exception:
            pass 