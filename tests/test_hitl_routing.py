from health_agent.agent.graph import (
    route_after_review,
    route_after_risk,
)


def test_high_risk_goes_review():
    assert route_after_risk({"risk_level": "high"}) == "human_review"


def test_normal_goes_router():
    assert route_after_risk({"risk_level": "normal"}) == "router"


def test_review_rejects():
    assert route_after_review({"review_approved": False}) == "safe_answer"


def test_review_approves():
    assert route_after_review({"review_approved": True}) == "router"
