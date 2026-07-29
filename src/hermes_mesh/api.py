import os
import tempfile
from pathlib import Path

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .config import MeshConfig
from .mesh import AnnealedMesh
from .voice import VoiceClient

load_dotenv()

WEB_DIR = Path(__file__).with_name("web")
MAX_AUDIO_BYTES = 15 * 1024 * 1024

app = FastAPI(
    title="Hermes Mesh",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
)


class TaskRequest(BaseModel):
    task: str = Field(min_length=1, max_length=12_000)


class TaskResponse(BaseModel):
    answer: str


class TranscriptResponse(BaseModel):
    transcript: str


def env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing server setting: {name}")
    return value


def voice_client() -> VoiceClient:
    return VoiceClient(
        env("ASR_BASE_URL"),
        env("TTS_BASE_URL"),
        api_key=os.getenv("SPEECH_API_KEY", ""),
        voice=os.getenv("TTS_VOICE", "English-US-Magpie-Flow.Female-1"),
        language=os.getenv("TTS_LANGUAGE", "en-US"),
        sample_rate=int(os.getenv("TTS_SAMPLE_RATE", "22050")),
    )


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/run", response_model=TaskResponse)
async def run_task(request: TaskRequest) -> TaskResponse:
    try:
        async with AnnealedMesh(MeshConfig.load()) as mesh:
            result = await mesh.run(request.task)
    except (ValueError, RuntimeError, httpx.HTTPError) as error:
        raise HTTPException(status_code=502, detail=str(error)) from error
    return TaskResponse(answer=result.answer)


@app.post("/api/transcribe", response_model=TranscriptResponse)
async def transcribe(audio: UploadFile = File(...)) -> TranscriptResponse:
    content = await audio.read(MAX_AUDIO_BYTES + 1)
    if not content or len(content) > MAX_AUDIO_BYTES:
        raise HTTPException(status_code=413, detail="Audio must be under 15 MB")

    suffix = Path(audio.filename or "recording.wav").suffix.lower()
    if suffix not in {".wav", ".flac", ".opus"}:
        raise HTTPException(status_code=415, detail="Use WAV, FLAC, or OPUS")

    path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp:
            temp.write(content)
            path = Path(temp.name)
        async with voice_client() as voice:
            text = await voice.transcribe(path)
    except (ValueError, RuntimeError, httpx.HTTPError) as error:
        raise HTTPException(status_code=502, detail=str(error)) from error
    finally:
        if path:
            path.unlink(missing_ok=True)
    return TranscriptResponse(transcript=text)


@app.post("/api/speech")
async def speech(request: TaskRequest) -> Response:
    path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp:
            path = Path(temp.name)
        async with voice_client() as voice:
            await voice.synthesize(request.task, path)
        audio = path.read_bytes()
    except (ValueError, RuntimeError, httpx.HTTPError) as error:
        raise HTTPException(status_code=502, detail=str(error)) from error
    finally:
        if path:
            path.unlink(missing_ok=True)
    return Response(audio, media_type="audio/wav")


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(WEB_DIR / "index.html")


app.mount("/", StaticFiles(directory=WEB_DIR), name="web")


def main() -> None:
    import uvicorn

    uvicorn.run(
        "hermes_mesh.api:app",
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "8080")),
        proxy_headers=True,
    )
