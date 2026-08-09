# PROMPT POUR BIG PICKLE — Phase 1 Setup ETAU + KB Obsidian

## Contexte d'Andrei

- **OS**: NixOS avec direnv
- **Projects folder**: ~/Projects/ (56+ projets existants)
- **Template**: python ~/Templates/init_project.py "Nom Projet"
- **KB**: Obsidian local (~/Knowledge/) + Google Drive sync
- **API keys**: Anthropic + Deepseek disponibles
- **Budget**: $10/mois pour Phase 1
- **Stratégie 12-semaines**: 
  - Weeks 1–3: Phase 1 (Env + KB)
  - Weeks 4–6: ETAU POC (orchestrator + synthesizer)
  - Weeks 7–9: Auto-research (Ruflo/OmniRoute)
  - Weeks 10–12: Converters + YouTube KB

---

## MISSION: Setup Phase 1 End-to-End

Tu dois créer une structure **prête à démarrer lundi matin**.

### Livrables à la Fin

- [ ] Dossier `~/Projects/XX_ETAU/` crée avec architecture complète
- [ ] `shell.nix` avec Python + Anthropic SDK + Deepseek SDK
- [ ] Trois scripts exécutables:
  - `./scripts/run.sh "Votre question"` → lance orchestrator
  - `python src/kb_sync.py` → pousse résultat à ~/Knowledge/brainstorms/
  - `python scripts/observer.py` → show weekly tasks
- [ ] Premier test: exécuter ETAU sur une question exemple
- [ ] Token cost logging (CSV) qui tracks chaque appel
- [ ] Documentation en FRANÇAIS dans docs/

---

## Ressources

Andrei a déjà:
- Template init_project.py → respecter sa structure
- project.relations.yml pattern → l'utiliser pour dépendances
- Obsidian vault → intégrer comme cible KB (pas Notion)
- Deepseek + Anthropic API keys → utiliser tous les deux pour réduire coût

---

## Plan d'Exécution (4 heures = ce qu'on va faire ensemble)

### STEP 1: Créer la structure (30 min)

```bash
cd ~/Projects
python ~/Templates/init_project.py "XX_ETAU" --identity symbioticode
cd XX_ETAU
```

