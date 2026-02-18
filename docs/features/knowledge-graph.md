# Clan Knowledge Graph (KAG)

**Knowledge Augmented Generation (KAG)** — the next evolution beyond RAG!

## What is KAG?

- **Traditional RAG:** Query → Vector Search → Retrieve Chunks → Generate
- **KAG:** Query → Knowledge Graph → Logical Reasoning → Structured Answer

## Why It's Game-Changing

- **Multi-hop reasoning** — Connect facts across relationships
- **Logical inference** — Reasons over knowledge, not just retrieves
- **Schema-aware** — Domain expertise built into the structure
- **Relationship tracking** — Who did what, when, and why

## How It Works

```
User: "What did Lexington suggest for auth that Xanatos reviewed?"

KAG Process:
1. Find "Lexington" entity
2. Find "auth" entity
3. Find "suggested" relationship
4. Find "Xanatos" entity
5. Find "reviewed" relationship
6. Return: "Lexington suggested OAuth2, Xanatos reviewed on Tuesday"
```

## Entity Types

- **ClanMember** — Goliath, Lexington, Brooklyn, etc.
- **Technology** — Python, OAuth, Kubernetes, etc.
- **Project** — Active projects and initiatives
- **Decision** — Decisions made by the clan
- **SecurityIssue** — Vulnerabilities and concerns
- **Task** — Action items and todos

## Relationship Types

- `suggested`, `reviewed`, `implemented`, `involves`, `depends_on`, `discovered`, `leads`

## CLI Commands

```bash
# Add entities
/kg-add-entity 'Lexington' ClanMember
/kg-add-entity 'OAuth2' Technology

# Add relationships
/kg-add-rel 'Lexington' suggested 'OAuth2'
/kg-add-rel 'Xanatos' reviewed 'OAuth2'

# Query the graph
/kg-reason 'What did Lexington suggest for authentication?'
/kg-query Lexington suggested Project

# Extract from text
/kg-extract 'Lexington implemented OAuth2 for the API'

# Visualize
/kg-visualize
/kg-status
```

## Example Queries

```bash
/kg-reason "What did Lexington suggest that involved security?"
/kg-reason "What involves both security and Brooklyn?"
/kg-reason "Who worked on Project X?"
```
