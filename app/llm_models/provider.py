from abc import ABC, abstractmethod
from typing import Generic, TypeVar

I = TypeVar("I")
O = TypeVar("O")
T = TypeVar("T")

class ModelProvider(ABC, Generic[I, O]):

    def __init__(self, thinking: bool | None = None, options: dict | None = None):
        self.thinking = thinking
        self.options = options
    
    @abstractmethod
    async def chat(self, input: I) -> O:
        pass

    @abstractmethod
    async def structured(self, input: I, output_type: type[T]) -> T:
        pass