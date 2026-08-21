from abc import ABC, abstractmethod
from typing import Generic, TypeVar

I = TypeVar("I")
O = TypeVar("O")

class ModelProvider(ABC, Generic[I, O]):
    
    @abstractmethod
    def chat(self, input: I) -> O:
        pass