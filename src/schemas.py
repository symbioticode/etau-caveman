# src/schemas.py — Schémas de sortie structurée du POC CAVEMAN v2
"""Schémas hérités du banc-essai ETAU/SECS (schemas.py), allégés pour le
produit d'appel : chaque IA produit des unités comparables (findings) à
statut épistémique et confiance graduée. Rien n'est CONFIRMÉ sans vérification
croisée (voir THESE_ETAU_POC.md, invariant 4)."""
from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional


class EpistemicState(str, Enum):
    """Logique de Belnap à 4 valeurs."""
    T = "T"          # soutenu par la réponse
    F = "F"          # contredit par la réponse
    B = "B"          # conflit/contradiction
    N = "N"          # ni l'un ni l'autre (non testé / inconnu)


class ConfidenceLevel(str, Enum):
    """Confiance graduée — assignée UNIQUEMENT en synthèse, jamais par l'appelant."""
    FORT = "FORT"
    PROBABLE = "PROBABLE"
    FAIBLE = "FAIBLE"


# =========================================================================
# FAMILIES — carte des familles CAVEMAN (ROLE_MODEL)
# =========================================================================
# VÉRIFIÉ santé 2026-08-09 (analyse call_logs SQLite 24h, voir
# 65_OMNIROUTE/docs/omniroute-guide.md §11 — requête de diagnostic santé).
#
# ÉTAT OPÉRATIONNEL — 3 modèles configurés et sains lors du relevé :
#   - groq/llama-3.3-70b-versatile   : 22/22 OK   → sain
#   - mistral/mistral-small-latest   : 17/17 OK   → sain
#   - cerebras/gemma-4-31b           :  8/8  OK   → sain
# Leur indépendance n'est ni affirmée ni mesurée ici : cette calibration
# appartient à AGORA/substrat-bench, hors pipeline CAVEMAN.
#
# EXCLUSIONS EXPLICITES (définitives pour les runs) :
#   - openrouter/*:free  → non fiable (quota free-models-per-day épuisé :
#     gemma-4-26b = 7/143 OK, nemotron = 7/38 OK). Réintroduire UNIQUEMENT
#     après confirmation du reset (omniroute usage quota) et d'un bench vert.
#   - cerebras/zai-glm-4.7 → CASSÉ (30 échecs 502 sur 32). Ne jamais
#     réutiliser ce modèle précis ; cerebras/gemma-4-31b et
#     cerebras/gpt-oss-120b restent sains.
#
# Préfixe "<provider>/" OBLIGATOIRE : Omniroute route par provider dans sa
# table de connexions (sans préfixe → 404 "No active credentials for provider").
FAMILIES = {
    "na":      "groq/llama-3.3-70b-versatile",        # Groq (Llama 3.3 70B)
    "asia":    "mistral/mistral-small-latest",        # Mistral (small)
    "eu":      "cerebras/gemma-4-31b",                # Cerebras (Gemma 4 31B)
    "diverse": "groq/openai/gpt-oss-120b",            # Groq (GPT-OSS 120B — substrat OpenAI, partage groq)
}

DEEPSEEK_MODEL = "deepseek-v4-flash"
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"


@dataclass
class Finding:
    """Unité atomique de réponse : une affirmation + son statut épistémique.

    - `epistemic_state` : la logique Belnap — ce que l'IA prétend, pas ce
      qui est vrai. Une IA qui répond à une question qu'elle ne peut pas
      trancher doit dire `N`, pas inventer.
    - `confidence` : laissée vide au niveau extraction (jamais assignée par
      l'appelant) — remplie par le synthétiseur.
    """
    text: str
    epistemic_state: EpistemicState = EpistemicState.N
    confidence: Optional[ConfidenceLevel] = None
    source_family: str = ""
    reasoning: str = ""


@dataclass
class FamilyResponse:
    """Réponse structurée d'une famille d'IA pour un variant donné."""
    family: str
    model: str
    provider: str                      # "omniroute" | "deepseek"
    findings: list[Finding] = field(default_factory=list)
    raw_text: str = ""
    error: Optional[str] = None
    latency_s: Optional[float] = None
    tokens_in: int = 0
    tokens_out: int = 0


@dataclass
class SynthesisResult:
    """Résultat de synthèse : accords, désaccords, angles morts, zones ouvertes."""
    common_ground: list[str] = field(default_factory=list)
    disagreements: list[str] = field(default_factory=list)
    blind_spots: list[str] = field(default_factory=list)
    open_zones: list[str] = field(default_factory=list)     # non-convergence signalée
    hypotheses: list[str] = field(default_factory=list)
    graded_findings: list[dict] = field(default_factory=list)  # findings + confidence


@dataclass
class PipelineResult:
    """Sortie complète du pipeline CAVEMAN v2 — ce qui est renvoyé au client."""
    pipeline: str                       # "ETAU-CAVEMAN-v0.2"
    question: str
    timestamp: str
    variants: dict                      # family -> variant text (toujours la question ici, v0.2)
    responses: dict                     # family -> FamilyResponse
    synthesis: SynthesisResult
    metadata: dict                      # latence, échecs, tokens, coût estimé

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, indent=2, default=str)


def validate_findings(data: dict) -> list[str]:
    """Valide la sortie structurée d'une IA. Retourne la liste des erreurs (vide = OK)."""
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["la sortie n'est pas un objet JSON"]
    findings = data.get("findings")
    if not isinstance(findings, list) or not findings:
        return ["aucune entrée 'findings' (liste non vide requise)"]
    for i, f in enumerate(findings):
        if not isinstance(f, dict) or not isinstance(f.get("text"), str) or not f["text"].strip():
            errors.append(f"finding[{i}]: 'text' requis (chaîne non vide)")
        if "epistemic_state" in f and f["epistemic_state"] not in {e.value for e in EpistemicState}:
            errors.append(f"finding[{i}]: 'epistemic_state' invalide ({f['epistemic_state']})")
    return errors
