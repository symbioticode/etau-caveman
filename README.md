# ETAU — POC CAVEMAN

> **Note de collision de nom** : Omniroute possède aussi un moteur appelé
> « Caveman » (compression de messages) — sans rapport avec ce projet.
> Ne pas confondre dans les logs/KBM.

**ETAU** (Epistemically Trustworthy Agent for Uncertainty) est une méthode de
brainstorming : une question est soumise en parallèle à plusieurs IA de familles
distinctes, puis synthétisée avec un statut épistémique gradué.

**CAVEMAN** est le nom de code de ce POC : une implémentation volontairement
minimale d'ETAU, pour établir une baseline mesurable avant toute version rigoureuse.

## Ce que CAVEMAN fait

1. Une question est soumise en parallèle aux familles NA / Asie / Europe / diverse
2. Chaque famille appelle un modèle via **Omniroute** (localhost:20128), en
   parallèle réel, avec garde-fou wall-clock (`CALL_TIMEOUT_S = 120`)
3. Chaque réponse est **structurée en JSON** (findings gradués FORT/PROBABLE/FAIBLE
   + statut épistémique Belnap T/F/B/N) — extraction `build_extraction_prompt_short()`
   pour les modèles reasoning (DeepSeek), template JSON sans accolades doublées
4. Un **health-check** ping les providers retenus **avant** l'extraction — un
   échec bloque le run proprement au lieu d'éclater en plein (voir §Santé)
5. Un seul modèle synthétise les réponses : accords, désaccords, angles morts

## Substrats — état vérifié au 2026-08-09

> **3 substrats pleinement indépendants, PAS 4.** Le 4e rôle (diverse) partage
> le provider groq (openai/gpt-oss-120b est un substrat de fondation OpenAI,
> mais il route par la même connexion groq). Ne pas présenter CAVEMAN comme
> « 4 familles indépendantes » : ce serait faux. Une 4e indépendance exigerait
> une 4e clé (openai, anthropic, …).

| Rôle | Modèle | Santé vérifiée (call_logs 24h) |
|---|---|---|
| na | `groq/llama-3.3-70b-versatile` | 22/22 OK — sain |
| asia | `mistral/mistral-small-latest` | 17/17 OK — sain |
| eu | `cerebras/gemma-4-31b` | 8/8 OK — sain |
| diverse | `groq/openai/gpt-oss-120b` | 10/12 OK (partage groq) |

**Exclusions explicites** (verrouillées dans `src/schemas.py` et
`src/orchestrator.py`) :
- `openrouter/*:free` — non fiable : quota `free-models-per-day` épuisé
  (gemma-4-26b 7/143, nemotron 7/38). Réintroduire UNIQUEMENT après reset
  confirmé (`omniroute usage quota`) + bench vert.
- `cerebras/zai-glm-4.7` — CASSÉ (30 × 502 sur 32 appels). Ne jamais réutiliser.
- `deepseek-v4-flash/-pro` en extraction longue — piège reasoning : consomme tout
  le budget en tokens de raisonnement (finish:length, sortie vide). Correctif :
  `reasoning_effort="low"` (JSON valide ~22s).

## Ce que CAVEMAN ne fait PAS (limites assumées)

- Pas de vérification d'indépendance réelle entre les flux — et aujourd'hui on a
  **3 substrats indépendants, pas 4** (limite assumée, documentée, non maquillée)
- Pas de statut épistémique gradué sur toutes les affirmations (gradué en synthèse)
- La synthèse n'est pas contradictoire (un seul modèle juge, pas un arbitrage croisé)
- "Perspective asiatique/européenne" = persona sur un modèle donné, pas garantie
  d'une famille d'entraînement réellement distincte

## Usage

```bash
nix-shell
python scripts/model_bench.py            # bench multi-providers via Omniroute
python src/orchestrator.py "Ta question ici"
```

> `orchestrator.py` à la racine est OBSOLÈTE (v1 OpenRouter, vidé) — le pipeline
> réel est `src/orchestrator.py` + `src/schemas.py`. Les refs restantes dans
> `brainstorming/` sont des notes historiques.

## Statut

POC — sert à établir une baseline comparable à une future implémentation
rigoureuse d'ETAU. Les résultats de CAVEMAN ne doivent pas être traités comme
des conclusions de recherche fiables, seulement comme des points de comparaison.
