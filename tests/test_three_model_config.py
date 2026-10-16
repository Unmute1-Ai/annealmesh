import os
import unittest
from unittest.mock import patch

from hermes_mesh.config import MeshConfig


BASE_ENV = {
    "HERMES_BASE_URL": "http://judge/v1",
    "HERMES_API_KEY": "test",
    "HERMES_MODEL": "judge",
}


def specialist_env() -> dict[str, str]:
    values = dict(BASE_ENV)
    for prefix, port, model in (
        ("NEMOTRON_LIGHTNING", 8001, "lightning"),
        ("NEMOTRON_BOLT", 8002, "bolt"),
        ("NEMOTRON_SUPER_VL", 8003, "super-vl"),
    ):
        values[f"{prefix}_BASE_URL"] = f"http://localhost:{port}/v1"
        values[f"{prefix}_API_KEY"] = "test"
        values[f"{prefix}_MODEL"] = model
    return values


class ThreeModelConfigTests(unittest.TestCase):
    def test_legacy_single_worker_mode_remains_supported(self) -> None:
        env = dict(BASE_ENV)
        env.update(
            NEMOTRON_BASE_URL="http://worker/v1",
            NEMOTRON_API_KEY="test",
            NEMOTRON_MODEL="legacy-worker",
        )
        with patch.dict(os.environ, env, clear=True):
            config = MeshConfig.load()
        self.assertEqual(config.nemotron.model, "legacy-worker")
        self.assertIsNone(config.lightning)
        self.assertIsNone(config.bolt)
        self.assertIsNone(config.super_vl)

    def test_three_model_mode_does_not_require_legacy_worker(self) -> None:
        with patch.dict(os.environ, specialist_env(), clear=True):
            config = MeshConfig.load()
        self.assertIsNone(config.nemotron)
        self.assertEqual(config.lightning.model, "lightning")
        self.assertEqual(config.bolt.model, "bolt")
        self.assertEqual(config.super_vl.model, "super-vl")

    def test_partial_specialist_configuration_is_rejected(self) -> None:
        env = dict(BASE_ENV)
        env.update(
            NEMOTRON_LIGHTNING_BASE_URL="http://localhost:8001/v1",
            NEMOTRON_LIGHTNING_API_KEY="test",
            NEMOTRON_LIGHTNING_MODEL="lightning",
        )
        with patch.dict(os.environ, env, clear=True):
            with self.assertRaisesRegex(ValueError, "Configure all three specialist endpoints"):
                MeshConfig.load()

    def test_width_must_cover_all_three_specialists(self) -> None:
        env = specialist_env()
        env["MESH_WIDTH"] = "2"
        with patch.dict(os.environ, env, clear=True):
            with self.assertRaisesRegex(ValueError, "MESH_WIDTH must be at least 3"):
                MeshConfig.load()


if __name__ == "__main__":
    unittest.main()
