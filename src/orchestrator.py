# src/orchestrator.py — Pipeline CAVEMAN v2 (produit d'appel ETAU via Omniroute)
"""Pipeline : question → N familles d'IA en parallèle (isolation par le code,
sortie structurée Belnap) → synthèse graduée (FORT/PROBABLE/FAIBLE) → résultat
JSON renvoyé au client. La "cuisine" entre le prompt client et le résultat.

Ce fichier REMPLACE l'ancien orchestrator CAVEMAN v1 (OpenRouter direct,
modèles figés, séquentiel, synthèse par 1 seul modèle non structurée).
"""
from __future__ import annotations

import asyncio
import json
import time
from datetime import datetime
from typing import Optional

from openai import OpenAI

from . import schemas
from .isolation import build_synthesis_prompt
from .llm_clients import DeepSeekClient, OmnirouteClient, parse_extraction_json
from .prompts import SYNTHESIS_TEMPLATE
from .schemas import (
    ConfidenceLevel,
    FamilyResponse,
    PipelineResult,
    SynthesisResult,
)

PIPELINE_NAME = "ETAU-CAVEMAN-v0.2"

# Timeout wall-clock par appel de famille — garde-fou contre les free tiers qui stallent.
CALL_TIMEOUT_S = 120

# --- Health-check pré-run (mission 2026-08-09) ----------------------------
# Ping rapide AVANT l'extraction : un PONG max_tokens=5 par provider retenu,
# sans retry (le run consomme déjà du quota). Si un provider échoue ici, on
# bloque AVANT de lancer l'extraction — on ne découvre pas l'échec en plein
# run. Liste verrouillée sur les substrats sains (voir src/schemas.py) ;
# n'y ajouter un provider qu'après un bench vert + reset de quota confirmé.
HEALTH_CHECK_MODELS = [
    "groq/llama-3.3-70b-versatile",
    "mistral/mistral-small-latest",
    "cerebras/gemma-4-31b",
]
HEALTH_TIMEOUT_S = 25

# Les 4 familles free passent par Omniroute ; DeepSeek est une famille bonus
# en API directe (hors catalogue Omniroute — limite documentée).
FAMILY_PROVIDERS = {
    "na": "omniroute",
    "asia": "omniroute",
    "eu": "omniroute",
    "diverse": "omniroute",
    "deepseek": "deepseek",
}

# Coût estimé par token (USD/1k, approximatif, à affiner en production)
COST_PER_1K_IN = 0.0       # familles :free OpenRouter
COST_PER_1K_OUT = 0.0
DEEPSEEK_IN_PER_1K = 0.0   # deepseek-v4-flash (tiers gratuits du moment, à confirmer)
DEEPSEEK_OUT_PER_1K = 0.0


def _parse_synthesis_json(raw: str) -> dict:
    """Parse la sortie JSON de synthèse (mêmes stratégies de secours que l'extraction)."""
    candidates = [raw]
    if "{" in raw:
        candidates.append(raw[raw.index("{"):])
    for c in list(candidates):
        if c.rfind("}") > c.find("{"):
            candidates.append(c[:c.rfind("}") + 1])
    candidates.append(raw.replace("\n", "").replace("\r", ""))
    for c in dict.fromkeys(candidates):
        try:
            return json.loads(c)
        except json.JSONDecodeError:
            continue
    raise ValueError(f"sortie de synthèse non-JSON ({len(raw)} chars)")


def _synthesis_from_dict(data: dict) -> SynthesisResult:
    """Convertit le dict JSON de synthèse en SynthesisResult (tolérant)."""
    def _list(key: str) -> list[str]:
        v = data.get(key, [])
        return [str(x).strip() for x in v if str(x).strip()] if isinstance(v, list) else []

    graded = []
    for g in data.get("graded_findings", []) if isinstance(data.get("graded_findings"), list) else []:
        if isinstance(g, dict) and g.get("text"):
            graded.append({
                "text": g["text"],
                "confidence": g.get("confidence", "FAIBLE"),
                "source_families": g.get("source_families", []),
            })
    return SynthesisResult(
        common_ground=_list("common_ground"),
        disagreements=_list("disagreements"),
        blind_spots=_list("blind_spots"),
        open_zones=_list("open_zones"),
        hypotheses=_list("hypotheses"),
        graded_findings=graded,
    )


