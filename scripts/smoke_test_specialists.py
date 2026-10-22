#!/usr/bin/env python3
"""Verify each configured Nemotron endpoint with a real OpenAI-compatible request.

Run this from the host/container that can reach the three model servers after
loading the environment variables from .env. API keys and model response text are
never printed. Exit status is non-zero if any endpoint fails.
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass


@dataclass
class CheckResult:
    role: str
    ok: bool
    model: str
    latency_ms: float | None = None
    discovered_model: bool | None = None
    error: str | None = None


def request_json(url: str, api_key: str, payload: dict | None, timeout: float) -> dict:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {"Authorization": f"Bearer {api_key}", "Accept": "application/json"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def check_role(role: str, timeout: float = 45.0) -> CheckResult:
    prefix = f"NEMOTRON_{role.upper()}"
    base_url = os.getenv(f"{prefix}_BASE_URL", "").strip().rstrip("/")
    api_key = os.getenv(f"{prefix}_API_KEY", "").strip()
    model = os.getenv(f"{prefix}_MODEL", "").strip()
    if not all((base_url, api_key, model)):
        return CheckResult(role, False, model or "(unset)", error="required endpoint configuration is missing")

    try:
        models_payload = request_json(f"{base_url}/models", api_key, None, timeout)
        listed_ids = [
            item.get("id") for item in models_payload.get("data", [])
            if isinstance(item, dict) and isinstance(item.get("id"), str)
        ]
        discovered = model in listed_ids if listed_ids else None
        if discovered is False:
            return CheckResult(
                role, False, model, discovered_model=False,
                error="configured model ID is not listed by this endpoint's /models response",
            )

        started = time.perf_counter()
        result = request_json(
            f"{base_url}/chat/completions",
            api_key,
            {
                "model": model,
                "messages": [
                    {"role": "system", "content": "You are an inference smoke-test assistant. Be concise."},
                    {"role": "user", "content": "Reply with exactly: U1_INFERENCE_OK"},
                ],
                "temperature": 0,
                "max_tokens": 24,
            },
            timeout,
        )
        latency_ms = round((time.perf_counter() - started) * 1000, 2)
        choices = result.get("choices", [])
        content = ""
        if choices and isinstance(choices[0], dict):
            message = choices[0].get("message", {})
            if isinstance(message, dict):
                content = str(message.get("content", "")).strip()
        if not content:
            return CheckResult(
                role, False, model, latency_ms, discovered,
                error="chat completion returned no text content",
            )
        return CheckResult(role, True, model, latency_ms, discovered)
    except urllib.error.HTTPError as exc:
        # Do not echo the response body; providers may include request details.
        return CheckResult(role, False, model, error=f"HTTP {exc.code} from endpoint")
    except urllib.error.URLError as exc:
        reason = getattr(exc, "reason", None)
        return CheckResult(
            role, False, model,
            error=f"endpoint unreachable ({type(reason).__name__ if reason else 'network error'})",
        )
    except (TimeoutError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        return CheckResult(role, False, model, error=f"invalid or timed-out response ({type(exc).__name__})")


def main() -> int:
    timeout = float(os.getenv("MODEL_SMOKE_TIMEOUT_SECONDS", "45"))
    results = [check_role(role, timeout) for role in ("lightning", "bolt", "super_vl")]
    print(json.dumps({
        "suite": "annealmesh-nemotron-live-smoke-v1",
        "results": [asdict(result) for result in results],
        "passed": sum(result.ok for result in results),
        "total": len(results),
    }, indent=2))
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    sys.exit(main())
