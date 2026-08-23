from dataclasses import dataclass

from app.context.context import ContextBuilder
from app.context.context_source_factory import ContextSourceFactory
from .execution_factory import TaskExecutionFactory
from app.context.context_input_provider import ContextInputProvider

@dataclass(frozen=True)
class TaskComponents:
    context_source_factory: ContextSourceFactory
    context_builder: ContextBuilder
    execution_factory: TaskExecutionFactory
    context_input_provider: ContextInputProvider