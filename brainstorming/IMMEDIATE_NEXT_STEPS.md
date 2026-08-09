# 🎯 NEXT 2 HOURS — Action Plan

You have ~2 hours starting now. Use them to **lock in the 12-week plan** so Week 1 can start immediately.

---

## In Parallel (You + Claude)

### 1️⃣ Decision Checkpoint — 15 minutes

**Read this and decide YES/NO on each**:

- [ ] **Phase order OK?** (Env → ETAU → Research → Converters/YouTube)
  - If NO: What should move? (reply and we re-sort)
  
- [ ] **Notion is your KB platform?** (or switch to Obsidian/LogSeq?)
  - If YES: I'll scaffold full schema below
  
- [ ] **GitHub public or private?**
  - If PUBLIC: All code visible, blog links work natively
  - If PRIVATE: Blog posts won't show repos directly
  
- [ ] **LLM access for ETAU**:
  - Sonnet 5.0 only? ✅ (cheaper, faster to start)
  - + Qwen/GLM-4? (need Ali Baba / Zhipu API key)
  - + Mistral? (need Mistral API key)
  - For Week 4 start, Sonnet-only is fine. Add others in Week 2.
  
- [ ] **Publish budget for 12 weeks**:
  - Blog post cadence: 1 per phase (4 total)?
  - Platform: Substack + Medium? Or just Substack?
  - You need Substack auth ready by Week 3 end.

---

### 2️⃣ Notion Schema Setup — 45 minutes

**Do this while I create the template**:

1. Create a new Notion workspace (or use existing?)
2. Create root page: `/Andrei KB/` (or name it what you want)
3. Create database pages:
   - [ ] `/projects/`
   - [ ] `/brainstorms/`
   - [ ] `/research/`
   - [ ] `/youtube-kb/`
   - [ ] `/sources/`
   - [ ] `/deliverables/`

**I'll send you the full schema below** — copy the field definitions into each database.

4. Install Notion MCP:
   ```bash
   # Verify it's in your ~/.config/claude/mcp.json or equivalent
   # If not, add:
   {
     "mcp_servers": {
       "notion": {
         "url": "https://mcp.notion.com/mcp"
       }
     }
   }
   ```

