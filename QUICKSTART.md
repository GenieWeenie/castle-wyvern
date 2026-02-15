# Castle Wyvern - Quick Start Tutorial
## 5 Minutes to Your First AI-Powered Project

---

## Step 1: Installation (1 minute)

```bash
# Clone Castle Wyvern
git clone https://github.com/GenieWeenie/castle-wyvern.git
cd castle-wyvern

# Install dependencies
pip install -r requirements.txt

# Configure API keys
cp .env.example .env
# Edit .env and add your keys:
# ZAI_API_KEY=your_key_here
# Or: OPENAI_API_KEY=your_key_here
```

---

## Step 2: Launch Castle Wyvern (30 seconds)

```bash
python castle_wyvern_cli.py
```

You'll see the Castle Wyvern banner and prompt:
```
🏰 CASTLE WYVERN v1.0+

"We are defenders of the night!"
"We are Gargoyles!"

👤 You:
```

---

## Step 3: Your First Interaction (1 minute)

Try asking a question:

```bash
👤 You: ask What is Python?
🎯 Intent: ask (98% confidence)
🛡️  Routed to: 🦁 Goliath

🦁 Goliath:
Python is a high-level, interpreted programming language known for 
its readability and versatility. It supports multiple paradigms...
```

**What just happened?**
1. You asked a question
2. Castle Wyvern detected the intent (question answering)
3. Routed to Goliath (best for general knowledge)
4. Goliath provided a comprehensive answer

---

## Step 4: Request Code (1 minute)

Let's get some code from Lexington:

```bash
👤 You: code Write a function to reverse a string
🎯 Intent: code (99% confidence)  
🛡️  Routed to: 🔧 Lexington

🔧 Lexington:
def reverse_string(s):
    """Reverse a string."""
    return s[::-1]

# Example usage:
print(reverse_string("Hello"))  # Output: olleH
```

**Try variations:**
- `code Create a class for a Bank Account`
- `code Write a REST API endpoint in FastAPI`
- `code Build a React component for a login form`

---

## Step 5: Get a Code Review (1 minute)

Paste some code and get Xanatos to review it:

```bash
👤 You: review
[paste your code here]
🎯 Intent: review (97% confidence)
🛡️  Routed to: 🎭 Xanatos

🎭 Xanatos:
Security Analysis:
- ⚠️ Line 15: SQL injection risk detected
- ✅ Line 23: Proper input validation
- 💡 Suggestion: Use parameterized queries

Potential vulnerabilities:
1. User input not sanitized before SQL query
2. No rate limiting on authentication endpoint

Recommendations:
- Use SQLAlchemy ORM
- Add input validation middleware
- Implement rate limiting
```

---

## Step 6: Create Architecture Plan (1 minute)

Ask Brooklyn for architectural guidance:

```bash
👤 You: plan Design a microservices architecture for an e-commerce app
🎯 Intent: plan (96% confidence)
🛡️  Routed to: 🎯 Brooklyn

🎯 Brooklyn:
Architecture Plan: E-Commerce Microservices

1. Service Decomposition:
   - User Service: Authentication, profiles
   - Product Service: Catalog, inventory
   - Order Service: Cart, checkout
   - Payment Service: Transactions
   - Notification Service: Email, SMS

2. Communication:
   - Async: Message queue (RabbitMQ/Kafka)
   - Sync: gRPC for internal, REST for external

3. Data Management:
   - Each service has its own database
   - CQRS for read-heavy operations
   - Event sourcing for order history

4. Deployment:
   - Docker containers
   - Kubernetes orchestration
   - CI/CD with GitHub Actions
```

---

## Step 7: Try the Knowledge Graph (2 minutes)

Track your project decisions:

```bash
# Add entities
/kg-add-entity "You" ClanMember
/kg-add-entity "FastAPI" Technology
/kg-add-entity "My Project" Project

# Add relationships
/kg-add-rel "You" suggested "FastAPI"
/kg-add-rel "You" leads "My Project"
/kg-add-rel "My Project" involves "FastAPI"

# Query your knowledge
/kg-reason "What technology did I suggest?"
→ "You suggested FastAPI"

/kg-query You suggested
→ Shows everything you've suggested
```

---

## Step 8: Visual Automation Demo (2 minutes)

Try visual GUI control:

```bash
# Analyze your screen
/visual-scan
→ Analyzes current screenshot
→ Shows detected UI elements

# Try clicking (simulated in demo)
/visual-click "submit button"
→ Would click at coordinates (x, y)

# Type into field
/visual-type "hello world" "input field"
→ Would type into detected field
```

---

## Step 9: Start a Workflow (2 minutes)

Use BMAD methodology:

```bash
# Create a workflow
workflow-create my_first_api

# Add steps
workflow-add build "Design API endpoints"
workflow-add measure "Write tests"
workflow-add analyze "Load testing"
workflow-add deploy "Docker setup"

# Execute
workflow-run my_first_api
```

---

## What's Next?

### Explore More Features

**Browser Agent:**
```bash
/search "Python best practices"
/browse https://docs.python.org
/research "Latest Python web frameworks"
```

**Docker Sandbox:**
```bash
/sandbox-status
/sandbox-exec "print('Hello from Docker!')"
/sandbox-lang javascript
/sandbox-exec "console.log('Hello JS')"
```

**Goal-Based Agent:**
```bash
/goal "Build a CLI tool in Python"
/goal-execute <goal_id>
/goal-status <goal_id>
```

**Self-Building Functions:**
```bash
/function-create "Fetch weather from API"
/function-list
/function-show <function_name>
```

### Read Full Documentation

- [Complete User Guide](USER_GUIDE.md)
- [API Reference](docs/API.md)
- [Architecture Overview](docs/ARCHITECTURE.md)

### Join the Community

- GitHub: https://github.com/GenieWeenie/castle-wyvern
- Discord: [Coming Soon]

---

## Common Commands Cheat Sheet

| Command | Purpose | Routes To |
|---------|---------|-----------|
| `ask` | General questions | Goliath |
| `code` | Code generation | Lexington |
| `review` | Security/code review | Xanatos |
| `plan` | Architecture planning | Brooklyn |
| `summarize` | Summarize content | Broadway |
| `help` | Show all commands | - |
| `status` | System status | - |
| `/kg-reason` | Knowledge graph query | - |
| `/visual-scan` | Analyze screen | - |
| `/sandbox-exec` | Execute code safely | - |

---

## Tips for Success

1. **Be specific** - "Create a Python function to validate email" works better than "Write code"
2. **Use clan specialties** - Lexington for code, Xanatos for security, Brooklyn for architecture
3. **Build your knowledge graph** - Track decisions and technologies from day one
4. **Use workflows** - Break complex projects into BMAD phases
5. **Experiment** - Try different commands and features!

---

**You're ready to build amazing things with Castle Wyvern! 🏰🔥**

For help: Type `help` in the CLI or check the [User Guide](USER_GUIDE.md)
