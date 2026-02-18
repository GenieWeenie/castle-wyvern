# Natural Language Clan Creation

Create new clan members by **describing them in plain English**!

## How It Works

```bash
/clan-create "A DevOps expert who knows Kubernetes and AWS"
```

Castle Wyvern will:

1. Detect specialty (devops, security, data, frontend, etc.)
2. Generate appropriate name (from themed pools)
3. Assign matching emoji and color
4. Create system prompt with expertise
5. Show preview for confirmation

## Example Creation

```
/clan-create "Security specialist for penetration testing"

🎭 NEW CLAN MEMBER PREVIEW
═══════════════════════════
Name:     Cipher
Emoji:    🔒
Role:     Security Specialist
Specialty: Security

System Prompt:
You are Cipher, a cybersecurity specialist...

Type /clan-create-confirm to create this member!
```

## Supported Specialties

- **DevOps** ☁️ — Kubernetes, Docker, AWS, Terraform
- **Security** 🔒 — Pentesting, vulnerabilities, compliance
- **Data** 📊 — SQL, analytics, visualization
- **Frontend** 🎨 — React, CSS, UI/UX
- **Backend** ⚙️ — APIs, databases, architecture
- **Mobile** 📱 — iOS, Android, cross-platform
- **AI** 🧠 — Machine learning, LLMs, models
