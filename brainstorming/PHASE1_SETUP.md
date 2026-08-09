# Phase 1 Setup: Environment & Assistant Scaffold (Weeks 1–3)

## Your 8 Dimensions — Fill This First

This is your project methodology anchor. **Copy this into `shared/methodology.md`** and customize.

```markdown
# Andrei's Project Methodology

## 8 Dimensions (Every Project)

### 1. Brainstorm/Sense-Making
- **Tool**: ETAU (starting Week 4) or manual multi-LLM approach
- **Format**: Question → 4 perspectives → synthesis
- **Output**: Notion card under `/brainstorms/{date}/`
- **Token budget**: ~5K per brainstorm (unless high-complexity)

### 2. Documentation
- **Format**: Markdown in GitHub (preferred) + Notion (for visibility)
- **Style**: Code comments for technical; prose for strategic
- **Target**: "Someone (or future-you) can pick this up in 30 min"
- **Publishing cadence**: At end of Week 2 or 3 (blog post? GitHub wiki?)

### 3. Versioning
- **Git workflow**: main + feature branches, semantic versioning (v0.1, v1.0)
- **Commits**: Atomic, descriptive ("Add ETAU prompt reformatter" not "wip")
- **Releases**: One per phase (end of Week 3)
- **Archiving**: Move completed phases to `/archive/` in GitHub

### 4. Methodology & Rigor (Calibrated per Project)
- **Level 1** (Exploration): POC, fast iteration, minimal tests, 40% token efficiency acceptable
- **Level 2** (Production-Ready): Full test suite, documentation, 80% token efficiency target
- **Level 3** (Shipping): Peer review, benchmarks, <70% token waste, full CI/CD
- **Decision**: At Phase 1 end, classify each project (1/2/3) for next cycle

### 5. Token Economy
- **Tracking**: Log API calls (model, tokens in/out, cost) in a Notion table
- **Budget**: [You decide: $50/mo? $200/mo?] per project
- **Optimization**: Use cheaper models for batch work, Sonnet for reasoning
- **Review**: Weekly check-in, flag overages

### 6. Model Selection
- **Rule of thumb**:
  - Claude Sonnet 5.0 → reasoning, synthesis, code review
  - Claude Haiku 4.5 → extraction, classification, cheap parallelism
  - Qwen/GLM-4 → Asia-specific perspectives (ETAU)
  - Mistral → EU-specific perspectives (ETAU)
  - Local/open models → high-volume, low-cost work (fallback)

### 7. Narrative & Pedagogical Generation
- **Goal**: Every project produces at least one "teachable" output
- **Format**: Blog post, thread, or tutorial explaining what you learned
- **Audience**: Someone 3 steps behind you on this topic
- **Tone**: Conversational, show the mistakes, explain the why
- **Output location**: Draft in Notion, polish, then publish to Substack/Medium/GitHub

### 8. Publication
- **Cadence**: One piece per phase (or per project if overlapping phases)
- **Platforms**:
  - **Substack**: Deep dives, strategic thinking (TIE framework updates)
  - **Medium**: Technical tutorials (ETAU usage, research setup)
  - **GitHub**: Code + wikis (methodology docs, tool READMEs)
  - **Blog** (future): Personal domain, aggregated thoughts
- **Cross-linking**: Every published piece links to related KB entries and past posts

---

## Notion Schema (MCP Integration)

Create these pages under your root KB:

### `/projects/`
**Purpose**: Master view of all active/archived projects

**Template Page**: `/projects/{slug}/`
- **Fields**:
  - `project-name` (text)
  - `phase` (select: 1/2/3/4)
  - `status` (select: planning/active/on-hold/completed)
  - `start-date` (date)
  - `end-date` (date, auto-calculated as start + 3 weeks)
  - `token-budget` (number, monthly)
  - `token-spent` (number, auto-summed from API logs)
  - `dimension-focus` (multi-select: sense/doc/version/rigor/tokens/models/narrative/publish)
  - `github-repo` (URL)
  - `next-review-date` (date, defaults to end-of-week)
  - `notes` (text)
  - **Linked databases**:
    - Brainstorms (linked to `/brainstorms/`)
    - Research (linked to `/research/`)
    - Deliverables (linked to `/deliverables/`)

### `/brainstorms/`
**Purpose**: All multi-LLM brainstorming results

**Template Page**: `/brainstorms/{YYYY-MM-DD}-{topic-slug}/`
- **Fields**:
  - `date` (date, auto-fill)
  - `topic` (text)
  - `original-question` (long text)
  - `variants-used` (multi-select: NA/Asia/EU/diverse)
  - `synthesizer-version` (text: "ETAU-v0.1" or "manual")
  - `synthesis` (long text, full markdown)
  - `hypotheses-extracted` (array of strings)
  - `blind-spots` (text)
  - `linked-research` (linked to `/research/`)
  - `linked-project` (linked to `/projects/`)
  - `status` (select: draft/synthesis-complete/research-queued/archived)
  - `token-cost` (number)

### `/research/`
**Purpose**: All research findings and hypothesis validation

**Template Page**: `/research/{YYYY-MM-DD}-{hypothesis-slug}/`
- **Fields**:
  - `date` (date)
  - `hypothesis` (long text)
  - `sources` (linked to `/sources/`)
  - `evidence-for` (long text)
  - `evidence-against` (long text)
  - `confidence` (select: high/medium/low)
  - `runner` (select: manual/ruflo/omniroute/hybrid)
  - `linked-brainstorm` (linked to `/brainstorms/`)
  - `linked-project` (linked to `/projects/`)
  - `status` (select: in-progress/finding-sources/validating/complete/archived)

### `/youtube-kb/`
**Purpose**: All saved YouTube videos + extracted concepts

**Template Page**: `/youtube-kb/{YYYY-MM-DD}-{channel}-{title-slug}/`
- **Fields**:
  - `url` (URL)
  - `channel` (text)
  - `title` (text)
  - `date-published` (date)
  - `duration` (number, minutes)
  - `transcript` (long text, full)
  - `concepts` (array: [{name, definition, timestamp}])
  - `quotes` (array: [{text, timestamp, context}])
  - `tags` (multi-select)
  - `linked-brainstorms` (linked to `/brainstorms/` for cross-ref)
  - `linked-research` (linked to `/research/`)
  - `status` (select: queued/extracted/indexed/archived)

### `/sources/`
**Purpose**: Reference library for research validation

**Template Page**: `/sources/{YYYY-MM-DD}-{domain}-{title-slug}/`
- **Fields**:
  - `url` (URL)
  - `domain` (text)
  - `title` (text)
  - `type` (select: academic/blog/news/video/tool-docs/other)
  - `snippet` (long text, key quote)
  - `date-accessed` (date)
  - `credibility-score` (select: high/medium/low)
  - `linked-research` (linked to `/research/`)

### `/deliverables/`
**Purpose**: All published outputs (blog posts, tools, docs)

**Template Page**: `/deliverables/{YYYY-MM-DD}-{title-slug}/`
- **Fields**:
  - `title` (text)
  - `type` (select: blog-post/tutorial/tool/research-report/framework-update)
  - `platform` (select: substack/medium/github/personal-blog)
  - `url` (URL)
  - `date-published` (date)
  - `linked-project` (linked to `/projects/`)
  - `linked-brainstorms` (linked to `/brainstorms/`)
  - `linked-research` (linked to `/research/`)
  - `status` (select: draft/published/archived)

---

## Directory Structure (nixos)

Create this skeleton in `~/projects/`:

```
~/projects/
├── ratio/                           # Existing repo
├── .etau/                           # Week 4 project
├── .research-automation/            # Week 7 project
├── shared/
│   ├── methodology.md               # (YOU FILL THIS: 8 dimensions)
│   ├── project-template/            # Copy for each new project
│   │   ├── README.md
│   │   ├── config/
│   │   │   └── settings.yaml
│   │   ├── src/
│   │   │   └── main.py
│   │   ├── tests/
│   │   │   └── test_main.py
│   │   ├── docs/
│   │   │   └── ARCHITECTURE.md
│   │   └── .gitignore
│   ├── task-observer/
│   │   ├── observer.py              # Runs daily, pushes to Notion
│   │   ├── observer.config.yaml     # Configure reminders
│   │   └── cron-setup.sh            # Install as cron job
│   └── token-tracker/
│       ├── tracker.py               # Logs API calls
│       └── export-to-notion.py      # Weekly sync to Notion
├── archive/                         # Completed phases
│   └── phase1-environment-2026-01/
└── README.md                        # Master index
```

---

## Task-Observer Setup (Week 1)

**Goal**: A daily reminder that tells you:
- What's due this week?
- What went un-updated 10+ days?
- What's blocking you?

**Implementation** (simple version for now):

```python
# shared/task-observer/observer.py
#!/usr/bin/env python3
import os
from datetime import datetime, timedelta
from notion_client import Client

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
client = Client(auth=NOTION_TOKEN)

