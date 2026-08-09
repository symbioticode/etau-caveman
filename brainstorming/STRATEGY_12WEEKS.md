# 12-Week Project Sequencing Strategy

**Constraint**: Max 3 weeks per project. Mental load = alternation. Signal preservation = context fragmentation risk.

**Solution**: Serialize projects so earlier work *enables* later work. This creates psychological momentum and reduces ramp-up friction.

---

## Why This Order?

### Phase 1 (Weeks 1–3): Projet 3 — Environment & Assistant Scaffold
**Status**: FOUNDATIONAL

**Why first**: Everything downstream needs:
- A reproducible notebook structure (GitHub + Notion + nixos paths)
- A task-observer (reminds you of formats, timing, pending actions)
- A methodology anchor (brainstorm/doc/version/rigor/tokenomics/model-selection/narrative/publish — your 8 dimensions)
- An assistant interface that knows your patterns

**Output**:
- `/projects/{project-slug}/` — per-project directory structure
- Notion MCP setup with templates (TBD, brainstorm results, methodology card)
- CLI/UI scaffolding for task reminders
- A "project lifecycle" document (you copy it for each new project)

**Why it unblocks**: ETAU needs a home for its results. The assistant needs to know "it's time to publish" or "this brainstorm result needs archiving."

**Key decision**: Use Notion as the "brain" (KB + task tracking) via MCP, GitHub for code/config, nixos folders for work-in-progress isolation.

---

### Phase 2 (Weeks 4–6): Projet 1 — ETAU (Multi-LLM Brainstorming)
**Status**: PROOF OF CONCEPT

**Why second**: 
- The infrastructure is fresh and battle-tested.
- You're building confidence in multi-agent coordination (Claude + Sonnet + Asian LLM + European LLM).
- Results feed directly into your Notion KB and can be archived for Projet 2.

**Architecture**:
```
User prompt
    ↓
[Claude Sonnet 5] — Reformat prompt into 4 variants (one per LLM region/style)
    ↓
Parallel calls:
  - [Claude Sonnet 5.0] (North American)
  - [GLM-4 or Qwen] (Asian)
  - [Mistral or local EU model] (European)
    ↓
[Claude Sonnet 5.0] — Synthesize + extract novelty + identify blind spots
    ↓
Output:
  - Web UI (POST prompt → GET synthesis, live polling)
  - CLI (single command, jq-parseable JSON output)
  - Auto-save to Notion KB under `/brainstorms/{date}/`
```

**Why this matters**: 
- Reduces the search space in your epistemic landscape (TIE framework).
- Forces you to formalize what "good synthesis" means.
- The synthesizer becomes reusable for other projects.

**Key decision**: Start with Sonnet 5.0 as the orchestrator (fast, cheap). If it's too slow, add a lightweight router (regex-based) that picks which prompts need multi-LLM vs single-LLM.

**Output**:
- `/etau/` folder with:
  - `orchestrator.py` (Claude API + LLM routing)
  - `web/` (React or HTML artifact serving as UI)
  - `cli.py` (stdin → stdout, Notion push)
- Notion integration: auto-create cards under `/brainstorms/` with metadata (timestamp, topic, synthesizer version)

---

### Phase 3 (Weeks 7–9): Projet 2 — Automatic Research (Ruflo + OmniRoute)
**Status**: PRODUCTION AUTOMATION

**Why third**:
- You now have a proven multi-agent pattern (from ETAU).
- You have a KB structure (from Projet 3) where results live.
- Ruflo/OmniRoute become *hypothesis generators*, feeding into automated search.

**Architecture**:
```
ETAU Synthesis
    ↓
[Hypothesis extractor] — Parse synthesis for testable claims
    ↓
[Ruflo/OmniRoute] — Search the web for evidence/counter-evidence
    ↓
[Validator agent] — Cross-check findings, flag contradictions
    ↓
Output:
  - Research report (Notion card)
  - Evidence links + metadata
  - Updated KB with backlinks
```

**Integration point**: When ETAU produces a synthesis, a webhook or scheduled job asks "Should we auto-research this?" (based on topic/priority/token budget). If yes, Ruflo + OmniRoute spin up.

