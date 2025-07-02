from fastapi import FastAPI, HTTPException, Request, APIRouter, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse,StreamingResponse
from src.models.test_template import PromptRequest, TestTemplate, TestCaseRequest
from src.utilities.config_manager import load_config
import pandas as pd
from io import BytesIO
from typing import Optional, Dict, List, Any
import json
import logging
import time
import requests
from src.utilities.id_extractor import get_last_ids
from src.services.requirement_extractor import RequirementExtractor
from src.services.test_case_generator_from_pdf import TestCaseService
from uuid import uuid4
from langchain_core.documents import Document
import yaml
from src.utilities.file_processor import process_uploaded_file

# Import our improved services
from src.services.embedding_service import EmbeddingService
from src.services.vector_store_service import VectorStore
from src.services.text_extraction_service import TextExtractionService
from src.services.adaptive_rag_service import AdaptiveRAGService
SPRINGBOOT_URL = "http://localhost:8081/api"
# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)
    print(config["openai"]["api_key"])

# Initialize services
test_case_service = TestCaseService(config=config)
text_extractor = TextExtractionService()
embedding_service = EmbeddingService(config=config)
vector_store = VectorStore(config=config)
# requirement_extractor =  RequirementExtractor.extract_requirements_from_pdf()

def get_embedding_service():
    """Get or create embedding service instance"""
    global embedding_service
    if embedding_service is None:
        embedding_service = EmbeddingService()
        logger.info("EmbeddingService initialized")
    return embedding_service

def get_vector_store(collection_name: str = "software_documents"):
    """Get or create vector store instance"""
    global vector_store
    if vector_store is None:
        vector_store = VectorStore(collection_name=collection_name, config=config)
        logger.info(f"VectorStore initialized with collection: {collection_name}")
    return vector_store

# FastAPI app setup
app = FastAPI(
    title="Test Case Generation API",
    description="Enhanced API for test case generation with vector embeddings",
    version="2.0.0"
)

# CORS middleware
origins = [
    "http://localhost:3000", 
    "http://localhost:8081",  
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"],    
    allow_headers=["*"],   
)

# Router setup
test_case_router = APIRouter(prefix="/test-cases", tags=["Test Cases"])

@test_case_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "services": {
            "embedding_service": "ready",
            "vector_store": "ready",
            "text_extractor": "ready"
        }
    }
