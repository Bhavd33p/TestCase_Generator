import io
import re
import unicodedata
from openai import OpenAI
from fastapi import UploadFile, HTTPException
from PyPDF2 import PdfReader
from src.utilities.config_manager import load_config
from typing import List, Dict, Any
import logging
import json
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_numbered_requirements(text: str) -> list:
    pattern = r"\d+\.\s+(.*?)(?=\n\d+\.|\Z)"
    return [req.strip() for req in re.findall(pattern, text, re.DOTALL)]

def clean_text(text: str) -> str:
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")

async def process_pdf_file(file: UploadFile) -> str:
    """Process PDF file and extract text content."""
    contents = await file.read()
    reader = PdfReader(io.BytesIO(contents))
    text_parts = []
    
    for i, page in enumerate(reader.pages):
        page_text = page.extract_text() or ""
        if i > 0:
            text_parts.append("\nThe following content is a continuation of the previous page.\n")
        text_parts.append(page_text)
    
    raw_text = "".join(text_parts).strip()
    if not raw_text:
        raise HTTPException(status_code=400, detail="No text found in the PDF.")
    
    return clean_text(raw_text)

class RequirementExtractor:
    def __init__(self, config: Dict):
        self.config = config
        self.client = OpenAI(api_key=config['openai']['api_key'])
        self.llm = ChatOpenAI(
            api_key=config['openai']['api_key'],
            model=config['openai']['model'],
            temperature=config['openai']['temperature']
        )

    # def extract_requirements(self, documents: List[Document]) -> Dict[str, Any]:
    #     """Extract requirements from documents using LangChain."""
    #     try:
    #         requirements = []
    #         for doc in documents:
    #             prompt = f"""Extract requirements from the following text in JSON format:
                
    #             Text:
    #             {doc.page_content}
                
    #             Generate requirements with the following structure:
    #             {{
    #                 "requirement_id": "unique_id",
    #                 "requirement_text": "clear description",
    #                 "type": "Functional/Non-functional",
    #                 "priority": "High/Medium/Low",
    #                 "dependencies": ["list", "of", "dependencies"]
    #             }}
                
    #             Generate multiple requirements if needed. Return only the JSON array of requirements.
    #             """
                
    #             response = self.llm.invoke(prompt)
    #             try:
    #                 doc_requirements = json.loads(response.content)
    #                 if isinstance(doc_requirements, list):
    #                     requirements.extend(doc_requirements)
    #                 else:
    #                     requirements.append(doc_requirements)
    #             except json.JSONDecodeError:
    #                 logger.warning(f"Failed to parse requirements from response: {response.content}")
    #                 continue

    #         return {
    #             "status": "success",
    #             "requirements": requirements,
    #             "num_documents": len(documents)
    #         }

    #     except Exception as e:
    #         logger.error(f"Error extracting requirements: {str(e)}")
    #         raise Exception(f"Failed to extract requirements: {str(e)}")

    async def extract_requirements_from_pdf(self, file: UploadFile, model_name: str) -> List[str]:
        """Extract requirements from PDF file using OpenAI."""
        try:
            safe_text = await process_pdf_file(file)
            prompt = (
                "You are a domain expert in the insurance industry and a skilled requirements analyst. "
                "From the following document, extract software requirements that are complete, well-structured, and industry-relevant. "
                "Ensure every relevant detail is included, and avoid using any formatting such as bold text, headings, bullet points, or special characters—only plain text in a numbered list format. "
                "Avoid missing any important information. Use plain English and organize the requirements logically.\n\n"
                "Document Content:\n"
                f"{safe_text}"
            )

            response = self.client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are a requirements extractor."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.7
            )

            generated_text = response.choices[0].message.content.strip()
            return extract_numbered_requirements(generated_text)

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing PDF: {e}")
