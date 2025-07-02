from typing import List, Dict, Any, Optional
import logging
from langchain_core.documents import Document
# from src.services.ollama_service import OllamaService
from src.services.embedding_service import EmbeddingService
from src.services.vector_store_service import VectorStore
import json
from langchain.prompts import PromptTemplate
from langchain.prompts import ChatPromptTemplate
from langchain import hub
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
import re

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
class GradeHallucinations(BaseModel):
    """Binary score for hallucination present in generation answer."""
    binary_score: str = Field(description="Answer is grounded in the facts, 'yes' or 'no'")
class AdaptiveRAGService:
    def __init__(self, config: Dict):
        """
        Initialize the Adaptive RAG service.
        
        Args:
            config (Dict): Configuration dictionary
        """
        self.config = config
        # self.ollama_service = OllamaService()
        self.embedding_service = EmbeddingService(config=config)
        self.vector_store = VectorStore(config=config)
        logger.info("AdaptiveRAGService initialized")

    async def process_query(
        self,
        requirements: List[str],
        template_columns: List[str],
        project_name: str,
        filter_metadata: Optional[Dict[str, Any]] = None,
        n_results: int = 5
    ) -> Dict[str, Any]:
        """
        Process a list of requirements using adaptive RAG with consistent test case format.
        
        Args:
            requirements (List[str]): List of requirement strings
            template_columns (List[str]): Template columns for consistent format
            project_name (str): Project name for filtering and organization
            filter_metadata (Optional[Dict]): Additional filtering metadata
            n_results (int): Number of results to return per requirement
            
        Returns:
            Dict[str, Any]: Generated test cases with metadata
        """
        try:
            logger.info(f"Processing {len(requirements)} requirements for project: {project_name}")
            logger.info(f"Template columns: {template_columns}")
            
            all_test_cases = []
            adaptive_rag_metadata = {
                "total_requirements": len(requirements),
                "routes_taken": [],
                "documents_used_total": 0,
                "relevant_contexts_found": 0,
                "knowledge_base_fallbacks": 0,
                "grading_results": []
            }
            
            # Set up filter metadata
            if not filter_metadata:
                filter_metadata = {"project_name": project_name}
            elif "project_name" not in filter_metadata:
                filter_metadata["project_name"] = project_name
            
            # Process each requirement
            for idx, requirement in enumerate(requirements):
                logger.info(f"Processing requirement {idx + 1}/{len(requirements)}")
                
                try:
                    # Step 1: Generate query embedding and search
                    # requirement=requirements[0]
                    # idx=0
                    query_embedding = self.embedding_service.embed_query(requirement)
                    logger.info(f"Embedded requirement {idx + 1}")
                    
                    # Step 2: Search vector store for relevant documents
                    search_results = self.vector_store.search(
                        query=query_embedding,
                        n_results=n_results,
                        filter_metadata=filter_metadata
                    )
                    logger.info(f"Found {len(search_results)} documents for requirement {idx + 1}")
                    
                    # Step 3: Grade documents for relevance
                    relevant_context = ""
                    is_relevant = False
                    route_taken = "knowledge_base"
                    
                    if search_results:
                        context = "\n\n".join([result['text'] for result in search_results])
                        is_relevant = await self.grade_documents(query=requirement, context=context)
                        
                        if is_relevant:
                            relevant_context = context
                            route_taken = "rag_with_context"
                            adaptive_rag_metadata["relevant_contexts_found"] += 1
                            adaptive_rag_metadata["documents_used_total"] += len(search_results)
                        else:
                            adaptive_rag_metadata["knowledge_base_fallbacks"] += 1
                    else:
                        adaptive_rag_metadata["knowledge_base_fallbacks"] += 1
                    
                    adaptive_rag_metadata["routes_taken"].append(route_taken)
                    adaptive_rag_metadata["grading_results"].append({
                        "requirement_index": idx + 1,
                        "documents_found": len(search_results),
                        "is_relevant": is_relevant,
                        "route": route_taken
                    })
                    
                    # Step 4: Generate test cases using appropriate method
                    logger.info(is_relevant)
                    # logger.info(relevant_context)
                    if is_relevant and relevant_context:
                        # Use RAG with relevant context
                        logger.info(f"Generating with context for requirement {idx + 1}")
                        logger.info(f"Requirement: {requirement}")
                        logger.info(f"Context: {relevant_context[:100]}...")  # Log first 500 chars
                        logger.info(f"Template Columns: {template_columns}")
                        logger.info(f"Project Name: {project_name}")
                        test_cases = await self._generate_with_context(
                            requirement=requirement,
                            context=relevant_context,
                            template_columns=template_columns,
                            requirement_index=idx + 1,
                            project_name=project_name
                        )
                        logger.info(f"Generated {len(test_cases)} test cases using RAG with context")
                    else:
                        logger.info(f"Generating without context for requirement {idx + 1} (fallback)")
                        test_cases = await self._generate_with_context(
                            requirement=requirement,
                            context="",  # No context
                            template_columns=template_columns,
                            requirement_index=idx + 1,
                            project_name=project_name
                        )
                        logger.info(f"Generated {len(test_cases)} test cases using knowledge base")
                    
                    all_test_cases.extend(test_cases)
                    
                except Exception as e:
                    logger.error(f"Error processing requirement {idx + 1}: {e}")
            
            # Step 5: Ensure consistent IDs
            all_test_cases = await self._ensure_consistent_ids(all_test_cases)
            # Log number and sample of test cases
            logger.info(f"Total test cases collected: {len(all_test_cases)}")

            # Log a preview (first 3 test cases) to avoid log flooding
            try:
                preview = all_test_cases[:5] if isinstance(all_test_cases, list) else []
                logger.info("Sample test cases (first 3):")
                for i, tc in enumerate(preview, 1):
                    logger.info(f"Test Case {i}:\n{json.dumps(tc, indent=2, ensure_ascii=False)}")
            except Exception as log_ex:
                logger.warning(f"Failed to log test case preview: {log_ex}")

            
            # Step 6: Calculate success metrics
            successful_generations = sum(1 for route in adaptive_rag_metadata["routes_taken"] 
                                       if route not in ["error_fallback"])
            
            result = {
                "success": True,
                "project_name": project_name,
                "total_requirements_processed": len(requirements),
                "total_test_cases_generated": len(all_test_cases),
                "test_cases": all_test_cases,
                "adaptive_rag_metadata": {
                    **adaptive_rag_metadata,
                    "successful_generations": successful_generations,
                    "success_rate": successful_generations / len(requirements) if requirements else 0,
                    "pipeline_version": "adaptive_rag_v2.1"
                },
                "generation_summary": {
                    "requirements_with_relevant_context": adaptive_rag_metadata["relevant_contexts_found"],
                    "requirements_with_knowledge_base": adaptive_rag_metadata["knowledge_base_fallbacks"],
                    "total_documents_used": adaptive_rag_metadata["documents_used_total"],
                    "average_documents_per_requirement": (
                        adaptive_rag_metadata["documents_used_total"] / len(requirements) 
                        if requirements else 0
                    )
                }
            }
            
            logger.info(f"Adaptive RAG processing completed successfully")
            logger.info(f"Generated {len(all_test_cases)} test cases from {len(requirements)} requirements")
            logger.info(f"Success rate: {result['adaptive_rag_metadata']['success_rate']:.2%}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing requirements: {str(e)}")
            raise Exception(f"Requirements processing failed: {str(e)}")

    async def add_documents(
        self,
        documents: List[Document],
        project_name: str,
        source: str
    ) -> Dict[str, Any]:
        """
        Add documents to the RAG system.
        
        Args:
            documents (List[Document]): List of documents to add
            project_name (str): Project name
            source (str): Document source
            
        Returns:
            Dict[str, Any]: Processing results
        """
        try:
            # Generate embeddings
            embeddings = self.embedding_service.embed_documents(documents)
            
            # Add to vector store
            self.vector_store.add_documents(
                documents=documents,
                embeddings=embeddings
            )
            
            return {
                "status": "success",
                "num_documents": len(documents),
                "project_name": project_name,
                "source": source
            }
            
        except Exception as e:
            logger.error(f"Error adding documents: {str(e)}")
            raise Exception(f"Document addition failed: {str(e)}")

    async def get_project_stats(self, project_name: str) -> Dict[str, Any]:
        """
        Get statistics for a project.
        
        Args:
            project_name (str): Project name
            
        Returns:
            Dict[str, Any]: Project statistics
        """
        try:
            # Get collection stats
            stats = self.vector_store.get_stats()
            
            # Filter by project
            project_docs = self.vector_store.search(
                query="",
                n_results=1000,
                filter_metadata={"project_name": project_name}
            )
            
            return {
                "project_name": project_name,
                "total_documents": len(project_docs),
                "collection_stats": stats
            }
            
        except Exception as e:
            logger.error(f"Error getting project stats: {str(e)}")
            raise Exception(f"Failed to get project stats: {str(e)}") 
    async def grade_documents(self, query: str, context: str) -> bool:
        """Grade documents for relevance using binary scoring (yes/no)."""
        try:
            logger.info("Initializing grading LLM...")
            llm = ChatOpenAI(
                api_key=self.config["openai"]["api_key"],
                model=self.config["openai"]["model"],
                temperature=0.7
            )
            logger.info("Grading LLM initialized successfully.")

            prompt = PromptTemplate(
                template="""You are a grader assessing relevance of a retrieved document to a user question. \n 
                Here is the retrieved document: \n\n {document} \n\n
                Here is the user question: {question} \n
                If the document contains keywords related to the user question, grade it as relevant. \n
                It does not need to be a stringent test. The goal is to filter out erroneous retrievals. \n
                Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question. \n
                Provide the binary score as a JSON with a single key 'score' and no preamble or explanation.""",
                input_variables=["question", "document"],
            )

            logger.info("PromptTemplate created. Preparing to evaluate relevance...")

            retrieval_grader = prompt | llm | JsonOutputParser()

            # logger.debug(f"Grading Input — Query: {query[:100]}..., Context: {context[:200]}...")
            result = retrieval_grader.invoke({
                "question": query,
                "document": context
            })

            # logger.debug(f"Grading Output: {result}")
            decision = result.get('score', 'no').strip().lower() == 'yes'
            logger.info(f"Grading decision: {'Relevant' if decision else 'Not relevant'}")

            return 1

        except Exception as e:
            logger.exception("Error grading documents")
            return False
    async def _ensure_consistent_ids(self, test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Ensure consistent ID numbering across all test cases"""
        logger = logging.getLogger(__name__)
        for idx, test_case in enumerate(test_cases):
            test_case["Test Case ID"] = f"TC_{idx + 1:03d}"
            logger.info(f"Assigned test_case id: {test_case['Test Case ID']} for test case index {idx}")
            if "requirement_index" in test_case:
                test_case["Requirement ID"] = f"REQ_{test_case['requirement_index']:03d}"
                logger.info(f"Assigned requirement_id: {test_case['Requirement ID']} for requirement_index {test_case['requirement_index']}")
            else:
                logger.warning(f"No requirement_index found for test case index {idx}, skipping requirement_id assignment.")
        logger.info(f"Total test cases processed for ID assignment: {len(test_cases)}")
        return test_cases
    async def hallucination_grader(self, documents: str, generation: str) -> str:
        """Grade LLM generation for hallucination using OpenAI and LangChain."""
        llm = ChatOpenAI(
            api_key=self.config["openai"]["api_key"],
            model=self.config["openai"]["model"],
            temperature=0
        )
        prompt = (
            "You are a grader assessing whether an LLM generation is grounded in / supported by a set of retrieved facts.\n"
            "Give a binary score 'yes' or 'no'. 'Yes' means that the answer is grounded in / supported by the set of facts.\n"
            "Set of facts:\n\n{documents}\n\n"
            "LLM generation:\n{generation}\n\n"
            "Is the generation grounded in the facts? Respond with only 'yes' or 'no'."
        )
        # Format the prompt with the actual documents and generation
        formatted_prompt = prompt.format(documents=documents, generation=generation)
        response = await llm.ainvoke(formatted_prompt)
        # Extract the answer (yes/no) from the response
        return response.content.strip().lower()
    
    async def _generate_with_context(
        self,
        requirement: str,
        context: str,
        template_columns: list,
        requirement_index: int,
        project_name: str,
        source: str = "rag"
    ) -> list:
        """Generate test cases using RAG with relevant context, in your custom format."""
        try:
            logger.info(f"Starting test case generation for requirement index {requirement_index}")

            # Build the prompt
            logger.info("Constructing enhanced prompt from template columns")
            template_structure = "\n".join([f"- {col}: <Provide details>" for col in template_columns])
            enhanced_prompt = (
                f"Generate detailed test cases for the following specific requirement. Use the provided context for assistance.\n\n"
                f"**Requirement:**\n{requirement}\n\n"
                f"**Context:**\n{context}\n\n"
                f"**Output Format:**\n"
                f"Produce one or more test cases. Each test case must follow this structure exactly:\n"
                f"{template_structure}\n\n"
                f"Separate each test case with a line containing only '---'. "
                "Do not add any introductory or concluding text."
            )
            logger.debug(f"Enhanced prompt created:\n{enhanced_prompt[:500]}...")

            # Call OpenAI via LangChain
            logger.info("Calling LLM to generate test cases...")
            llm = ChatOpenAI(
                api_key=self.config["openai"]["api_key"],
                model=self.config["openai"]["model"],
                temperature=0.7
            )
            response = await llm.ainvoke(enhanced_prompt)
            generated_text = response.content.strip()
            logger.info("Received generation response from LLM")
            logger.info(f"Generated Text: {generated_text}")

            # Check for hallucination
            logger.info("Checking generation for hallucination...")
            hallucination_score = await self.hallucination_grader(context, generated_text)
            logger.info(f"Hallucination score: {hallucination_score}")

            if hallucination_score.strip().lower() == "no":
                logger.warning(f"Requirement {requirement_index}: Generation is hallucinated. Retrying with a stricter prompt.")
                
                # Build a stricter prompt
                stricter_prompt = (
                    f"You are a test case generator. You MUST ONLY use the information from the 'Context' provided. "
                    f"Do not add any information that is not present in the context. "
                    f"Generate detailed test cases for the following specific requirement based *strictly* on the provided context.\n\n"
                    f"**Requirement:**\n{requirement}\n\n"
                    f"**Context:**\n{context}\n\n"
                    f"**Output Format:**\n"
                    f"Produce one or more test cases. Each test case must follow this structure exactly:\n"
                    f"{template_structure}\n\n"
                    f"Separate each test case with a line containing only '---'. "
                    "Do not add any introductory or concluding text."
                )
                
                # Retry the call with the stricter prompt
                response = await llm.ainvoke(stricter_prompt)
                generated_text = response.content.strip()
                logger.info("Received response from retry with stricter prompt.")
                logger.info(f"New Generated Text: {generated_text}")


            # Parse the generated text
            logger.info("Parsing generated text into structured test cases")
            test_cases = []
            # Splitting by '---' separator which is more robust
            for case in re.split(r'\n\s*---\s*\n', generated_text):
                case = case.strip()
                if not case or "Test Case ID:" not in case:
                    continue
                
                formatted_case = {}
                for col in template_columns:
                    col_pattern = re.compile(
                        rf"[-\s]*\**{re.escape(col)}\**:\s*(.+?)(?=\n[-\s]*\**[A-Za-z ]+\**:|\n---|\Z)", re.DOTALL
                    )
                    match = col_pattern.search(case)
                    extracted_value = match.group(1).strip() if match else "N/A"
                    extracted_value = re.sub(r"\*\*|\n---|\n\s*- ", "", extracted_value).strip()
                    formatted_case[col] = extracted_value
                
                # Only add if we have found at least one piece of data.
                if any(v != "N/A" for v in formatted_case.values()):
                    logger.info(f"Extracted test case: {formatted_case}")
                    test_cases.append(formatted_case)


            if not test_cases:
                logger.warning("No test cases extracted. LLM response may be incorrectly formatted.")
                raise ValueError("Extracted test cases list is empty. Possible formatting issue in AI response.")

            for tc in test_cases:
                tc["project_name"] = project_name
                tc["requirement_index"] = requirement_index
                tc["source"] = source
                logger.info(
                    f"Enriched test case with project_name={project_name}, requirement_index={requirement_index}, source={source}"
                )

            logger.info(f"Successfully generated {len(test_cases)} test cases for requirement {requirement_index}")
            return test_cases

        except Exception as e:
            logger.error(f"Error generating test cases for requirement {requirement_index}: {e}", exc_info=True)
            return [{
                "project_name": project_name,
                "requirement_index": requirement_index,
                "source": source,
                "error": str(e)
            }]