@test_case_router.post("/embed-documents/{file_type}")
async def embed_documents(
    file_type: str,
    files: List[UploadFile] = File(..., description="List of files to embed"),
    project_name: str = Form("default"),
    model_name: str = Form(None),
    source: str = Form("upload")
) -> Dict[str, Any]:
    """
    Embed multiple documents from uploaded files.
    Args:
        file_type (str): Type of file (pdf, word, etc.)
        files (List[UploadFile]): Uploaded files
        project_name (str): Name of the project
        model_name (str): Name of the model (optional)
        source (str): Source of the file (e.g., SWAD, ICD, etc.)
    Returns:
        Dict[str, Any]: Embedding results for all files
    """
    results = []
    try:
        for file in files:
            # Process uploaded file
          
            documents = await process_uploaded_file(file, file_type)
            # Add metadata
            for doc in documents:
                doc.metadata.update({
                    "project_name": project_name,
                    "model_name": model_name,
                    "source": source,
                    "filename": file.filename,
                    "content_type": file.content_type
                })
            # Generate embeddings and store documents
            embeddings = test_case_service.embedding_service.embed_documents(documents)
            result = test_case_service.vector_store.add_documents(documents, embeddings)
            results.append({
                "filename": file.filename,
                "status": result.get("status", "unknown"),
                "num_documents": result.get("num_documents", 0)
            })
        return {"results": results, "total_files": len(results)}
    except Exception as e:
        logger.error(f"Error embedding documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@test_case_router.get("/project/{project_name}")
async def get_project_test_cases(
    project_name: str,
    n_results: int = 5
) -> List[Dict[str, Any]]:
    """
    Get test cases for a project.
    
    Args:
        project_name (str): Name of the project
        n_results (int): Number of results to return
        
    Returns:
        List[Dict[str, Any]]: Test cases
    """
    try:
        return test_case_service.get_project_test_cases(project_name, n_results)
    except Exception as e:
        logger.error(f"Error getting project test cases: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@test_case_router.post("/generate-test-cases/{file_type}")
async def generate_test_cases(
    file: UploadFile = File(...),
    project_name: str = Form("default"),
    model_name: Optional[str] = Form("gpt-4"),
    source: str = Form("upload"),
    template_columns: Optional[str] = Form(None),
    source_id: Optional[str] = Form(None)
):
    try:
        logger.info(f"[START] Generating test cases")
        logger.info(f"Received file: {file.filename}")
        logger.info(f"Project: {project_name}, Source: {source}, Model: {model_name}")

        # Step 1: Extract requirements from PDF
        logger.info("Step 1: Extracting requirements from PDF...")
        requirement_extractor = RequirementExtractor(config)
        extracted_requirements = await requirement_extractor.extract_requirements_from_pdf(file, model_name)

        if not extracted_requirements:
            logger.warning("No requirements extracted from PDF.")
            raise HTTPException(status_code=400, detail="No requirements extracted from PDF.")

        logger.info(f"Extracted {len(extracted_requirements)} requirements")

        # Step 2: Parse template_columns JSON
        if not template_columns:
            logger.error("Missing template_columns in request")
            raise HTTPException(status_code=400, detail="Missing template_columns")

        try:
            parsed_template_columns = json.loads(template_columns)
            logger.info(f"Parsed template_columns: {parsed_template_columns}")
        except json.JSONDecodeError:
            logger.error("Invalid JSON format in template_columns")
            raise HTTPException(status_code=400, detail="Invalid template_columns JSON")

        # Step 3: Generate test cases using Adaptive RAG
        logger.info("Step 3: Calling Adaptive RAG pipeline for test case generation...")
        adaptive_rag = AdaptiveRAGService(config=config)
        result = await adaptive_rag.process_query(
            requirements=extracted_requirements,
            template_columns=parsed_template_columns,
            project_name=project_name,
            filter_metadata={"project_name": project_name},
            n_results=5
        )

        test_cases = result.get("test_cases", [])
        logger.info(f"Adaptive RAG returned {len(test_cases)} test cases")

        if not test_cases:
            logger.warning("Adaptive RAG returned no test cases.")
            raise HTTPException(status_code=204, detail="No test cases generated.")
       
        # Log type of test_cases
        logger.info(f"Type of test_cases: {type(test_cases)}")

        # Log number of test cases if it's a list
        if isinstance(test_cases, list):
            logger.info(f"Number of test cases: {len(test_cases)}")
        else:
            logger.warning("test_cases is not a list!")

        # Log test_cases content (first 3 items only to avoid flooding logs)
        try:
            logger.info("Sample test_cases payload:")
            logger.info(json.dumps(test_cases[:3], indent=2, ensure_ascii=False))
        except Exception as e:
            logger.error(f"Failed to log test_cases sample: {e}")

        # Step 4: Filter test cases to only include template columns
        filtered_test_cases = []
        for tc in test_cases:
            filtered = {}
            for col in parsed_template_columns:
                if col == "Test Case ID":
                    filtered[col] = tc.get("id", tc.get(col, ""))
                elif col=="Requirement ID":
                    filtered[col]=tc.get("requirement_id",tc.get(col,""))
                else:
                    filtered[col] = tc.get(col, "")
            filtered_test_cases.append(filtered)

        payload = {
                    "project_name": project_name,
                    "generated_test_cases": filtered_test_cases,
                    "source": source
                }
        # if source_id:
        #     payload["source_id"] = source_id
        # if hash:
        #     payload["hash"] = hash

        # POST to Spring Boot
        springboot_response = requests.post(
            f"{SPRINGBOOT_URL}/process-json",
            json=payload
        )

        if springboot_response.status_code == 200:
            logger.info("Download URL set to: %s", springboot_response.json().get("download_url"))
            return springboot_response.json()
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to store test cases in Spring Boot: {springboot_response.text}"
            )

    except HTTPException as http_exc:
        logger.error(f"HTTPException: {http_exc.detail}")
        raise
    except Exception as e:
        logger.exception("Unexpected error during test case generation")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@test_case_router.post("/search")
async def search_documents(
    query: str = Form(..., description="Search query"),
    collection_name: str = Form(default="software_documents", description="Collection to search"),
    project_name: Optional[str] = Form(default=None, description="Filter by project name"),
    n_results: int = Form(default=5, description="Number of results to return")
):
    """Search for similar documents in the vector database"""
    processing_id = str(uuid4())
    logger.info(f"[{processing_id}] Searching for: {query}")
    
    try:
        embedding_svc = get_embedding_service()
        vector_db = get_vector_store(collection_name)
        
        # Generate query embedding
        query_embedding = embedding_svc.embed_query(query)
        
        # Search vector database
        results = vector_db.search(
            query_embedding=query_embedding,
            n_results=n_results,
            project_name=project_name
        )
        
        logger.info(f"[{processing_id}] Found {len(results)} results")
        
        return JSONResponse(
            status_code=200,
            content={
                "processing_id": processing_id,
                "query": query,
                "filters": {
                    "project_name": project_name,
                    "collection_name": collection_name
                },
                "results": results,
                "total_results": len(results),
                "timestamp": time.time()
            }
        )
    except Exception as e:
        logger.error(f"[{processing_id}] Search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


app.include_router(test_case_router)

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    try:
        # Initialize all services
        get_embedding_service()
        get_vector_store()
        logger.info("All services initialized successfully")
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)