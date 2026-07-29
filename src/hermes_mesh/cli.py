import argparse
import asyncio
import json
import sys

from dotenv import load_dotenv

from .config import MeshConfig
from .mesh import AnnealedMesh


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the model mesh")
    parser.add_argument("task", nargs="+")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    return parser


async def run(args: argparse.Namespace) -> None:
    log = (lambda line: print(line, file=sys.stderr)) if args.verbose else None
    async with AnnealedMesh(MeshConfig.load(), log) as mesh:
        result = await mesh.run(" ".join(args.task))
    output = (
        json.dumps(result.to_dict(), indent=2, ensure_ascii=False)
        if args.json
        else result.answer
    )
    print(output)


def main() -> None:
    load_dotenv()
    try:
        asyncio.run(run(build_parser().parse_args()))
    except (ValueError, RuntimeError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(2) from error


if __name__ == "__main__":
    main()
