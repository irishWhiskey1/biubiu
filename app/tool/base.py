from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseTool(ABC):
    @abstractmethod
    async def execute(self,toolName:str, kwargs) -> Any:
        """Execute the tool with given parameters."""

    @abstractmethod
    def to_param(self,toolName :str) -> Dict:
        """Convert tool to function call format."""