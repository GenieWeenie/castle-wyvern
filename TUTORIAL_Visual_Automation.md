# Tutorial: Visual Automation with OmniParser
## Control Any GUI Through Screenshots

---

## What You'll Learn

By the end of this tutorial, you'll:
- ✅ Analyze screenshots to detect UI elements
- ✅ Click buttons and interact with forms visually
- ✅ Automate web browsing visually
- ✅ Build visual automation workflows

---

## What is Visual Automation?

Traditional automation requires APIs or DOM access:
```python
# Traditional (requires API access)
driver.find_element(By.ID, "submit-button").click()
```

Visual automation works through screenshots:
```python
# Visual (works with any GUI)
1. Take screenshot
2. AI detects "Submit" button at (340, 250)
3. Click at coordinates (340, 250)
```

**The difference:** Visual automation works with **anything** you can see.

---

## Part 1: Basic Screen Analysis (5 min)

### Step 1: Start Castle Wyvern

```bash
python castle_wyvern_cli.py
```

### Step 2: Check Visual Status

```bash
/visual-status
```

Output:
```
👁️ Visual Automation (OmniParser)
Available: ✅ Yes
Screen Analyzed: ❌ No
Elements on Screen: 0
Action History: 0
```

### Step 3: Analyze Your Screen

```bash
/visual-scan
```

Output:
```
✅ Screen analyzed!
   Elements found: 6
   Interactive: 5

Screen Analysis:
==================================================
Interactive Elements (5):
  • button: 'Submit' at (160, 220)
  • button: 'Cancel' at (300, 220)
  • input: 'Username' at (250, 117)
  • input: 'Password' at (250, 167)
  • link: 'Forgot Password?' at (175, 270)
```

**What just happened?**
- Castle Wyvern captured your screen
- OmniParser analyzed the image
- Detected buttons, inputs, and links
- Identified their types and coordinates

---

## Part 2: Clicking Elements (5 min)

### Click a Button

```bash
/visual-click "submit button"
```

Output:
```
✅ Would click at (160, 220)
```

**Behind the scenes:**
1. Finds element with type "button" and text "Submit"
2. Gets center coordinates: (160, 220)
3. Would execute click at that location

### Click by Partial Text

```bash
/visual-click "cancel"
```

Works even if you don't type the full "Cancel button".

### Try Different Targets

```bash
/visual-click "login"
/visual-click "sign up"
/visual-click "menu"
```

---

## Part 3: Typing Text (5 min)

### Type Into a Field

```bash
/visual-type "myusername" "username field"
```

Output:
```
✅ Would type: myusername
```

**Behind the scenes:**
1. Finds input field with text "Username"
2. Gets center coordinates
3. Would click field, then type text

### Type Without Specifying Field

```bash
/visual-type "password123"
```

Uses currently focused field.

### Combine Click and Type

```bash
# Click username field
/visual-click "username field"

# Type username
/visual-type "john_doe"

# Click password field
/visual-click "password field"

# Type password
/visual-type "secret123"

# Click submit
/visual-click "submit button"
```

---

## Part 4: Visual Browser Agent (10 min)

### Start a Session

```bash
/visual-browser-start
```

Output:
```
✅ Visual browser session started!
   Elements detected: 8

Screen Analysis:
==================================================
Interactive Elements (8):
  • button: 'Sign In' at (340, 280)
  • input: 'Email' at (340, 150)
  • input: 'Password' at (340, 200)
  • link: 'Sign Up' at (340, 320)
  • link: 'Forgot Password?' at (340, 340)
```

### Execute Tasks

```bash
/visual-browser-task "Click the sign in button"
```

Output:
```
✅ Task executed!
   Action: click
   Target: sign in button
   Coordinates: (340, 280)
```

### Fill Out Forms

```bash
/visual-browser-task "Type john@example.com in the email field"
/visual-browser-task "Type secret123 in the password field"
/visual-browser-task "Click the sign in button"
```

### Navigate Websites

```bash
# On a search page
/visual-browser-task "Type 'Python tutorials' in the search box"
/visual-browser-task "Click the search button"

# On search results
/visual-browser-task "Click the first result"

# Read content
/visual-browser-task "Scroll down"
/visual-browser-task "Click the next page link"
```

### End Session

```bash
/visual-browser-end
```

Output:
```
✅ Visual browser session ended!
   Actions performed: 5
```

---

## Part 5: Real-World Example (10 min)

### Scenario: Automating a Login Form

**Your goal:** Log into a website automatically

**Step 1: Navigate to the page**
- Open your browser
- Go to the login page
- Keep it visible on screen

**Step 2: Analyze the screen**

```bash
/visual-browser-start
```

**Step 3: Identify elements**

Look at the output. You should see:
```
  • input: 'Email' at (x, y)
  • input: 'Password' at (x, y)
  • button: 'Log In' at (x, y)
```

**Step 4: Execute the login sequence**

```bash
# Fill email
/visual-browser-task "Type myemail@example.com in the email field"

# Fill password
/visual-browser-task "Type mypassword123 in the password field"

# Click login
/visual-browser-task "Click the log in button"
```

