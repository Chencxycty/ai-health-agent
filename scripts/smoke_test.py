import argparse
import json
import sys
import urllib.error
import urllib.request
from uuid import uuid4


def get_json(url: str) -> dict:
    with urllib.request.urlopen(
        url,
        timeout=20,
    ) as response:
        if response.status != 200:
            raise RuntimeError(f"Unexpected status: {response.status}")

        return json.loads(response.read())


def post_json(
    url: str,
    payload: dict,
    timeout: int = 180,
) -> dict:
    body = json.dumps(
        payload,
        ensure_ascii=False,
    ).encode("utf-8")

    request = urllib.request.Request(
        url=url,
        data=body,
        headers={
            "Content-Type": "application/json",
        },
        method="POST",
    )

    with urllib.request.urlopen(
        request,
        timeout=timeout,
    ) as response:
        if response.status != 200:
            raise RuntimeError(f"Unexpected status: {response.status}")

        return json.loads(response.read().decode("utf-8"))


def check_health(base_url: str) -> None:
    result = get_json(f"{base_url}/health")

    assert result["status"] == "ok"
    print("[PASS] FastAPI health")


def check_chat(base_url: str) -> None:
    result = post_json(
        f"{base_url}/agent/query",
        {
            "message": "你好",
            "thread_id": f"smoke-chat-{uuid4()}",
        },
    )

    assert result["answer"]
    assert not result["interrupted"]

    print("[PASS] Agent chat")


def check_rag(base_url: str) -> None:
    result = post_json(
        f"{base_url}/agent/query",
        {
            "message": "什么是高血压？",
            "thread_id": f"smoke-rag-{uuid4()}",
        },
    )

    assert result["route"] == "medical_knowledge"
    assert result["answer"]
    assert not result["interrupted"]

    # 这里只验证 RAG 路径成功；
    # citation 正确性还需要 Golden Dataset 评测。
    print("[PASS] Medical RAG")


def check_mcp(base_url: str) -> None:
    result = post_json(
        f"{base_url}/agent/query",
        {
            "message": ("我身高175厘米，体重80公斤，请计算BMI。"),
            "thread_id": f"smoke-mcp-{uuid4()}",
        },
    )

    assert result["route"] == "health_calculation"
    assert result["tool_name"] == "calculate_bmi"
    assert result["answer"]
    assert not result["interrupted"]

    print("[PASS] Agent MCP tool")


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--base-url",
        default="http://127.0.0.1:8000",
    )

    parser.add_argument(
        "--full",
        action="store_true",
        help="Run RAG and MCP tests too.",
    )

    args = parser.parse_args()
    base_url = args.base_url.rstrip("/")

    try:
        check_health(base_url)
        check_chat(base_url)

        if args.full:
            check_rag(base_url)
            check_mcp(base_url)

    except (
        AssertionError,
        urllib.error.URLError,
        TimeoutError,
        RuntimeError,
        ValueError,
    ) as exc:
        print(
            f"[FAIL] Smoke test: {exc}",
            file=sys.stderr,
        )
        sys.exit(1)

    print("\nAll selected smoke tests passed.")


if __name__ == "__main__":
    main()
