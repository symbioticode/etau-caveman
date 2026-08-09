# src/llm_clients.py — Clients LLM du POC CAVEMAN v2
"""Deux voies d'appel, une interface commune :
- Omniroute (endpoint OpenAI-compatible localhost:20128/v1) pour les familles
  free OpenRouter — le routeur qui doit devenir le point de passage unique.
- DeepSeek en API directe (OpenAI-compatible) — DeepSeek n'est pas au
  catalogue Omniroute ; appelé en direct, pattern identique à AGORA.

Toute la sélection de modèle est pilotée par `schemas.FAMILIES`.
"""
from __future__ import annotations

import json
import os
import time
from typing import Optional

from openai import OpenAI

from . import schemas
from .isolation import build_extraction_messages
from .prompts import build_extraction_prompt, PERSONAS
from .schemas import EpistemicState, FamilyResponse, Finding

OMNIROUTE_BASE_URL = os.getenv("OMNIROUTE_BASE_URL", "http://localhost:20128/v1")


def _newline_json(raw: str) -> str:
    """Certains modèles free émettent du JSON multi-lignes malformé :
    on tente de le réparer en supprimant les retours à la ligne INSIDE strings
    est complexe — approche pragmatique : tenter json.loads sur le brut, puis
    sur une version sans sauts de ligne hors accolades."""
    return raw


def parse_extraction_json(raw: str) -> dict:
    """Parse la sortie JSON d'une famille avec 3 stratégies de secours.
    Lève ValueError si aucune ne passe — l'appelant capte et marque l'erreur."""
    candidates = [raw]
    # couper tout ce qui précède la première "{" (certains modèles préfixent)
    if "{" in raw:
        candidates.append(raw[raw.index("{"):])
    # retirer tout ce qui suit la dernière "}" (certains modèles suffixent)
    for c in list(candidates):
        if c.rfind("}") > c.find("{"):
            candidates.append(c[:c.rfind("}") + 1])
    # JSON en une ligne (sans retours à la ligne)
    candidates.append(raw.replace("\n", "").replace("\r", ""))
    for c in dict.fromkeys(candidates):
        try:
            return json.loads(c)
        except json.JSONDecodeError:
            continue
    raise ValueError(f"sortie non-JSON ({len(raw)} chars)")


def parse_findings(data: dict, family: str) -> list[Finding]:
    """Convertit le dict JSON d'une famille en liste de Finding (validation stricte)."""
    findings = data.get("findings", [])
    out: list[Finding] = []
    for f in findings if isinstance(findings, list) else []:
        text = (f.get("text") or "").strip() if isinstance(f, dict) else ""
        if not text:
            continue
        state_raw = (f.get("epistemic_state") or "N") if isinstance(f, dict) else "N"
        try:
            state = EpistemicState(state_raw)
        except ValueError:
            state = EpistemicState.N
        out.append(Finding(
            text=text,
            epistemic_state=state,
            source_family=family,
            reasoning=(f.get("reasoning") or "").strip() if isinstance(f, dict) else "",
        ))
    return out


class OmnirouteClient:
    """Client vers Omniroute (OpenAI-compatible). Utilise les modèles FAMILIES."""

    def __init__(self, base_url: str = OMNIROUTE_BASE_URL, max_retries: int = 2, retry_backoff_s: float = 3.0):
        self.client = OpenAI(base_url=base_url, api_key=os.getenv("OMNIROUTE_API_KEY", "omni"))
        self.max_retries = max_retries
        self.retry_backoff_s = retry_backoff_s

    def call(self, family: str, question: str, timeout_s: int = 45) -> FamilyResponse:
        model = schemas.FAMILIES[family]
        persona = PERSONAS[family]
        system = build_extraction_prompt(persona, question)
        messages = build_extraction_messages(system, question)  # isolation structurée
        t0 = time.time()
        resp = FamilyResponse(family=family, model=model, provider="omniroute")

        last_err: Optional[str] = None
        for attempt in range(self.max_retries + 1):
            try:
                r = self.client.chat.completions.create(
                    model=model, messages=messages, max_tokens=2000, timeout=timeout_s)
                raw = (r.choices[0].message.content or "").strip()
                if not raw and attempt < self.max_retries:
                    last_err = "réponse vide (upstream 502/empty)"
                    time.sleep(self.retry_backoff_s)
                    continue
                resp.latency_s = round(time.time() - t0, 2)
                resp.raw_text = raw
                resp.tokens_in = getattr(r.usage, "prompt_tokens", 0) or 0
                resp.tokens_out = getattr(r.usage, "completion_tokens", 0) or 0
                data = parse_extraction_json(raw)
                resp.findings = parse_findings(data, family)
                if resp.findings:
                    return resp
                last_err = "sortie JSON sans findings exploitables"
            except Exception as e:
                last_err = f"{type(e).__name__}: {str(e)[:200]}"
            if attempt < self.max_retries:
                time.sleep(self.retry_backoff_s)

        resp.latency_s = round(time.time() - t0, 2)
        resp.error = last_err or "échec inconnu"
        return resp


class DeepSeekClient:
    """Client DeepSeek en API directe (OpenAI-compatible)."""

    def __init__(self, max_retries: int = 2, retry_backoff_s: float = 2.0):
        self.client = OpenAI(base_url=schemas.DEEPSEEK_BASE_URL,
                             api_key=os.getenv("DEEPSEEK_API_KEY"))
        self.model = schemas.DEEPSEEK_MODEL
        self.max_retries = max_retries
        self.retry_backoff_s = retry_backoff_s

    def call(self, family: str, question: str, timeout_s: int = 45) -> FamilyResponse:
        persona = PERSONAS.get(family, PERSONAS["diverse"])
        system = build_extraction_prompt(persona, question)
        messages = build_extraction_messages(system, question)
        t0 = time.time()
        resp = FamilyResponse(family=family, model=self.model, provider="deepseek")

        last_err: Optional[str] = None
        for attempt in range(self.max_retries + 1):
            try:
                r = self.client.chat.completions.create(
                    model=self.model, messages=messages, max_tokens=1200,
                    reasoning_effort="low",  # sinon le raisonnement caché consomme tout le budget
                    timeout=timeout_s)
                raw = (r.choices[0].message.content or "").strip()
                resp.latency_s = round(time.time() - t0, 2)
                resp.raw_text = raw
                resp.tokens_in = getattr(r.usage, "prompt_tokens", 0) or 0
                resp.tokens_out = getattr(r.usage, "completion_tokens", 0) or 0
                data = parse_extraction_json(raw)
                resp.findings = parse_findings(data, family)
                if resp.findings:
                    return resp
                last_err = "sortie JSON sans findings exploitables"
            except Exception as e:
                last_err = f"{type(e).__name__}: {str(e)[:200]}"
            if attempt < self.max_retries:
                time.sleep(self.retry_backoff_s)

        resp.latency_s = round(time.time() - t0, 2)
        resp.error = last_err or "échec inconnu"
        return resp
