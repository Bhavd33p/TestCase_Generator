import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
from uuid import uuid4
import hashlib
import logging
import os

class VectorStore:
    def __init__(self, collection_name: str = "demo_collection", persist_directory: str = ".chromadb"):
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Ensure persist directory exists
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize Chroma client
        self._initialize_client()
        
        # Create or get existing collection
        self._setup_collection()

    def _initialize_client(self):
        """Initialize ChromaDB client with proper settings"""
        try:
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            self.logger.info(f"ChromaDB client initialized with persist directory: {self.persist_directory}")
        except Exception as e:
            self.logger.error(f"Failed to initialize ChromaDB client: {e}")
            raise

    def _setup_collection(self):
        """Create or get existing collection"""
        try:
            # Try to get existing collection first
            self.collection = self.client.get_collection(name=self.collection_name)
            self.logger.info(f"Collection '{self.collection_name}' loaded.")
        except Exception:
            # Create new collection if it doesn't exist
            try:
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    metadata={"description": "Vector store for embeddings with metadata"}
                )
                self.logger.info(f"Created collection: {self.collection_name}")
            except Exception as e:
                self.logger.error(f"Failed to create collection: {e}")
                raise

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

    def search(self, query_embedding: List[float] = None, query_text: str = None, 
               n_results: int = 5, project_name: Optional[str] = None, 
               source: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search for similar vectors with optional filtering"""
        
        if query_embedding is None and query_text is None:
            raise ValueError("Either query_embedding or query_text must be provided")
        
        # Build where clause for filtering
        where_clause = {}
        if project_name and source:
            where_clause = {"$and": [{"project_name": project_name}, {"source": source}]}
        elif project_name:
            where_clause = {"project_name": project_name}
        elif source:
            where_clause = {"source": source}
        
        try:
            if query_embedding:
                # Vector similarity search
                results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=n_results,
                    where=where_clause if where_clause else None,
                    include=["documents", "metadatas", "distances"]
                )
            else:
                # Text-based search (ChromaDB will handle embedding)
                results = self.collection.query(
                    query_texts=[query_text],
                    n_results=n_results,
                    where=where_clause if where_clause else None,
                    include=["documents", "metadatas", "distances"]
                )
            
            # Format results
            formatted_results = []
            if results.get("documents") and results["documents"][0]:  # Check if we have results
                documents = results["documents"][0]
                metadatas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(documents)
                distances = results["distances"][0] if results.get("distances") else [0] * len(documents)
                ids = results["ids"][0] if results.get("ids") else [""] * len(documents)
                
                for i, (doc, metadata, distance, doc_id) in enumerate(zip(documents, metadatas, distances, ids)):
                    formatted_results.append({
                        "id": doc_id,
                        "content": doc,
                        "distance": distance,
                        "similarity": 1 / (1 + distance) if distance > 0 else 1.0,  # Convert distance to similarity
                        "metadata": metadata or {}
                    })
            
            return formatted_results
            
        except Exception as e:
            self.logger.error(f"Search failed: {e}")
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
                "collection_name": self.collection_name,
                "total_documents": len(collection_info.get("ids", [])),
                "persist_directory": self.persist_directory
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
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Vector store for embeddings with metadata"}
            )
            self.logger.info(f"Reset collection: {self.collection_name}")
        except Exception as e:
            self.logger.error(f"Failed to reset collection: {e}")
            raise

# Example usage and testing
if __name__ == "__main__":
    # Initialize vector store
    vector_store = VectorStore(collection_name="test_collection")
    
    # Example data
    embeddings = [[0.1] * 1536, [0.2] * 1536, [0.3] * 1536]
    chunks = ["Test case 1: User login functionality", 
              "Test case 2: Password reset feature", 
              "Test case 3: User profile update"]
    metadata = {
        "project_name": "test_project",
        "model_name": "text-embedding-ada-002",
        "source": "requirements_doc",
        "source_id": "req_001"
    }
    
    try:
        # Store embeddings
        inserted_count = vector_store.store_embeddings(embeddings, chunks, metadata)
        print(f"✅ Inserted {inserted_count} records")
        
        # Search by embedding
        query_embedding = [0.15] * 1536
        results = vector_store.search(query_embedding=query_embedding, n_results=3, project_name="test_project")
        print(f"🔍 Found {len(results)} similar records:")
        for result in results:
            print(f"  - Similarity: {result['similarity']:.3f}, Content: {result['content'][:50]}...")
        
        # Search by text
        text_results = vector_store.search(query_text="user login", n_results=2)
        print(f"📝 Text search found {len(text_results)} results")
        
        # Get stats
        stats = vector_store.get_collection_stats()
        print(f"📊 Collection stats: {stats}")
        
        # List projects
        projects = vector_store.list_projects()
        print(f"📁 Projects: {projects}")
        
        # Test deletion
        deleted_count = vector_store.delete_by_project("test_project")
        print(f"🗑️ Deleted {deleted_count} records")
        
    except Exception as e:
        print(f"❌ Error: {e}") 