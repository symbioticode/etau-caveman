# tests/test_isolation.py — Isolation réelle entre familles (par le code)
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.isolation import build_extraction_messages, validate_isolation, build_synthesis_prompt
from src.prompts import build_extraction_prompt, PERSONAS


def test_extraction_messages_is_single_user_message():
    """Une famille reçoit exactement 1 message user — pas d'historique."""
    for family in PERSONAS:
        system = build_extraction_prompt(PERSONAS[family], "Question de test ?")
        messages = build_extraction_messages(system, "Question de test ?")
        assert len(messages) == 1
        assert messages[0]["role"] == "user"


def test_validate_isolation_rejects_history():
    assert validate_isolation([{"role": "user", "content": "a"}]) == []
    assert validate_isolation([{"role": "system", "content": "a"}])
    assert validate_isolation([{"role": "user", "content": "a"}, {"role": "assistant", "content": "b"}])
    assert validate_isolation([])


def test_extraction_prompt_has_no_other_family_output():
    """Le prompt d'extraction ne peut pas contenir de réponse d'une autre famille :
    la variable {question} est le seul point d'injection."""
    system = build_extraction_prompt(PERSONAS["na"], "Q ?")
    assert "responses" not in system.lower()
    assert "accès aux réponses des autres" in system.lower()  # consigne d'indépendance


def test_synthesis_prompt_contains_only_structured_json():
    """Le synthétiseur reçoit le JSON structuré injecté dans {responses_json} —
    pas de raw_text. Vérifie que build_synthesis_prompt remplace bien les deux
    variables."""
    tpl = "question={question}\nresponses={responses_json}"
    out = build_synthesis_prompt(tpl, "Q?", '{"findings": []}')
    assert "question=Q?" in out
    assert 'responses={"findings": []}' in out
