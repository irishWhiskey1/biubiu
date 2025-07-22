from abc import ABC,abstractmethod
from pydantic import BaseModel

class BaseAgent(BaseModel,ABC):
    name:str = "BaseAgent"
    class Config:
        arbitrary_types_allowed = True
        extra = "allow"  # Allow extra fields for flexibility in subclasses

    @abstractmethod
    async def run(self)->str:
        """
        智能体的运行，包括思考、执行、输出结果
        :return:
        """