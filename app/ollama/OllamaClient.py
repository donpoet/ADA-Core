import httpx

class OllamaClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')


    async def generate(
            self, 
            model: str, 
            prompt: str
            ) -> str:
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/generate",
                json=payload,
            )
            response.raise_for_status()

            data = response.json()

            return data["response"]

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