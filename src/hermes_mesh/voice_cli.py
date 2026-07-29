import argparse
import asyncio
import os
import sys
from pathlib import Path

import httpx
from dotenv import load_dotenv

from .config import MeshConfig
from .mesh import AnnealedMesh
from .voice import VoiceClient


def env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(f"Missing required setting: {name}")
    return value


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the mesh from an audio file")
    parser.add_argument("audio", type=Path, help="WAV, FLAC, or OPUS file")
    parser.add_argument("-o", "--output", type=Path, default=Path("answer.wav"))
    parser.add_argument("--verbose", action="store_true")
    return parser


async def run(args: argparse.Namespace) -> None:
    log = (lambda line: print(line, file=sys.stderr)) if args.verbose else None
    voice_args = {
        "api_key": os.getenv("SPEECH_API_KEY", ""),
        "voice": os.getenv("TTS_VOICE", "English-US-Magpie-Flow.Female-1"),
        "language": os.getenv("TTS_LANGUAGE", "en-US"),
        "sample_rate": int(os.getenv("TTS_SAMPLE_RATE", "22050")),
    }
    async with VoiceClient(
        env("ASR_BASE_URL"), env("TTS_BASE_URL"), **voice_args
    ) as voice:
        transcript = await voice.transcribe(args.audio)
        print(f"transcript: {transcript}", file=sys.stderr)
        async with AnnealedMesh(MeshConfig.load(), log) as mesh:
            result = await mesh.run(transcript)
        await voice.synthesize(result.answer, args.output)

    print(result.answer)
    print(f"audio: {args.output.resolve()}", file=sys.stderr)


def main() -> None:
    load_dotenv()
    try:
        asyncio.run(run(build_parser().parse_args()))
    except (ValueError, RuntimeError, httpx.HTTPError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(2) from error


if __name__ == "__main__":
    main()
