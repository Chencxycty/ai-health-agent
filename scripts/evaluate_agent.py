import json
import time
from pathlib import Path
from uuid import uuid4

from health_agent.agent.factory import build_agent_service


EVAL_FILE = Path("data/eval/agent_golden.json")


def main() -> None:
    with EVAL_FILE.open(encoding="utf-8") as file:
        cases = json.load(file)

    agent = build_agent_service()

    route_correct = 0
    tool_correct = 0
    interrupt_correct = 0
    source_correct = 0
    answer_correct = 0
    task_success = 0

    tool_cases = 0
    source_cases = 0
    answer_cases = 0
    total_turns = 0
    total_latency_ms = 0.0

    for case in cases:
        # All turns in one scenario share a thread so context is preserved.
        thread_id = f"eval-{uuid4()}"
        turns = case.get("turns", [case])

        for turn_index, turn in enumerate(turns, start=1):
            start = time.perf_counter()
            result = agent.query(
                message=turn["query"],
                thread_id=thread_id,
            )
            latency_ms = (time.perf_counter() - start) * 1000

            total_turns += 1
            total_latency_ms += latency_ms

            route_ok = result.route == turn["expected_route"]
            # A high-risk request is interrupted before the router runs.
            if turn["expected_interrupt"]:
                route_ok = True

            interrupt_ok = result.interrupted == turn["expected_interrupt"]

            expected_tool = turn["expected_tool"]
            tool_ok = True
            if expected_tool is not None:
                tool_cases += 1
                tool_ok = result.tool_name == expected_tool
                tool_correct += int(tool_ok)

            source_ok = True
            if turn["sources_required"]:
                source_cases += 1
                source_ok = bool(result.sources)
                source_correct += int(source_ok)

            answer_ok = True
            expected_text = turn.get("expected_answer_contains")
            if expected_text is not None:
                answer_cases += 1
                answer_ok = expected_text in result.answer
                answer_correct += int(answer_ok)

            route_correct += int(route_ok)
            interrupt_correct += int(interrupt_ok)

            success = all((route_ok, tool_ok, interrupt_ok, source_ok, answer_ok))
            task_success += int(success)

            label = case["id"]
            if len(turns) > 1:
                label = f"{label}.t{turn_index}"

            print(
                f"{label} | category={case['category']} | "
                f"route={route_ok} | tool={tool_ok} | "
                f"interrupt={interrupt_ok} | sources={source_ok} | "
                f"answer={answer_ok} | success={success} | "
                f"{latency_ms:.2f}ms"
            )

    print()
    print("=" * 70)
    print("Scenarios:", len(cases))
    print("Evaluated Turns:", total_turns)
    print("Router Accuracy:", route_correct / total_turns)

    if tool_cases:
        print("Tool Selection Accuracy:", tool_correct / tool_cases)

    print("Interrupt Accuracy:", interrupt_correct / total_turns)

    if source_cases:
        print("RAG Source Accuracy:", source_correct / source_cases)

    if answer_cases:
        print("Expected Answer Accuracy:", answer_correct / answer_cases)

    print("Task Success Rate:", task_success / total_turns)
    print("Average Latency ms:", total_latency_ms / total_turns)


if __name__ == "__main__":
    main()
