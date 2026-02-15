# Castle Wyvern Configuration

## Environment Variables

### AI Providers (Required - at least one)
```bash
# Z.ai (Primary - recommended)
ZAI_API_KEY=your_zai_key_here

# OpenAI (Fallback)
OPENAI_API_KEY=your_openai_key_here

# Ollama (Local - optional)
OLLAMA_HOST=http://localhost:11434
```

### Integrations (Optional)
```bash
# Slack
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...

# Discord
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...

# Email (SMTP)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_FROM=your_email@gmail.com
```

### Security (Optional)
```bash
# Encryption key (auto-generated if not set)
CASTLE_WYVERN_ENCRYPTION_KEY=your_secret_key

# API key for external access
CASTLE_WYVERN_API_KEY=your_api_key
```

## Configuration Files

### MCP Client Configuration
Create `~/.config/claude/claude_desktop_config.json`:
```json
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

### A2A Agent Discovery
Castle Wyvern exposes its agent card at:
```
http://localhost:18795/.well-known/agent.json
```

## Ports Used

| Service | Port | Purpose |
|---------|------|---------|
| CLI | N/A | Interactive terminal |
| REST API | 18791 | HTTP API endpoints |
| Web Dashboard | 18792 | Browser UI |
| Webhook Server | 18793 | Incoming webhooks |
| MCP Server | stdio | MCP protocol |
| A2A Server | 18795 | Agent-to-Agent protocol |

## Data Storage

All data stored in `~/.castle_wyvern/`:
```
~/.castle_wyvern/
├── config.json           # User configuration
├── api_keys.json         # API keys
├── .key                  # Encryption key
├── audit/                # Audit logs
│   └── audit_YYYY-MM-DD.jsonl
├── workflows/            # Saved workflows
├── vector_memory/        # Semantic memory
│   └── vector_memory.pkl
├── plugins/              # Plugin directory
│   └── example_plugin/
├── sessions/             # CLI sessions
└── history.json          # Command history
```

## Getting Started

1. **Clone and setup:**
   ```bash
   git clone https://github.com/GenieWeenie/castle-wyvern.git
   cd castle-wyvern
   pip install -r requirements.txt
   ```

2. **Configure AI provider:**
   ```bash
   export ZAI_API_KEY=your_key
   # or
   export OPENAI_API_KEY=your_key
   ```

3. **Run Castle Wyvern:**
   ```bash
   python castle_wyvern_cli.py
   ```

4. **Try commands:**
   ```
   ask What is Python?
   code Write a fibonacci function
   /web-start
   /mcp-start
   /workflow-template bmad_full
   ```
