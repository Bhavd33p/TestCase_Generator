import re
from typing import List  
import requests
from fastapi import HTTPException
from src.models.test_template import PromptRequest, TestTemplate, TestCasePrompt
import json
from src.utilities.config_manager import load_config
from src.services.ollama_service import OllamaService

# Initialize config
config = load_config()

class TestCaseGeneratorService:
    def __init__(self, model_name: str, template_columns: List[str], springboot_url: str):
        self.model_name = model_name
        self.template_columns = template_columns
        self.springboot_url = springboot_url
        self.ollama_service = OllamaService()

    def fetch_template(self, project_name: str):
        """Fetch the test template for the given project."""
        return self.db_service.get_test_template_by_project(project_name)

    def generate_test_case(self, prompt: str, project_name: str, source: str, source_id: str = None, hash: str = None, start_req_index: int = 1, start_index: int = 1, last_req_prefix: str = None, last_prefix: str = None) -> dict:
        """Generate test cases using Ollama and return them without storing in MongoDB."""

        try:
            print("\n🔹 Full Request Data Received in Test Case Generator:")
            print(f"Prompt: {prompt}")
            print(f"Project Name: {project_name}")
            print(f"Source: {source}")
            print(f"Source ID: {source_id}")  
            print(f"Hash: {hash}")
            print(f"Template Columns: {self.template_columns}")

            prefix_instruction = ""
            if last_prefix:
                prefix_instruction += f"\nUse the test case ID prefix '{last_prefix}' and start numbering from {start_index:03}."
            if last_req_prefix:
                prefix_instruction += f"\nUse the requirement ID prefix '{last_req_prefix}' and start numbering from {start_req_index:03}."

            template_structure = "\n".join([f"- {col}: <Provide details>" for col in self.template_columns])
            enhanced_prompt = (
                f"Generate test cases using the following structure:\n\n"
                f"{template_structure}\n\n"
                f"Context:\n{prompt}\n\n"
                f"{prefix_instruction}\n"
                "Ensure the output is structured correctly with each field in a separate line with the field name with it, do not use any formatting like headings, bold text or bullet points."
            )

            # Generate completion using Ollama
            generated_text = self.ollama_service.generate_completion(
                prompt=enhanced_prompt,
                model=self.model_name,
                temperature=0.7
            ).strip()

            print("Generated Text:\n", generated_text,"\n\n")

            test_cases = []
            for case in generated_text.split("\n\n"):
                formatted_case = {}

                for col in self.template_columns:
                    col_pattern = re.compile(rf"[-\s]*\**{re.escape(col)}\**:\s*(.+?)(?=\n[-\s]*\**[A-Za-z ]+\**:|\n---|\Z)", re.DOTALL)
                    match = col_pattern.search(case)
                    extracted_value = match.group(1).strip() if match else "N/A"
                    extracted_value = re.sub(r"\*\*|\n---|\n\s*- ", "", extracted_value).strip()
                    formatted_case[col] = extracted_value

                test_cases.append(formatted_case)

            print("Extracted Test Cases:\n", test_cases)
            if not test_cases:
                raise ValueError("Extracted test cases list is empty. Possible formatting issue in AI response.")

            payload = {
                "project_name": project_name,
                "generated_test_cases": test_cases,
                "source": source
            }

            if source in ["jira", "confluence"]:
                payload["source_id"] = source_id
            elif source in ["word", "text", "plaintext"]:
                payload["hash"] = hash

            print("Sending Data to Spring Boot:", payload)

            springboot_response = requests.post(
                f"{self.springboot_url}/api/process/{source}",  
                json=payload
            )

            if springboot_response.status_code == 200:
                print("Test cases successfully stored in Spring Boot!")
                return springboot_response.json()   
            else:
                print("Failed to store test cases in Spring Boot:", springboot_response.text)
                return {"error": "Failed to store test cases in Spring Boot", "details": springboot_response.text}

        except Exception as e:
            print("Error:", str(e))
            return {"error": f"Error generating test case: {str(e)}"}