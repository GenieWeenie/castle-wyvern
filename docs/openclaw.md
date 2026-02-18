# OpenClaw Integration

Castle Wyvern works seamlessly with [OpenClaw](https://openclaw.ai) — the multi-channel AI assistant platform.

## Why Use Them Together?

| OpenClaw | Castle Wyvern | Combined Power |
|----------|--------------|----------------|
| Multi-channel messaging (Telegram, WhatsApp, Discord) | Multi-agent technical execution | Chat anywhere, execute everywhere |
| Always-on availability | Deep technical workflows | Simple questions → quick answers, Complex tasks → deep execution |
| Conversation continuity | Code generation & review | Natural discussion → production code |
| Skills system | Plugin system + MCP/A2A | Extensible on both sides |

## Integration Methods

### 1. Castle Wyvern as OpenClaw Skill

Install Castle Wyvern as an OpenClaw skill and use the clan from any channel:

```
User (Telegram): "Write a Python function to calculate Fibonacci"
OpenClaw: Delegates to Castle Wyvern
Lexington: Generates the code
OpenClaw: Sends code back to user on Telegram
```

### 2. Hybrid Mode

- **OpenClaw** handles: Scheduling, reminders, quick lookups, conversation
- **Castle Wyvern** handles: Code generation, architecture planning, security reviews, complex workflows

### 3. Shared Infrastructure

Both can share:

- **Memory** (Grimoorum) — Conversation history persists across both
- **Configuration** (`.env` files) — Same API keys, same providers
- **Docker** — Shared sandbox for safe code execution

## Setup

```bash
# 1. Install OpenClaw
npm install -g openclaw

# 2. Install Castle Wyvern skill for OpenClaw
openclaw skills install castle-wyvern

# 3. Configure both to use the same .env
# Both read AI_API_KEY, OLLAMA_HOST, etc.

# 4. Start using!
# Message your OpenClaw bot: "Ask Lexington to review this code"
```

## Example Workflows

**Code Review Pipeline:**

```
You (WhatsApp) → OpenClaw → Castle Wyvern (Xanatos reviews)
→ Result back to WhatsApp with security analysis
```

**Architecture Planning:**

```
You (Discord): "Plan a microservices architecture for e-commerce"
OpenClaw → Castle Wyvern (Brooklyn architects + Goliath approves)
→ Full architecture document in Discord
```

**Continuous Monitoring:**

```
OpenClaw cron → Castle Wyvern (Bronx monitors) → Alert via Telegram when issues found
```
