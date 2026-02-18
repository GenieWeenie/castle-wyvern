# Tutorial: Building a Knowledge Graph
## Track Your Project's DNA with Castle Wyvern

---

## What You'll Learn

By the end of this tutorial, you'll:
- ✅ Create entities (people, technologies, projects)
- ✅ Build relationships between them
- ✅ Query with multi-hop reasoning
- ✅ Extract knowledge from text
- ✅ Use logical inference to answer complex questions

---

## Why Knowledge Graph?

### Traditional Search (RAG)
```
You: "What did Lexington suggest?"
System: Searches documents → Finds mentions of Lexington
Problem: Can't connect facts across documents
```

### Knowledge Graph (KAG)
```
You: "What did Lexington suggest for auth that Xanatos reviewed?"
System: 
  1. Finds "Lexington" entity
  2. Follows "suggested" edges
  3. Finds "auth" technology
  4. Finds "Xanatos" entity
  5. Follows "reviewed" edge to auth
  6. Returns: "Lexington suggested OAuth2, Xanatos reviewed it"
```

**The difference:** Knowledge Graph connects facts through relationships.

---

## Part 1: Creating Your First Entities (5 min)

### Step 1: Start Castle Wyvern

```bash
python castle_wyvern_cli.py
```

### Step 2: Check Status

```bash
/kg-status
```

Output:
```
Total Entities: 0
Total Relationships: 0
```

### Step 3: Add Your First Clan Member

```bash
/kg-add-entity "You" ClanMember
```

Output:
```
✅ Added entity: You (ClanMember)
   ID: ClanMember_abc123...
```

### Step 4: Add Technologies

```bash
/kg-add-entity "Python" Technology
/kg-add-entity "FastAPI" Technology
/kg-add-entity "PostgreSQL" Technology
/kg-add-entity "Docker" Technology
```

### Step 5: Add a Project

```bash
/kg-add-entity "My Web App" Project
```

### Step 6: Check Status Again

```bash
/kg-status
```

Output:
```
Total Entities: 5
Total Relationships: 0
Entity Types:
  • ClanMember: 1
  • Technology: 4
  • Project: 1
```

---

## Part 2: Building Relationships (5 min)

### Step 1: Connect You to Technologies

```bash
/kg-add-rel "You" suggested "Python"
/kg-add-rel "You" suggested "FastAPI"
/kg-add-rel "You" suggested "PostgreSQL"
/kg-add-rel "You" suggested "Docker"
```

### Step 2: Connect You to Project

```bash
/kg-add-rel "You" leads "My Web App"
```

### Step 3: Connect Project to Technologies

```bash
/kg-add-rel "My Web App" involves "Python"
/kg-add-rel "My Web App" involves "FastAPI"
/kg-add-rel "My Web App" involves "PostgreSQL"
/kg-add-rel "My Web App" involves "Docker"
```

### Step 4: Check Visualization

```bash
/kg-visualize
```

Output:
```
Entity Types:
  • ClanMember: 1 entities
    Examples: You
  • Technology: 4 entities
    Examples: Python, FastAPI, PostgreSQL, Docker
  • Project: 1 entities
    Examples: My Web App

Relationship Types:
  • suggested: 4 relationships
  • leads: 1 relationships
  • involves: 4 relationships
```

---

## Part 3: Querying the Graph (5 min)

### Query 1: What Did You Suggest?

```bash
/kg-reason "What did I suggest?"
```

Output:
```
Type: suggestion_reasoning
Person: You
Suggestions (4):
  • Python (Technology)
  • FastAPI (Technology)
  • PostgreSQL (Technology)
  • Docker (Technology)
```

### Query 2: What Technologies Does Your Project Use?

```bash
/kg-query "My Web App" involves
```

Output:
```
Paths found: 4
  Path 1: My Web App → involves → Python
  Path 2: My Web App → involves → FastAPI
  Path 3: My Web App → involves → PostgreSQL
  Path 4: My Web App → involves → Docker
```

