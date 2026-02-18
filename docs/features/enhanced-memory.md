# Enhanced Memory

Castle Wyvern features **vector-based semantic memory** with embedding search!

## What Makes It Enhanced

- **Vector Embeddings** — 384-dimensional semantic representations
- **Semantic Search** — Find memories by meaning, not just keywords
- **Context Awareness** — Automatic context retrieval for conversations
- **Memory Consolidation** — Compress old, rarely-used memories
- **Importance Scoring** — Prioritize high-value memories

## How It Works

```
Traditional Search: "Python code" → finds "Python code"
Semantic Search: "Python code" → finds "Flask web framework",
                                      "programming tutorials",
                                      "REST API examples"
```

## CLI Commands

```bash
# Add a memory with embedding
/memory-add "Machine learning is fascinating"

# Search by semantic similarity
/memory-search "Tell me about AI"

# Get context for a conversation
/memory-context "How do I build a web app?"

# Show statistics
/memory-stats

# Consolidate old memories
/memory-consolidate
```

## Technical Details

- **384-dimensional embeddings** using hash-based generation
- **Cosine similarity** for semantic matching
- **Ready for upgrade** to OpenAI or sentence-transformers embeddings
- **Persistent storage** in `~/.castle_wyvern/vector_memory/`
