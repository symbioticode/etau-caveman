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

1. Un LLM reformule la demande en prompt de recherche approfondie
2. Le prompt est soumis en parallèle à au moins 3 substrats configurés
3. Chaque famille appelle un modèle via **Omniroute** (localhost:20128), en
   parallèle réel, avec garde-fou wall-clock (`CALL_TIMEOUT_S = 120`)
4. Chaque réponse est **structurée en JSON** (findings gradués FORT/PROBABLE/FAIBLE
   + statut épistémique Belnap T/F/B/N) — extraction `build_extraction_prompt_short()`
   pour les modèles reasoning (DeepSeek), template JSON sans accolades doublées
5. Un **health-check** ping les providers retenus **avant** l'extraction — un
   échec bloque le run proprement au lieu d'éclater en plein (voir §Santé)
6. Un 4e appel LLM synthétise les réponses : accords, désaccords, angles morts

## Substrats — état vérifié au 2026-08-09

> **Cadrage corrigé** : CAVEMAN exige au moins 3 modèles configurés distincts
> pour exécuter son pipeline. Il ne mesure ni ne prouve leur indépendance
> épistémique. Cette calibration appartient exclusivement à
> **AGORA/substrat-bench**, sans Omniroute. Les chiffres ci-dessous décrivent la
> santé opérationnelle observée, pas une validation d'indépendance.

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

- Pas de calibration ni de preuve d'indépendance : hors scope CAVEMAN, traité
  séparément par AGORA/substrat-bench
- Pas de statut épistémique gradué sur toutes les affirmations (gradué en synthèse)
- La synthèse n'est pas contradictoire (un seul modèle juge, pas un arbitrage croisé)
- "Perspective asiatique/européenne" = persona sur un modèle donné, pas garantie
  d'une famille d'entraînement réellement distincte

## Usage

```bash
nix-shell
python scripts/model_bench.py            # bench multi-providers via Omniroute
python src/orchestrator.py "Ta question ici"
/home/andrei/Projects/64_ETAU_CAVEMAN/.venv/bin/python \
  ../65_OMNIROUTE/scripts/recherche_hypotheses_stub.py "Ta question ici"
```

> `orchestrator.py` à la racine est OBSOLÈTE (v1 OpenRouter, vidé) — le pipeline
> réel est `src/orchestrator.py` + `src/schemas.py`. Les refs restantes dans
> `brainstorming/` sont des notes historiques.

## Scheduling — daemon Ruflo (livré et testé 2026-08-09)

> Besoin 2 (batch en heures creuses / gestion coût-quota) : couvert nativement
> par le daemon Ruflo (`ruflo daemon`), configuré pour ce projet.

**Ce qui tourne** : un daemon Ruflo en arrière-plan, propriétaire de ce
workspace, qui exécute des workers à intervalles fixes. Aujourd'hui en mode
**local-only ($0, aucune clé API)** : `map` (structure du code, 15 min), `audit`
(sécurité, 10 min), `optimize` (15 min), `consolidate` (mémoire, 30 min),
`testgaps` (20 min), `backup` (24 h), `harness` (6 h). Les workers AI
(`--headless`) sont désactivés par défaut ; toute exécution AI future reste
plafonnée par le budget global (`daemon budget` : 2 lancements/heure, 12/24 h).

**Config** : `.claude-flow/config.json` (versionné) — daemon scoped au projet.

```json
{
  "daemon.maxConcurrent": 2,
  "daemon.ttlSecs": 43200,
  "daemon.idleSecs": 3600,
  "daemon.workerTimeoutMs": 120000,
  "daemon.aiWorkers.enabled": false,
  "daemon.resourceThresholds.maxCpuLoad": 80,
  "daemon.resourceThresholds.minFreeMemoryPercent": 10
}
```

**Superviseur** : unité `~/.config/systemd/user/ruflo-daemon.service` (instalée
via `ruflo daemon install-supervisor`), `WorkingDirectory` = ce projet, avec
`Restart=on-failure` + `loginctl enable-linger andrei` → le daemon **survit au
crash, au reboot et à la déconnexion**. Testé réellement : `systemctl --user
restart` → redémarrage auto (PID 137263 → 137577).

**Vérification** :
```bash
ruflo daemon status          # RUNNING, workers On/Runs/Success
ruflo daemon trigger --worker map   # exécution manuelle réelle
ruflo daemon budget          # lancements AI : 0/2 h, 0/12 j
systemctl --user status ruflo-daemon.service
```

**Limite documentée** : le daemon est cadencé par intervalles, pas par créneau
horaire (pas de fenêtre « 2 h–6 h » native). Le « batch en heures creuses » est
assuré par TTL 12 h + supervision + budget, pas par une restriction horaire
stricte — si un créneau strict devient nécessaire, ce sera un timer systemd
autour du service (non fait, non nécessaire aujourd'hui).

## Statut

POC — sert à établir une baseline comparable à une future implémentation
rigoureuse d'ETAU. Les résultats de CAVEMAN ne doivent pas être traités comme
des conclusions de recherche fiables, seulement comme des points de comparaison.

## Horizon de convergence — non construit dans cette session

Trois feedback loops restent distincts et parallèles :

1. **ETAU-CAVEMAN + Omniroute** : pipeline de recherche approfondie exécutable.
2. **AGORA/substrat-bench sans Omniroute** : calibration indépendante des
   substrats et mesure expérimentale.
3. **Ruflo** : orchestration/scheduling des projets explicitement confiés.

À moyen terme, CAVEMAN pourra intégrer les résultats calibrés d'AGORA puis
converger vers ETAU rigoureux. Cet horizon n'autorise aujourd'hui ni fusion des
projets, ni import des conclusions de substrat-bench dans CAVEMAN.
