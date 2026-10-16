import asyncio
import json
from dataclasses import asdict, dataclass
from typing import Callable

from .client import ChatModel
from .config import MeshConfig

PLAN_PROMPT = "Make a short plan. Include constraints, risks, and success criteria."
WORKER_PROMPT = "Solve the task. Be specific, check assumptions, and cover failures."
LIGHTNING_PROMPT = """You are the fast intent and structured-output specialist.
Produce a precise candidate answer. Identify the user's intent, entities, constraints,
and any authorization that would be required before an external action. Never claim
that a proposed action has been executed."""
BOLT_PROMPT = """You are the multistep planning specialist.
Produce a feasible ordered plan with prerequisites, checks, failure handling, and
recovery considerations. Treat every tool call or external effect as a proposal only.
You do not grant permission or execute actions."""
SUPER_VL_PROMPT = """You are the deep-reasoning and ambiguity specialist.
Test assumptions, look for counterexamples, and examine privacy, accessibility, and
safety implications. Use only evidence present in the supplied task; do not claim to
have seen images, video, or other modalities that were not supplied."""
JUDGE_PROMPT = """Score each candidate for correctness and feasibility.
Treat model scores as advisory, not as proof or authorization.
Return only a JSON array with this shape:
[{"index": 1, "score": 80, "critique": "brief reason"}]"""
FINAL_PROMPT = """Write the final answer from the plan and finalists. Resolve conflicts,
state material uncertainty, and never imply that model agreement grants authorization."""

STRATEGIES = (
    "Start from first principles.",
    "Focus on edge cases.",
    "Focus on operational simplicity.",
    "Try a different approach.",
)


@dataclass(frozen=True)
class Candidate:
    text: str
    score: float = 0
    critique: str = ""


@dataclass(frozen=True)
class MeshResult:
    task: str
    plan: str
    answer: str
    finalists: list[Candidate]

    def to_dict(self) -> dict:
        return asdict(self)


