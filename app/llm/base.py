from abc import ABC,abstractmethod
from pydantic import BaseModel
from typing import Any

class BaseLLM(ABC,BaseModel):
    name:str
    def __init__(self,modelConf:dict):
        if "model" not in modelConf:
            raise ValueError(
                'param model is not in conf'
            )
        if "api_key" not in modelConf:
            raise ValueError(
                'api_key is not in conf'
            )
        if "base_url" not in modelConf:
            raise ValueError(
                'base_url is not in conf'
            )
        self.model = modelConf["model"]
        self.apiKey = modelConf["api_key"]
        self.baseURL = modelConf["base_url"]
        self.max_tokens = modelConf.get("max_tokens",4096)
        self.temperature = modelConf.get("temperature",0.2)
    @abstractmethod
    async def execute(self,context:list[dict[str, str]],tools:list[dict])->Any:
        """Execute the LLM with a given context and tools"""

        