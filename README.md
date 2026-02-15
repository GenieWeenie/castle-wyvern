# Castle Wyvern
## A Decentralized Multi-Agent AI Infrastructure

**Project Castle Wyvern** is a hardware-agnostic, modular framework for building a personal AI infrastructure. It bridges local "Stone" nodes (Desktops/Laptops) with "Cloud" keeps to create a resilient, private, and agentic assistant ecosystem.

> "One thousand years ago, superstition and the sword ruled. It was a time of darkness. It was a world of fear. It was the age of gargoyles."

![Version](https://img.shields.io/badge/version-0.2.0-blue)
![Python](https://img.shields.io/badge/python-3.9+-brightgreen)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 🏰 The Manhattan Clan

Castle Wyvern features a council of specialized AI agents, each with unique personalities and capabilities:

| Agent | Role | Specialty |
|-------|------|-----------|
| 🦁 **Goliath** | Leader | High-level reasoning, orchestration |
| 🔧 **Lexington** | Technician | Code, automation, technical execution |
| 🎯 **Brooklyn** | Strategist | Multi-path planning, architecture |
| 📜 **Broadway** | Chronicler | Documentation, summarization |
| 📚 **Hudson** | Archivist | Historical context, long-term memory |
| 🐕 **Bronx** | Watchdog | Security monitoring, alerts |
| 🌉 **Elisa** | Bridge | Human context, ethics, legal |
| 🎭 **Xanatos** | Red Team | Adversarial testing, vulnerabilities |
| 🔥 **Demona** | Failsafe | Error prediction, worst-case scenarios |

---

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/GenieWeenie/castle-wyvern.git
cd castle-wyvern

# Install dependencies
pip install -r requirements.txt
pip install rich  # For beautiful CLI

# Configure
cp .env.example .env
# Edit .env with your API keys (Z.ai, OpenAI optional)

# Awaken the clan (interactive CLI)
python castle_wyvern_cli.py
```

---

## 🎮 Using Castle Wyvern

### Interactive CLI (New!)

The Rich-powered CLI provides a beautiful interface to interact with the clan:

```bash
python castle_wyvern_cli.py
```

**Commands:**
- `ask <question>` - Ask the clan anything
- `code <description>` - Request code from Lexington
- `review <code/description>` - Get code review from Xanatos
- `summarize <text>` - Request summary from Broadway
- `plan <description>` - Get architecture from Brooklyn
- `status` - Show full dashboard
- `health` - Check Phoenix Gate status
- `members` - List clan members
- `help` - Show all commands
- `quit` - Exit Castle Wyvern

**Example Session:**
```
🏰 CASTLE WYVERN v0.2.0

👤 You: code Write a function to calculate fibonacci
🎯 Intent: code (95% confidence)
🛡️  Routed to: 🔧 Lexington

🔧 Lexington:
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
```

---

## 📂 Project Structure

```
Castle-Wyvern/
├── bmad/                   # BMAD Method integration
│   ├── agents/             # Agent BMAD specializations
│   ├── commands/           # BMAD workflow commands
│   ├── templates/          # Reusable templates
│   └── workflows/          # Phase workflows
├── clan_members/           # Custom agent implementations
├── eyrie/                  # Connectivity & routing
│   ├── phoenix_gate.py     # AI API gateway with retry/circuit breaker
│   ├── intent_router.py    # Smart agent routing
│   └── error_handler.py    # Error handling & logging
├── grimoorum/              # Memory & archives
│   └── memory_manager.py   # Conversation persistence
├── prompts/                # Agent system prompts
├── spells/                 # Reusable prompt templates
├── tests/                  # Test suite (31 tests)
├── castle_wyvern_cli.py    # 🆕 Rich interactive CLI
├── clan_wyvern.py          # Main entry point
├── pyproject.toml          # Package configuration
├── install.sh              # Installation script
├── .env.example            # Configuration template
└── README.md               # This file
```

---

## 🧪 Running Tests

```bash
# Install pytest
pip install pytest pytest-cov

# Run all tests
pytest tests/test_castle_wyvern.py -v

# Run with coverage
pytest tests/test_castle_wyvern.py --cov=eyrie
```

**Current Status:** 31 tests passing ✅

---

## 🎯 BMAD Integration

Castle Wyvern implements the **BMAD Method** (Build, Measure, Analyze, Deploy):

```bash
# Simple path (bug fixes, small features)
python bmad/commands/quick_spec.py "fix login button"
python bmad/commands/dev_story.py
python bmad/commands/code_review.py

# Full planning (products, complex features)
python bmad/commands/product_brief.py "build AI feature"
```

---

## 🛡️ Security & Privacy

- **Local-first:** Prioritizes local LLM processing (Ollama)
- **Circuit breakers:** Prevents cascading failures
- **Automatic retry:** Exponential backoff for API calls
- **Encrypted memory:** Conversations stored securely
- **No data sharing:** Your data stays on your machines
- **Audit logging:** Full transparency of system actions

---

## 🌟 Features

### Phase 1 ✅ Complete
- ✅ Real AI API calls via Phoenix Gate (Z.ai/GLM-4-Plus)
- ✅ Dependency management (pyproject.toml)
- ✅ Error handling with retry logic & circuit breakers
- ✅ Comprehensive logging

### Phase 2 ✅ Complete
- ✅ Intent-based routing (smart agent selection)
- ✅ 31-test pytest suite
- ✅ Rich CLI interface with beautiful dashboard
- ✅ Live clan status monitoring

### Phase 3 ✅ Complete
- ✅ Document ingestion (RAG)
- ✅ Memory improvements (Grimoorum upgrades)
- ✅ Multi-node distribution
- ✅ Auto-discovery (mDNS/Zeroconf node discovery)
- ✅ REST API Server (HTTP endpoints for all clan functions)
- ✅ Web Dashboard (browser-based UI)

### Phase 4 ✅ Complete
- ✅ Plugin System (extensible architecture with hooks)
- ✅ Advanced Monitoring (metrics, health checks, alerts)
- ✅ CLI Improvements (history, aliases, sessions, config wizard)
- ✅ Integration APIs (Slack, Discord, Email, Webhooks)
- ✅ Security Enhancements (audit logging, encryption, API keys, intrusion detection)

### Stretch Goals ✅ Complete
- ✅ Advanced AI Features (ensemble voting, streaming, prompt optimization, code execution)
- ✅ Performance Optimizations (caching, connection pooling, lazy loading, profiling)
- ✅ Documentation Generator (auto-docs, API docs, architecture diagrams)

### Post-Release Enhancements
- ✅ **MCP Protocol Support** - Model Context Protocol server for integration with Claude Desktop, Cursor, and other MCP clients
- ✅ **A2A Protocol Support** - Agent-to-Agent protocol for communicating with other agent frameworks

---

## 🔌 MCP (Model Context Protocol)

Castle Wyvern now implements Microsoft's **Model Context Protocol** — the emerging standard for AI agent interoperability!

### What This Means
Connect Castle Wyvern to any MCP-compatible client:
- **Claude Desktop** - Use the Manhattan Clan directly in Claude
- **Cursor IDE** - Get coding help from Lexington in your editor
- **Any MCP client** - Universal compatibility

### Available MCP Tools
- `ask_goliath` - Strategic guidance from the leader
- `ask_lexington` - Code generation and technical help
- `ask_brooklyn` - Architecture and planning
- `ask_xanatos` - Security reviews
- `ask_broadway` - Documentation and summarization
- `castle_wyvern_status` - System health check

### Quick Start
```bash
# In Castle Wyvern CLI
/mcp-install  # Show installation instructions
/mcp-start    # Start MCP server
```

Then configure your MCP client to connect to Castle Wyvern!

---

## 🚀 Project Status

**🎉 ALL 21 FEATURES COMPLETE! 🎉**

| Phase | Features | Status |
|-------|----------|--------|
| Phase 1 | 4/4 | ✅ 100% |
| Phase 2 | 4/4 | ✅ 100% |
| Phase 3 | 5/5 | ✅ 100% |
| Phase 4 | 5/5 | ✅ 100% |
| Stretch | 3/3 | ✅ 100% |
| **TOTAL** | **21/21** | **✅ 100%** |
| **Protocols** | MCP + A2A | **✅ Done** |

## 🛠️ Tech Stack

- **Python 3.9+**
- **Local LLM:** Ollama
- **Cloud Primary:** Z.ai (GLM-4-Plus)
- **Cloud Fallback:** OpenAI (GPT-3.5)
- **CLI:** Rich (beautiful terminal UI)
- **Testing:** pytest
- **Memory:** JSON-based Grimoorum
- **Routing:** Hybrid keyword + AI classification
- **Protocols:** MCP, A2A

---

## 🔗 A2A (Agent-to-Agent Protocol)

Castle Wyvern implements Google's **Agent-to-Agent Protocol** — enabling communication with other agent frameworks!

### What This Means
Castle Wyvern can now:
- **Talk to CrewAI agents** - Delegate tasks to CrewAI agents
- **Collaborate with LangGraph** - Integrate with LangGraph workflows
- **Form agent swarms** - Create multi-framework agent networks
- **Be discovered** - Other A2A agents can find and use Castle Wyvern

### A2A Server Features
- **Agent Discovery** - `/.well-known/agent.json` endpoint
- **Task Management** - Create, monitor, cancel tasks
- **Streaming Support** - Real-time response streaming
- **5 Exposed Skills**:
  - Strategic Leadership (Goliath)
  - Technical Implementation (Lexington)
  - Architecture Planning (Brooklyn)
  - Security Review (Xanatos)
  - Documentation (Broadway)

### Quick Start
```bash
# Start A2A server
/a2a-start

# Discover other A2A agents
/a2a-discover http://localhost:8080 http://localhost:9090

# Delegate task to another agent
/a2a-delegate crew-ai-agent "Analyze this codebase"
```

### A2A + MCP = Ecosystem Ready
- **MCP** connects Castle Wyvern to clients (Claude, Cursor)
- **A2A** connects Castle Wyvern to other agents (CrewAI, LangGraph)
- Together: Full ecosystem interoperability!

---

## 📜 License

MIT License — see LICENSE for details.

---

*"We are defenders of the night! We are gargoyles!"*

---

## 🗺️ Roadmap

See [docs/cli_research.md](docs/cli_research.md) for CLI research and [roadmap.json](roadmap.json) for full feature roadmap.

**Recent Commits:**
- `f269df9` 🔗 Add A2A Protocol Support - Inter-framework agent communication!
- `825b75a` 🔌 Add MCP Protocol Support - Microsoft Model Context Protocol
- `8361557` 🎉 ALL 21 FEATURES COMPLETE! (Features 19-21 - Stretch Goals)
- `5c6b9fd` Phase 4 COMPLETE! (Feature 18 - Security Enhancements)
- `5a221ab` Phase 4: Security Enhancements (Feature 18)