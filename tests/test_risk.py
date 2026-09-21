from health_agent.agent.risk import (
    assess_risk,
)


def test_high_risk() -> None:
    result = assess_risk("我突然剧烈胸痛")

    assert result.level == "high"


def test_normal() -> None:
    result = assess_risk("什么是高血压？")

    assert result.level == "normal"
