# Castle Wyvern - Project Context

## Goal
Verify that Castle Wyvern is production-ready: all 63 commits, 39+ features, 97 tests passing, documentation complete.

## Specs
- 21 original features (Phases 1-4 + Stretch Goals)
- MCP Protocol Support (6 tools, 3 resources, 2 prompts)
- A2A Protocol Support (5 exposed skills)
- Visual Workflow Builder (7+ node types)
- Browser Agent (Jade) - web search, fetch, research
- Natural Language Clan Creation
- Docker Sandbox
- Goal-Based Agent
- Extended Workflow Nodes
- Self-Building Functions (BabyAGI)
- llama.cpp Integration
- CrewAI-Style Backstories
- nanoGPT Integration
- Knowledge Graph (KAG)
- OmniParser Visual Automation
- Agent Coordination Loops
- CLI Experience (auto-complete, history)
- Error Handling & Logging (structured logs)
- Testing & Quality (97 tests)

## Project Structure
- castle_wyvern_cli.py - Main CLI interface
- eyrie/ - Core modules (knowledge_graph, omni_parser, agent_coordination, etc.)
- tests/ - Test suite (97 tests)
- docs/ - Documentation

## Backpressure
Run: pytest tests/ -v
All tests should pass.

## Completion Condition
All 97 tests pass + no critical issues found.
