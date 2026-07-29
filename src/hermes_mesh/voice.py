import wave
from pathlib import Path

import httpx

SUPPORTED_INPUTS = {".wav", ".flac", ".opus"}


class VoiceClient:
    def __init__(
        self,
        asr_url: str,
        tts_url: str,
        *,
        api_key: str = "",
        voice: str = "English-US-Magpie-Flow.Female-1",
        language: str = "en-US",
        sample_rate: int = 22050,
        timeout: float = 180,
    ) -> None:
        if sample_rate <= 0:
            raise ValueError("TTS_SAMPLE_RATE must be positive")
        headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        self._client = httpx.AsyncClient(headers=headers, timeout=timeout)
        self._asr_url = asr_url.rstrip("/")
        self._tts_url = tts_url.rstrip("/")
        self._voice = voice
        self._language = language
        self._sample_rate = sample_rate

    async def __aenter__(self) -> "VoiceClient":
        return self

    async def __aexit__(self, *_: object) -> None:
        await self._client.aclose()

    async def transcribe(self, path: Path) -> str:
        if not path.is_file():
            raise ValueError(f"Audio file not found: {path}")
        if path.suffix.lower() not in SUPPORTED_INPUTS:
            raise ValueError("Input must be WAV, FLAC, or OPUS")

        with path.open("rb") as audio:
            response = await self._client.post(
                f"{self._asr_url}/v1/audio/transcriptions",
                files={"file": (path.name, audio)},
                data={"response_format": "json"},
            )
        response.raise_for_status()
        text = response.json().get("text")
        if not isinstance(text, str) or not text.strip():
            raise RuntimeError("ASR returned no text")
        return text.strip()

    async def synthesize(self, text: str, output: Path) -> None:
        response = await self._client.post(
            f"{self._tts_url}/v1/audio/synthesize_online",
            data={
                "language": self._language,
                "text": text,
                "voice": self._voice,
                "sample_rate_hz": str(self._sample_rate),
            },
        )
        response.raise_for_status()
        if not response.content:
            raise RuntimeError("TTS returned no audio")

        output.parent.mkdir(parents=True, exist_ok=True)
        with wave.open(str(output), "wb") as wav:
            wav.setparams((1, 2, self._sample_rate, 0, "NONE", "not compressed"))
            wav.writeframes(response.content)
