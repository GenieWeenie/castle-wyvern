# Agent Coordination

**Self-organizing agent swarms** with dynamic team formation!

## The Coordination Loop

```
1. MATCH → Find optimal team based on task requirements
2. EXCHANGE → Agents share expertise, refine approach
3. EXECUTE → Team executes the task
4. SCORE → Evaluate performance
5. RE-MATCH → Learn and improve future teams
```

## How It Works

**Traditional:** You say "Build an API" → System always uses Lexington.

**Coordination:** You say "Build a secure API" → System matches requirements [security, coding, architecture] → Selects Lexington + Xanatos + Brooklyn → EXCHANGE (agents discuss) → EXECUTE (parallel) → SCORE (update performance).

## CLI Commands

```bash
# Check coordination system
/coord-status

# Get optimal team for a task
/coord-team "Build auth system" security,coding

# Run full coordination loop
/coord-run "Build secure API" security,coding,architecture

# View agent stats
/coord-agents
/coord-agent lexington
```

## Why It's Powerful

- **Dynamic teams** — Different tasks get different team compositions
- **Performance learning** — System learns which agents work best together
- **Collaboration scoring** — Tracks how well agents collaborate
- **Self-improving** — Teams get better over time
