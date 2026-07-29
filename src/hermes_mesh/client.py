from openai import AsyncOpenAI

from .config import ModelConfig


class ChatModel:
    def __init__(self, config: ModelConfig, timeout: float) -> None:
        self.name = config.model
        self._client = AsyncOpenAI(
            api_key=config.api_key,
            base_url=config.base_url,
            timeout=timeout,
            max_retries=2,
        )

    async def close(self) -> None:
        await self._client.close()

    async def complete(
        self, system: str, user: str, *, temperature: float = 0.2
    ) -> str:
        response = await self._client.chat.completions.create(
            model=self.name,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=temperature,
        )
        text = response.choices[0].message.content
        if not text or not text.strip():
            raise RuntimeError(f"{self.name} returned no text")
        return text.strip()