class AnnealedMesh:
    def __init__(
        self, config: MeshConfig, log: Callable[[str], None] | None = None
    ) -> None:
        self.config = config
        self.hermes = ChatModel(config.hermes, config.timeout)
        self.nemotron = (\n            ChatModel(config.nemotron, config.timeout)\n            if config.nemotron is not None\n            else None\n        )
        self.lightning = (
            ChatModel(config.lightning, config.timeout)
            if config.lightning is not None
            else None
        )
        self.bolt = (
            ChatModel(config.bolt, config.timeout)
            if config.bolt is not None
            else None
        )
        self.super_vl = (
            ChatModel(config.super_vl, config.timeout)
            if config.super_vl is not None
            else None
        )
        self.log = log or (lambda _: None)

    async def __aenter__(self) -> "AnnealedMesh":
        return self

    async def __aexit__(self, *_: object) -> None:
        clients = [
            self.hermes,
            self.nemotron,
            self.lightning,
            self.bolt,
            self.super_vl,
        ]
        await asyncio.gather(
            *(client.close() for client in clients if client is not None)
        )

    def temperature(self, round_number: int) -> float:
        if self.config.rounds == 1:
            return self.config.min_temperature
        fraction = round_number / (self.config.rounds - 1)
        span = self.config.temperature - self.config.min_temperature
        return self.config.temperature - fraction * span

    def _specialists(self) -> list[tuple[str, ChatModel]]:
        configured = (self.lightning, self.bolt, self.super_vl)
        if all(model is None for model in configured):
            if self.nemotron is None:\n                raise ValueError("NEMOTRON must be configured when specialist MoA is disabled")\n            return [("default", self.nemotron)]
        if any(model is None for model in configured):
            # MeshConfig.load rejects partial setup; keep direct construction safe too.
            raise ValueError("All three Nemotron specialist models must be configured")
        return [
            ("lightning", self.lightning),
            ("bolt", self.bolt),
            ("super_vl", self.super_vl),
        ]  # type: ignore[list-item]

    async def run(self, task: str) -> MeshResult:
        task = task.strip()
        if not task:
            raise ValueError("Task cannot be empty")

        specialists = self._specialists()
        if len(specialists) == 3 and self.config.width < 3:
            raise ValueError("MESH_WIDTH must be at least 3 when three-model MoA is enabled")

        plan = await self.hermes.complete(PLAN_PROMPT, task)
        finalists: list[Candidate] = []

        for round_number in range(self.config.rounds):
            temperature = self.temperature(round_number)
            prompts = self._worker_inputs(task, plan, finalists, round_number)
            requests = []
            for index, prompt in enumerate(prompts):
                role, model = specialists[index % len(specialists)]
                system = {
                    "default": WORKER_PROMPT,
                    "lightning": LIGHTNING_PROMPT,
                    "bolt": BOLT_PROMPT,
                    "super_vl": SUPER_VL_PROMPT,
                }[role]
                requests.append(model.complete(system, prompt, temperature=temperature))
            texts = await asyncio.gather(*requests)
            finalists = await self._rank(
                task, plan, [Candidate(text) for text in texts]
            )
            self.log(
                f"round={round_number + 1} "
                f"temperature={temperature:.2f} kept={len(finalists)} "
                f"workers={','.join(specialists[index % len(specialists)][0] for index in range(len(prompts)))}"
            )

        answer = await self.hermes.complete(
            FINAL_PROMPT, self._final_input(task, plan, finalists), temperature=0.1
        )
        return MeshResult(task, plan, answer, finalists)

    def _worker_inputs(
        self,
        task: str,
        plan: str,
        finalists: list[Candidate],
        round_number: int,
    ) -> list[str]:
        previous = "\n\n".join(item.text for item in finalists)
        context = f"Task:\n{task}\n\nPlan:\n{plan}"
        if previous:
            context += f"\n\nPrevious best:\n{previous}"
        return [
            f"{context}\n\nRound {round_number + 1}: "
            f"{STRATEGIES[index % len(STRATEGIES)]}"
            for index in range(self.config.width)
        ]

    async def _rank(
        self, task: str, plan: str, candidates: list[Candidate]
    ) -> list[Candidate]:
        entries = "\n\n".join(
            f"[{index}] {candidate.text}"
            for index, candidate in enumerate(candidates, 1)
        )
        raw = await self.hermes.complete(
            JUDGE_PROMPT,
            f"Task:\n{task}\n\nPlan:\n{plan}\n\nCandidates:\n{entries}",
            temperature=0,
        )
        rankings = self._parse_rankings(raw, len(candidates))
        ranked = [
            Candidate(
                text=candidates[item["index"] - 1].text,
                score=float(item["score"]),
                critique=str(item.get("critique", "")),
            )
            for item in rankings
        ]
        return sorted(ranked, key=lambda item: item.score, reverse=True)[
            : self.config.survivors
        ]

    @staticmethod
    def _parse_rankings(raw: str, candidate_count: int) -> list[dict]:
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as error:
            raise RuntimeError("Judge returned invalid JSON") from error
        if not isinstance(data, list):
            raise RuntimeError("Judge response must be a JSON array")

        rankings = []
        seen = set()
        for item in data:
            if not isinstance(item, dict):
                continue
            index = item.get("index")
            score = item.get("score")
            if (
                isinstance(index, int)
                and not isinstance(index, bool)
                and 1 <= index <= candidate_count
                and isinstance(score, (int, float))
                and not isinstance(score, bool)
                and index not in seen
            ):
                seen.add(index)
                rankings.append(item)
        if not rankings:
            raise RuntimeError("Judge returned no usable scores")
        return rankings

    @staticmethod
    def _final_input(
        task: str, plan: str, finalists: list[Candidate]
    ) -> str:
        entries = "\n\n".join(
            f"Score {item.score}: {item.text}\nCritique: {item.critique}"
            for item in finalists
        )
        return f"Task:\n{task}\n\nPlan:\n{plan}\n\nFinalists:\n{entries}"
