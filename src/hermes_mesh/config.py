from __future__ import annotations

import os
from dataclasses import dataclass


def _required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(f"Missing required setting: {name}")
    return value


@dataclass(frozen=True)
class ModelConfig:
    base_url: str
    api_key: str
    model: str

    @classmethod
    def load(cls, prefix: str) -> "ModelConfig":
        return cls(
            _required(f"{prefix}_BASE_URL"),
            _required(f"{prefix}_API_KEY"),
            _required(f"{prefix}_MODEL"),
        )


@dataclass(frozen=True)
class MeshConfig:
    hermes: ModelConfig
    nemotron: ModelConfig
    width: int
    rounds: int
    survivors: int
    temperature: float
    min_temperature: float
    timeout: float

    @classmethod
    def load(cls) -> "MeshConfig":
        cfg = cls(
            ModelConfig.load("HERMES"),
            ModelConfig.load("NEMOTRON"),
            int(os.getenv("MESH_WIDTH", "4")),
            int(os.getenv("MESH_ROUNDS", "3")),
            int(os.getenv("MESH_SURVIVORS", "2")),
            float(os.getenv("MESH_TEMPERATURE", "0.85")),
            float(os.getenv("MESH_MIN_TEMPERATURE", "0.20")),
            float(os.getenv("MESH_TIMEOUT_SECONDS", "180")),
        )
        if min(cfg.width, cfg.rounds, cfg.survivors) < 1:
            raise ValueError("Mesh width, rounds, and survivors must be positive")
        if cfg.survivors > cfg.width:
            raise ValueError("MESH_SURVIVORS cannot exceed MESH_WIDTH")
        return cfg
