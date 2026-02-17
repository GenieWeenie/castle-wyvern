# Docker Sandbox

**Secure code execution** in isolated Docker containers!

## Safety Features

- 🔒 **Isolated containers** — Code runs in its own environment
- 🔒 **Read-only filesystem** — Can't modify container
- 🔒 **Network isolation** — Optional (can enable for web requests)
- 🔒 **Resource limits** — CPU and memory constraints
- 🔒 **Auto-cleanup** — Containers removed after execution
- 🔒 **Time limits** — Prevents infinite loops

## Supported Languages

- Python (3.11)
- JavaScript/Node (18)
- Bash (Alpine)
- Go (1.21)
- Rust (1.70)
- Java (OpenJDK 17)

## CLI Commands

```bash
# Check Docker status
/sandbox-status

# Execute Python code
/sandbox-exec "print('Hello World')"

# Switch language
/sandbox-lang javascript
/sandbox-exec "console.log('Hello from Node')"

# List running containers
/sandbox-list

# Clean up all containers
/sandbox-cleanup
```

## Security Note

Without Docker installed, code execution is **disabled** for security. Install Docker to enable sandbox execution.
