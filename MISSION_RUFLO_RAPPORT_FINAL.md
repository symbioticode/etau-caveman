# Mission Ruflo — rapport final des 4 besoins (2026-08-09)

> Portée : évaluer ce que Ruflo apporte aux besoins d'orchestration/batch de la
> session ETAU/CAVEMAN. Quatre verdicts, dont trois non-conclusions assumées.
> **Un verdict négatif documenté vaut autant qu'un livrable positif** — aucun
> besoin n'est minimisé, la règle du projet est « 1 besoin bien configuré et
> testé plutôt que 4 esquissés ».

---

## 1. Pipeline CAVEMAN — LIVRÉ, TESTÉ hors Ruflo

**Verdict corrigé : CAVEMAN exécute le pipeline; la validation épistémique
appartient à AGORA/substrat-bench et ne bloque pas son exécution.**

- `65_OMNIROUTE/scripts/recherche_hypotheses.py`
  reformule la question, appelle trois modèles configurés via Omniroute, puis
  délègue la synthèse à l'orchestrateur ETAU/CAVEMAN.
- Test réel du 2026-08-09 : Mistral a reformulé; Groq, Mistral et Cerebras ont
  tous répondu; la synthèse a réussi en 18,4 s, coût estimé $0.
- Ruflo n'est pas dans ce chemin LLM. Son transport SSE reste une limite connue
  pour ses propres workers AI, mais elle n'est ni un blocage CAVEMAN ni une
  raison de confondre pipeline et calibration.
- La mesure d'indépendance, l'isolation et la calibration des substrats restent
  du ressort d'AGORA/substrat-bench, sans Omniroute.

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

## 3. Veille promo — SYSTEMD CONSERVÉ, TESTÉ À $0

**Verdict : ne pas migrer vers Ruflo; le timer systemd-user est plus simple à
maintenir pour ce script arbitraire.**

- Le daemon Ruflo courant est propriétaire du workspace 64 et expose sept
  workers internes prédéfinis; il n'est pas un ordonnanceur générique de
  commandes Python.
- Une migration demanderait un worker Ruflo personnalisé et un second daemon ou
  un changement de portée workspace. Le timer existant exprime directement la
  cadence, `Persistent=true`, le rétablissement après reboot et le journal.
- L'interprétation ponctuelle passe par Omniroute local vers un tier gratuit;
  aucun provider payant et coût observé/estimé $0.
- Le service a été corrigé pour retourner succès après un changement traité :
  le code `1` signalait auparavant à tort un échec systemd.

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
| 1. Pipeline CAVEMAN | **LIVRÉ + TESTÉ** | hors Ruflo; 3 substrats + synthèse |
| 2. Scheduling batch/coût | **LIVRÉ + TESTÉ** | livrable fonctionnel |
| 3. Veille promo | **SYSTEMD CONSERVÉ + TESTÉ** | migration Ruflo plus complexe |
| 4. Heartbeat inter-harnais | PAS DE PONT NATIF | non-livrable, cause prouvée |

Règle appliquée : Ruflo orchestre les projets qui lui sont confiés; il ne sert
ni de couche de calibration AGORA ni de remplacement systématique à systemd.
