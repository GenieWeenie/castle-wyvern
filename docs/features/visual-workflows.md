# Visual Workflow Builder

Castle Wyvern includes a **drag-and-drop workflow editor** for creating BMAD workflows visually!

## Features

- **Visual Editor** — Drag and drop nodes to design workflows
- **7 Node Types** — Start, End, Clan Member, BMAD Phase, Decision, Webhook, Delay
- **3 Templates** — Pre-built workflows to get started quickly
- **Live Execution** — Run workflows directly from the editor
- **Import/Export** — Share workflows as JSON

## Built-in Templates

| Template | Description | Nodes |
|----------|-------------|-------|
| **BMAD Full** | Complete Build-Measure-Analyze-Deploy | 6 nodes |
| **Code Review** | Multi-agent parallel review | 7 nodes |
| **Security Audit** | Comprehensive security workflow | 6 nodes |

## Quick Start

```bash
# Open the workflow builder
/workflow-open

# Or create from template
/workflow-template bmad_full
/workflow-template code_review
/workflow-template security_audit

# List workflows
/workflow-list

# Execute a workflow
/workflow-run <workflow_id>
```

## Access

- **URL**: http://localhost:18792/workflows (after `/web-start`)
- **Features**: Drag-and-drop, node palette, templates, execution
