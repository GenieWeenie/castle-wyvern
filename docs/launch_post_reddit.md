# Castle Wyvern - Multi-Agent AI Infrastructure (Now Open Source!)

Hey r/selfhosted and r/LocalLLaMA!

I've been building **Castle Wyvern** - a multi-agent AI infrastructure that's designed to run locally-first with Ollama, but can fall back to cloud APIs when needed.

## What Makes It Different?

Instead of chatting with one AI model, you have **10 specialized agents** ("The Manhattan Clan") that each have their own expertise:

- **Lexington** writes code
- **Xanatos** does security reviews  
- **Brooklyn** handles architecture
- **Broadway** writes docs
- **Hudson** manages long-term memory
- **Bronx** monitors for issues
- **Jade** browses the web autonomously
- **Goliath** orchestrates everything

Plus 3 more with specific roles.

## Local-First Design

- **Primary**: Ollama (local LLMs)
- **Fallback**: Z.ai or OpenAI
- **All data stays local** unless you choose otherwise
- **Docker sandbox** for safe code execution

## Cool Features

🔹 **Visual Workflow Builder** - Drag-and-drop workflows  
🔹 **Knowledge Graph** - Entities and relationships between everything  
🔹 **BabyAGI-style** - Create tools dynamically from descriptions  
🔹 **Visual Automation** - Screen parsing + GUI control  
🔹 **nanoGPT Training** - Train custom models for your agents  
🔹 **MCP & A2A Protocols** - Works with other AI frameworks  

## Try It

```bash
git clone https://github.com/GenieWeenie/castle-wyvern.git
cd castle-wyvern
pip install -r requirements.txt
python castle_wyvern_cli.py
```

You'll get a beautiful terminal dashboard with all 10 agents.

## Why I Built This

I was tired of general-purpose AI that was okay at everything but great at nothing. I wanted specialists that could collaborate like a real team.

Also works as an [OpenClaw](https://openclaw.ai) skill if you want to use it from Telegram/WhatsApp/Discord.

**GitHub**: https://github.com/GenieWeenie/castle-wyvern

MIT Licensed | 73 commits | 98 tests passing

Would love your thoughts! Particularly:
- Is the multi-agent approach actually useful?
- What local models work best with it?
- What integrations would you want?
