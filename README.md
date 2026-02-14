# Castle Wyvern
## A Decentralized Multi-Agent AI Infrastructure

**Project Castle Wyvern** is a hardware-agnostic, modular framework for building a personal AI infrastructure. It bridges local "Stone" nodes (Desktops/Laptops) with "Cloud" keeps to create a resilient, private, and agentic assistant ecosystem.

> "One thousand years ago, superstition and the sword ruled. It was a time of darkness. It was a world of fear. It was the age of gargoyles."

---

## 🏰 The Manhattan Clan

Castle Wyvern features a council of specialized AI agents, each with unique personalities and capabilities:

| Agent | Role | Specialty |
|-------|------|-----------|
| **Goliath** | Leader | High-level reasoning, orchestration |
| **Lexington** | Technician | Code, automation, technical execution |
| **Brooklyn** | Strategist | Multi-path planning, architecture |
| **Broadway** | Chronicler | Documentation, summarization |
| **Hudson** | Archivist | Historical context, long-term memory |
| **Bronx** | Watchdog | Security monitoring, alerts |
| **Elisa** | Bridge | Human context, ethics, legal |
| **Xanatos** | Red Team | Adversarial testing, vulnerabilities |
| **Demona** | Failsafe | Error prediction, worst-case scenarios |

---

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Configure
 cp .env.example .env
# Edit .env with your API keys

# Awaken the clan
python clan_wyvern.py
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
│   ├── phoenix_gate.py     # AI API gateway
│   └── sentinel_ping.py    # Node health checker
├── grimoorum/              # Memory & archives
│   └── memory_manager.py   # Conversation persistence
├── prompts/                # Agent system prompts
├── spells/                 # Reusable prompt templates
├── clan_wyvern.py          # Main entry point
├── .env.example            # Configuration template
└── README.md               # This file
```

---

## 🛡️ Security & Privacy

- **Local-first:** Prioritizes local LLM processing
- **Encrypted memory:** Conversations stored securely
- **No data sharing:** Your data stays on your machines
- **Audit logging:** Full transparency of system actions

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

## 🌟 Features

- ✅ Multi-agent council with distinct personalities
- ✅ BMAD Method workflow integration
- ✅ Hybrid local/cloud AI routing
- ✅ Persistent conversation memory
- ✅ Security-focused architecture
- ✅ Thematic Gargoyles design

---

## 🛠️ Tech Stack

- **Python 3.9+**
- **Local LLM:** Ollama
- **Cloud Fallback:** OpenAI / Z.ai
- **Memory:** JSON-based Grimoorum
- **Dependencies:** Minimal (requests, python-dotenv)

---

## 📜 License

MIT License — see LICENSE for details.

---

*"We are defenders of the night! We are gargoyles!"*