Cela crée:
- `docs/learn`, `docs/specs`, `docs/theory`, `milestones`
- `src/`, `tests/`, `scripts/`
- `.envrc`, `shell.nix`, `justfile`, `.gitignore`
- `project.relations.yml` (vide pour l'instant)
- `.env` (prêt à utiliser)

**Vérifier**: `tree XX_ETAU` et montrer que tout est là

### STEP 2: Adapter shell.nix (20 min)

Remplacer le shell.nix générique par une version qui inclut:
- Python 3.12
- `anthropic` package
- `requests` (pour Deepseek API)
- `pytest` + `black`
- Tools: `just`, `git`

### STEP 3: Implémenter orchestrator.py (90 min)

**Fichier**: `src/orchestrator.py`

Faire une version **ultra-simple** (pas async, pas erreurs complexes):

```python
#!/usr/bin/env python3
"""
Orchestrator ETAU v0.1
Usage: python src/orchestrator.py "Votre question"

Phase 1 POC: Sonnet + Deepseek seulement (pas Qwen/Mistral pour l'instant)
"""

import os
import json
import sys
from datetime import datetime
from pathlib import Path
from anthropic import Anthropic

# Init
ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY")
DEEPSEEK_KEY = os.getenv("DEEPSEEK_API_KEY")

client = Anthropic(api_key=ANTHROPIC_KEY)

class ETAU:
    def __init__(self):
        self.tokens_log = []
    
    def reformat(self, user_query: str) -> dict:
        """Step 1: Claude reformate en 4 variantes"""
        prompt = f"""
Tu es un expert en épistémologie. Reformat cette question en 4 variantes pour 4 perspectives différentes.

Question originale: {user_query}

Donne-moi EXACTEMENT ce JSON (pas de préambule):
{{
  "na": "Variante pour perspective américaine/tech-optimiste",
  "eu": "Variante pour perspective européenne/critique",
  "asia": "Variante pour perspective asiatique/harmonieuse",
  "diverse": "Variante pour perspective intersectionnelle/pluraliste"
}}
"""
        
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Log tokens
        self.log_tokens("sonnet", response.usage.input_tokens, response.usage.output_tokens, "reformat")
        
        # Parse
        try:
            return json.loads(response.content[0].text)
        except:
            return {
                "na": user_query,
                "eu": user_query,
                "asia": user_query,
                "diverse": user_query
            }
    
    def call_llm(self, variant_name: str, query: str) -> str:
        """Step 2: Appelle un LLM (Sonnet ou Deepseek selon variant)"""
        
        # Pour Phase 1, on alterne Sonnet et Deepseek
        # NA = Sonnet, EU = Deepseek, ASIA = Sonnet, DIVERSE = Deepseek
        use_sonnet = variant_name in ["na", "asia"]
        
        system_prompts = {
            "na": "Tu es un conseiller pragmatique américain. Emphasis: innovation, rapidité, agence individuelle.",
            "eu": "Tu es un conseiller critique européen. Emphasis: théorie, hypothèses fondamentales, limites.",
            "asia": "Tu es un conseiller asiatique. Emphasis: harmonie, pensée long-terme, bénéfice collectif.",
            "diverse": "Tu es un conseiller inclusif. Emphasis: perspectives marginalisées, pouvoir, intersectionnalité.",
        }
        
        if use_sonnet:
            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=800,
                system=system_prompts.get(variant_name, ""),
                messages=[{"role": "user", "content": query}]
            )
            self.log_tokens("sonnet", response.usage.input_tokens, response.usage.output_tokens, variant_name)
        else:
            # TODO: Deepseek API call (Phase 1.5)
            # Pour l'instant, juste repeat la question
            response_text = f"[Deepseek response pending] {query[:100]}..."
            return response_text
        
        return response.content[0].text
    
    def synthesize(self, responses: dict) -> str:
        """Step 3: Synthetise 4 réponses"""
        responses_text = "\n\n".join([
            f"### {name.upper()}\n{resp[:500]}..."
            for name, resp in responses.items()
        ])
        
        prompt = f"""
Tu as 4 perspectives sur une question. Synthetise-les:

{responses_text}

Format ta réponse:

# Synthèse

## Consensus (Ce qu'ils disent tous)
[1–2 paragraphes]

## Insights Uniques
- **NA**: [seul NA dit ça]
- **EU**: [seul EU dit ça]
- **ASIA**: [seul ASIA dit ça]
- **DIVERSE**: [seul DIVERSE dit ça]

## Aveugles Collectifs (Quoi manque)
[1–2 paragraphes]

## Hypothèses Testables
- Hypothèse 1
- Hypothèse 2
- Hypothèse 3

## Prochaines Étapes
1. [Recherche step 1]
2. [Recherche step 2]
"""
        
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )
        
        self.log_tokens("sonnet", response.usage.input_tokens, response.usage.output_tokens, "synthesize")
        
        return response.content[0].text
    
    def log_tokens(self, model: str, tokens_in: int, tokens_out: int, step: str):
        """Log token usage for budget tracking"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "model": model,
            "step": step,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "total": tokens_in + tokens_out,
        }
        self.tokens_log.append(entry)
    
    def run(self, user_query: str) -> dict:
        """Full pipeline"""
        print(f"🧠 ETAU: Reformatting query...")
        variants = self.reformat(user_query)
        
        print(f"🌍 Calling LLMs...")
        responses = {name: self.call_llm(name, query) for name, query in variants.items()}
        
        print(f"✨ Synthesizing...")
        synthesis = self.synthesize(responses)
        
        result = {
            "timestamp": datetime.now().isoformat(),
            "query": user_query,
            "variants": variants,
            "responses": responses,
            "synthesis": synthesis,
            "tokens": self.tokens_log,
            "total_tokens": sum(t["total"] for t in self.tokens_log),
        }
        
        return result

def main():
    if len(sys.argv) < 2:
        print("Usage: python src/orchestrator.py 'Votre question'")
        sys.exit(1)
    
    query = sys.argv[1]
    etau = ETAU()
    result = etau.run(query)
    
    print("\n" + "="*60)
    print(result["synthesis"])
    print("="*60)
    print(f"\n💾 Tokens utilisés: {result['total_tokens']}")
    
    # Save to JSON for kb_sync.py
    with open("output.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    main()
```

**Tu dois**:
- [ ] Créer ce fichier
- [ ] Tester: `python src/orchestrator.py "Comment les limites épistémiques affectent-elles la conception d'IA?"`
- [ ] Vérifier qu'il produit `output.json`
- [ ] Noter le token cost

### STEP 4: KB Sync (30 min)

**Fichier**: `src/kb_sync.py`

```python
#!/usr/bin/env python3
"""
Push ETAU results to ~/Knowledge/brainstorms/
"""

import json
import sys
from pathlib import Path
from datetime import datetime

KB_PATH = Path.home() / "Knowledge" / "brainstorms"

def save_to_obsidian(result: dict):
    """Save as markdown to Obsidian"""
    
    KB_PATH.mkdir(parents=True, exist_ok=True)
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    query_slug = result["query"][:40].replace(" ", "-").lower()
    filename = f"{date_str}_{query_slug}.md"
    filepath = KB_PATH / filename
    
    # Format markdown
    md = f"""# Brainstorm: {result['query']}

**Date**: {result['timestamp']}
**Tokens utilisés**: {result['total_tokens']}

## Variantes
"""
    
    for name, variant in result["variants"].items():
        md += f"\n### {name.upper()}\n{variant}\n"
    
    md += "\n## Synthèse\n" + result["synthesis"]
    
    md += "\n\n## Hypothèses Testables\n"
    # Extract hypotheses from synthesis
    for line in result["synthesis"].split("\n"):
        if line.startswith("- Hypothèse"):
            md += f"{line}\n"
    
    # Save
    filepath.write_text(md)
    print(f"✅ Sauvegardé: {filepath}")
    
    # Link in Obsidian
    return filepath

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python src/kb_sync.py path/to/output.json")
        sys.exit(1)
    
    output_file = sys.argv[1]
    with open(output_file) as f:
        result = json.load(f)
    
    save_to_obsidian(result)
```

### STEP 5: Observer (Token Tracking) (20 min)

**Fichier**: `scripts/observer.py`

Simple: lis output.json, log to CSV

```python
#!/usr/bin/env python3
import json
import csv
from pathlib import Path

LOG_FILE = Path.home() / "Projects" / "XX_ETAU" / "token_log.csv"

def log_tokens(output_json: str):
    with open(output_json) as f:
        result = json.load(f)
    
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        for token_entry in result["tokens"]:
            writer.writerow([
                token_entry["timestamp"],
                token_entry["model"],
                token_entry["step"],
                token_entry["tokens_in"],
                token_entry["tokens_out"],
                token_entry["total"],
            ])
    
    print(f"✅ Logged to {LOG_FILE}")

if __name__ == "__main__":
    log_tokens("output.json")
```

### STEP 6: Test End-to-End (20 min)

```bash
cd ~/Projects/XX_ETAU
direnv allow
nix-shell
python src/orchestrator.py "Comment les limites épistémiques affectent-elles la design d'IA?"
python src/kb_sync.py output.json
python scripts/observer.py
ls ~/Knowledge/brainstorms/  # Vérifier que c'est là
cat token_log.csv  # Vérifier costs
```

---

## Ce que Big Pickle FAIT PAS (Andrei le Fait)

- [ ] Setup Deepseek API call (Phase 1.5, après test avec Sonnet seul)
- [ ] Setup Notion → Obsidian migration (utiliser Obsidian directement)
- [ ] Setup Qwen/Mistral routing (Week 2 de Phase 2)
- [ ] Auto-cron task-observer (Andrei lance `observer.py` quand il veut)

---

## Success Criteria Phase 1 Week 1

✅ Code runs end-to-end
✅ First brainstorm result in ~/Knowledge/brainstorms/
✅ Token costs tracked in token_log.csv
✅ project.relations.yml updated with dependencies
✅ GitHub repo initialized + first commit

---

## Prochaines Étapes (Après Big Pickle)

1. **Andrei teste**: Exécute orchestrator.py 5 fois (5 questions différentes)
2. **Andrei valide KB**: Vérifie que les fichiers markdown sont bons
3. **Andrei ajuste**: Reformat prompt si les synthèses sont mauvaises
4. **Week 2**: Deepseek API integration
5. **Week 3**: Blog post + archive

---

Tu veux que je commence par STEP 1, ou tu as des questions d'abord?
