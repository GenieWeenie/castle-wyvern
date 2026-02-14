# BMAD Method Integration for Castle Wyvern
## Breakthrough Method of Agile AI Driven Development

**Version:** 1.0  
**Integration Date:** February 14, 2026  
**Status:** Active Development

---

## Overview

BMAD (Build, Measure, Analyze, Deploy) integrated with the Manhattan Clan's unique abilities. Each clan member specializes in specific BMAD phases, bringing their Gargoyles character and expertise to the agile development process.

---

## The BMAD Cycle

```
    BUILD ←—————— DEPLOY
      ↑             ↓
   ANALYZE ←——— MEASURE
```

**Each phase invokes specific clan members based on their strengths.**

---

## Clan Member BMAD Specializations

| Phase | Primary | Secondary | Support |
|-------|---------|-----------|---------|
| **BUILD** | Lexington (Tech) | Brooklyn (Strategy) | Goliath (Leadership) |
| **MEASURE** | Broadway (Chronicler) | Bronx (Monitor) | Elisa (Human Context) |
| **ANALYZE** | Brooklyn (Strategy) | Xanatos (Red Team) | Demona (Failsafe) |
| **DEPLOY** | Lexington (Tech) | Bronx (Security) | Goliath (Final Approval) |

---

## Quick Commands

### Simple Path (Bug Fixes, Small Features)
- `/quick-spec` — Goliath + Brooklyn analyze and create tech spec
- `/dev-story` — Lexington implements with Broadway documenting
- `/code-review` — Xanatos reviews, Demona finds edge cases

### Full Planning Path (Products, Complex Features)
- `/product-brief` — Goliath defines vision, Elisa adds human context
- `/create-prd` — Broadway writes PRD, Hudson checks historical patterns
- `/create-architecture` — Brooklyn designs, Xanatos tests for vulnerabilities
- `/create-epics-and-stories` — Goliath breaks down, Brooklyn strategizes
- `/sprint-planning` — Elisa coordinates, Bronx monitors
- Loop: `/create-story` → `/dev-story` → `/code-review`

---

## Party Mode

Invoke multiple clan members for collaborative sessions:

```bash
python clan_wyvern.py --party "plan architecture for new feature"
# Summons: Goliath, Brooklyn, Lexington, Xanatos
```

---

## Directory Structure

```
bmad/
├── workflows/          # Phase-specific workflow templates
│   ├── build_phase.md
│   ├── measure_phase.md
│   ├── analyze_phase.md
│   └── deploy_phase.md
├── agents/             # Clan member BMAD specializations
│   ├── lexington_builder.md
│   ├── brooklyn_architect.md
│   ├── broadway_chronicler.md
│   ├── bronx_monitor.md
│   ├── xanatos_redteam.md
│   └── demona_failsafe.md
├── commands/           # Executable BMAD commands
│   ├── quick_spec.py
│   ├── dev_story.py
│   ├── code_review.py
│   ├── product_brief.py
│   ├── create_prd.py
│   ├── create_architecture.py
│   └── sprint_planning.py
└── templates/          # Reusable templates
    ├── tech_spec_template.md
    ├── prd_template.md
    ├── architecture_template.md
    └── story_template.md
```

---

## Usage

From Castle Wyvern root:

```bash
# Simple path
python bmad/commands/quick_spec.py "fix login bug"
python bmad/commands/dev_story.py
python bmad/commands/code_review.py

# Full planning
python bmad/commands/product_brief.py "build AI chat feature"
python bmad/commands/create_prd.py
python bmad/commands/create_architecture.py
```

---

*"We protect the code that protects the night."* — Lexington
