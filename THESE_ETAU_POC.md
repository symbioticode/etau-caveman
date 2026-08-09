# THESE ETAU/POC — point d'ancrage de la session

> **ETAU** = **E**pistemically **T**rustworthy **A**gent for **U**ncertainty

## La thèse

Une seule IA, aussi bonne soit-elle, ne peut pas produire à elle seule une
synthèse épistémiquement fiable : ses limites (biais d'entraînement, angles
morts corrélés, chambre d'écho) sont **partagées par toutes ses réponses**,
et donc invisibles depuis l'intérieur. La fiabilité ne peut émerger que de la
**confrontation de perspectives réellement indépendantes**.

## Le principe opératoire

Une question (de recherche, de stratégie) est reformulée en plusieurs
variantes, soumise **en parallèle** à plusieurs IA de **familles distinctes**,
puis synthétisée en un cadre : ce sur quoi elles s'accordent, ce qui les
oppose, et ce que le consensus laisse collectivement invisible.

La synthèse n'est **pas** une conclusion à valider telle quelle : c'est un
cadre de travail pour la décision humaine. Les désaccords et les angles morts
sont des **résultats valides**, pas des défauts à masquer.

## Les invariants qui découlent de la thèse

1. **Indépendance réelle des flux** — deux réponses venant du même modèle (ou
   de la même famille d'entraînement) ne comptent pas pour deux perspectives.
2. **Isolation par le code, pas par la promesse** — les IA ne doivent pas
   avoir accès aux réponses des autres pendant leur travail.
3. **Sortie structurée** — chaque IA produit des réponses à schéma contraint,
   pas de la prose libre : la comparaison et la synthèse exigent des unités comparables.
4. **Statut épistémique gradué, jamais absolu** — confiance graduée
   (FORT/PROBABLE/FAIBLE) et logique Belnap (T/F/B/N) ; rien n'est
   « CONFIRMÉ » sans vérification.
5. **Non-convergence = résultat valide** — si les familles divergent, la zone
   est signalée comme zone ouverte, jamais clôturée de force.
6. **Source traçable** — toute affirmation doit pouvoir être ramenée à la
   réponse d'une IA et au variant qui l'a produite.

## La trajectoire

- **CAVEMAN (ce POC)** : le produit d'appel. Prompt → plusieurs IA free via
  Omniroute → réponses structurées → synthèse. Baseline mesurable, pas chère.
- **banc-essai ETAU/SECS** : l'étape de validation expérimentale (métriques
  M01-M10, isolation, granularité de confiance).
- **AGORA** : le produit de luxe, débat contradictoire entre agents
  hétérogènes + juge, coûteux en tokens, pas encore calibré. **Hors périmètre
  aujourd'hui.**
- **ETAU version ultime** (TI-360, TOML, graphe Source→Extraction→Decision) :
  la cible lointaine. **Hors périmètre aujourd'hui.**

## Ce que je construis aujourd'hui (session 2026-08-09)

La **cuisine ETAU** du produit d'appel : le pipeline et les templates qui se
tiennent entre le prompt du client et le résultat qui lui est renvoyé —
pensés pour être réutilisés tels quels quand AGORA sera prêt.

Priorité : documenté, élaboré, **testé réellement avec Omniroute**.

---

## Goulots et pièges documentés (2026-08-09, testés en réel)

Ces découvertes sont issues de la session et doivent orienter la production.

1. **Le quota free OpenRouter est le goulot n°1 du produit d'appel.**
   `free-models-per-day` : ~36 requêtes 200/jour suffisent à l'épuiser, puis
   tout passe en 429 (« Add 10 credits to unlock 1000 free model requests per
   day »). Un run CAVEMAN à 4 familles + synthèse ≈ 5 appels × 2 runs =
   l'essentiel du quota. **Contournement retenu** : panacher plusieurs
   providers libres (Groq, Mistral, Cerebras) en plus d'OpenRouter — chaque
   provider a son propre quota. Détails : `65_OMNIROUTE/docs/omniroute-guide.md` §7.

2. **Les modèles "reasoning" (DeepSeek v3/v4) avalent tout le budget de sortie
   en `reasoning_tokens` cachés** sur les prompts complexes → `finish: length`
   et contenu visible vide. Testé sur `deepseek-v4-flash` et `-pro` avec
   `max_tokens` de 1200 à 8000 : TOUS en échec. **Correctif** : paramètre
   `reasoning_effort="low"` (validé, ~22 s, JSON correct). Détails :
   `65_OMNIROUTE/docs/omniroute-guide.md` §9.

3. **Les templates JSON avec accolades doublées `{{` cassent les modèles
   "obéissants"** (Groq Llama 3.3 70B reproduit `{{` fidèlement → JSON invalide).
   Résidu d'un ancien `.format()`, corrigé en `{` dans `src/prompts.py`.

4. **Le préfixe `<provider>/` est obligatoire** devant tout modèle Omniroute
   (ex. `groq/...`, `openrouter/...`) — sans lui : 404 silencieux
   « No active credentials ».

5. **Latence par provider (extraction, prompt complet)** — mesurée en réel :
   Groq ~4–8 s, Mistral ~7–18 s, Cerebras ~2–4 s, DeepSeek ~15 s. Total run
   4 familles + synthèse : **10–36 s** (loin sous le garde-fou de 120 s).

6. **Seuil `max_tokens` extraction = 2000** — découvert le 2026-08-09 :
   `groq/openai/gpt-oss-120b` génère parfois > 1200 tokens de sortie ; à
   `max_tokens=1200` il est tronqué en plein JSON (`finish: length`) → parse
   invalide → échec famille. Correctif : `max_tokens=2000` pour l'extraction
   Omniroute (`src/llm_clients.py`). Un JSON coupé en milieu d'objet se
   manifeste par `ValueError: sortie non-JSON (NNNN chars)` — penser d'abord
   à la troncature, pas au modèle.

## Résultats réels P2 (session 2026-08-09, sans quota OpenRouter)

> **VERROU SUBSTRATS (2026-08-09) — 3 substrats pleinement indépendants, PAS 4.**
> Santé vérifiée sur `call_logs` 24h (requête SQLite : `omniroute-guide.md` §11) :
> groq/llama-3.3-70b-versatile 22/22, mistral/mistral-small-latest 17/17,
> cerebras/gemma-4-31b 8/8. Le 4e rôle (diverse = groq/openai/gpt-oss-120b)
> partage le provider groq → ce n'est PAS une 4e famille indépendante. Une 4e
> indépendance exigerait une 4e clé (openai, anthropic, …).
>
> Exclusions explicites (verrouillées dans `src/schemas.py`) : `openrouter/*:free`
> (quota free-models-per-day épuisé, non fiable), `cerebras/zai-glm-4.7`
> (CASSÉ : 30×502 sur 32 appels).

### Health-check pré-run (ajout 2026-08-09)

Avant chaque run, l'orchestrateur ping les 3 providers retenus (PONG
`max_tokens=5`, parallèle, sans retry) : un provider down **bloque le run
proprement** au lieu d'éclater en plein. Résultat dans `metadata.health_check`.
C'est la traduction de l'invariant 1 (indépendance) en garde-fou opérationnel.

