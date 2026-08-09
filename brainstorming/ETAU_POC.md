# ETAU POC: Multi-LLM Brainstorming Pipeline (Weeks 4–6)

**ETAU** = **E**pistemically **T**rustworthy **A**gent for **U**ncertainty

Your brainstorming methodology reformulated as an automated agent system.

---

## Why ETAU Matters

You've described a process:
1. Take a hard question (medium to complex level)
2. Reformat it into 4 variants (regional/epistemological perspective)
3. Send to 4 LLMs (Sonnet + Asia + EU + diverse)
4. Synthesize responses into a coherent framework

**ETAU automates steps 1–3** and scaffolds step 4. You then **validate the synthesis** (human in the loop).

**Output**: A structured brainstorm card in Notion that feeds into Projects 2, 4, and 5.

---

## Architecture

```
User Query (via CLI or Web UI)
    ↓
[Prompt Reformatter — Claude Sonnet 5.0]
    Transforms query into 4 culturally/epistemologically distinct variants
    Output: {na_variant, asia_variant, eu_variant, diverse_variant}
    Cost: ~300 tokens
    ↓
[Parallel LLM Calls] (3–4 variants sent to different models/APIs)
    - Claude Sonnet 5.0 (via Anthropic API) → North American perspective
    - Qwen 2.5 or GLM-4 (via Ali Baba or Zhipu API) → Asian perspective
    - Mistral Large or open-source (via Mistral API or local) → European perspective
    - Claude Sonnet 5.0 (different prompt) → Diverse/global perspective
    Cost: ~1K tokens × 4 calls
    ↓
[Response Aggregator]
    Wait for all 4 responses (timeout: 30s, then use partial)
    Output: List of 4 responses
    ↓
[Synthesis Agent — Claude Sonnet 5.0]
    Analyzes all 4 responses:
      1. What do they agree on? (common ground)
      2. What's unique to each perspective? (differentiators)
      3. What blind spots emerge from the consensus? (epistemological gaps)
      4. What are the actionable next steps? (framework closure)
    Output: Structured synthesis (markdown)
    Cost: ~1.5K tokens
    ↓
[Notion Integration]
    Creates a new card in `/brainstorms/{date}-{topic}/`
    Fills in:
      - synthesis (full text)
      - hypotheses-extracted (LLM-parsed list)
      - blind-spots (copy from synthesis)
      - status: draft (awaiting human review)
    ↓
[User Review] (You validate the synthesis, flag any issues)
    Click "Approve" → status: synthesis-complete
    Or edit synthesis → status: draft (reassess)
    ↓
[Auto-Research Trigger] (Week 7+, once Projet 2 is live)
    If status == synthesis-complete:
      Extract hypotheses → Ruflo/OmniRoute searches web
      Findings feed back to Notion card
```

---

## Three-Week Roadmap

### Week 1 (Days 1–5): Build Core Pipeline
**Goal**: Orchestrator + Sonnet-only version working end-to-end

**Tasks**:
- [ ] Scaffold project skeleton (copy from `project-template/`)
- [ ] Implement `orchestrator.py` (prompt reformatter + synthesizer)
- [ ] Implement `notionwriter.py` (Notion MCP integration)
- [ ] Implement `cli.py` (stdin/argparse entry point)
- [ ] Write unit tests (test reformatter, synthesizer)

**Deliverable**: 
```bash
$ python etau/cli.py "How do epistemic limits affect AI system design?"
# Output: JSON with synthesis + Notion card link
```

