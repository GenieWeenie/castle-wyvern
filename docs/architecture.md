# Castle Wyvern — Architecture

A short design overview for contributors and integrators.

## High-level layers

```
┌─────────────────────────────────────────────────────────────────┐
│  Entry points: CLI (castle_wyvern_cli.py), REST API (port 18791) │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│  Intent routing (eyrie/intent_router.py)                         │
│  Classifies user input → code / review / plan / ask / summarize  │
└─────────────────────────────────────────────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        ▼                           ▼                           ▼
┌───────────────┐         ┌─────────────────┐         ┌─────────────────┐
│ Phoenix Gate  │         │ Grimoorum       │         │ Knowledge Graph │
│ (eyrie/)      │         │ (grimoorum/)    │         │ (eyrie/)        │
│ LLM gateway,  │         │ Memory: search, │         │ KAG: facts,     │
│ circuit       │         │ ingest,         │         │ reasoning,      │
│ breakers      │         │ conversations   │         │ get_stats       │
└───────────────┘         └─────────────────┘         └─────────────────┘
        │                           │                           │
        └───────────────────────────┼───────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        ▼                           ▼                           ▼
┌───────────────┐         ┌─────────────────┐         ┌─────────────────┐
│ Clan          │         │ Node Manager    │         │ BMAD             │
│ Coordination  │         │ (eyrie/)        │         │ (bmad/)          │
│ (eyrie/)      │         │ Stone/Cloud     │         │ Spec, review,    │
│ match→execute │         │ node discovery  │         │ product brief    │
│ →score        │         │                 │         │                 │
└───────────────┘         └─────────────────┘         └─────────────────┘
```

## Data flow

- **User request** (CLI or API) → **Intent router** decides code / review / plan / ask / summarize.
- **Phoenix Gate** is the single LLM gateway: local (Ollama) or cloud (Z.ai, OpenAI), with circuit breakers and retries.
- **Clan** members (Goliath, Lexington, Brooklyn, etc.) are logical roles; routing picks one and Phoenix Gate generates the reply with a role-specific system prompt.
- **Memory** (Grimoorum): search and ingest are independent of intent; the API and CLI expose them directly.
- **KAG**: facts and relationships live in the knowledge graph; `logical_reasoning(query)` runs multi-hop inference, separate from vector RAG.
- **Coordination**: `ClanCoordinationManager` wraps an internal coordination loop (match → exchange → execute → score); the API exposes team selection and status.

## Where things live

| Concern            | Location                    |
|--------------------|-----------------------------|
| API server         | `eyrie/api_server.py`       |
| LLM / circuit      | `eyrie/phoenix_gate.py`     |
| Intent classification | `eyrie/intent_router.py` |
| Memory             | `grimoorum/`                |
| Knowledge graph    | `eyrie/knowledge_graph.py`  |
| Agent coordination | `eyrie/agent_coordination.py` |
| Nodes (Stone/Cloud)| `eyrie/node_manager.py`     |
| BMAD workflows     | `bmad/`                     |
| CLI                | `castle_wyvern_cli.py`      |

## Protocols and extensions

- **MCP (Model Context Protocol)** and **A2A (Agent-to-Agent)** tooling live in `eyrie/`; the same stack serves CLI, API, and external clients.
- **Plugins** extend capabilities without changing core routing; see `eyrie/plugin_system.py` and feature docs under `docs/features/`.

For deeper dives on a feature, see [docs/features/README.md](features/README.md) and [docs/api-examples.md](api-examples.md).
