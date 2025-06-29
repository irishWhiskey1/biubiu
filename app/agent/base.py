from abc import ABC,abstractmethod

class BaseAgent(ABC):
    @abstractmethod
    def think(self)