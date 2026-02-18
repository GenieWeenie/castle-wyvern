# Castle Wyvern - Complete User Guide
## Your Personal AI Infrastructure

---

## Table of Contents
1. [Getting Started](#getting-started)
2. [The Manhattan Clan](#the-manhattan-clan)
3. [Core Features](#core-features)
4. [Advanced Features](#advanced-features)
5. [Tutorials](#tutorials)
6. [API Reference](#api-reference)
7. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Installation

```bash
# Clone the repository
git clone https://github.com/GenieWeenie/castle-wyvern.git
cd castle-wyvern

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

### First Launch

```bash
python castle_wyvern_cli.py
```

You'll see:
```
🏰 CASTLE WYVERN v1.0+

"We are defenders of the night!"
"We are Gargoyles!"

👤 You:
```

### Basic Commands

```bash
ask What is Python?                    # Ask the clan
code Write a fibonacci function        # Request code
review this code...                    # Get code review
summarize this text...                 # Summarize content
plan How to build an API               # Get architecture plan
status                                 # Show full dashboard
help                                   # Show all commands
```

---

## The Manhattan Clan

### Meet Your Agents

| Member | Role | Best For | Emoji |
|--------|------|----------|-------|
| **Goliath** | Leader | Strategy, high-level decisions | 🦁 |
| **Lexington** | Technician | Code, technical execution | 🔧 |
| **Brooklyn** | Strategist | Architecture, planning | 🎯 |
| **Broadway** | Chronicler | Documentation, summaries | 📜 |
| **Hudson** | Archivist | Memory, historical context | 📚 |
| **Bronx** | Watchdog | Security alerts, monitoring | 🐕 |
| **Elisa** | Bridge | Human context, ethics | 🌉 |
| **Xanatos** | Red Team | Security reviews, pentesting | 🎭 |
| **Demona** | Failsafe | Error prediction, edge cases | 🔥 |
| **Jade** | Web Surfer | Research, browsing | 🌐 |

### How Routing Works

Castle Wyvern automatically routes your requests to the best clan member:

```
You: "Write a Python function"
↓
Intent Router analyzes: 95% code intent
↓
Routes to: 🔧 Lexington (Technician)
↓
Lexington generates code
```

---

## Core Features

### 1. Intent-Based Routing

Castle Wyvern automatically understands what you want:

```bash
# Technical questions → Lexington
ask How do I use asyncio in Python?

# Strategy questions → Brooklyn  
ask What's the best architecture for a microservice?

# Security questions → Xanatos
ask Is this code vulnerable to SQL injection?

# Documentation → Broadway
ask Summarize this README
```

### 2. BMAD Workflow

**Build-Measure-Analyze-Deploy** methodology:

```bash
# Start a BMAD workflow
workflow-start my_api_project

# Add BMAD commands
/build Design the API endpoints
/measure Create test suite
/analyze Performance benchmarks
/deploy Docker configuration

# Execute the workflow
workflow-execute my_api_project
```

### 3. Memory System (Grimoorum)

Castle Wyvern remembers everything:

```bash
# Add to memory
remember "OAuth2 is the authentication standard"

# Recall from memory
recall authentication standards

# Get context-aware responses
ask What should I use for auth?
→ "Based on your previous note about OAuth2..."
```

### 4. Multi-Node Distribution

Scale across multiple machines:

```bash
# Start auto-discovery
/discover-start

# Check discovered nodes
/discover-status

# View connected nodes
/nodes

# Delegate task to specific node
/delegate node-2 "Process this large file"
```

---

## Advanced Features

### Knowledge Graph (KAG)

**Multi-hop reasoning over structured knowledge:**

```bash
# Add entities
/kg-add-entity "Lexington" ClanMember
/kg-add-entity "OAuth2" Technology
/kg-add-entity "API Project" Project

# Add relationships
/kg-add-rel "Lexington" suggested "OAuth2"
/kg-add-rel "Lexington" leads "API Project"
/kg-add-rel "API Project" involves "OAuth2"

# Query with reasoning
/kg-reason "What did Lexington suggest for the API?"
→ "Lexington suggested OAuth2 for API Project"

# Multi-hop query
/kg-query Lexington suggested Project
→ Shows all projects Lexington suggested tech for

# Extract from text
/kg-extract "Brooklyn suggested Kubernetes for deployment"
→ Auto-creates entities and relationships
```

**Why it's powerful:**
- Traditional RAG: "Find text about Lexington"
- Knowledge Graph: "What did Lexington suggest that Xanatos reviewed?"

### Visual Automation (OmniParser)

**Control GUIs through vision:**

```bash
# Analyze current screen
/visual-scan
→ Detected elements:
  • button: 'Submit' at (340, 250)
  • input: 'Username' at (340, 150)
  • input: 'Password' at (340, 200)

# Click elements
/visual-click "submit button"
→ Would click at (340, 250)

# Type into fields
/visual-type "myusername" "username field"
→ Would type into field at (340, 150)

# Visual browser session
/visual-browser-start
/visual-browser-task "Click the login button"
/visual-browser-task "Type admin in the username field"
/visual-browser-end
```

### Self-Building Functions

**Create tools from descriptions:**

```bash
# Create a function
/function-create "Fetch weather from OpenWeatherMap API"
→ Generates Python code for API calls
→ Saves to ~/.castle_wyvern/functions/
→ Ready to use

# List functions
/function-list
→ Shows all created functions

# View function code
/function-show fetch_weather
→ Displays generated code

# Use in workflows
function:fetch_weather(city="Denver")
```

### Docker Sandbox

**Execute code safely:**

```bash
# Check status
/sandbox-status
→ Docker available: Yes
→ Supported: Python, JavaScript, Go, Rust, Java

# Execute Python
/sandbox-exec "print('Hello World')"
→ Runs in isolated container
→ Returns output

# Switch language
/sandbox-lang javascript
/sandbox-exec "console.log('Hello')"

# Language options: python, javascript, bash, go, rust, java
```

### Goal-Based Agent

**Autonomous task execution:**

```bash
# Create a goal
/goal "Build a REST API for a todo app"
→ Creates subtasks:
  1. Analyze requirements (Brooklyn)
  2. Design database schema (Brooklyn)
  3. Implement endpoints (Lexington)
  4. Add authentication (Xanatos)
  5. Write tests (Broadway)

# Execute autonomously
/goal-execute <goal_id>
→ Executes each subtask
→ Routes to appropriate clan member
→ Reports progress

# Check status
/goal-status <goal_id>
→ Shows completed/running/pending tasks
```

### Browser Agent

**Web research automation:**

```bash
# Search the web
/search "Python async best practices"
→ Returns top 5 search results

# Browse specific page
/browse https://docs.python.org/3/library/asyncio.html
→ Fetches and summarizes page

# Deep research
/research "Latest Python web frameworks 2025"
→ Searches multiple sources
→ Compiles comprehensive report

# View history
/browser-history
→ Shows visited pages
```

---

## Tutorials

### Tutorial 1: Building Your First API

**Goal:** Build a REST API with authentication

```bash
# Step 1: Plan with Brooklyn
plan Create a REST API with JWT authentication for a todo app

# Step 2: Start BMAD workflow
workflow-start todo_api

# Step 3: Build phase
/build Create FastAPI todo endpoints with JWT auth

# Step 4: Review security
review Show me the authentication code
→ Routes to Xanatos for security review

# Step 5: Add to knowledge graph
/kg-add-entity "Todo API" Project
/kg-add-rel "Lexington" implemented "Todo API"

# Step 6: Document
/docs-generate
→ Generates API documentation
```

### Tutorial 2: Security Audit Workflow

**Goal:** Audit your codebase for vulnerabilities

```bash
# Step 1: Start security scan
/security-scan

# Step 2: Review with Xanatos
ask Xanatos to review the authentication module

# Step 3: Add findings to knowledge graph
/kg-add-entity "Auth Vulnerability" SecurityIssue
/kg-add-rel "Xanatos" discovered "Auth Vulnerability"

# Step 4: Create remediation task
/goal "Fix authentication vulnerabilities"

# Step 5: Track in workflow
workflow-create security_audit
```

### Tutorial 3: Visual Web Automation

**Goal:** Automate a web form

```bash
# Step 1: Start visual browser
/visual-browser-start

# Step 2: Analyze the page
/visual-scan
→ Shows all interactive elements

# Step 3: Fill form
/visual-type "admin" "username field"
/visual-type "secret123" "password field"

# Step 4: Submit
/visual-click "login button"

# Step 5: End session
/visual-browser-end
```

### Tutorial 4: Knowledge Graph for Projects

**Goal:** Track project decisions and relationships

```bash
# Add project
/kg-add-entity "Castle Wyvern v2" Project

# Add team members
/kg-add-entity "You" ClanMember

# Add technologies
/kg-add-entity "Python" Technology
/kg-add-entity "Docker" Technology

# Track decisions
/kg-add-rel "You" suggested "Docker"
/kg-add-rel "Xanatos" reviewed "Docker"
/kg-add-rel "Lexington" implemented "Docker"

# Query later
/kg-reason "What did I suggest that Xanatos reviewed?"
→ "You suggested Docker, Xanatos reviewed it"

/kg-reason "Who worked on Docker?"
→ "You suggested it, Xanatos reviewed it, Lexington implemented it"
```

---

## API Reference

### REST API

Castle Wyvern exposes a REST API on port 18791:

```bash
# Start API server
/api-start

# Health check
curl http://localhost:18791/health

# Ask the clan
curl -X POST http://localhost:18791/clan/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is Python?"}'

# Request code
curl -X POST http://localhost:18791/clan/code \
  -H "Content-Type: application/json" \
  -d '{"description": "fibonacci function"}'

# List clan members
curl http://localhost:18791/clan
```

### MCP Protocol

Connect to Claude Desktop, Cursor, etc.:

```bash
# Start MCP server
/mcp-start

# Configure Claude Desktop:
# Add to claude_desktop_config.json:
{
  "mcpServers": {
    "castle-wyvern": {
      "command": "python",
      "args": ["-m", "eyrie.mcp_server"],
      "cwd": "/path/to/castle-wyvern"
    }
  }
}
```

Available tools:
- `ask_goliath` - Strategic guidance
- `ask_lexington` - Code generation
- `ask_brooklyn` - Architecture planning
- `ask_xanatos` - Security reviews
- `ask_broadway` - Documentation

### A2A Protocol

Connect to other agent frameworks:

```bash
# Start A2A server
/a2a-start

# Discover other agents
/a2a-discover http://localhost:8080

# Delegate task to external agent
/a2a-delegate crewai-agent "Analyze this data"
```

---

## Troubleshooting

### Common Issues

**1. "Docker not available" when using sandbox**
```bash
# Install Docker
# macOS: brew install --cask docker
# Ubuntu: sudo apt install docker.io
# Then: sudo usermod -aG docker $USER
```

**2. "Knowledge graph empty"**
```bash
# Add some entities first
/kg-add-entity "Lexington" ClanMember
/kg-add-entity "Python" Technology
/kg-add-rel "Lexington" suggested "Python"
```

**3. "Visual automation not working"**
```bash
# Visual automation is simulated by default
# For real OmniParser integration, install:
pip install omniparser
# And download OmniParser models
```

**4. API server won't start**
```bash
# Check if port 18791 is in use
lsof -i :18791
# Kill process or use different port
```

**5. Clan members not responding**
```bash
# Check Phoenix Gate status
/health

# Check clan status
/status

# Restart if needed
quit
# Then restart: python castle_wyvern_cli.py
```

### Getting Help

```bash
# Show all commands
help

# Show specific command help
/help kg-add-entity
/help visual-scan

# Check system status
/status

# View recent logs
/logs
```

---

## Tips & Best Practices

### 1. Use BMAD for Complex Projects
Break large projects into Build-Measure-Analyze-Deploy phases

### 2. Build Your Knowledge Graph
Track decisions, technologies, and relationships from day one

### 3. Leverage Clan Specialties
- Code → Lexington
- Security → Xanatos
- Strategy → Brooklyn
- Docs → Broadway

### 4. Secure Your Code
Always use `/sandbox-exec` for untrusted code

### 5. Document Everything
Use `/docs-generate` to keep documentation current

---

## Next Steps

- Explore [Example Projects](examples/)
- Join the [Community Discord](https://discord.gg/castlewyvern)
- Read [Architecture Documentation](docs/ARCHITECTURE.md)
- Contribute on [GitHub](https://github.com/GenieWeenie/castle-wyvern)

**Happy building! 🏰**
