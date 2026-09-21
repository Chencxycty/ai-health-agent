from dataclasses import dataclass


@dataclass(frozen=True)
class RiskAssessment:
    level: str
    reason: str


HIGH_RISK_PATTERNS = [
    "剧烈胸痛",
    "严重胸痛",
    "无法呼吸",
    "呼吸困难",
    "意识丧失",
    "昏迷",
    "大量出血",
    "大出血",
    "严重过敏",
    "抽搐不止",
]


def assess_risk(
    text: str,
) -> RiskAssessment:
    normalized = text.strip()

    for pattern in HIGH_RISK_PATTERNS:
        if pattern in normalized:
            return RiskAssessment(
                level="high",
                reason=(f"Matched high-risk pattern: {pattern}"),
            )

    return RiskAssessment(
        level="normal",
        reason="",
    )
