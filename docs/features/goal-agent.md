# Goal-Based Agent

Give **high-level goals**; Castle Wyvern **plans and executes autonomously**!

## The Difference

| Traditional | Goal-Based |
|-------------|------------|
| `/code "Write a function"` | `/goal "Build a REST API for a todo app"` |
| One task, one agent | Multiple tasks, multiple agents |
| You break down work | AI breaks down work |

## How It Works

1. **Analyze** — Brooklyn analyzes the goal
2. **Plan** — Creates subtasks with dependencies
3. **Assign** — Routes to appropriate clan members
4. **Execute** — Runs tasks sequentially/parallel
5. **Report** — Shows completion summary

## CLI Commands

```bash
# Create a goal
/goal Build a REST API for a todo app

# Execute autonomously
/goal-execute <goal_id>

# Check progress
/goal-status <goal_id>

# List all goals
/goal-list
```

## Goal Types Auto-Detected

- **API Projects** — Design → Schema → Implement → Secure → Test
- **Web Projects** — Design → HTML → CSS → JS → Review
- **Scripts** — Plan → Implement → Error handling → Security
- **Research** — Scope → Gather → Analyze → Summarize
