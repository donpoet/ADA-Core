import pytest

from app.tasks.enums import TaskType
from app.application.tasks.components import TaskComponents
from app.application.tasks.component_registry import TaskComponentRegistry
from app.dependencies import task_component_registry
from app.chat.context_input_provider import ChatContextInputProvider
from app.ollama.context_source_factory import OllamaChatContextSourceFactory
from app.ollama.context_builder import OllamaContextBuilder
from app.application.tasks.executions.weak_llm.execution_factory import WeakLLMTaskExecutionFactory

def test_register_and_get_components():
    registry = TaskComponentRegistry()

    source_factory = object()
    context_builder = object()
    execution_factory = object()
    context_input_provider=object()

    components = TaskComponents(
        context_builder=context_builder,
        context_source_factory=source_factory,
        execution_factory=execution_factory,
        context_input_provider=context_input_provider
    )

    registry.register(TaskType.WEAK_LLM, components)

    result = registry.get(TaskType.WEAK_LLM)

    assert result is components
    assert result.context_source_factory is source_factory
    assert result.context_builder is context_builder
    assert result.context_input_provider is context_input_provider

def test_weak_llm_components_is_composed_correctly():
    components = task_component_registry.get(TaskType.WEAK_LLM)

    assert isinstance(
        components.context_input_provider,
        ChatContextInputProvider
    )

    
    assert isinstance(
        components.context_source_factory,
        OllamaChatContextSourceFactory
    )

    
    assert isinstance(
        components.context_builder,
        OllamaContextBuilder
    )

    
    assert isinstance(
        components.execution_factory,
        WeakLLMTaskExecutionFactory
    )