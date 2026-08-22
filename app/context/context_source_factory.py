from abc import ABC, abstractmethod
from typing import Generic, TypeVar

C = TypeVar("C")
S = TypeVar("S")

class ContextSourceFactory(ABC, Generic[C,S]):

    @abstractmethod
    def create(self, context: C) -> S:
        pass