# tests/test_schemas.py — Validation des schémas de sortie structurée
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.schemas import (
    ConfidenceLevel,
    EpistemicState,
    FamilyResponse,
    Finding,
    PipelineResult,
    SynthesisResult,
    validate_findings,
)


def test_finding_default_state_is_N():
    """Un finding sans état explicite = N (ni T ni F ni B)."""
    f = Finding(text="une affirmation")
    assert f.epistemic_state is EpistemicState.N


def test_finding_confidence_is_none_at_extraction():
    """La confiance n'est JAMAIS assignée au niveau extraction."""
    f = Finding(text="x", epistemic_state=EpistemicState.T)
    assert f.confidence is None


def test_confidence_only_in_synthesis():
    """La confiance graduée n'existe que dans la synthèse."""
    s = SynthesisResult(graded_findings=[{"text": "y", "confidence": "FORT"}])
    assert s.graded_findings[0]["confidence"] == "FORT"


def test_validate_findings_ok():
    data = {"findings": [{"text": "fait atomique", "epistemic_state": "T"}]}
    assert validate_findings(data) == []


def test_validate_findings_missing_text():
    data = {"findings": [{"epistemic_state": "T"}]}
    assert validate_findings(data)


def test_validate_findings_bad_state():
    data = {"findings": [{"text": "x", "epistemic_state": "POSSIBLE"}]}
    assert validate_findings(data)


def test_validate_findings_no_findings():
    assert validate_findings({"other": 1})
    assert validate_findings("not a dict")


def test_pipeline_result_json_roundtrip():
    r = PipelineResult(
        pipeline="ETAU-CAVEMAN-v0.2",
        question="q",
        timestamp="2026-08-09T00:00:00",
        variants={"na": "q"},
        responses={"na": FamilyResponse(family="na", model="m", provider="omniroute")},
        synthesis=SynthesisResult(common_ground=["a"], graded_findings=[{"text": "x", "confidence": "FORT"}]),
        metadata={"total_latency_s": 1.0},
    )
    import json
    d = json.loads(r.to_json())
    assert d["pipeline"] == "ETAU-CAVEMAN-v0.2"
    assert d["responses"]["na"]["family"] == "na"
    assert d["synthesis"]["graded_findings"][0]["confidence"] == "FORT"
