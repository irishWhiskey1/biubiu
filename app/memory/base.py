from abc import ABC,abstractmethod
from pydantic import BaseModel
class BaseMemory(ABC,BaseModel):
    class Config:
        arbitrary_types_allowed = True
        extra = "allow"  # Allow extra fields for flexibility in subclasses
    @abstractmethod
    def set_context(self, ctx: list[dict[str, str]]):
        pass
    @abstractmethod
    def get_context(self) -> list[dict[str, str]]:
        pass
    