**Key decision**: Don't run Ruflo/OmniRoute on *every* ETAU output. You'll burn API credits. Instead, tag ETAU results with a `research_priority` (low/medium/high) and only trigger auto-research on medium/high.

**Output**:
- `/research-automation/` folder with:
  - `hypothesis_extractor.py` (LLM-based claim extraction)
  - `ruflo_wrapper.py` + `omniroute_wrapper.py` (API interfaces)
  - `validator.py` (fact-check pipeline)
- Notion automation: adds research cards to `/research/{date}/` with linked evidence

---

### Phase 4 (Weeks 10–12): Projets 4 & 5 — KB Feeders (Parallel)
**Status**: UTILITY / PRODUCTION

**Projet 4: Document Converters (Word ↔ MD ↔ PDF)**

**Why parallel with 5**:
- No inter-dependency.
- Both feed your KB.
- Removes friction in publishing workflow (Substack/Medium often need specific formats).

**Output**:
- CLI tool: `convert-doc [input] [--to {pdf,md,docx}]`
- Uses `python-docx`, `pypdf`, `md2pdf` libraries
- Integrates into Notion: "Export this page as PDF/Word/MD" button (MCP action)

**Projet 5: YouTube → KB Pipeline**

**Architecture**:
```
YouTube URL
    ↓
[youtube-transcript-api] — Fetch transcript
    ↓
[Concept extractor] — LLM parses transcript, extracts key ideas
    ↓
[Quote harvester] — Memorable phrases with timestamps
    ↓
Notion card:
  - Transcript (full text)
  - Concepts (structured list with backlinks)
  - Quotes (with video links @timestamp)
  - Metadata (channel, date, duration, tags)
```

**Output**:
- CLI: `extract-youtube [url]`
- Notion integration: "Save this YouTube to KB" (browser extension or direct MCP call)
- Auto-creates a YouTube KB section

---

## Getting Started: Immediate Actions (Next 2 Hours)

### Within 30 min:

1. **Freeze your directory structure** (nixos):
   ```
   ~/projects/
   ├── ratio/                    (existing repo)
   ├── .chamoise-agent/
   ├── .etau/                    (new)
   ├── .research-automation/     (new)
   └── shared/
       ├── methodology.md        (YOUR 8 DIMENSIONS)
       ├── project-template/
       └── task-observer.config
   ```

2. **Document your 8 dimensions** (in `shared/methodology.md`):
   - Brainstorm/sense-making
   - Documentation
   - Versioning
   - Methodology rigor (calibrated per project)
   - Token economy
   - Model selection
   - Narrative (pedagogical/vulgarisation)
   - Publication (Substack/Medium/GitHub)

3. **Create a Notion template** (via MCP):
   - Page: `/projects/{slug}/` with fields: status, phase, token-budget, next-review-date
   - Page: `/brainstorms/{date}/` with fields: topic, synthesizer-version, hypotheses, kb-links
   - Page: `/research/{date}/` with fields: hypothesis, evidence, confidence, sources
   - Page: `/youtube-kb/` with fields: url, transcript, concepts, quotes, tags

### Within 1 hour (Projet 3 scaffold):

4. **Wire up task-observer** (simple version for now):
   - A Notion view: "This week's actions" (filtered by due-date, status=pending)
   - A reminder script that runs daily (cron or systemd timer)
   - Outputs: "You have 3 pending docs. XYZ was last updated 10 days ago."

5. **Clone and adapt** an existing project folder structure:
   - Copy `/chamoise-agent/` as template
   - Rename to `/etau/`
   - Delete non-essential files; keep `README.md`, `config/`, `src/`, `tests/`, `.gitignore`

### Within the final hour (ETAU skeleton):

6. **Scaffold ETAU POC**:

