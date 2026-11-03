"""Run the fixed Week 4 regression set and save a detailed Day 22 baseline."""

import argparse
import json
import math
import os
import platform
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from health_agent.core.config import get_settings
from health_agent.mcp.client import HealthMCPClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET = PROJECT_ROOT / "data" / "eval" / "week4_regression.json"
DEFAULT_OUTPUT = PROJECT_ROOT / "reports" / "week4" / "baseline.json"


def percentile(values: list[float], fraction: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = max(0, math.ceil(len(ordered) * fraction) - 1)
    return round(ordered[index], 2)


def post_json(url: str, payload: dict[str, Any], timeout: float) -> tuple[int, Any]:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raw_body = exc.read().decode("utf-8")
        try:
            response_body = json.loads(raw_body)
        except json.JSONDecodeError:
            response_body = {"raw_body": raw_body}
        return exc.code, response_body


def assert_agent_response(
    status: int,
    body: dict[str, Any],
    expected: dict[str, Any],
) -> None:
    assert status == expected["status"], f"status={status}"

    for field in ("route", "tool_name", "interrupted"):
        if field in expected:
            assert body.get(field) == expected[field], (
                f"{field}={body.get(field)!r}, expected={expected[field]!r}"
            )

    if expected.get("answer_required"):
        assert body.get("answer"), "answer is empty"
    if expected.get("sources_required"):
        assert body.get("sources"), "sources are empty"


def run_agent_query(
    case: dict[str, Any],
    base_url: str,
    timeout: float,
) -> dict[str, Any]:
    thread_id = f"baseline-{case['id']}-{uuid4()}"
    status, body = post_json(
        f"{base_url}/agent/query",
        {"message": case["message"], "thread_id": thread_id},
        timeout,
    )
    assert_agent_response(status, body, case["expected"])
    return {"http_status": status, "route": body.get("route")}


def run_agent_sequence(
    case: dict[str, Any],
    base_url: str,
    timeout: float,
) -> dict[str, Any]:
    thread_id = f"baseline-{case['id']}-{uuid4()}"
    observed_routes = []

    for turn in case["turns"]:
        status, body = post_json(
            f"{base_url}/agent/query",
            {"message": turn["message"], "thread_id": thread_id},
            timeout,
        )
        assert_agent_response(status, body, turn["expected"])
        observed_routes.append(body.get("route"))

    return {"turn_count": len(case["turns"]), "routes": observed_routes}


def run_hitl(
    case: dict[str, Any],
    base_url: str,
    timeout: float,
) -> dict[str, Any]:
    thread_id = f"baseline-{case['id']}-{uuid4()}"
    query_status, query_body = post_json(
        f"{base_url}/agent/query",
        {"message": case["message"], "thread_id": thread_id},
        timeout,
    )
    assert query_status == 200, f"query status={query_status}"
    assert query_body.get("interrupted") is True, "query did not interrupt"
    assert query_body.get("interrupt_payload"), "interrupt payload is empty"

    resume_status, resume_body = post_json(
        f"{base_url}/agent/resume",
        {"thread_id": thread_id, "approved": case["approved"]},
        timeout,
    )
    assert resume_status == 200, f"resume status={resume_status}"
    assert resume_body.get("interrupted") is False, "resume remained interrupted"
    assert resume_body.get("answer"), "resume answer is empty"

    return {
        "query_status": query_status,
        "resume_status": resume_status,
        "approved": case["approved"],
    }


def run_invalid_request(
    case: dict[str, Any],
    base_url: str,
    timeout: float,
) -> dict[str, Any]:
    status, body = post_json(
        f"{base_url}/agent/query",
        case["payload"],
        timeout,
    )
    assert status == case["expected_status"], f"status={status}"
    return {"http_status": status, "error_count": len(body.get("detail", []))}


def run_mcp_tool(
    case: dict[str, Any],
    client: HealthMCPClient,
) -> dict[str, Any]:
    result = client.call_tool(case["tool_name"], case["arguments"])
    assert not result.is_error, result.error or "MCP tool failed"
    serialized = json.dumps(result.data, ensure_ascii=False)
    assert case["expected_contains"] in serialized, (
        f"tool result does not contain {case['expected_contains']!r}"
    )
    return {"tool_name": case["tool_name"], "result_present": result.data is not None}


def run_case(
    case: dict[str, Any],
    base_url: str,
    timeout: float,
    mcp_client: HealthMCPClient,
) -> dict[str, Any]:
    runners = {
        "agent_query": lambda: run_agent_query(case, base_url, timeout),
        "agent_sequence": lambda: run_agent_sequence(case, base_url, timeout),
        "hitl": lambda: run_hitl(case, base_url, timeout),
        "invalid_request": lambda: run_invalid_request(case, base_url, timeout),
        "mcp_tool": lambda: run_mcp_tool(case, mcp_client),
    }

    started = time.perf_counter()
    try:
        observed = runners[case["kind"]]()
        status = "passed"
        error = None
    except Exception as exc:  # noqa: BLE001 - every case must be recorded
        observed = None
        status = "failed"
        error = f"{type(exc).__name__}: {exc}"
    latency_ms = round((time.perf_counter() - started) * 1000, 2)

    return {
        "id": case["id"],
        "category": case["category"],
        "kind": case["kind"],
        "status": status,
        "latency_ms": latency_ms,
        "observed": observed,
        "error": error,
    }


def git_revision() -> str | None:
    try:
        process = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return None
    return process.stdout.strip() or None


def build_report(
    cases: list[dict[str, Any]],
    results: list[dict[str, Any]],
    base_url: str,
    dataset_path: Path,
) -> dict[str, Any]:
    settings = get_settings()
    latencies = [item["latency_ms"] for item in results]
    passed = sum(item["status"] == "passed" for item in results)

    return {
        "schema_version": 1,
        "captured_at": datetime.now().astimezone().isoformat(),
        "git_revision": git_revision(),
        "environment": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "machine": platform.machine(),
            "processor": platform.processor() or None,
            "logical_cpu_count": os.cpu_count(),
            "cuda_visible_devices": os.getenv("CUDA_VISIBLE_DEVICES"),
            "api_base_url": base_url,
            "model": settings.llm_model,
        },
        "dataset": {
            "path": str(dataset_path),
            "case_count": len(cases),
        },
        "summary": {
            "total": len(results),
            "passed": passed,
            "failed": len(results) - passed,
            "pass_rate": round(passed / len(results), 4) if results else 0.0,
            "latency_ms": {
                "p50": percentile(latencies, 0.50),
                "p95": percentile(latencies, 0.95),
            },
        },
        "results": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--timeout", type=float, default=180.0)
    args = parser.parse_args()

    with args.dataset.open(encoding="utf-8") as file:
        cases = json.load(file)

    settings = get_settings()
    mcp_client = HealthMCPClient(settings.mcp_health_server_url)
    base_url = args.base_url.rstrip("/")
    results = []
    for case in cases:
        result = run_case(case, base_url, args.timeout, mcp_client)
        results.append(result)
        print(
            f"[{result['status'].upper()}] {result['id']} "
            f"{result['latency_ms']:.2f}ms"
        )

    report = build_report(cases, results, base_url, args.dataset)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(report["summary"], ensure_ascii=False, indent=2))
    print(f"Detailed report: {args.output}")

    if report["summary"]["failed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
