"""Découvre les modèles :free actuellement dispo — à lancer avant model_bench.py,
   jamais coder les slugs en dur (catalogue instable, cf. sources conflictuelles 2026)."""
import os, json, requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")

def discover():
    r = requests.get("https://openrouter.ai/api/v1/models",
        headers={"Authorization": f"Bearer {OPENROUTER_KEY}"}, timeout=30)
    r.raise_for_status()
    models = r.json()["data"]

    free = [m for m in models
            if float(m.get("pricing", {}).get("prompt", "1")) == 0.0
            and float(m.get("pricing", {}).get("completion", "1")) == 0.0]

    # Tri par taille de contexte décroissante — proxy grossier de "capacité"
    free.sort(key=lambda m: m.get("context_length", 0), reverse=True)

    print(f"{len(free)} modèles gratuits trouvés aujourd'hui :\n")
    for m in free:
        print(f"  {m['id']:<50} ctx={m.get('context_length','?')}")

    Path("results").mkdir(exist_ok=True)
    with open("results/free_models_current.json", "w", encoding="utf-8") as f:
        json.dump([m["id"] for m in free], f, indent=2)
    print(f"\nSauvegardé : results/free_models_current.json")
    return [m["id"] for m in free]

if __name__ == "__main__":
    discover()