import pytest

from app.tasks.enums import TaskType
from app.application.tasks.components import TaskComponents
from app.application.tasks.component_registry import TaskComponentRegistry

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