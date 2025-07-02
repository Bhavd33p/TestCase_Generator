from typing import List, Dict, Any, Optional
import logging
import json
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI
from src.services.embedding_service import EmbeddingService
from src.services.vector_store_service import VectorStore

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestCaseService:
    def __init__(self, config: Dict):
        """
        Initialize the test case service.
        
        Args:
            config (Dict): Configuration dictionary containing OpenAI API key
        """
        self.logger = logging.getLogger(__name__)
        try:
            self.config = config
            self.embedding_service = EmbeddingService(config=config)
            self.vector_store = VectorStore(config=config)
            self.llm = ChatOpenAI(
                api_key=config['openai']['api_key'],
                model=config['openai']['model'],
                temperature=config['openai']['temperature']
            )
            self.logger.info("Test case service initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing test case service: {str(e)}")
            raise

    def generate_test_cases_from_documents(
        self,
        documents: List[Document],
        project_name: str,
        source: str
    ) -> Dict[str, Any]:
        """
        Generate test cases from documents.
        
        Args:
            documents (List[Document]): List of documents to process
            project_name (str): Name of the project
            source (str): Source of the documents
            
        Returns:
            Dict[str, Any]: Generated test cases
        """
        try:
            # Add metadata to documents
            for doc in documents:
                doc.metadata.update({
                    "project_name": project_name,
                    "source": source
                })

            # Generate embeddings and store documents
            embeddings = self.embedding_service.embed_documents(documents)
            self.vector_store.add_documents(documents, embeddings)

            # Generate test cases using OpenAI
            test_cases = []
            for doc in documents:
                prompt = f"""Based on the following requirements, generate test cases in JSON format:
                
                Requirements:
                {doc.page_content}
                
                Generate test cases with the following structure:
                {{
                    "test_case_id": "unique_id",
                    "test_case_name": "descriptive_name",
                    "preconditions": ["list", "of", "preconditions"],
                    "test_steps": ["step1", "step2", "step3"],
                    "expected_results": ["expected1", "expected2"],
                    "priority": "High/Medium/Low",
                    "test_type": "Functional/Non-functional"
                }}
                
                Generate multiple test cases if needed. Return only the JSON array of test cases.
                """
                
                response = self.llm.invoke(prompt)
                try:
                    doc_test_cases = json.loads(response.content)
                    if isinstance(doc_test_cases, list):
                        test_cases.extend(doc_test_cases)
                    else:
                        test_cases.append(doc_test_cases)
                except json.JSONDecodeError:
                    self.logger.warning(f"Failed to parse test cases from response: {response.content}")
                    continue

            return {
                "status": "success",
                "test_cases": test_cases,
                "num_documents": len(documents)
            }

        except Exception as e:
            self.logger.error(f"Error generating test cases: {str(e)}")
            raise Exception(f"Failed to generate test cases: {str(e)}")

    def get_project_test_cases(
        self,
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
            # Search for project documents
            results = self.vector_store.search(
                query=project_name,
                n_results=n_results,
                filter_metadata={"project_name": project_name}
            )

            return results

        except Exception as e:
            self.logger.error(f"Error getting project test cases: {str(e)}")
            raise Exception(f"Failed to get project test cases: {str(e)}") 