### Query 3: Multi-Hop Query

```bash
/kg-query You suggested
```

This finds everything you suggested, traversing the "suggested" edge.

---

## Part 4: Adding More Complexity (5 min)

### Step 1: Add More Clan Members

```bash
/kg-add-entity "Lexington" ClanMember
/kg-add-entity "Xanatos" ClanMember
/kg-add-entity "Brooklyn" ClanMember
```

### Step 2: Add Security Technology

```bash
/kg-add-entity "OAuth2" Technology
/kg-add-entity "JWT" Technology
```

### Step 3: Add Relationships

```bash
/kg-add-rel "Lexington" suggested "OAuth2"
/kg-add-rel "Xanatos" reviewed "OAuth2"
/kg-add-rel "Brooklyn" suggested "JWT"
/kg-add-rel "Xanatos" reviewed "JWT"
/kg-add-rel "Lexington" implemented "My Web App"
```

### Step 4: Add to Project

```bash
/kg-add-rel "My Web App" involves "OAuth2"
/kg-add-rel "My Web App" involves "JWT"
```

---

## Part 5: Advanced Queries (5 min)

### Query: What Did Lexington Suggest That Xanatos Reviewed?

```bash
/kg-reason "What did Lexington suggest for authentication?"
```

**Behind the scenes:**
1. Find Lexington entity
2. Follow "suggested" edges → finds OAuth2
3. Find Xanatos entity
4. Check if Xanatos reviewed OAuth2 → Yes!
5. Return: "Lexington suggested OAuth2, Xanatos reviewed it"

### Query: Who Reviewed Security Technologies?

```bash
/kg-reason "Who reviewed OAuth2?"
```

Output:
```
People (1):
  • Xanatos (Red Team)
```

### Query: Find Intersections

```bash
/kg-reason "What involves both security and Brooklyn?"
```

**This finds projects/technologies that involve security and that Brooklyn worked on.**

---

## Part 6: Extracting from Text (5 min)

### Extract from Natural Language

```bash
/kg-extract "Lexington implemented OAuth2 using Python and FastAPI"
```

**What happens:**
- Extracts entities: Lexington, OAuth2, Python, FastAPI
- Creates relationships: Lexington → implemented → OAuth2

### Extract from Meeting Notes

```bash
/kg-extract "Brooklyn suggested Kubernetes for deployment. Xanatos reviewed the plan."
```

**Creates:**
- Entity: Kubernetes (Technology)
- Relationships: Brooklyn → suggested → Kubernetes

---

## Part 7: Real-World Example (10 min)

### Scenario: Building a SaaS Application

**Your team:**
- You: Product owner
- Lexington: Lead developer
- Brooklyn: Architect
- Xanatos: Security lead
- Broadway: Documentation

**Step 1: Add the team**

```bash
/kg-add-entity "SaaS Project" Project
/kg-add-entity "Lexington" ClanMember
/kg-add-entity "Brooklyn" ClanMember
/kg-add-entity "Xanatos" ClanMember
/kg-add-entity "Broadway" ClanMember
```

**Step 2: Add technologies**

```bash
/kg-add-entity "React" Technology
/kg-add-entity "Node.js" Technology
/kg-add-entity "MongoDB" Technology
/kg-add-entity "Stripe" Technology
/kg-add-entity "AWS" Technology
```

**Step 3: Build relationships**

```bash
# Who does what
/kg-add-rel "Brooklyn" leads "SaaS Project"
/kg-add-rel "Lexington" implemented "SaaS Project"
/kg-add-rel "Xanatos" reviewed "SaaS Project"
/kg-add-rel "Broadway" reviewed "SaaS Project"

# Technology decisions
/kg-add-rel "Brooklyn" suggested "React"
/kg-add-rel "Brooklyn" suggested "Node.js"
/kg-add-rel "Brooklyn" suggested "MongoDB"
/kg-add-rel "Brooklyn" suggested "Stripe"
/kg-add-rel "Brooklyn" suggested "AWS"

# Tech used in project
/kg-add-rel "SaaS Project" involves "React"
/kg-add-rel "SaaS Project" involves "Node.js"
/kg-add-rel "SaaS Project" involves "MongoDB"
/kg-add-rel "SaaS Project" involves "Stripe"
/kg-add-rel "SaaS Project" involves "AWS"

# Security review
/kg-add-rel "Xanatos" reviewed "Stripe"
/kg-add-rel "Xanatos" reviewed "AWS"
```

