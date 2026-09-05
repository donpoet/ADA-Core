from abc import ABC, abstractmethod
from typing import Generic, TypeVar

I = TypeVar("I")
O = TypeVar("O")
T = TypeVar("T")

class ModelProvider(ABC, Generic[I, O]):
    
    @abstractmethod
    async def chat(self, input: I, thinking: bool | None = None, options: dict | None = None) -> O:
        pass

    @abstractmethod
    async def structured(self, input: I, output_type: type[T], thinking: bool | None = None, options: dict | None = None) -> T:
        pass