5. Get your Notion credentials:
   - [ ] NOTION_TOKEN (from https://www.notion.so/my-integrations)
   - [ ] Database IDs (right-click each DB → Copy link → extract UUID)
   - [ ] Store in `~/.env` or environment variables

**Command to test**:
```bash
export NOTION_TOKEN="secret_..."
python -c "from notion_client import Client; c = Client(auth=NOTION_TOKEN); print(c.users.me())"
```

---

### 3️⃣ GitHub Skeleton — 30 minutes

Create 3 new repos (or branches in `ratio`):

```bash
cd ~/projects

# Repo 1: Shared utilities
mkdir -p shared-setup
cd shared-setup
git init
mkdir -p {task-observer,token-tracker,project-template}
# (I'll populate these below)

# Repo 2: ETAU (for Week 4)
mkdir -p etau
cd etau
git init
mkdir -p src tests web docs
# (Skeleton is in ETAU_POC.md)

# Repo 3: Research automation (for Week 7)
mkdir -p research-automation
cd research-automation
git init
mkdir -p src tests docs
```

**GitHub setup**:
```bash
# For each repo:
cd repo-name
git remote add origin https://github.com/symbioticode/repo-name.git
git branch -M main
git push -u origin main
```

---

### 4️⃣ Fill in Your 8 Dimensions — 20 minutes

Open `shared/methodology.md` (see PHASE1_SETUP.md for template).

**At minimum, fill in**:
- Brainstorm tool: ETAU (starting Week 4) or manual now
- Documentation format: Markdown in GitHub + Notion visibility
- Versioning: Your git branching strategy
- Model selection: Sonnet for what? Haiku for what?
- Publication: Substack? Medium? Frequency?

**This is YOUR north star.** Every project references it.

---

### 5️⃣ Create Directory Structure in nixos — 20 minutes

```bash
cd ~/projects

# Master index
cat > README.md << 'EOF'
# Andrei's Projects (12-Week Sequence)

## Structure
- `shared/` — methodology, templates, task-observer, token-tracker
- `etau/` — Multi-LLM brainstorming (Weeks 4–6)
- `research-automation/` — Automated hypothesis research (Weeks 7–9)
- `archive/` — Completed phases

## Current Phase
**Week 1–3**: Environment & Assistant Scaffold (Projet 3)

See STRATEGY_12WEEKS.md for full roadmap.
EOF

# Shared setup
mkdir -p shared/{task-observer,token-tracker,project-template}
cp PHASE1_SETUP.md shared/SETUP_GUIDE.md
cat > shared/methodology.md << 'EOF'
# Your 8 Dimensions
(Fill this from PHASE1_SETUP.md template)
EOF

# Project templates
cp -r etau-template/ shared/project-template/  # Or create from scratch

# Archive folder
mkdir -p archive
echo "# Archive" > archive/README.md

# ETAU setup
mkdir -p etau/{src,tests,web,docs}
cp ETAU_POC.md etau/
cat > etau/README.md << 'EOF'
# ETAU: Multi-LLM Brainstorming Pipeline
See ETAU_POC.md for full architecture.
EOF

git add .
git commit -m "chore: initial 12-week structure"
```

---

### 6️⃣ Lock in Week 1 Deliverables — Final 10 minutes

By end of Week 3, you MUST have:

**Technical**:
- ✅ Notion KB populated (schema + 5 test brainstorms)
- ✅ task-observer running as cron job
- ✅ Token tracker logging all API calls
- ✅ GitHub repos ready for Week 4

**Content**:
- ✅ 1 blog post published ("Why I'm Automating My Research")
- ✅ methodology.md finalized
- ✅ 6 manual brainstorms in Notion (test the schema)

**Documentation**:
- ✅ ARCHITECTURE.md in `etau/` folder
- ✅ README with onboarding instructions
- ✅ LLM setup guide (for Week 2 multi-LLM integration)

---

## Questions to Answer (Help Me Help You)

Reply to these *in chat* (don't need written docs):

1. **Notion status**: Do you have a Notion workspace set up? Can I scaffold the schema?

2. **GitHub username**: Is it `symbioticode`? I'll reference correct repo paths.

3. **LLM keys**: Do you have:
   - [ ] Anthropic API key (for Sonnet)?
   - [ ] Qwen/GLM-4 key (Asia LLM)?
   - [ ] Mistral API key (Europe LLM)?
   - For Week 4, Sonnet-only is fine. Others can wait until Week 2.

4. **Blog platform**: Substack + Medium, or just one?

5. **Token budget**: What's your monthly API ceiling? (This affects model selection.)

6. **nixos question**: Are you using Nix flakes? Or just bash scripts for env setup?

---

## Final Checklist (Before Midnight)

- [ ] Read STRATEGY_12WEEKS.md (15 min)
- [ ] Read PHASE1_SETUP.md (20 min)
- [ ] Read ETAU_POC.md (15 min)
- [ ] Answer the 6 questions above (10 min)
- [ ] Create Notion schema (45 min)
- [ ] Create GitHub skeleton (30 min)
- [ ] Fill methodology.md (20 min)
- [ ] Create directory structure (20 min)
- [ ] Commit to GitHub (5 min)

**Total: ~2 hours 20 minutes**

If you finish early: Start writing your Week 1 plan document (what you'll do each day).

---

## After the 2 Hours: Phase 1 Starts

**Monday morning, Week 1**:
- [ ] First Notion setup session (test schema with 1 manual brainstorm)
- [ ] Install task-observer cron job
- [ ] Create first project page: `/projects/environment-scaffold/`
- [ ] Log first brainstorm attempt

**By Friday end of Week 1**:
- [ ] Notion KB fully operational
- [ ] 2 test brainstorms in KB
- [ ] GitHub repos populated with skeleton code

---

Go. You got this. 🚀

(Any blockers, ping me. I'll help unblock immediately.)