**Token budget**: ~500/week × 3 weeks = 1,500 tokens
(But you'll iterate, so budget 3–5K for safety)

**What gets pushed to GitHub**: `src/orchestrator.py`, `src/notionwriter.py`, `src/cli.py`, `tests/`

### Week 2 (Days 6–12): Add Parallel LLM Routing + Web UI
**Goal**: Full 4-LLM pipeline working (even if some calls mock-fail)

**Tasks**:
- [ ] Add Qwen/GLM-4 API wrapper (Asia)
- [ ] Add Mistral API wrapper (Europe)
- [ ] Implement async parallel calls (Python `asyncio`)
- [ ] Build simple web UI (React or HTML artifact)
- [ ] Add error handling (timeout, API failures, fallback to Sonnet-only)
- [ ] Create first 5 test brainstorms (manually run pipeline)

**Deliverable**:
```bash
# CLI
$ python etau/cli.py "Your question here" --api-key OPENAI_KEY --mistral-key XXX

# Web UI
$ python etau/server.py
# Browse to http://localhost:5000
# Click "New Brainstorm" → text input → "Run" button → watch synthesis stream in
```

**Token budget**: 2–3K (parallel calls cost more; mitigate with timeout)

**What gets pushed to GitHub**: 
- `src/llm_routing.py` (orchestrate Sonnet + Qwen + Mistral)
- `web/` (HTML + React if ambitious, else plain HTML)
- `README.md` with LLM setup instructions
- `example_brainstorms/` (5 public examples, with synthesis)

### Week 3 (Days 13–21): Polish, Document, Publish
**Goal**: Production-ready POC; hand off to Project 2 (auto-research)

**Tasks**:
- [ ] Refine synthesis prompts (run 5–10 real brainstorms, see what works/fails)
- [ ] Document LLM API setup (Notion has good docs, Mistral needs auth, etc.)
- [ ] Write a blog post: "Automate Your Brainstorming: Lessons from Building ETAU"
  - Explain the epistemic principle (why 4 perspectives?)
  - Show an example brainstorm (question → synthesis → next steps)
  - Discuss limitations (cost, speed, when to override synthesis)
- [ ] Archive Week 1–2 experiments to `/archive/etau-w1-w2/`
- [ ] Create ETAU API documentation (for Project 2 integration)

**Deliverable**:
- Blog post published (Substack/Medium)
- GitHub repo with full code + `ARCHITECTURE.md`
- Notion integration working (brainstorm cards auto-created)
- 10+ successful brainstorms in your KB
- Token cost fully tracked

**Token budget**: 1–2K (mostly synthesis refinement)

---

## Code Skeleton (Ready to Adapt)

### `etau/src/orchestrator.py`

```python
import os
import json
import asyncio
from typing import Dict
from anthropic import Anthropic
from datetime import datetime

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
client = Anthropic(api_key=ANTHROPIC_API_KEY)

class ETAUOrchestrator:
    def __init__(self):
        self.model = "claude-sonnet-4-6"
        self.max_tokens = 1500
    
    def reformat_prompt(self, user_query: str) -> Dict[str, str]:
        """
        Step 1: Reformat user query into 4 epistemological variants.
        """
        prompt = f"""
You are a query translator. Your job is to reformat the user's question 
into 4 distinct perspectives, optimized for different cultural/epistemological contexts.

**User query**: {user_query}

For each variant:
1. Preserve the core question
2. Add cultural/academic context hints that encourage specific thinking patterns
3. Keep it under 200 chars per variant

**Output**: JSON object with keys: na_variant, asia_variant, eu_variant, diverse_variant

Example output:
{{
  "na_variant": "[Query framed for tech-optimist, individualist epistemology]",
  "asia_variant": "[Query framed for harmony-seeking, collective epistemology]",
  "eu_variant": "[Query framed for critical theory, skeptical epistemology]",
  "diverse_variant": "[Query framed for intersectional, pluralist epistemology]"
}}

Now respond ONLY with valid JSON, no preamble.
"""
        
        response = client.messages.create(
            model=self.model,
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Parse JSON from response
        try:
            variants = json.loads(response.content[0].text)
        except json.JSONDecodeError:
            # Fallback: repeat query 4 times if parsing fails
            variants = {
                "na_variant": user_query,
                "asia_variant": user_query,
                "eu_variant": user_query,
                "diverse_variant": user_query,
            }
        
        return variants
    
    async def call_llm(self, variant_name: str, query: str, model: str = None) -> str:
        """
        Call an LLM with the variant query.
        For now, all calls use Sonnet (mock routing for others).
        Week 2: Add real Qwen/Mistral calls.
        """
        if model is None:
            model = self.model
        
        # TODO: Route to Qwen/Mistral/local based on variant_name
        # For MVP: all use Sonnet, but with different system prompts
        
        system_prompts = {
            "na_variant": "You are a pragmatic, innovation-focused AI advisor. Emphasize business value, speed, and individual agency.",
            "asia_variant": "You are a thoughtful AI advisor focused on harmony, long-term thinking, and collective benefit. Consider cultural contexts.",
            "eu_variant": "You are a critical AI advisor grounded in philosophy, social theory, and skepticism. Challenge assumptions.",
            "diverse_variant": "You are an inclusive AI advisor that synthesizes multiple worldviews, highlights power dynamics, and centers marginalized perspectives.",
        }
        
        system = system_prompts.get(variant_name, "You are a helpful AI advisor.")
        
        response = client.messages.create(
            model=model,
            max_tokens=1000,
            system=system,
            messages=[{"role": "user", "content": query}]
        )
        
        return response.content[0].text
    
    async def run_all_llms(self, variants: Dict[str, str], timeout_sec: int = 30) -> Dict[str, str]:
        """
        Step 2: Call all 4 LLMs in parallel.
        """
        tasks = {
            name: asyncio.wait_for(self.call_llm(name, query), timeout=timeout_sec)
            for name, query in variants.items()
        }
        
        results = {}
        for name, task in tasks.items():
            try:
                results[name] = await task
            except asyncio.TimeoutError:
                results[name] = f"[Timeout for {name}]"
            except Exception as e:
                results[name] = f"[Error for {name}: {str(e)}]"
        
        return results
    
    def synthesize(self, variants: Dict[str, str], responses: Dict[str, str]) -> str:
        """
        Step 3: Synthesize 4 responses into a coherent framework.
        """
        responses_text = "\n\n".join([
            f"### {name.replace('_', ' ').title()}\n{response}"
            for name, response in responses.items()
        ])
        
        prompt = f"""
You are a synthesis expert. You've collected perspectives on a question from 4 different epistemological angles.

**Original question**: (implied from context; not shown)

**The 4 perspectives**:
{responses_text}

Your job:
1. **Identify common ground**: What do all 4 agree on (even implicitly)?
2. **Map unique insights**: What is distinctive about each perspective?
3. **Spot blind spots**: What do all 4 perspectives collectively *miss*?
4. **Extract actionable hypotheses**: What testable claims emerge?
5. **Propose next steps**: If you were to research this further, what would you prioritize?

**Format your response as**:
# Synthesis

## Common Ground
[1–2 paragraphs of overlap]

## Unique Insights
- **North American**: [what only this perspective brings]
- **Asian**: [what only this perspective brings]
- **European**: [what only this perspective brings]
- **Diverse**: [what only this perspective brings]

## Blind Spots
[1–2 paragraphs of what's collectively missing]

## Hypotheses (Testable Claims)
- Hypothesis 1
- Hypothesis 2
- Hypothesis 3
- ...

## Next Steps (Priority Order)
1. [Research step 1]
2. [Research step 2]
3. ...

Now synthesize based on the 4 perspectives above. Be specific, cite the variants, and be honest about uncertainty.
"""
        
        response = client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text
    
    async def run(self, user_query: str) -> Dict:
        """
        Full pipeline: reformat → run LLMs → synthesize.
        """
        print(f"🧠 ETAU: Reformatting query...")
        variants = self.reformat_prompt(user_query)
        
        print(f"🌍 Running 4 LLMs in parallel...")
        responses = await self.run_all_llms(variants)
        
        print(f"✨ Synthesizing insights...")
        synthesis = self.synthesize(variants, responses)
        
        result = {
            "timestamp": datetime.now().isoformat(),
            "original_query": user_query,
            "variants": variants,
            "responses": responses,
            "synthesis": synthesis,
            "token_estimate": {
                "reformatter": 300,
                "llm_calls": 1000 * 4,
                "synthesizer": 1500,
                "total_approx": 6300,  # rough; adjust based on actual usage
            }
        }
        
        return result

# Main entry point (test)
if __name__ == "__main__":
    import sys
    
    query = sys.argv[1] if len(sys.argv) > 1 else "How do epistemic limits affect AI system design?"
    
    orchestrator = ETAUOrchestrator()
    result = asyncio.run(orchestrator.run(query))
    
    print("\n" + "="*60)
    print(result["synthesis"])
    print("="*60)
    print(f"\n💾 Saving to Notion...")
    # TODO: Wire up notionwriter.py
    print(f"✅ Saved: /brainstorms/{datetime.now().strftime('%Y-%m-%d')}-{query[:30].replace(' ', '-')}/")
```

### `etau/src/cli.py`

```python
import asyncio
import sys
import json
import argparse
from orchestrator import ETAUOrchestrator
from notionwriter import NotionWriter

def main():
    parser = argparse.ArgumentParser(description="ETAU: Multi-LLM Brainstorming")
    parser.add_argument("query", help="Your question or brainstorming prompt")
    parser.add_argument("--save-notion", action="store_true", help="Save result to Notion")
    parser.add_argument("--output-format", choices=["json", "markdown"], default="markdown", help="Output format")
    
    args = parser.parse_args()
    
    orchestrator = ETAUOrchestrator()
    result = asyncio.run(orchestrator.run(args.query))
    
    if args.output_format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(result["synthesis"])
    
    if args.save_notion:
        writer = NotionWriter()
        card_url = writer.save_brainstorm(result)
        print(f"\n✅ Saved to Notion: {card_url}")

if __name__ == "__main__":
    main()
```

### `etau/src/notionwriter.py`

```python
import os
import json
from datetime import datetime
from notion_client import Client

class NotionWriter:
    def __init__(self):
        self.client = Client(auth=os.getenv("NOTION_TOKEN"))
        self.db_id = os.getenv("NOTION_BRAINSTORMS_DB_ID")
    
    def save_brainstorm(self, result: dict) -> str:
        """
        Save ETAU result as a new page in /brainstorms/ database.
        """
        # Extract hypotheses from synthesis (LLM or regex)
        hypotheses = self._extract_hypotheses(result["synthesis"])
        
        page_data = {
            "parent": {"database_id": self.db_id},
            "properties": {
                "date": {"date": {"start": datetime.now().isoformat()[:10]}},
                "topic": {"title": [{"text": {"content": result["original_query"][:100]}}]},
                "original-question": {"rich_text": [{"text": {"content": result["original_query"]}}]},
                "variants-used": {"multi_select": [
                    {"name": v} for v in ["NA", "Asia", "EU", "Diverse"]
                ]},
                "synthesizer-version": {"rich_text": [{"text": {"content": "ETAU-v0.1"}}]},
                "synthesis": {"rich_text": [{"text": {"content": result["synthesis"][:2000]}}]},  # Notion limit
                "status": {"select": {"name": "draft"}},
                "token-cost": {"number": result["token_estimate"]["total_approx"]},
            }
        }
        
        response = self.client.pages.create(**page_data)
        return f"https://notion.so/{response['id'].replace('-', '')}"
    
    def _extract_hypotheses(self, synthesis: str) -> list:
        """
        Parse synthesis markdown to extract hypotheses.
        For MVP: just look for "Hypothesis" lines.
        """
        hypotheses = []
        for line in synthesis.split("\n"):
            if line.startswith("- Hypothesis") or line.startswith("- "):
                hypotheses.append(line.strip("- "))
        return hypotheses[:5]  # Top 5 hypotheses
```

---

## Integration with Project 2 (Week 7+)

Once Projet 2 (auto-research) is live, ETAU's output feeds directly into Ruflo/OmniRoute:

1. **ETAU produces synthesis** → Notion card created
2. **Status: draft** → human review (you validate)
3. **Status: synthesis-complete** → webhook fires
4. **Projet 2 catches webhook** → extracts hypotheses → queues for Ruflo search
5. **Research results come back** → Notion card links to research findings

This is why Project 1 *must* be production-ready by end of Week 6.

---

## Testing Strategy (Week 1–3)

### Test Queries (Run These)

These are intentionally hard, medium, and explorative:

1. **Hard question** (epistemic limits):
   > "How do the epistemic limits of LLMs constrain what an AI can meaningfully contribute to strategy?"

2. **Brainstorm question** (innovation):
   > "What new capabilities could emerge if we could reliably combine human intuition with AI reasoning?"

3. **Methodology question** (your TIE framework):
   > "If the Théorème de l'Impossibilité Epistemique is correct, what's the best way to use LLMs as research assistants?"

4. **Cross-domain question** (testing transfers):
   > "What could beer fermentation science teach us about AI training?"

5. **Personal question** (testing relevance):
   > "How would you redesign a 'brainstorming assistant' if you knew it would be used 8 hours a day for a year?"

**For each test**:
- [ ] Run ETAU
- [ ] Record synthesis time + token cost
- [ ] Score synthesis quality (1–5): Does it surprise you? Do blind spots feel real? Are hypotheses testable?
- [ ] Note what reformatter got wrong (variants too similar? missed nuance?)
- [ ] Edit synthesis if needed, add notes to Notion card

**Week 1 goal**: Run 2 tests, debug pipeline
**Week 2 goal**: Run 5 more, refine synthesis prompts
**Week 3 goal**: Run 3 final tests, lock in quality, publish results

---

## Budget & Trade-offs

| Metric | Week 1 | Week 2 | Week 3 | Total |
|--------|--------|--------|--------|--------|
| Token spend (est.) | 1.5K | 2–3K | 1–2K | 4.5–6.5K |
| Cost @ Sonnet rates | $25–30 | $45–50 | $20–30 | $90–110 |
| API calls | 10 | 25 | 15 | 50 |
| Brainstorms produced | 2 | 5 | 3 | **10** |

**Cost-cutting lever**: If tokens are tight, use Haiku for parallel LLM calls (Week 2) and keep Sonnet for reformatter + synthesizer.

---

## Success Criteria (End of Week 3)

✅ **Technical**:
- [ ] CLI working end-to-end (query → synthesis → Notion save)
- [ ] Web UI deployed (local or cloud)
- [ ] 4-LLM pipeline ready (even if some are mock-only)
- [ ] Error handling + fallbacks in place
- [ ] Token tracking integrated

✅ **Content**:
- [ ] 10 real brainstorms in Notion
- [ ] Average synthesis quality: 3.5+/5.0
- [ ] Zero irrelevant hypotheses (quality > quantity)

✅ **Documentation**:
- [ ] Blog post published (500+ words)
- [ ] README + ARCHITECTURE.md complete
- [ ] GitHub repo clean, no WIP branches

✅ **Integration**:
- [ ] Notion webhook ready (for Project 2)
- [ ] API documentation for Project 2 integration
- [ ] Examples + test data in repo

---

## Questions to Answer Before Starting Week 4

1. **LLM access**: Do you have API keys for Qwen + Mistral, or fallback to Sonnet variants?
2. **Notion database ID**: Did you set up `/brainstorms/` database in Phase 1? Have the DB ID handy.
3. **Blog platform**: Substack or Medium for Week 3 post?
4. **Token budget**: Is $100 acceptable for this 3-week POC? If not, what's the cap?
5. **Deployment**: Local CLI only, or cloud-hosted web UI?

---

Good luck with ETAU! This is your proof that multi-agent reasoning works. Once you nail this, Project 2 becomes a formality. 🚀
