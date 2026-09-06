from app.returns.enums import ReturnAction
from app.events.models import TaskExecutionCompletedEvent
from app.context.context_source_factory import ContextSourceFactory
from app.context.context import ContextBuilder
from app.llm_models.provider import ModelProvider

class ReturnDecisionService:

    def __init__(
        self, 
        context_source_factory: ContextSourceFactory, 
        context_builder: ContextBuilder,
        model_provider: ModelProvider):
        self._context_source_factory = context_source_factory
        self._context_builder = context_builder
        self._model_provider = model_provider


    async def decide(self, event: TaskExecutionCompletedEvent) -> ReturnAction:
        context_source = self._context_source_factory.create(event)
        context = self._context_builder.build(context_source)
        
        result = await self._model_provider.structured(context, ReturnAction)

        return result
