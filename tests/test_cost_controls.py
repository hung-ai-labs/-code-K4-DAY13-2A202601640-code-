from __future__ import annotations

from app import agent as agent_module
from app.cost_controls import cap_output_tokens
from app.incidents import disable, enable


def test_cap_output_tokens_limits_spike() -> None:
    assert cap_output_tokens(720) == 180
    assert cap_output_tokens(120) == 120


def test_cost_spike_is_capped_in_agent(monkeypatch) -> None:
    monkeypatch.setenv("MAX_OUTPUT_TOKENS", "180")
    monkeypatch.setattr(agent_module, "RESPONSE_CACHE_ENABLED", False)
    monkeypatch.setattr(agent_module, "cap_output_tokens", lambda n: min(n, 180))
    enable("cost_spike")
    try:
        agent = agent_module.LabAgent()
        result = agent_module.LabAgent.run.__wrapped__(
            agent,
            user_id="u01",
            feature="qa",
            session_id="s01",
            message="Explain cost controls",
        )
        assert result.tokens_out <= 180
    finally:
        disable("cost_spike")


def test_response_cache_avoids_repeat_cost(monkeypatch) -> None:
    monkeypatch.setattr(agent_module, "RESPONSE_CACHE_ENABLED", True)
    agent = agent_module.LabAgent()
    kwargs = {
        "user_id": "u01",
        "feature": "qa",
        "session_id": "s01",
        "message": "Same question for cache test",
    }
    first = agent_module.LabAgent.run.__wrapped__(agent, **kwargs)
    second = agent_module.LabAgent.run.__wrapped__(agent, **kwargs)

    assert first.cost_usd > 0
    assert second.cost_usd == 0.0
    assert second.tokens_out == 0