**Step 4: Query your project**

```bash
# What did Brooklyn suggest?
/kg-reason "What did Brooklyn suggest?"

# What technologies does the project use?
/kg-query "SaaS Project" involves

# What did Xanatos review?
/kg-reason "What did Xanatos review?"

# Who worked on the project?
/kg-reason "Who worked on SaaS Project?"
```

---

## Part 8: Schema Customization (Advanced)

### Understanding the Schema

Castle Wyvern comes with predefined entity and relationship types:

**Entity Types:**
- ClanMember - People in your team
- Technology - Tools, frameworks, languages
- Project - Software projects
- Decision - Decisions made
- SecurityIssue - Vulnerabilities, concerns
- Task - Action items

**Relationship Types:**
- suggested - Who suggested what
- reviewed - Who reviewed what
- implemented - Who built what
- involves - What projects involve what
- depends_on - Dependencies
- discovered - Who found security issues
- leads - Who manages/leads

### Custom Schema (Optional)

You can extend the schema by editing `~/.castle_wyvern/knowledge_graph/schema.json`.

---

## Best Practices

### 1. Be Consistent with Names

```bash
# Good - same spelling
/kg-add-entity "OAuth2" Technology
/kg-add-rel "Lexington" suggested "OAuth2"

# Bad - different spellings
/kg-add-entity "OAuth 2.0" Technology  # Different!
```

### 2. Track Decisions

```bash
# Add decisions as entities
/kg-add-entity "Use PostgreSQL" Decision
/kg-add-rel "Brooklyn" suggested "Use PostgreSQL"
/kg-add-rel "You" leads "Use PostgreSQL"
```

### 3. Update Regularly

Make knowledge graph updates part of your workflow:
- After meetings: Extract decisions
- After code reviews: Track who reviewed what
- After deployments: Update project status

### 4. Use Descriptive Names

```bash
# Good
/kg-add-entity "User Authentication Service" Project

# Bad
/kg-add-entity "Auth" Project  # Too vague
```

---

## Common Patterns

### Pattern 1: Track Technology Stack

```bash
/kg-add-entity "MyApp" Project
/kg-add-entity "Python" Technology
/kg-add-entity "Django" Technology
/kg-add-rel "MyApp" involves "Python"
/kg-add-rel "MyApp" involves "Django"
```

### Pattern 2: Track Code Reviews

```bash
/kg-add-entity "Auth Module" Project
/kg-add-rel "Lexington" implemented "Auth Module"
/kg-add-rel "Xanatos" reviewed "Auth Module"
```

### Pattern 3: Track Decisions

```bash
/kg-add-entity "Use Redis for caching" Decision
/kg-add-rel "Brooklyn" suggested "Use Redis for caching"
/kg-add-rel "You" leads "Use Redis for caching"
/kg-add-rel "MyApp" involves "Redis"
```

---

## Troubleshooting

### "Entity not found"

Make sure the entity name matches exactly:
```bash
# Check existing entities
/kg-visualize
```

### "Invalid relationship"

Check the schema for valid relationship types:
```bash
# Valid: suggested, reviewed, implemented, involves, depends_on, discovered, leads
```

### "Knowledge graph is empty"

Start adding entities!
```bash
/kg-add-entity "You" ClanMember
/kg-add-entity "Python" Technology
```

---

## Next Steps

- Try the **Visual Automation** tutorial
- Explore **Self-Building Functions**
- Read the **Complete User Guide**

**Your knowledge graph is now your project's brain! 🧠🏰**
