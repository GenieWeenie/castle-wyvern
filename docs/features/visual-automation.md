# Visual Automation (OmniParser)

**Vision-based GUI control** powered by Microsoft OmniParser!

## What It Does

- **Screenshots → Structured UI Elements** — Parse any GUI visually
- **Identify Interactive Elements** — Buttons, inputs, links, icons
- **Visual Automation** — Click and type without APIs
- **Control Any GUI** — Web, desktop, mobile through vision

## How It Works

```
1. Capture Screenshot
        ↓
2. OmniParser analyzes image
        ↓
3. Detects UI elements with coordinates
        ↓
4. Execute actions (click, type) visually
```

## Example Workflow

```bash
# Analyze the screen
/visual-scan

# Click the submit button
/visual-click 'submit button'

# Type into username field
/visual-type 'myuser' 'username field'
```

## Visual Browser Agent

```bash
/visual-browser-start
/visual-browser-task 'Click the login button'
/visual-browser-task 'Type admin in the username field'
/visual-browser-task 'Click submit'
/visual-browser-end
```

## CLI Commands

```bash
/visual-status              # Check visual automation status
/visual-scan                # Analyze current screen
/visual-click <target>      # Click element by description
/visual-type <text> [field] # Type text
/visual-browser-start       # Start visual browser
/visual-browser-task <task> # Execute visual task
/visual-browser-end         # End browser session
```
