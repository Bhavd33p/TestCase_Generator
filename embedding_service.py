import logging
import os
import torch
from typing import List, Optional, Dict, Any, Union
from sentence_transformers import SentenceTransformer
import numpy as np
from langchain.text_splitter import RecursiveCharacterTextSplitter
import tiktoken
import hashlib
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmbeddingService:
    """
    Robust embedding service with comprehensive error handling,
    batch processing, and ChromaDB compatibility.
    """
    
    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        device: Optional[str] = None,
        batch_size: int = 32,
        max_seq_length: int = 512
    ):
        """
        Initialize the embedding service.
        
        Args:
            model_name: Name of the sentence transformer model
            device: Device to use ('cuda', 'cpu', or None for auto-detection)
            batch_size: Batch size for processing
            max_seq_length: Maximum sequence length
        """
        self.model_name = model_name
        self.batch_size = batch_size
        self.max_seq_length = max_seq_length
        self.model = None
        self.device = self._detect_device(device)
        self.text_splitter = None
        self.tokenizer = None
        
        # Initialize components
        self._initialize_model()
        self._initialize_text_splitter()
        
        logger.info(f"EmbeddingService initialized with model: {model_name}, device: {self.device}")
    
    def _detect_device(self, device: Optional[str] = None) -> str:
        """Auto-detect the best available device."""
        if device:
            return device
        
        if torch.cuda.is_available():
            device = "cuda"
            logger.info("CUDA detected, using GPU")
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            device = "mps"
            logger.info("MPS detected, using Apple Silicon GPU")
        else:
            device = "cpu"
            logger.info("Using CPU")
        
        return device
    
    def _initialize_model(self):
        """Initialize the sentence transformer model with error handling."""
        try:
            self.model = SentenceTransformer(self.model_name, device=self.device)
            self.model.max_seq_length = self.max_seq_length
            logger.info(f"Model {self.model_name} loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model {self.model_name}: {e}")
            # Fallback to a smaller model
            try:
                self.model_name = "all-MiniLM-L6-v2"
                self.model = SentenceTransformer(self.model_name, device=self.device)
                logger.info(f"Fallback model {self.model_name} loaded successfully")
            except Exception as fallback_error:
                logger.error(f"Failed to load fallback model: {fallback_error}")
                raise RuntimeError("Could not initialize any embedding model")
    
    def _initialize_text_splitter(self):
        """Initialize text splitter with tiktoken or fallback."""
        try:
            # Try to use tiktoken for better tokenization
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=50,
                length_function=self._tiktoken_len,
                separators=["\n\n", "\n", " ", ""]
            )
            logger.info("Text splitter initialized with tiktoken")
        except Exception as e:
            logger.warning(f"Failed to initialize tiktoken: {e}, using character-based splitter")
            # Fallback to character-based splitting
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=50,
                separators=["\n\n", "\n", " ", ""]
            )
    
    def _tiktoken_len(self, text: str) -> int:
        """Calculate text length using tiktoken."""
        try:
            if self.tokenizer:
                return len(self.tokenizer.encode(text))
            return len(text)
        except Exception:
            return len(text)
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        if not text or not isinstance(text, str):
            return ""
        
        # Remove excessive whitespace
        text = " ".join(text.split())
        
        # Remove control characters
        text = "".join(char for char in text if ord(char) >= 32 or char in ['\n', '\t'])
        
        return text.strip()
    
    def _generate_chunk_id(self, text: str, index: int) -> str:
        """Generate a unique ID for a text chunk."""
        content_hash = hashlib.md5(text.encode()).hexdigest()[:8]
        return f"chunk_{index}_{content_hash}"
    
    def create_embeddings(self, texts: Union[str, List[str]]) -> List[List[float]]:
        """
        Create embeddings for text(s) with batch processing.
        
        Args:
            texts: Single text string or list of texts
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            logger.warning("Empty texts provided to create_embeddings")
            return []
        
        # Ensure texts is a list
        if isinstance(texts, str):
            texts = [texts]
        
        # Clean texts
        cleaned_texts = [self._clean_text(text) for text in texts]
        cleaned_texts = [text for text in cleaned_texts if text]  # Remove empty strings
        
        if not cleaned_texts:
            logger.warning("No valid texts after cleaning")
            return []
        
        try:
            # Process in batches
            all_embeddings = []
            for i in range(0, len(cleaned_texts), self.batch_size):
                batch = cleaned_texts[i:i + self.batch_size]
                
                try:
                    batch_embeddings = self.model.encode(
                        batch,
                        convert_to_tensor=False,
                        show_progress_bar=False,
                        batch_size=len(batch)
                    )
                    
                    # Ensure embeddings are lists of floats
                    if isinstance(batch_embeddings, np.ndarray):
                        batch_embeddings = batch_embeddings.tolist()
                    
                    all_embeddings.extend(batch_embeddings)
                    
                except Exception as batch_error:
                    logger.error(f"Error processing batch {i//self.batch_size + 1}: {batch_error}")
                    # Create zero embeddings for failed batch
                    embedding_dim = self.get_embedding_dimension()
                    zero_embeddings = [[0.0] * embedding_dim] * len(batch)
                    all_embeddings.extend(zero_embeddings)
            
            logger.info(f"Created {len(all_embeddings)} embeddings")
            return all_embeddings
            
        except Exception as e:
            logger.error(f"Failed to create embeddings: {e}")
            # Return zero embeddings as fallback
            embedding_dim = self.get_embedding_dimension()
            return [[0.0] * embedding_dim] * len(cleaned_texts)
    
    def create_query_embedding(self, query: str) -> List[float]:
        """
        Create embedding for a single query.
        
        Args:
            query: Query text
            
        Returns:
            Embedding vector
        """
        if not query or not isinstance(query, str):
            logger.warning("Invalid query provided")
            return [0.0] * self.get_embedding_dimension()
        
        cleaned_query = self._clean_text(query)
        if not cleaned_query:
            logger.warning("Empty query after cleaning")
            return [0.0] * self.get_embedding_dimension()
        
        try:
            embedding = self.model.encode([cleaned_query], convert_to_tensor=False)[0]
            
            if isinstance(embedding, np.ndarray):
                embedding = embedding.tolist()
            
            return embedding
            
        except Exception as e:
            logger.error(f"Failed to create query embedding: {e}")
            return [0.0] * self.get_embedding_dimension()
    
    def split_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Split text into chunks with metadata.
        
        Args:
            text: Text to split
            metadata: Optional metadata to attach to chunks
            
        Returns:
            List of chunk dictionaries with text, metadata, and IDs
        """
        if not text or not isinstance(text, str):
            logger.warning("Invalid text provided for splitting")
            return []
        
        cleaned_text = self._clean_text(text)
        if not cleaned_text:
            logger.warning("Empty text after cleaning")
            return []
        
        try:
            chunks = self.text_splitter.split_text(cleaned_text)
            
            chunk_docs = []
            for i, chunk in enumerate(chunks):
                if chunk.strip():  # Only include non-empty chunks
                    chunk_metadata = metadata.copy() if metadata else {}
                    chunk_metadata.update({
                        "chunk_index": i,
                        "chunk_id": self._generate_chunk_id(chunk, i),
                        "chunk_length": len(chunk),
                        "total_chunks": len(chunks)
                    })
                    
                    chunk_docs.append({
                        "text": chunk.strip(),
                        "metadata": chunk_metadata,
                        "id": chunk_metadata["chunk_id"]
                    })
            
            logger.info(f"Split text into {len(chunk_docs)} chunks")
            return chunk_docs
            
        except Exception as e:
            logger.error(f"Failed to split text: {e}")
            # Return original text as single chunk
            chunk_id = self._generate_chunk_id(cleaned_text, 0)
            return [{
                "text": cleaned_text,
                "metadata": {
                    **(metadata or {}),
                    "chunk_index": 0,
                    "chunk_id": chunk_id,
                    "chunk_length": len(cleaned_text),
                    "total_chunks": 1
                },
                "id": chunk_id
            }]
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings produced by the model."""
        try:
            if self.model:
                return self.model.get_sentence_embedding_dimension()
            return 384  # Default dimension for all-MiniLM-L6-v2
        except Exception:
            return 384
    
    def validate_embeddings(self, embeddings: List[List[float]]) -> bool:
        """
        Validate that embeddings have correct format and dimensions.
        
        Args:
            embeddings: List of embedding vectors
            
        Returns:
            True if valid, False otherwise
        """
        if not embeddings:
            return False
        
        expected_dim = self.get_embedding_dimension()
        
        for i, embedding in enumerate(embeddings):
            if not isinstance(embedding, list):
                logger.error(f"Embedding {i} is not a list")
                return False
            
            if len(embedding) != expected_dim:
                logger.error(f"Embedding {i} has dimension {len(embedding)}, expected {expected_dim}")
                return False
            
            if not all(isinstance(x, (int, float)) for x in embedding):
                logger.error(f"Embedding {i} contains non-numeric values")
                return False
        
        return True
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model."""
        return {
            "model_name": self.model_name,
            "device": self.device,
            "embedding_dimension": self.get_embedding_dimension(),
            "max_seq_length": self.max_seq_length,
            "batch_size": self.batch_size
        }
    
    def __del__(self):
        """Cleanup resources."""
        try:
            if hasattr(self, 'model') and self.model:
                del self.model
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except Exception:
            pass 