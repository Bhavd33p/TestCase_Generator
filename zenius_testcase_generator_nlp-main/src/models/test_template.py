from pydantic import BaseModel, Field
from typing import List, Optional

class TestTemplate(BaseModel):
    template_id: str
    columns: List[str]
    project_name: str = Field(..., description="Name of the project.")

class TestCasePrompt(BaseModel):
    prompt: str
    model_name: str
    project_name: str
    source: str  
    source_id: Optional[str] = None   
    hash: Optional[str] = None  
    
class TestCaseRequest(BaseModel):
    prompt: str
    project_name: str
    source: str
    source_id: Optional[str] = None
    hash: Optional[str] = None
    model_name: str
    template_columns: List[str]  


class PromptRequest(BaseModel):
    description: str
    model: str  

 