**Step 5: Verify success**

Look at your browser - you should be logged in!

**Step 6: End session**

```bash
/visual-browser-end
```

---

## Part 6: Advanced Techniques

### Handling Dynamic Content

When content changes, re-scan:

```bash
# Initial page
/visual-scan

# Click something that changes page
/visual-click "next page"

# Re-scan to see new elements
/visual-scan
```

### Precise Targeting

Use more specific descriptions:

```bash
# Less specific
/visual-click "button"

# More specific
/visual-click "submit button"

# Even more specific
/visual-click "blue submit button"
```

### Working with Lists

```bash
# Click first item
/visual-click "first item"

# Click by position
/visual-click "item at top"
/visual-click "item at bottom"
```

---

## Best Practices

### 1. Always Scan First

```bash
# Good
/visual-scan
/visual-click "submit button"

# Bad - might not find element
/visual-click "submit button"
```

### 2. Use Specific Descriptions

```bash
# Good
/visual-click "primary submit button"

# Bad - ambiguous
/visual-click "button"
```

### 3. Handle Errors

If element not found:
```bash
/visual-click "submit"
→ ❌ Target not found on screen

# Try re-scanning
/visual-scan
/visual-click "submit button"
```

### 4. Test on Static Screens First

Practice on stable pages before dynamic content.

---

## Common Patterns

### Pattern 1: Form Filling

```bash
/visual-browser-start
/visual-browser-task "Type name in the name field"
/visual-browser-task "Type email in the email field"
/visual-browser-task "Type message in the message field"
/visual-browser-task "Click the submit button"
/visual-browser-end
```

### Pattern 2: Navigation

```bash
/visual-browser-start
/visual-browser-task "Click the menu button"
/visual-browser-task "Click the settings link"
/visual-browser-task "Click the profile tab"
/visual-browser-task "Click the edit button"
/visual-browser-end
```

### Pattern 3: Search and Extract

```bash
/visual-browser-start
/visual-browser-task "Type 'Python documentation' in the search field"
/visual-browser-task "Click the search button"
/visual-browser-task "Click the first result"
# Now use /browse to extract content
/visual-browser-end
```

---

## Troubleshooting

### "Target not found on screen"

**Cause:** Element not detected or description doesn't match

**Solutions:**
1. Re-scan the screen: `/visual-scan`
2. Check exact text: `/visual-status` shows detected elements
3. Use different description: Try "submit" instead of "submit button"

### "Screen not analyzed yet"

**Cause:** Trying to click before scanning

**Solution:**
```bash
/visual-scan  # Always do this first
/visual-click "target"
```

### Elements not detected

**Cause:** Element might be:
- Too small
- Not clearly visible
- Part of a complex UI

**Solutions:**
- Scroll to make element visible
- Zoom in
- Try different description

### Visual automation not available

**Cause:** OmniParser not installed or configured

**Solution:**
```bash
# Current version uses simulation
# For real OmniParser:
pip install omniparser
# Download OmniParser models
```

---

## Combining with Other Features

### Visual + Browser Agent

```bash
# Research a topic
/research "Python async best practices"

# Get search results
# Open a result in browser
# Use visual automation to navigate
/visual-browser-start
/visual-browser-task "Click the documentation link"
/visual-browser-task "Scroll down to examples"
/visual-browser-end
```

### Visual + Knowledge Graph

```bash
# After visual automation session
/kg-extract "Successfully logged into AWS console using visual automation"
→ Creates entities and relationships

# Track what you accessed
/kg-add-entity "AWS Console" Technology
/kg-add-rel "You" accessed "AWS Console"
```

### Visual + Docker Sandbox

```bash
# Test visual automation code safely
/sandbox-exec ""
""
# Python code that uses visual automation
from visual_automation import VisualAutomation

va = VisualAutomation()
va.analyze_screen()
va.click('submit button')
"""
"""
```

---

## Limitations

### Current Limitations

1. **Simulation Mode** - Current version simulates OmniParser (for demo)
2. **2D Only** - Works with flat screenshots, not 3D
3. **Static Analysis** - Best for stable UIs, not rapidly changing content
4. **Single Screen** - Analyzes one screen at a time

### Future Improvements

- Real OmniParser API integration
- Video stream analysis
- Multi-screen support
- Mobile device automation

---

## Exercises

### Exercise 1: Login Form (Easy)

1. Open any login page
2. Use `/visual-browser-start`
3. Fill in username and password
4. Click login
5. Use `/visual-browser-end`

### Exercise 2: Form Completion (Medium)

1. Find a contact form
2. Fill all fields using visual automation
3. Submit the form
4. Verify success message

### Exercise 3: Navigation Flow (Hard)

1. Start on a homepage
2. Navigate to a specific page through menus
3. Fill out a form
4. Submit and verify
5. Navigate back to homepage

---

## Next Steps

- Try the **Knowledge Graph** tutorial
- Explore **Self-Building Functions**
- Read the **Complete User Guide**

**You can now automate any GUI visually! 👁️🏰**
