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

    @classmethod
    def load_optional(cls, prefix: str) -> "ModelConfig | None":
        names = (
            f"{prefix}_BASE_URL",
            f"{prefix}_API_KEY",
            f"{prefix}_MODEL",
        )
        present = [bool(os.getenv(name, "").strip()) for name in names]
        if not any(present):
            return None
        if not all(present):
            missing = [name for name, is_present in zip(names, present) if not is_present]
            raise ValueError(
                f"Incomplete {prefix} model configuration; missing: {', '.join(missing)}"
            )
        return cls.load(prefix)


@dataclass(frozen=True)
class MeshConfig:
    hermes: ModelConfig
    nemotron: ModelConfig | None
    width: int
    rounds: int
    survivors: int
    temperature: float
    min_temperature: float
    timeout: float
    lightning: ModelConfig | None = None
    bolt: ModelConfig | None = None
    super_vl: ModelConfig | None = None

    @classmethod
    def load(cls) -> "MeshConfig":
        lightning = ModelConfig.load_optional("NEMOTRON_LIGHTNING")
        bolt = ModelConfig.load_optional("NEMOTRON_BOLT")
        super_vl = ModelConfig.load_optional("NEMOTRON_SUPER_VL")
        configured_roles = sum(model is not None for model in (lightning, bolt, super_vl))
        if configured_roles not in (0, 3):
            raise ValueError(
                "Configure all three specialist endpoints together: "
                "NEMOTRON_LIGHTNING, NEMOTRON_BOLT, and NEMOTRON_SUPER_VL"
            )

        nemotron = ModelConfig.load_optional("NEMOTRON")
        if configured_roles == 0 and nemotron is None:
            raise ValueError(
                "Configure NEMOTRON for legacy single-worker mode, or configure all "
                "three specialist endpoints for three-model MoA mode"
            )

        cfg = cls(
            hermes=ModelConfig.load("HERMES"),
            nemotron=nemotron,
            width=int(os.getenv("MESH_WIDTH", "4")),
            rounds=int(os.getenv("MESH_ROUNDS", "3")),
            survivors=int(os.getenv("MESH_SURVIVORS", "2")),
            temperature=float(os.getenv("MESH_TEMPERATURE", "0.85")),
            min_temperature=float(os.getenv("MESH_MIN_TEMPERATURE", "0.20")),
            timeout=float(os.getenv("MESH_TIMEOUT_SECONDS", "180")),
            lightning=lightning,
            bolt=bolt,
            super_vl=super_vl,
        )
        if min(cfg.width, cfg.rounds, cfg.survivors) < 1:
            raise ValueError("Mesh width, rounds, and survivors must be positive")
        if cfg.survivors > cfg.width:
            raise ValueError("MESH_SURVIVORS cannot exceed MESH_WIDTH")
        if cfg.min_temperature < 0 or cfg.temperature < cfg.min_temperature:
            raise ValueError("Temperatures must satisfy 0 <= minimum <= initial")
        if configured_roles == 3 and cfg.width < 3:
            raise ValueError("MESH_WIDTH must be at least 3 for three-model MoA mode")
        return cfg
