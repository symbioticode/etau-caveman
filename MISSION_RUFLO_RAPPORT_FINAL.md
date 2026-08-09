# Mission Ruflo — rapport final des 4 besoins (2026-08-09)

> Portée : évaluer ce que Ruflo apporte aux besoins d'orchestration/batch de la
> session ETAU/CAVEMAN. Quatre verdicts, dont trois non-conclusions assumées.
> **Un verdict négatif documenté vaut autant qu'un livrable positif** — aucun
> besoin n'est minimisé, la règle du projet est « 1 besoin bien configuré et
> testé plutôt que 4 esquissés ».

---

## 1. Stub — BLOQUÉ (confirmé, aucun contournement tenté)

**Verdict : Ruflo ne débloque pas le blocage épistémique du stub.**

- Le stub (`65_OMNIROUTE/scripts/recherche_hypotheses_stub.py`) exige de prouver
  que 2-3 combos Omniroute servent des modèles **réellement indépendants**.
- Ruflo ne fournit pas cette preuve : son consensus (BFT/Raft/Gossip/CRDT) est un
  protocole de **coordination entre agents d'un swarm**, pas un croisement
  épistémique des modèles sous-jacents.
- Aucune clé API sur la machine → aucun appel multi-provider réel possible.
- **Nouveauté cette session (éclaircie)** : la voie env
  `OPENROUTER_BASE_URL`/`--endpoint` → Omniroute existe désormais côté CLI v3.34,
  mais Omniroute répond **SSE par défaut** même sans `stream:true`, et Ruflo
  n'envoie jamais `stream:false` → `res.json()` échoue. La connexion transport
  reste donc bloquée par le SSE, indépendamment de la config. **Décision :
  ne pas construire de proxy-wedge** — même réparé, il ne résout pas la question
  d'indépendance épistémique. Effort mal ciblé.
- Prochaine étape réelle (indépendante de Ruflo) : tester 2-3 combos Omniroute
  explicitement distincts et mesurer l'indépendance de leurs réponses.

## 2. Scheduling (batch heures creuses / coût-quota) — LIVRÉ, TESTÉ

**Verdict : couvert nativement par `ruflo daemon`, configuré et testé réellement
dans 64_ETAU_CAVEMAN.**

- Daemon propriétaire du workspace, workers à intervalles fixes (map 15 min,
  audit 10 min, optimize 15 min, consolidate 30 min, testgaps 20 min, backup
  24 h, harness 6 h).
- **Local-only par défaut ($0, aucune clé)** ; workers AI opt-in avec budget
  global `daemon budget` (2 lancements/h, 12/24 h) — le coût reste plafonné.
- Config versionnée : `.claude-flow/config.json` (maxConcurrent, TTL 12 h,
  idle 1 h, timeout worker, seuils CPU/mémoire).
- **Superviseur systemd-user** (`ruflo-daemon.service`, `Restart=on-failure`,
  `WorkingDirectory` = projet) + `loginctl enable-linger` → survit au crash,
  au reboot et à la déconnexion. **Testé : `systemctl --user restart` →
  redémarrage auto (PID 137263 → 137577).**
- **Test réel** : `ruflo daemon trigger --worker map` → succès 12 ms sur le
  projet ; `daemon status` → map 2/2 runs 100 % ; budget 0/2 h.
- Limite documentée : cadence par intervalles, pas de créneau horaire strict
  (pas de fenêtre « 2 h–6 h » native). Si besoin futur : timer systemd autour
  du service.

## 3. Veille (surveillance intelligente) — HORS PORTÉE, À REPRENDRE

**Verdict : bloquée par l'absence de clé LLM, pas par Ruflo.**

- Ruflo peut orchestrer de la veille (workers `map`/`audit`/`testgaps`,
  metaharness `drift-from-history`, task-observer scanner local), mais toute
  veille « intelligente » (résumé, priorisation sémantique) exige un appel LLM.
- **Aucune clé API sur la machine** → pas de test réel possible aujourd'hui.
- **Reprise documentée** : quand une clé sera disponible, la chaîne probable est
  daemon (intervalles) + workers dédiés + budget, sur le modèle du besoin 2 déjà
  livré. Les workers et le budget sont déjà en place ; il ne manque que la clé.

## 4. Heartbeat (connexions inter-harnais Claude Code ↔ Codex ↔ OpenCode) — PAS DE PONT NATIF

**Verdict : Ruflo n'offre PAS de heartbeat de connexion entre harnais CLI
(Claude Code ↔ Codex ↔ OpenCode). Ce qui existe est interne et signé.**

- Le mot « heartbeat » dans Ruflo a deux sémantiques, ni l'une ni l'autre ne
  répond à la question de connexion entre harnais :
  1. **Federation** (`@claude-flow/plugin-agent-federation`) : messages
     `heartbeat` entre **nœuds d'agents Ruflo** (signés ed25519/JCS, autorisation
     `federation:connect`, intervalle `heartbeatInterval`). C'est un protocole
     **inter-agents internes**, pas un pont vers Codex/OpenCode.
  2. **Transport WebSocket MCP** : ping-pong de santé de connexion
     (`heartbeatInterval`/`heartbeatTimeout`), purement transport.
- Pas de mécanisme de « qui est connecté » transversal aux harnais. Le seul outil
  transversal est `metaharness` (audit/score/drift d'un harness) — analytique,
  pas un heartbeat.
- **Conclusion** : pour un vrai heartbeat inter-harnais, il faudrait construire
  une couche dédiée (ex. signaux mTLS entre harnais) — hors périmètre Ruflo.

---

## Synthèse

| Besoin | Verdict | Nature |
|---|---|---|
| 1. Stub (indépendance épistémique) | BLOQUÉ | non-livrable, cause prouvée |
| 2. Scheduling batch/coût | **LIVRÉ + TESTÉ** | livrable fonctionnel |
| 3. Veille | HORS PORTÉE | dépend d'une clé LLM |
| 4. Heartbeat inter-harnais | PAS DE PONT NATIF | non-livrable, cause prouvée |

Règle appliquée : 1 besoin réellement livré et testé (scheduling), 3 verdicts
négatifs documentés avec leur cause — **le négatif documenté vaut le positif**.
