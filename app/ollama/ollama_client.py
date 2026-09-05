import httpx
from app.ollama.models import(
    OllamaResponse,
    OllamaChatResponse
)

class OllamaClient:
    def __init__(self, base_url: str, timeout: int):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout


    async def generate(
            self, 
            model: str, 
            prompt: str
            ) -> OllamaResponse:
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json=payload,
            )
            response.raise_for_status()

            data = response.json()

            return OllamaResponse(**data)


    async def chat(
            self,
            model: str, 
            messages: list[dict[str, str]],
            thinking: bool | None = None,
            options: dict | None = None,
    ) -> OllamaChatResponse:
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "think": thinking,
            "options" : options if options else {}
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/api/chat",
                json=payload,
            )

        response.raise_for_status()
        data = response.json()

        return OllamaChatResponse(**data)

    async def structured(
            self,
            model: str, 
            messages: list[dict[str, str]],
            output_type: type[T],
            thinking: bool | None = None,
            options: dict | None = None,
    ) -> OllamaChatResponse:
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "think": thinking,
            "format": output_type.model_json_schema(),
            "options" : options if options else {}
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/api/chat",
                json=payload,
            )

        response.raise_for_status()
        data = response.json()
 
        return OllamaChatResponse(**data)
        

    async def health(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{self.base_url}/api/tags"
                )
                response.raise_for_status()
                return True
        except (httpx.TimeoutException, httpx.HTTPError):
            return False