def check_projects():
    """Query Notion /projects/ database for this week's reviews."""
    db_id = os.getenv("NOTION_PROJECTS_DB_ID")
    
    today = datetime.now().date()
    week_end = today + timedelta(days=7)
    
    response = client.databases.query(
        database_id=db_id,
        filter={
            "and": [
                {"property": "status", "select": {"equals": "active"}},
                {"property": "next-review-date", "date": {
                    "on_or_before": week_end.isoformat()
                }}
            ]
        }
    )
    
    print(f"\n📋 Task Observer Report — {today.strftime('%a %b %d')}")
    print(f"{'='*60}")
    
    if not response["results"]:
        print("✅ All clear. No reviews due this week.")
        return
    
    for item in response["results"]:
        name = item["properties"]["project-name"]["title"][0]["text"]["content"]
        phase = item["properties"]["phase"]["select"]["name"]
        review_date = item["properties"]["next-review-date"]["date"]["start"]
        
        days_until = (datetime.fromisoformat(review_date).date() - today).days
        
        status_emoji = "🔴" if days_until <= 0 else "🟡" if days_until <= 3 else "🟢"
        print(f"{status_emoji} {name} (Phase {phase}) — due {review_date} ({days_until}d)")
    
    print(f"{'='*60}\n")

if __name__ == "__main__":
    check_projects()
