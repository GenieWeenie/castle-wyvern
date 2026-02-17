# MCP & A2A Protocols

Castle Wyvern implements **MCP** (Model Context Protocol) and **A2A** (Agent-to-Agent Protocol) for ecosystem interoperability.

## MCP (Model Context Protocol)

Microsoft's standard for AI agent interoperability. Connect Castle Wyvern to:

- **Claude Desktop** — Use the Manhattan Clan directly in Claude
- **Cursor IDE** — Get coding help from Lexington in your editor
- **Any MCP client** — Universal compatibility

### Available MCP Tools

- `ask_goliath`, `ask_lexington`, `ask_brooklyn`, `ask_xanatos`, `ask_broadway`
- `castle_wyvern_status` — System health check

### Quick Start

```bash
# In Castle Wyvern CLI
/mcp-install  # Show installation instructions
/mcp-start    # Start MCP server
```

Then configure your MCP client to connect to Castle Wyvern.

---

## A2A (Agent-to-Agent Protocol)

Google's protocol for communication between agent frameworks. Castle Wyvern can:

- **Talk to CrewAI agents** — Delegate tasks
- **Collaborate with LangGraph** — Integrate workflows
- **Form agent swarms** — Multi-framework networks
- **Be discovered** — Other A2A agents can find and use Castle Wyvern

### A2A Server Features

- **Agent Discovery** — `/.well-known/agent.json` endpoint
- **Task Management** — Create, monitor, cancel tasks
- **Streaming Support** — Real-time response streaming
- **5 Exposed Skills:** Goliath (Leadership), Lexington (Technical), Brooklyn (Architecture), Xanatos (Security), Broadway (Documentation)

### Quick Start

```bash
# Start A2A server
/a2a-start

# Discover other A2A agents
/a2a-discover http://localhost:8080 http://localhost:9090

# Delegate task to another agent
/a2a-delegate crew-ai-agent "Analyze this codebase"
```

## MCP + A2A Together

- **MCP** connects Castle Wyvern to *clients* (Claude, Cursor)
- **A2A** connects Castle Wyvern to *other agents* (CrewAI, LangGraph)
- Together: full ecosystem interoperability
