from abc import ABC,abstractmethod
from pydantic import BaseModel
from typing import Any

class BaseLLM(ABC,BaseModel):
    name:str
    model:str
    api_key:str
    base_url:str
    max_tokens:int = 4096
    temperature:float = 0.2
    class Config:
        arbitrary_types_allowed = True
        extra = "allow"  # Allow extra fields for flexibility in subclasses
    @abstractmethod
    async def execute(self,context:list[dict[str, str]],tools:list[dict])->Any:
        """Execute the LLM with a given context and tools"""

        