### Runs validés (0 échec d'extraction)

- **Run 1** (`results/run_20260809_154408.json`) — 10,5 s, question "limites des
  LLM pour la recherche" : 3 accords, 5 findings gradués dont **1 FORT** soutenu
  par 3 familles indépendantes.
- **Run 2** (`results/run_20260809_154455.json`) — 36 s, question "limites
  épistémiques des IA et stratégie" : 3 accords, 5 findings gradués dont
  **2 FORT** (3 familles, puis 2 familles).
- **Run 3** (`results/run_20260809_155850.json`) — 25 s, même question que le
  run 2, après verrouillage + health-check : health 3/3 OK, 5 findings gradués
  dont 2 FORT, 0 échec. Latences réelles par famille : na 7,6 s · asia 18,1 s ·
  eu 3,8 s · diverse 8,9 s · deepseek 14,6 s.

Les résultats complets (réponses brutes par famille + synthèse graduée)
sont dans `results/`. Non-convergences et zones ouvertes sont signalées en
l'état, jamais clôturées de force (invariant 5).

> **Note** : le run complet inclut DeepSeek par défaut (5e famille bonus, API
> directe hors Omniroute). Pour un run strictement sur les 3 substrats
> Omniroute : `families=["na","asia","eu","diverse"]`.
