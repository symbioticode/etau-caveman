# scripts/model_bench.py
"""Bench CAVEMAN — teste les modèles free/cheap via Omniroute (point de passage unique)
avant de figer FAMILIES dans src/schemas.py.

Pourquoi Omniroute et pas OpenRouter direct : chaque provider (groq, mistral,
cerebras, openrouter) a son propre quota daily — taper plusieurs providers
multiplie le budget free disponible. Voir 65_OMNIROUTE/docs/omniroute-guide.md §7.

Pourquoi le SDK OpenAI et pas requests : Omniroute répond TOUJOURS en SSE
(text/event-stream), même sans stream:true → requests.json() échoue.
Voir omniroute-guide.md §8.1.
"""
import os, time, json, sys
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
OMNIROUTE_URL = os.getenv("OMNIROUTE_BASE_URL", "http://localhost:20128/v1")
OMNIROUTE_KEY = os.getenv("OMNIROUTE_API_KEY", "omni")

# Modèles candidats par provider (validés 2026-08-09, voir omniroute-guide.md).
# Préfixe "<provider>/" OBLIGATOIRE (sinon 404 "No active credentials").
CANDIDATES = [
    "groq/llama-3.3-70b-versatile",
    "groq/openai/gpt-oss-120b",
    "mistral/mistral-small-latest",
    "mistral/ministral-8b-latest",
    "cerebras/gemma-4-31b",
    "cerebras/gpt-oss-120b",
    "openrouter/google/gemma-4-26b-a4b-it:free",
]

TEST_PROMPT = "En 3 phrases : quels sont les risques d'un système multi-agents où tous les agents partagent le même provider ?"


def bench_model(model: str) -> dict:
    client = OpenAI(base_url=OMNIROUTE_URL, api_key=OMNIROUTE_KEY)
    t0 = time.time()
    try:
        r = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": TEST_PROMPT}],
            max_tokens=300,
            timeout=60,
        )
        latency = time.time() - t0
        content = r.choices[0].message.content or ""
        usage = r.usage
        return {"model": model, "status": "OK", "latency_s": round(latency, 2),
                "tokens_out": getattr(usage, "completion_tokens", None),
                "response_preview": content[:200]}
    except Exception as e:
        return {"model": model, "status": "FAIL", "latency_s": round(time.time() - t0, 2), "error": str(e)[:200]}


def run_bench(candidates=None):
    candidates = candidates or CANDIDATES
    results = [bench_model(m) for m in candidates]

    Path("results").mkdir(exist_ok=True)
    fname = f"results/bench_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(fname, "w", encoding="utf-8") as f:
        json.dump({"timestamp": datetime.now().isoformat(), "results": results}, f, indent=2, ensure_ascii=False)

    print(f"\n{'Modèle':<45} {'Statut':<8} {'Latence':<10} {'Erreur'}")
    for r in results:
        err = r.get("error", "")[:60] if r["status"] == "FAIL" else ""
        print(f"{r['model']:<45} {r['status']:<8} {r.get('latency_s','-'):<10} {err}")
    print(f"\nSauvegardé : {fname}")


if __name__ == "__main__":
    run_bench(sys.argv[1:] or None)
