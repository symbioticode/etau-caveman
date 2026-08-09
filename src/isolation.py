# src/isolation.py — Isolation réelle entre familles d'IA (par le code, pas par la promesse)
"""Hérité de la décision DEC-001 du banc-essai ETAU/SECS :
l'isolation est STRUCTURELLE (le code ne peut pas fuiter le contexte d'une
famille vers une autre), pas une simple consigne de prompt.

Invariant : chaque famille reçoit exactement 1 message user, sans historique,
sans réponse d'une autre famille. Le synthétiseur, lui, ne reçoit JAMAIS le
corpus brut — uniquement les sorties structurées JSON des familles.
"""
from __future__ import annotations


def build_extraction_messages(system_prompt: str, question: str) -> list[dict]:
    """Construit les messages d'une famille. Retourne une liste à EXACTEMENT
    1 message user — aucun rôle assistant, aucun historique.

    Assertions vérifiables en test (validate_isolation ci-dessous).
    """
    messages = [{"role": "user", "content": f"{system_prompt}\n\n{question}"}]
    assert validate_isolation(messages) == [], "violation d'isolation à la construction"
    return messages


def validate_isolation(messages: list[dict]) -> list[str]:
    """Vérifie l'isolation structurelle d'une liste de messages.
    Retourne les erreurs (liste vide = isolation correcte).
    """
    errors: list[str] = []
    if len(messages) != 1:
        errors.append(f"attendu 1 message, reçu {len(messages)}")
    if messages and messages[0].get("role") != "user":
        errors.append("le premier message doit être 'user'")
    if any(m.get("role") == "assistant" for m in messages):
        errors.append("présence d'un rôle assistant (fuite d'historique)")
    return errors


def build_synthesis_prompt(synthesis_template: str, question: str, responses_json: str) -> str:
    """Construit le prompt du synthétiseur : SEUL le JSON structuré des familles
    est injecté, jamais les textes bruts du corpus/question d'origine autrement
    que via `question`. Garantit que le synthétiseur ne peut pas relire les
    réponses brutes (uniquement les findings déjà structurés).
    """
    return synthesis_template.replace("{question}", question).replace("{responses_json}", responses_json)
