from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from app.tasks.models import Task

I = TypeVar("I")

class ContextInputProvider(ABC, Generic[I]):
    @abstractmethod
    def get(self, task: Task) -> I:
        pass
