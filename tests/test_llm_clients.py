# tests/test_llm_clients.py — Parsing résilient + logique de mapping
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.llm_clients import parse_extraction_json, parse_findings
from src.schemas import EpistemicState


def test_parse_clean_json():
    raw = '{"findings": [{"text": "a", "epistemic_state": "T"}]}'
    assert parse_extraction_json(raw)["findings"][0]["text"] == "a"


def test_parse_json_with_markdown_fence():
    raw = '```json\n{"findings": [{"text": "a"}]}\n```'
    assert parse_extraction_json(raw)["findings"][0]["text"] == "a"


def test_parse_json_with_prefix_text():
    """Certains modèles free préfixent du texte avant le JSON."""
    raw = 'Voici mes findings : {"findings": [{"text": "a", "epistemic_state": "T"}]}'
    assert parse_extraction_json(raw)["findings"][0]["text"] == "a"


def test_parse_json_with_suffix_text():
    raw = '{"findings": [{"text": "a"}]} et c\'est tout'
    assert parse_extraction_json(raw)["findings"][0]["text"] == "a"


def test_parse_multiline_json():
    raw = '{\n  "findings": [\n    {"text": "a", "epistemic_state": "T"}\n  ]\n}'
    assert parse_extraction_json(raw)["findings"][0]["epistemic_state"] == "T"


def test_parse_invalid_raises():
    import pytest
    with pytest.raises(ValueError):
        parse_extraction_json("pas du json")


def test_parse_findings_skips_empty_and_bad_state():
    data = {"findings": [
        {"text": "ok", "epistemic_state": "T"},
        {"text": "", "epistemic_state": "T"},
        {"text": "bad state", "epistemic_state": "POSSIBLE"},
        {"text": "missing state"},
        "not a dict",
    ]}
    findings = parse_findings(data, "na")
    assert [f.text for f in findings] == ["ok", "bad state", "missing state"]
    assert findings[0].epistemic_state is EpistemicState.T
    assert findings[1].epistemic_state is EpistemicState.N  # état invalide → N
    assert findings[2].epistemic_state is EpistemicState.N  # absent → N


def test_family_providers_mapping():
    from src.orchestrator import FAMILY_PROVIDERS
    assert set(FAMILY_PROVIDERS) >= {"na", "asia", "eu", "diverse", "deepseek"}
    assert FAMILY_PROVIDERS["na"] == "omniroute"
    assert FAMILY_PROVIDERS["deepseek"] == "deepseek"
