from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
from typing import List, Optional, Dict, Any
import os
import logging
from dotenv import load_dotenv
import torch
from sentence_transformers import SentenceTransformer
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self, config: Dict = None):
        """
        Initialize the embedding service.
        
        Args:
            config (Dict): Configuration dictionary containing OpenAI API key
        """
        self.logger = logging.getLogger(__name__)
        try:
            # Get OpenAI API key from config
            api_key = config.get("openai", {}).get("api_key")
            if not api_key:
                raise ValueError("OpenAI API key not found in config")

            # Initialize OpenAI embeddings
            self.embeddings = OpenAIEmbeddings(
                openai_api_key=api_key,
                model=config["openai"]["embedding_model"]
            )
            # Set embedding_model to self.embeddings for compatibility
            self.embedding_model = self.embeddings
            
            # Initialize text splitter
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
                separators=["\n\n", "\n", " ", ""]
            )
            
            self.logger.info("Embedding service initialized with OpenAI")
        except Exception as e:
            self.logger.error(f"Error initializing embedding service: {str(e)}")
            raise

    def split_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[Document]:
        """
        Split text into chunks and create Document objects.
        
        Args:
            text (str): Text to split
            chunk_size (int): Size of each chunk
            overlap (int): Overlap between chunks
            
        Returns:
            List[Document]: List of Document objects
        """
        try:
            # Update splitter parameters if different from default
            if chunk_size != 1000 or overlap != 200:
                self.text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=chunk_size,
                    chunk_overlap=overlap,
                    length_function=len,
                    separators=["\n\n", "\n", " ", ""]
                )
            
            # Split text into chunks
            chunks = self.text_splitter.split_text(text)
            
            # Create Document objects
            documents = [
                Document(
                    page_content=chunk,
                    metadata={"chunk_index": i}
                )
                for i, chunk in enumerate(chunks)
            ]
            
            self.logger.info(f"Split text into {len(documents)} chunks")
            return documents
            
        except Exception as e:
            self.logger.error(f"Error splitting text: {str(e)}")
            raise Exception(f"Failed to split text: {str(e)}")

    def _initialize_embedding_model(self, device: Optional[str] = None):
        """Initialize the HuggingFace embedding model with proper error handling"""
        try:
            # Determine device
            if device is None:
                device = "cuda" if torch.cuda.is_available() else "cpu"
            
            # Model kwargs for better performance
            model_kwargs = {
                'device': device,
                'trust_remote_code': True
            }
            
            # Encode kwargs for better performance
            encode_kwargs = {
                'normalize_embeddings': True,  # Normalize embeddings for better similarity search
                'batch_size': 32  # Process in batches for efficiency
            }
            
            self.embedding_model = HuggingFaceEmbeddings(
                model_name=self.model_name,
                model_kwargs=model_kwargs,
                encode_kwargs=encode_kwargs
            )
            
            # Test the model with a simple embedding
            test_embedding = self.embedding_model.embed_query("test")
            self.embedding_dim = len(test_embedding)
            
            self.logger.info(f"Embedding model loaded successfully on {device}")
            self.logger.info(f"Embedding dimension: {self.embedding_dim}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize embedding model: {e}")
            raise RuntimeError(f"Could not load embedding model '{self.model_name}': {e}")

    def _initialize_text_splitter(self):
        """Initialize the text splitter with fallback options"""
        try:
            # Try tiktoken-based splitter first (more accurate for token counting)
            self.text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                separators=["\n\n", "\n", ". ", " ", ""]  # Better separation hierarchy
            )
            self.logger.info("Initialized tiktoken-based text splitter")
            
        except Exception as e:
            self.logger.warning(f"Tiktoken splitter failed, using character-based: {e}")
            # Fallback to character-based splitter
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                separators=["\n\n", "\n", ". ", " ", ""]
            )
            self.logger.info("Initialized character-based text splitter")

    def split_text(self, raw_text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Document]:
        """
        Splits the input raw text into smaller chunks using LangChain's RecursiveCharacterTextSplitter.
        
        Args:
            raw_text: The text to split
            metadata: Optional metadata to attach to each document chunk
            
        Returns:
            List of LangChain Document objects with metadata
        """
        if not raw_text or not raw_text.strip():
            self.logger.warning("Empty or whitespace-only text provided")
            return []
        
        try:
            # Clean the text
            cleaned_text = self._clean_text(raw_text)
            
            # Create document with metadata
            base_metadata = metadata or {}
            document = Document(
                page_content=cleaned_text,
                metadata=base_metadata
            )
            
            # Split the document
            chunks = self.text_splitter.split_documents([document])
            
            # Add chunk-specific metadata
            for i, chunk in enumerate(chunks):
                chunk.metadata.update({
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "chunk_size": len(chunk.page_content),
                    "source_length": len(cleaned_text)
                })
            
            self.logger.info(f"Split text into {len(chunks)} chunks")
            return chunks
            
        except Exception as e:
            self.logger.error(f"Failed to split text: {e}")
            raise RuntimeError(f"Text splitting failed: {e}")

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text for better processing"""
        # Remove excessive whitespace
        text = " ".join(text.split())
        
        # Remove or replace problematic characters
        text = text.replace('\x00', '')  # Remove null bytes
        text = text.replace('\r\n', '\n')  # Normalize line endings
        text = text.replace('\r', '\n')
        
        # Remove excessive newlines
        while '\n\n\n' in text:
            text = text.replace('\n\n\n', '\n\n')
        
        return text.strip()

    def embed_documents(self, documents: List[Document]) -> List[List[float]]:
        """
        Generates vector embeddings from a list of LangChain Document objects.
        
        Args:
            documents: List of Document objects to embed
            
        Returns:
            List of embedding vectors (each vector is a list of floats)
        """
        if not documents:
            self.logger.warning("No documents provided for embedding")
            return []
        
        try:
            # Extract text content from documents
            texts = []
            for doc in documents:
                if not doc.page_content or not doc.page_content.strip():
                    self.logger.warning("Skipping empty document")
                    continue
                texts.append(doc.page_content)
            
            if not texts:
                self.logger.warning("No valid text content found in documents")
                return []
            
            # Generate embeddings in batches for memory efficiency
            embeddings = self._embed_texts_in_batches(texts)
            
            self.logger.info(f"Generated embeddings for {len(embeddings)} documents")
            return embeddings
            
        except Exception as e:
            self.logger.error(f"Failed to embed documents: {e}")
            raise RuntimeError(f"Document embedding failed: {e}")

    def _embed_texts_in_batches(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """Embed texts in batches to manage memory usage"""
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            try:
                batch_embeddings = self.embedding_model.embed_documents(batch)
                all_embeddings.extend(batch_embeddings)
                self.logger.debug(f"Processed batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}")
            except Exception as e:
                self.logger.error(f"Failed to embed batch {i//batch_size + 1}: {e}")
                raise
        
        return all_embeddings

    def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for a single query string.
        
        Args:
            query: Query string to embed
            
        Returns:
            Embedding vector as list of floats
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        
        try:
            cleaned_query = self._clean_text(query)
            embedding = self.embedding_model.embed_query(cleaned_query)
            self.logger.debug(f"Generated query embedding for: {query[:50]}...")
            return embedding
            
        except Exception as e:
            self.logger.error(f"Failed to embed query: {e}")
            raise RuntimeError(f"Query embedding failed: {e}")

    def get_embedding_dimension(self) -> int:
        """Get the dimension of the embedding vectors"""
        return self.embedding_dim

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model and configuration"""
        return {
            "model_name": self.model_name,
            "embedding_dimension": self.embedding_dim,
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "device": getattr(self.embedding_model.client, 'device', 'unknown')
        }

    def process_documents_for_storage(self, documents: List[Document]) -> tuple[List[List[float]], List[str], List[Dict[str, Any]]]:
        """
        Process documents for storage in vector database.
        
        Args:
            documents: List of Document objects
            
        Returns:
            Tuple of (embeddings, texts, metadatas) ready for vector store
        """
        if not documents:
            return [], [], []
        
        try:
            # Generate embeddings
            embeddings = self.embed_documents(documents)
            
            # Extract texts and metadata
            texts = [doc.page_content for doc in documents]
            metadatas = [doc.metadata for doc in documents]
            
            # Validate consistency
            if len(embeddings) != len(texts) or len(texts) != len(metadatas):
                raise ValueError("Inconsistent lengths between embeddings, texts, and metadata")
            
            self.logger.info(f"Processed {len(documents)} documents for storage")
            return embeddings, texts, metadatas
            
        except Exception as e:
            self.logger.error(f"Failed to process documents for storage: {e}")
            raise 