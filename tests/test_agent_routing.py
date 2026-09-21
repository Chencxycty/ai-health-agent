from health_agent.agent.graph import (
    route_after_review,
    route_after_risk,
    route_after_router,
)


def test_high_risk_goes_to_review():
    assert route_after_risk({"risk_level": "high"}) == "human_review"


def test_normal_risk_goes_to_router():
    assert route_after_risk({"risk_level": "normal"}) == "router"


def test_medical_route_goes_to_rag():
    assert route_after_router({"route": "medical_knowledge"}) == "rewrite_query"


def test_calculation_route_goes_to_tool():
    assert route_after_router({"route": "health_calculation"}) == "tool"


def test_chat_route_goes_to_chat():
    assert route_after_router({"route": "general_chat"}) == "chat"


def test_rejected_review_goes_safe():
    assert route_after_review({"approved": False}) == "safe_answer"