```

**Install as cron job**:
```bash
# shared/task-observer/cron-setup.sh
#!/bin/bash
# Run daily at 9 AM
(crontab -l 2>/dev/null; echo "0 9 * * * /home/andrei/projects/shared/task-observer/observer.py") | crontab -
```

---

## Token Tracker Setup (Week 1)

**Goal**: Know how much you're spending per project per week.

```python
# shared/token-tracker/tracker.py
import json
import os
from datetime import datetime

LOG_FILE = os.path.expanduser("~/.anthropic-api-log.jsonl")

def log_call(model: str, tokens_in: int, tokens_out: int, cost: float, project: str):
    """Append API call to log."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "model": model,
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
        "tokens_total": tokens_in + tokens_out,
        "cost": cost,
        "project": project,
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

def summarize_week(project: str = None):
    """Summarize costs for this week."""
    this_week = []
    with open(LOG_FILE, "r") as f:
        for line in f:
            entry = json.loads(line)
            if (datetime.fromisoformat(entry["timestamp"]).date() >= 
                (datetime.now().date() - timedelta(days=7))):
                if project is None or entry["project"] == project:
                    this_week.append(entry)
    
    total_tokens = sum(e["tokens_total"] for e in this_week)
    total_cost = sum(e["cost"] for e in this_week)
    
    print(f"This week: {total_tokens:,} tokens, ${total_cost:.2f}")
    
    # Group by project
    by_project = {}
    for e in this_week:
        if e["project"] not in by_project:
            by_project[e["project"]] = {"tokens": 0, "cost": 0}
        by_project[e["project"]]["tokens"] += e["tokens_total"]
        by_project[e["project"]]["cost"] += e["cost"]
    
    for proj, data in sorted(by_project.items(), key=lambda x: -x[1]["cost"]):
        print(f"  {proj}: {data['tokens']:,} tokens, ${data['cost']:.2f}")
```

**Integrate into Anthropic calls**:
```python
from anthropic import Anthropic
from tracker import log_call

client = Anthropic()

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1000,
    messages=[...]
)

# After response
log_call(
    model="claude-sonnet-4-6",
    tokens_in=response.usage.input_tokens,
    tokens_out=response.usage.output_tokens,
    cost=response.usage.input_tokens * 0.003 + response.usage.output_tokens * 0.015,  # Adjust rates
    project="etau"
)
```

---

## Week-by-Week Checklist

### Week 1: Setup
- [ ] Create Notion schema (copy templates above)
- [ ] Freeze directory structure in nixos
- [ ] Document your 8 dimensions in `shared/methodology.md`
- [ ] Install task-observer as cron job
- [ ] Install token tracker
- [ ] Create GitHub repos for `etau/`, `research-automation/`, `utils/`
- [ ] First brainstorm session (test ETAU with a hard question)

**Deliverable**: Notion KB live, directories ready, 1 brainstorm result

### Week 2: Operationalize
- [ ] Create 5 more brainstorms (testing prompt variants)
- [ ] Refine Notion workflows (adjust templates based on use)
- [ ] Document lessons learned in GitHub wiki
- [ ] Draft blog post: "Why I'm Automating My Research" (for Week 3 publish)
- [ ] Set up token budget tracking (log all calls)

**Deliverable**: 6 brainstorms in KB, 1 draft blog post, token tracking baseline

### Week 3: Polish & Handoff
- [ ] Archive Week 1–2 work to `/archive/phase1-environment/`
- [ ] Create ETAU quick-start guide (for Week 4 team)
- [ ] Publish blog post
- [ ] Final task-observer check (everything due in next 2 weeks is logged)
- [ ] Review token spend vs budget; adjust for Phases 2–4
- [ ] Write Phase 2 kickoff document (ETAU deep-dive)

**Deliverable**: Blog post published, ETAU repo ready for Week 4, methodology locked in

---

## Open Decisions (Finalize Before Starting)

1. **Notion or alternative?** (Obsidian, LogSeq, Roam?) You said Notion MCP works — sticking with it?

2. **GitHub visibility**: Are projects public or private? Affects publishing strategy.

3. **Token budget cap**: Per-project limit? Monthly total? Affects model choices in later phases.

4. **Publish cadence**: One blog post per phase (4 total)? Or more frequent (weekly)?

5. **LLM for ETAU reformatting**: Sonnet 5.0 or Haiku (cheaper)? If fast, Haiku saves tokens.

---

## Files to Create Now (If You Want to Jump In Immediately)

```bash
# In ~/projects/shared/
touch methodology.md
touch task-observer/observer.py
touch task-observer/cron-setup.sh
touch token-tracker/tracker.py

# In ~/projects/
mkdir -p .etau .research-automation archive
cp -r project-template .etau/
cp -r project-template .research-automation/
```

Ready to rock? 🚀