```python
# etau/orchestrator.py (skeleton)
import os
from anthropic import Anthropic

client = Anthropic()

def reformat_prompt(user_prompt: str) -> dict:
    """Claude reformats user query into 4 LLM-specific variants."""
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        messages=[{
            "role": "user",
            "content": f"""
Reformat this query for 4 different LLMs (North American, Asian, European, and a diverse approach).
Each variant should emphasize cultural/epistemological context.

User query: {user_prompt}

Return JSON:
{{
  "na_variant": "...",
  "asia_variant": "...",
  "eu_variant": "...",
  "diverse_variant": "..."
}}
"""
        }]
    )
    import json
    return json.loads(response.content[0].text)

def synthesize_responses(responses: list[str]) -> str:
    """Claude synthesizes 4 LLM outputs into a unified framework."""
    synthesis_prompt = f"""
Synthesize these 4 perspectives into a coherent framework. 
Highlight:
1. Common ground
2. Unique insights per LLM
3. Blind spots (what all 4 missed)
4. Actionable next steps

Responses:
{chr(10).join([f"  {i+1}. {r}" for i, r in enumerate(responses)])}
"""
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        messages=[{"role": "user", "content": synthesis_prompt}]
    )
    return response.content[0].text

def run_etau(user_prompt: str):
    print(f"🧠 ETAU: Processing '{user_prompt[:50]}...'")
    
    # Step 1: Reformat
    variants = reformat_prompt(user_prompt)
    print(f"✅ Reformatted into 4 variants")
    
    # Step 2: Mock parallel calls (replace with real LLM APIs later)
    responses = [
        f"[NA response to: {variants['na_variant'][:80]}...]",
        f"[Asia response to: {variants['asia_variant'][:80]}...]",
        f"[EU response to: {variants['eu_variant'][:80]}...]",
        f"[Diverse response to: {variants['diverse_variant'][:80]}...]",
    ]
    
    # Step 3: Synthesize
    synthesis = synthesize_responses(responses)
    print(f"✅ Synthesized\n\n{synthesis}")
    
    # TODO: Save to Notion KB
    return synthesis

if __name__ == "__main__":
    result = run_etau("How do epistemic limits affect AI system design?")
```

7. **Wire the CLI**:
```bash
# etau/run.sh
#!/bin/bash
python orchestrator.py "$@"
```

---

## Synergy Map

| Project | Feeds → | Consumes ← | KB Impact |
|---------|---------|-----------|-----------|
| **3: Environment** | Everything | Nothing | Establishes KB structure |
| **1: ETAU** | 2 (hypotheses), KB | 3 (notebook) | Brainstorm results, synthesis |
| **2: Research** | KB | 3 (notebook), 1 (hypotheses) | Research findings, evidence links |
| **4: Converters** | All (format) | Any (input format) | Utility; enables publishing |
| **5: YouTube KB** | KB | 3 (notebook) | YouTube KB section, cross-ref with brainstorms |

---

## Three-Week Cycle Checklist

**Week 1**: Setup, learn the tool, create 1–2 artifacts
**Week 2**: Iterate, refine, document as you go
**Week 3**: Polish, archive to KB, hand off to next project

### End-of-Phase Deliverables:

| Phase | Deliverable | Location |
|-------|-------------|----------|
| 1 | Notion KB + CLI scaffold | `shared/`, GitHub |
| 2 | ETAU MVP + 5 brainstorms | `etau/`, KB `/brainstorms/` |
| 3 | Research automation pipeline + 10 researches | `research-automation/`, KB `/research/` |
| 4–5 | Converter CLI + YouTube extraction tool | `utils/`, GitHub |

---

## Open Questions for You

1. **LLM routing for ETAU**: Do you have access to Asian (Qwen, GLM-4) and European (Mistral, local) models, or should we default to Sonnet 5.0 × 4 with prompt variants?

2. **Notion automation**: Are you comfortable with MCP webhooks, or should task-observer be a simple CLI script that pushes updates?

3. **Token budget**: What's your monthly API spend ceiling? This affects whether auto-research runs on all ETAU results or just high-priority ones.

4. **Ruflo/OmniRoute**: Have you used these before, or is this your first time? The learning curve might push Phase 3 beyond 3 weeks — consider a "research setup" mini-phase (1 week) before full automation.

---

## Next Steps (Post-2-Hour Session)

1. **Confirm the order** — does this sequence feel right to you?
2. **Freeze Notion schema** — I can scaffold the full template
3. **Start Phase 1 setup** — I can create the project template + nixos structure
4. **Early ETAU POC** — Have a working CLI by end of week 1 (Phase 2 prep)

You've got this. 🚀