class ETAUOrchestrator:
    """Orchestrateur CAVEMAN v2 — pipeline complet question → résultat."""

    def __init__(self, include_deepseek: bool = True):
        self.omni = OmnirouteClient()
        self.deepseek = DeepSeekClient() if include_deepseek else None

    def _route(self, family: str) -> OmnirouteClient | DeepSeekClient:
        if family == "deepseek":
            assert self.deepseek is not None
            return self.deepseek
        return self.omni

    async def _call_family(self, family: str, question: str) -> FamilyResponse:
        """Un appel de famille dans un thread (les clients OpenAI sont bloquants).
        Garde-fou wall-clock : chaque famille ne peut pas dépasser CALL_TIMEOUT_S."""
        client = self._route(family)
        try:
            return await asyncio.wait_for(
                asyncio.to_thread(client.call, family, question), timeout=CALL_TIMEOUT_S)
        except asyncio.TimeoutError:
            resp = FamilyResponse(family=family, model="", provider="")
            resp.error = f"timeout après {CALL_TIMEOUT_S}s"
            return resp

    async def _run_extraction(self, question: str, families: list[str]) -> dict[str, FamilyResponse]:
        results: dict[str, FamilyResponse] = {}
        # Parallélisme réel : chaque famille = une coroutine indépendante.
        tasks = {fam: asyncio.create_task(self._call_family(fam, question)) for fam in families}
        for fam, task in tasks.items():
            results[fam] = await task
        return results

    def _synthesize(self, question: str, responses: dict[str, FamilyResponse]) -> tuple[SynthesisResult, Optional[str]]:
        """Synthèse : reçoit UNIQUEMENT les sorties structurées JSON (jamais les
        textes bruts), conforme à la séparation des étages du banc-essai."""
        payload = {
            fam: {
                "findings": [
                    {"text": f.text, "epistemic_state": f.epistemic_state.value, "reasoning": f.reasoning}
                    for f in resp.findings
                ],
                "error": resp.error,
            }
            for fam, resp in responses.items()
        }
        prompt = build_synthesis_prompt(
            SYNTHESIS_TEMPLATE,
            question=question,
            responses_json=json.dumps(payload, ensure_ascii=False, indent=2),
        )
        synth = OpenAI(base_url=self.omni.client.base_url, api_key="omni")
        # Modèles candidats en ordre de préférence — fallback si upstream vide.
        # Providers indépendants du quota OpenRouter (épuisé le 2026-08-09) :
        # Groq, Mistral, Cerebras — voir schemas.FAMILIES.
        synth_models = [
            "groq/llama-3.3-70b-versatile",
            "mistral/mistral-small-latest",
            "cerebras/gemma-4-31b",
        ]
        for model in synth_models:
            try:
                r = synth.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=2500,
                    timeout=90,
                )
                raw = (r.choices[0].message.content or "").strip()
                if not raw:
                    continue
                data = _parse_synthesis_json(raw)
                return _synthesis_from_dict(data), None
            except Exception:
                continue
        return SynthesisResult(), "synthèse impossible : tous les modèles ont échoué"

    async def _health_check(self) -> dict[str, dict]:
        """Ping rapide des providers retenus AVANT l'extraction (PONG max_tokens=5,
        parallèle, pas de retry). Retourne l'état par provider."""
        async def ping(model: str) -> tuple[str, dict]:
            t0 = time.time()
            provider = model.split("/")[0]
            try:
                r = await asyncio.to_thread(
                    self.omni.client.chat.completions.create,
                    model=model,
                    messages=[{"role": "user", "content": "Réponds uniquement: PONG"}],
                    max_tokens=5,
                    timeout=HEALTH_TIMEOUT_S,
                )
                ok = bool((r.choices[0].message.content or "").strip())
                return provider, {"ok": ok, "latency_s": round(time.time() - t0, 2)}
            except Exception as e:
                return provider, {"ok": False, "latency_s": round(time.time() - t0, 2),
                                  "error": str(e)[:120]}

        tasks = [asyncio.create_task(ping(m)) for m in HEALTH_CHECK_MODELS]
        return {p: s for p, s in [await t for t in tasks]}

    async def run(self, question: str, families: Optional[list[str]] = None) -> PipelineResult:
        """Pipeline complet : question → health-check → réponses structurées → synthèse → résultat."""
        fams = families or list(FAMILY_PROVIDERS.keys())
        fams = [f for f in fams if f in FAMILY_PROVIDERS]
        t0 = time.time()

        health = await self._health_check()
        health_down = [p for p, s in health.items() if not s["ok"]]
        if health_down:
            metadata = {
                "total_latency_s": round(time.time() - t0, 2),
                "health_check": health,
                "preflight_error": f"providers en échec au health-check, extraction annulée: {health_down}",
                "failed_families": list(health_down),
                "synthesis_error": None,
                "tokens_in": 0,
                "tokens_out": 0,
                "estimated_cost_usd": 0.0,
                "provider_map": {f: FAMILY_PROVIDERS[f] for f in fams},
            }
            return PipelineResult(
                pipeline=PIPELINE_NAME,
                question=question,
                timestamp=datetime.now().isoformat(),
                variants={f: question for f in fams},
                responses={},
                synthesis=SynthesisResult(),
                metadata=metadata,
            )

        responses = await self._run_extraction(question, fams)
        synthesis, synth_error = self._synthesize(question, responses)

        failed = [f for f, r in responses.items() if r.error]
        total_in = sum(r.tokens_in for r in responses.values())
        total_out = sum(r.tokens_out for r in responses.values())
        # Metadata : latence par famille, échecs, tokens, coût estimé.
        metadata = {
            "total_latency_s": round(time.time() - t0, 2),
            "latency_by_family": {f: r.latency_s for f, r in responses.items()},
            "failed_families": failed,
            "synthesis_error": synth_error,
            "tokens_in": total_in,
            "tokens_out": total_out,
            "estimated_cost_usd": round((total_in * 0 + total_out * 0), 6),
            "provider_map": {f: FAMILY_PROVIDERS[f] for f in fams},
            "health_check": health,
        }

        return PipelineResult(
            pipeline=PIPELINE_NAME,
            question=question,
            timestamp=datetime.now().isoformat(),
            variants={f: question for f in fams},  # v0.2 : même question pour toutes les familles
            responses={f: r for f, r in responses.items()},
            synthesis=synthesis,
            metadata=metadata,
        )


if __name__ == "__main__":
    import sys
    from pathlib import Path
    from dotenv import load_dotenv

    load_dotenv()
    q = sys.argv[1] if len(sys.argv) > 1 else (
        "Comment les limites épistémiques des IA contraignent-elles "
        "leur contribution à la stratégie ?")
    result = asyncio.run(ETAUOrchestrator().run(q))
    Path("results").mkdir(exist_ok=True)
    fname = f"results/run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    Path(fname).write_text(result.to_json(), encoding="utf-8")
    print(result.to_json())
    print(f"\nSauvegardé : {fname}")
