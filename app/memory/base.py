from abc import ABC
from pydantic import BaseModel
class BaseMemory(ABC,BaseModel):
    def __init__(self,config):
        self.config = config
