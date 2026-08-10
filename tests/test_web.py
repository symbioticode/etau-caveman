from types import SimpleNamespace

from src.schemas import EpistemicState, FamilyResponse, Finding, SynthesisResult
from web.app import render_result


def test_result_is_readable_and_substrates_are_collapsible():
    responses = {}
    for family in ("na", "asia", "eu"):
        responses[family] = FamilyResponse(
            family=family,
            model=f"provider/{family}",
            provider="omniroute",
            findings=[Finding(text=f"Réponse {family}", epistemic_state=EpistemicState.T)],
            latency_s=1.2,
        )
    result = SimpleNamespace(
        synthesis=SynthesisResult(common_ground=["Accord lisible"]),
        responses=responses,
        metadata={"total_latency_s": 3.4, "estimated_cost_usd": 0.0},
    )

    rendered = render_result(result)

    assert "<h2>Synthèse</h2>" in rendered
    assert "Accord lisible" in rendered
    assert rendered.count("<details>") == 3
    assert "Réponse na" in rendered
    assert "{&quot;" not in rendered
