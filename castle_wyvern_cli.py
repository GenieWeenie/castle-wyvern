"""
Castle Wyvern Rich CLI Interface
Beautiful terminal UI with Rich library.
"""

import os
import sys
import time
from typing import Optional, Dict, List
from datetime import datetime

# Rich imports
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.spinner import Spinner
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.align import Align
from rich import box

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eyrie.phoenix_gate import PhoenixGate
from eyrie.intent_router import IntentRouter, IntentType
from eyrie.document_ingestion import DocumentIngestion
from eyrie.node_manager import NodeManager
from eyrie.auto_discovery import AutoDiscoveryService
from eyrie.api_server import CastleWyvernAPI
from eyrie.web_dashboard import WebDashboard
from eyrie.plugin_system import PluginManager
from eyrie.monitoring import MonitoringService
from eyrie.cli_improvements import CLIImprovements
from eyrie.integrations import IntegrationManager
from eyrie.security import SecurityManager
from eyrie.advanced_ai import AdvancedAIManager
from eyrie.performance import PerformanceManager
from eyrie.documentation import DocumentationGenerator
from eyrie.mcp_server import CastleWyvernMCPServer
from eyrie.a2a_protocol import A2AIntegration
from eyrie.workflow_builder import WorkflowManager, WorkflowExecutor
from eyrie.enhanced_memory import EnhancedGrimoorum
from eyrie.browser_agent import BrowserAgent
from eyrie.clan_creator import ClanCreator
from eyrie.docker_sandbox import DockerSandbox, SafeCodeExecutor
from eyrie.goal_agent import GoalBasedAgent
from eyrie.workflow_nodes import NODE_TYPES
from grimoorum.memory_manager import GrimoorumV2
from bmad.bmad_workflow import BMADWorkflow


# Castle Wyvern Theme Configuration
THEME = {
    "primary": "bright_cyan",
    "secondary": "bright_blue",
    "success": "bright_green",
    "warning": "bright_yellow",
    "error": "bright_red",
    "info": "bright_white",
    "muted": "dim",
    "border": "cyan"
}


class ClanMember:
    """Represents a clan member with UI state."""
    def __init__(self, name: str, emoji: str, role: str, color: str):
        self.name = name
        self.emoji = emoji
        self.role = role
        self.color = color
        self.status = "Ready"
        self.current_task = "Standing by"
        self.last_active = datetime.now()
    
    def set_busy(self, task: str):
        """Set member as busy with a task."""
        self.status = "Busy"
        self.current_task = task
        self.last_active = datetime.now()
    
    def set_ready(self):
        """Set member as ready."""
        self.status = "Ready"
        self.current_task = "Standing by"
        self.last_active = datetime.now()


class CastleWyvernCLI:
    """
    Rich CLI interface for Castle Wyvern.
    
    Features:
    - Beautiful themed dashboard
    - Live clan status
    - Phoenix Gate monitor
    - Interactive command loop
    """
    
    def __init__(self):
        self.console = Console()
        self.phoenix_gate = PhoenixGate()
        self.intent_router = IntentRouter(use_ai_classification=True)
        self.grimoorum = GrimoorumV2()
        
        # Enhanced Memory (Improvement #4)
        self.enhanced_memory = EnhancedGrimoorum(self.grimoorum)
        
        self.bmad = BMADWorkflow(self.console, self.phoenix_gate, self.grimoorum)
        self.documents = DocumentIngestion()
        self.nodes = NodeManager()
        
        # Feature 11: Auto-Discovery
        self.auto_discovery = None
        
        # Feature 12: REST API
        self.api_server = None
        
        # Feature 13: Web Dashboard
        self.web_dashboard = None
        
        # Feature 14: Plugin System
        self.plugin_manager = PluginManager(
            phoenix_gate=self.phoenix_gate,
            grimoorum=self.grimoorum
        )
        # Auto-load plugins on startup
        self.plugin_manager.load_all_plugins()
        
        # Feature 15: Monitoring Service
        self.monitoring = MonitoringService(
            phoenix_gate=self.phoenix_gate,
            grimoorum=self.grimoorum,
            plugins=self.plugin_manager
        )
        
        # Feature 16: CLI Improvements
        self.cli_improvements = CLIImprovements()
        
        # Feature 17: Integration Manager
        self.integrations = IntegrationManager()
        
        # Feature 18: Security Manager
        self.security = SecurityManager()
        
        # Feature 19: Advanced AI
        self.advanced_ai = AdvancedAIManager()
        
        # Feature 20: Performance Manager
        self.performance = PerformanceManager()
        
        # Feature 21: Documentation Generator
        self.documentation = DocumentationGenerator()
        
        # MCP Server
        self.mcp_server: Optional[CastleWyvernMCPServer] = None
        
        # A2A Protocol
        self.a2a: Optional[A2AIntegration] = None
        
        # Visual Workflow Builder
        self.workflow_manager = WorkflowManager()
        self.workflow_executor = WorkflowExecutor()
        
        # Browser Agent (Competitive Research Feature)
        self.browser = BrowserAgent()
        
        # Clan Creator (Competitive Research Feature)
        self.clan_creator = ClanCreator(existing_members=list(self.clan.keys()))
        self.pending_clan_creation = None  # Store preview before confirmation
        
        # Docker Sandbox (Competitive Research Feature)
        self.sandbox = DockerSandbox()
        self.safe_executor = SafeCodeExecutor()
        
        # Goal-Based Agent (Competitive Research Feature #4)
        self.goal_agent = None  # Initialized lazily
        
        # Extended workflow nodes available
        self.extended_workflow_nodes = list(NODE_TYPES.keys())
        
        # Initialize clan members
        self.clan = {
            "goliath": ClanMember("Goliath", "🦁", "Leader", "bright_yellow"),
            "lexington": ClanMember("Lexington", "🔧", "Technician", "bright_cyan"),
            "brooklyn": ClanMember("Brooklyn", "🎯", "Strategist", "bright_red"),
            "broadway": ClanMember("Broadway", "📜", "Chronicler", "bright_green"),
            "hudson": ClanMember("Hudson", "📚", "Archivist", "bright_blue"),
            "bronx": ClanMember("Bronx", "🐕", "Watchdog", "bright_magenta"),
            "elisa": ClanMember("Elisa", "🌉", "Bridge", "bright_white"),
            "xanatos": ClanMember("Xanatos", "🎭", "Red Team", "bright_black"),
            "demona": ClanMember("Demona", "🔥", "Failsafe", "bright_red"),
            "jade": ClanMember("Jade", "🌐", "Web Surfer", "bright_blue"),
        }
        
        self.running = True
        self.command_history = []
    
    def print_banner(self):
        """Print Castle Wyvern banner."""
        banner = """
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║                    🏰 CASTLE WYVERN v0.2.0                       ║
║                                                                  ║
║           "We are defenders of the night!"                       ║
║                     "We are Gargoyles!"                          ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
        """
        self.console.print(banner, style=THEME["primary"])
    
    def create_phoenix_gate_panel(self) -> Panel:
        """Create Phoenix Gate status panel."""
        try:
            health = self.phoenix_gate.health_check()
            
            if health["status"] == "ONLINE":
                status_icon = "🟢"
                status_style = THEME["success"]
            elif health["status"] == "DEGRADED":
                status_icon = "🟡"
                status_style = THEME["warning"]
            else:
                status_icon = "🔴"
                status_style = THEME["error"]
            
            content = f"""
{status_icon} Status: [{status_style}]{health['status']}[/{status_style}]
📡 Model: {health.get('model', 'Unknown')}
🔄 Providers: {len([p for p in health.get('providers', []) if p['status'] in ['ONLINE', 'AVAILABLE']])} online
            """.strip()
            
        except Exception as e:
            content = f"🔴 Status: [red]ERROR[/red]\n⚠️  {str(e)}"
        
        return Panel(
            content,
            title="⚔️  PHOENIX GATE",
            border_style=THEME["border"],
            box=box.ROUNDED
        )
    
    def create_circuit_breaker_panel(self) -> Panel:
        """Create circuit breaker status panel."""
        try:
            stats = self.phoenix_gate.get_stats()
            
            lines = []
            for name, data in stats.items():
                state = data['state']
                failures = data['failure_count']
                
                if state == "CLOSED":
                    icon = "🟢"
                    style = THEME["success"]
                elif state == "HALF_OPEN":
                    icon = "🟡"
                    style = THEME["warning"]
                else:
                    icon = "🔴"
                    style = THEME["error"]
                
                lines.append(f"{icon} [{style}]{name.replace('_', ' ').title()}[/{style}]: {state} ({failures} failures)")
            
            content = "\n".join(lines) if lines else "No circuit breakers active"
            
        except Exception:
            content = "Circuit breaker status unavailable"
        
        return Panel(
            content,
            title="🛡️  CIRCUIT BREAKERS",
            border_style=THEME["border"],
            box=box.ROUNDED
        )
    
    def create_clan_table(self) -> Table:
        """Create clan members status table."""
        table = Table(
            title="👥 THE MANHATTAN CLAN",
            box=box.ROUNDED,
            border_style=THEME["border"],
            header_style=THEME["primary"],
            expand=True
        )
        
        table.add_column("Agent", style=THEME["info"], width=15)
        table.add_column("Status", width=12)
        table.add_column("Role", style=THEME["muted"], width=15)
        table.add_column("Current Task", style=THEME["info"])
        
        for member in self.clan.values():
            if member.status == "Ready":
                status = f"[green]● {member.status}[/green]"
            else:
                status = f"[yellow]● {member.status}[/yellow]"
            
            table.add_row(
                f"{member.emoji} {member.name}",
                status,
                member.role,
                member.current_task
            )
        
        return table
    
    def create_dashboard(self) -> Layout:
        """Create full dashboard layout."""
        layout = Layout()
        
        # Split into top and bottom
        layout.split_column(
            Layout(name="top", size=8),
            Layout(name="main")
        )
        
        # Top: Phoenix Gate and Circuit Breakers side by side
        layout["top"].split_row(
            Layout(self.create_phoenix_gate_panel()),
            Layout(self.create_circuit_breaker_panel())
        )
        
        # Main: Clan table
        layout["main"].update(self.create_clan_table())
        
        return layout
    
    def print_dashboard(self):
        """Print the full dashboard."""
        self.console.print(self.create_dashboard())
    
    def print_help(self):
        """Print help information."""
        help_text = """
# Available Commands

## Clan Commands
- `ask <question>` - Ask the clan a question
- `code <description>` - Request code from Lexington
- `review <description>` - Request code review from Xanatos
- `summarize <text>` - Request summary from Broadway
- `plan <description>` - Request architecture from Brooklyn

## BMAD Workflow Commands
- `/spec <description>` - Quick technical spec (Goliath + Brooklyn)
- `/build <description>` - Implementation (Lexington + Broadway)
- `/review <code>` - Code review (Xanatos + Demona)
- `/brief <description>` - Full product brief (All clan)

## Document Commands
- `/ingest <filepath>` - Add a document to the library
- `/docs` - List all ingested documents
- `/search <query>` - Search document contents

## Node Commands
- `/nodes` - List all Stone nodes
- `/node-add <name> <host>` - Register a new node
- `/tasks` - List distributed tasks

## Auto-Discovery Commands (Feature 11)
- `/discover-start` - Start mDNS node discovery
- `/discover-stop` - Stop node discovery
- `/discover-status` - Show discovered nodes

## REST API Commands (Feature 12)
- `/api-start` - Start REST API server (port 18791)
- `/api-stop` - Stop API server
- `/api-status` - Check API server status

## Web Dashboard Commands (Feature 13)
- `/web-start` - Start web dashboard (port 18792)
- `/web-stop` - Stop web dashboard
- `/web-status` - Check web dashboard status

## Plugin System Commands (Feature 14)
- `/plugins` - List all loaded plugins
- `/plugin-load <name>` - Load a plugin
- `/plugin-unload <name>` - Unload a plugin
- `/plugin-reload <name>` - Reload a plugin
- `/plugin-enable <name>` - Enable a plugin
- `/plugin-disable <name>` - Disable a plugin
- `/plugin-info <name>` - Show plugin details
- `/hooks` - List available hooks

## Monitoring Commands (Feature 15)
- `/monitor-start` - Start monitoring service
- `/monitor-stop` - Stop monitoring service
- `/monitor-status` - Show monitoring status
- `/health-check` - Run health checks
- `/alerts` - Show active alerts
- `/metrics` - Show system metrics
- `/prometheus` - Export Prometheus metrics

## CLI Improvements Commands (Feature 16)
- `/alias <name> <command>` - Create command alias
- `/alias-list` - List all aliases
- `/alias-remove <name>` - Remove an alias
- `/session-save <name>` - Save current session
- `/session-load <name>` - Load a saved session
- `/session-list` - List saved sessions
- `/history-search <query>` - Search command history
- `/history-clear` - Clear command history
- `/config` - Run configuration wizard
- `/export <file>` - Export all data
- `/import <file>` - Import data

## Integration Commands (Feature 17)
- `/integrations` - Show integration status
- `/slack-config <webhook_url>` - Configure Slack
- `/discord-config <webhook_url>` - Configure Discord
- `/slack-test` - Test Slack notification
- `/discord-test` - Test Discord notification
- `/alert <message>` - Send alert to all channels
- `/webhook-start` - Start webhook server (port 18793)
- `/webhook-stop` - Stop webhook server

## Security Commands (Feature 18)
- `/security-status` - Show security status
- `/audit-log` - View recent audit log
- `/audit-search <query>` - Search audit log
- `/audit-export <file>` - Export audit log
- `/apikey-create <name>` - Create API key
- `/apikey-list` - List API keys
- `/apikey-revoke <key>` - Revoke API key
- `/security-scan` - Run security scan
- `/intrusion-check` - Check for intrusions

## Enhanced Memory (Improvement #4)
- `/memory-add <content>` - Add memory with embedding
- `/memory-search <query>` - Semantic search
- `/memory-context <query>` - Get context for conversation
- `/memory-stats` - Show memory statistics
- `/memory-consolidate` - Consolidate old memories

## Browser Agent (New!)
- `/browse <url>` - Fetch and summarize a webpage
- `/search <query>` - Search the web
- `/research <topic>` - Deep research on a topic
- `/browser-history` - Show browsing history
- `/browser-clear` - Clear browsing history

## Clan Creator (New!)
- `/clan-create <description>` - Preview new clan member
- `/clan-create-confirm` - Confirm and create pending member
- `/clan-create-cancel` - Cancel pending creation

## Docker Sandbox (New!)
- `/sandbox-status` - Check Docker sandbox status
- `/sandbox-exec <code>` - Execute code in sandbox
- `/sandbox-lang <lang>` - Set language (python, js, bash, go, rust, java)
- `/sandbox-list` - List running containers
- `/sandbox-cleanup` - Clean up all containers

## Goal-Based Agent (New!)
- `/goal <description>` - Start autonomous goal execution
- `/goal-status <id>` - Check goal progress
- `/goal-list` - List active and completed goals

## Extended Workflow Nodes (New!)
- Additional node types: http, condition, loop, delay, transform, variable

## Stretch Goals (Features 19-21)
- `/ai-optimize <prompt>` - Optimize a prompt
- `/ai-stats` - Advanced AI stats
- `/perf-stats` - Performance statistics
- `/perf-optimize` - Run memory optimization
- `/docs-generate` - Generate documentation
- `/docs-export <file>` - Export docs to markdown

## Visual Workflow Builder (New!)
- `/workflow-list` - List saved workflows
- `/workflow-create <name>` - Create new workflow
- `/workflow-open` - Open visual workflow builder in browser
- `/workflow-run <id>` - Execute a workflow
- `/workflow-delete <id>` - Delete a workflow
- `/workflow-export <id> <file>` - Export workflow
- `/workflow-import <file>` - Import workflow
- `/workflow-template <name>` - Create from template (bmad_full, code_review, security_audit)

## MCP Protocol (New!)
- `/mcp-start` - Start MCP server
- `/mcp-stop` - Stop MCP server
- `/mcp-tools` - List MCP tools
- `/mcp-install` - Install MCP in Claude/Cursor

## A2A Protocol (New!)
- `/a2a-start` - Start A2A server (port 18795)
- `/a2a-stop` - Stop A2A server
- `/a2a-discover <urls>` - Discover other A2A agents
- `/a2a-agents` - List known A2A agents
- `/a2a-delegate <agent> <message>` - Delegate task to agent

## System Commands
- `status` - Show full dashboard
- `health` - Check Phoenix Gate status
- `members` - List all clan members
- `history` - Show conversation history
- `memory` - Show memory system statistics
- `help` - Show this help
- `quit` / `exit` - Leave Castle Wyvern

## Examples
```
ask How do I reverse a string in Python?
code Write a function to calculate fibonacci numbers
review Is this authentication secure?
summarize Explain machine learning in simple terms
plan Design a microservices architecture for an e-commerce app
```
        """
        self.console.print(Markdown(help_text))
    
    def route_and_respond(self, user_input: str):
        """Route user input to appropriate clan member and display response."""
        # Classify intent
        with self.console.status("[cyan]Consulting the clan...[/cyan]", spinner="dots"):
            match = self.intent_router.classify(user_input)
        
        # Get primary agent
        agent_key = match.primary_agent
        agent = self.clan.get(agent_key, self.clan["goliath"])
        
        # Update agent status
        agent.set_busy(f"Processing: {user_input[:40]}...")
        
        # Display routing info
        self.console.print(f"\n[dim]🎯 Intent: {match.intent.value} ({match.confidence:.0%} confidence)[/dim]")
        self.console.print(f"[dim]🛡️  Routed to: {agent.emoji} {agent.name} - {match.reasoning}[/dim]\n")
        
        # Get agent's system prompt (would load from prompts/ directory)
        system_prompt = self._get_agent_prompt(agent_key)
        
        # Call AI with progress indicator
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True
        ) as progress:
            task = progress.add_task(f"[cyan]{agent.name} is responding...", total=None)
            
            try:
                response = self.phoenix_gate.call_ai(user_input, system_prompt)
            except Exception as e:
                response = f"⚠️  Error: {str(e)}"
        
        # Display response
        response_panel = Panel(
            Markdown(response),
            title=f"{agent.emoji} {agent.name}",
            border_style=agent.color,
            box=box.ROUNDED
        )
        self.console.print(response_panel)
        
        # Save to memory (NEW)
        self.grimoorum.record(
            user_input=user_input,
            agent_name=agent_key,
            agent_response=response,
            intent=match.intent.value,
            importance=3 if match.intent != IntentType.CHAT else 2,
            session_id="main_session"
        )
        
        # Update agent status back to ready
        agent.set_ready()
        
        # Add to history
        self.command_history.append({
            "input": user_input,
            "agent": agent.name,
            "response": response,
            "timestamp": datetime.now()
        })
    
    def _get_agent_prompt(self, agent_key: str) -> str:
        """Get system prompt for an agent."""
        prompts = {
            "goliath": "You are Goliath, leader of the Manhattan Clan. Be commanding, wise, and protective. Speak with authority but compassion.",
            "lexington": "You are Lexington, the technician of the clan. You excel at coding, technology, and practical solutions. Be enthusiastic about tech.",
            "brooklyn": "You are Brooklyn, the strategist. You think in terms of plans, contingencies, and architecture. Be tactical and forward-thinking.",
            "broadway": "You are Broadway, the chronicler. You love stories, explanations, and documentation. Be warm, narrative, and thorough.",
            "hudson": "You are Hudson, the archivist. You have deep knowledge of history and lore. Be wise, patient, and knowledgeable.",
            "bronx": "You are Bronx, the watchdog. You focus on security, threats, and protection. Be vigilant and serious about safety.",
            "elisa": "You are Elisa, the bridge to the human world. You understand human context, ethics, and law. Be grounding and practical.",
            "xanatos": "You are Xanatos, the red team. You find flaws, test assumptions, and think adversarially. Be clever and challenging.",
            "demona": "You are Demona, the failsafe. You predict failures and worst-case scenarios. Be cautious and protective.",
        }
        return prompts.get(agent_key, prompts["goliath"])
    
    def show_history(self):
        """Display conversation history from memory."""
        memories = self.grimoorum.get_recent_memories(limit=10)
        
        if not memories:
            self.console.print("[dim]No history yet. Start a conversation![/dim]")
            return
        
        self.console.print("\n[bold]📜 Conversation History[/bold]\n")
        for mem in memories:
            time_str = mem["timestamp"][11:19]  # Extract HH:MM:SS
            agent_emoji = self.clan.get(mem["agent_name"], {}).emoji if mem["agent_name"] in self.clan else "🎭"
            self.console.print(f"[dim]{time_str}[/dim] You: {mem['user_input'][:60]}...")
            self.console.print(f"[dim]     → {agent_emoji} {mem['agent_name'].title()}: {mem['agent_response'][:60]}...[/dim]\n")
    
    def show_memory_stats(self):
        """Show memory system statistics."""
        stats = self.grimoorum.get_stats()
        
        self.console.print("\n[bold]🧠 Memory System Statistics[/bold]\n")
        self.console.print(f"Total memories: {stats['total_memories']}")
        self.console.print(f"Total threads: {stats['total_threads']}")
        self.console.print(f"Agents with memories: {stats['agents_with_memories']}")
        self.console.print(f"High importance memories: {stats['high_importance']}")
        self.console.print(f"Storage size: {stats['storage_size_kb']} KB")
        
        if stats['agent_breakdown']:
            self.console.print("\n[dim]Agent memory counts:[/dim]")
            for agent, count in stats['agent_breakdown'].items():
                self.console.print(f"  {agent}: {count}")
        self.console.print()
    
    def run(self):
        """Main CLI loop."""
        self.console.clear()
        self.print_banner()
        self.print_dashboard()
        self.console.print("\n[dim]Type 'help' for commands or just start chatting with the clan![/dim]\n")
        
        while self.running:
            try:
                # Get user input
                user_input = self.console.input("[bold cyan]👤 You:[/bold cyan] ").strip()
                
                if not user_input:
                    continue
                
                # Expand aliases (Feature 16)
                original_input = user_input
                user_input = self.cli_improvements.expand_command(user_input)
                if user_input != original_input:
                    self.console.print(f"[dim]↳ Expanded: {user_input}[/dim]")
                
                # Record in history (Feature 16)
                self.cli_improvements.record_command(user_input)
                
                # Parse command
                parts = user_input.split(maxsplit=1)
                command = parts[0].lower()
                args = parts[1] if len(parts) > 1 else ""
                
                # Handle commands
                if command in ["quit", "exit", "bye"]:
                    self.console.print("\n[dim]🏰 Castle Wyvern sleeps until you return...[/dim]")
                    self.running = False
                
                elif command == "help":
                    self.print_help()
                
                elif command == "status":
                    self.print_dashboard()
                
                elif command == "health":
                    self.console.print(self.create_phoenix_gate_panel())
                
                elif command == "members":
                    self.console.print(self.create_clan_table())
                
                elif command == "history":
                    self.show_history()
                
                elif command == "memory":
                    self.show_memory_stats()
                
                elif command == "/spec":
                    if args:
                        self.bmad.quick_spec(args)
                    else:
                        self.console.print("[yellow]⚠️  Please provide a description for the spec.[/yellow]")
                
                elif command == "/build":
                    if args:
                        self.bmad.dev_story(args)
                    else:
                        self.console.print("[yellow]⚠️  Please provide what to build.[/yellow]")
                
                elif command == "/review":
                    if args:
                        self.bmad.code_review(args)
                    else:
                        self.console.print("[yellow]⚠️  Please provide code or description to review.[/yellow]")
                
                elif command == "/brief":
                    if args:
                        self.bmad.product_brief(args)
                    else:
                        self.console.print("[yellow]⚠️  Please provide product description.[/yellow]")
                
                elif command == "/ingest":
                    if args:
                        try:
                            doc_id = self.documents.ingest_file(args)
                            self.console.print(f"[green]✅ Document ingested: {doc_id}[/green]")
                        except Exception as e:
                            self.console.print(f"[red]⚠️  Error: {str(e)}[/red]")
                    else:
                        self.console.print("[yellow]⚠️  Please provide file path.[/yellow]")
                
                elif command == "/docs":
                    docs = self.documents.list_documents()
                    if docs:
                        table = Table(title="📚 Ingested Documents")
                        table.add_column("ID", style="dim")
                        table.add_column("Filename")
                        table.add_column("Type")
                        table.add_column("Chunks")
                        
                        for doc in docs:
                            table.add_row(doc['id'], doc['filename'], doc['type'], str(doc['chunks']))
                        
                        self.console.print(table)
                    else:
                        self.console.print("[dim]No documents ingested yet.[/dim]")
                
                elif command == "/search":
                    if args:
                        results = self.documents.search(args, top_k=5)
                        if results:
                            self.console.print(f"\n[bold]🔍 Search results for: {args}[/bold]\n")
                            for r in results:
                                self.console.print(Panel(
                                    r['content'][:300] + "...",
                                    title=f"📄 {r['document_name']} (score: {r['score']})",
                                    border_style="blue"
                                ))
                        else:
                            self.console.print("[dim]No results found.[/dim]")
                    else:
                        self.console.print("[yellow]⚠️  Please provide search query.[/yellow]")
                
                elif command == "/nodes":
                    nodes = self.nodes.list_nodes()
                    if nodes:
                        table = Table(title="🌐 Stone Nodes (Network)")
                        table.add_column("ID", style="dim", width=10)
                        table.add_column("Name")
                        table.add_column("Host")
                        table.add_column("Status")
                        table.add_column("Load")
                        table.add_column("Capabilities")
                        
                        for node in nodes:
                            status_color = "green" if node['status'] == 'online' else "red"
                            table.add_row(
                                node['id'][:8],
                                node['name'],
                                node['host'],
                                f"[{status_color}]{node['status']}[/{status_color}]",
                                f"{node['load']:.0%}",
                                ", ".join(node['capabilities'])
                            )
                        
                        self.console.print(table)
                    else:
                        self.console.print("[dim]No nodes registered.[/dim]")
                
                elif command == "/node-add":
                    parts = args.split()
                    if len(parts) >= 2:
                        name, host = parts[0], parts[1]
                        node_id = self.nodes.register_node(name, host)
                        self.console.print(f"[green]✅ Node registered: {node_id}[/green]")
                    else:
                        self.console.print("[yellow]⚠️  Usage: /node-add <name> <host>[/yellow]")
                
                elif command == "/tasks":
                    tasks = self.nodes.list_tasks()
                    if tasks:
                        table = Table(title="📋 Distributed Tasks")
                        table.add_column("ID", style="dim", width=12)
                        table.add_column("Type")
                        table.add_column("Status")
                        table.add_column("Priority")
                        table.add_column("Assigned Node")
                        
                        for task in tasks[-10:]:  # Last 10
                            status_color = {
                                'completed': 'green',
                                'failed': 'red',
                                'running': 'yellow',
                                'pending': 'dim'
                            }.get(task['status'], 'white')
                            
                            table.add_row(
                                task['id'][:12],
                                task['type'],
                                f"[{status_color}]{task['status']}[/{status_color}]",
                                str(task['priority']),
                                task.get('assigned_node', 'Unassigned')[:8] or "None"
                            )
                        
                        self.console.print(table)
                    else:
                        self.console.print("[dim]No tasks created yet.[/dim]")
                
                # ============ Feature 11: Auto-Discovery Commands ============
                elif command == "/discover-start":
                    if not self.auto_discovery:
                        self.auto_discovery = AutoDiscoveryService(
                            node_name="Castle-Wyvern-Main",
                            node_id="main-node",
                            port=18790,
                            capabilities=["cpu", "api"]
                        )
                    if self.auto_discovery.start():
                        self.console.print("[green]✅ Auto-discovery started[/green]")
                        self.console.print("[dim]   Broadcasting on mDNS...[/dim]")
                    else:
                        self.console.print("[red]⚠️  Failed to start auto-discovery[/red]")
                        self.console.print("[dim]   Run: pip install zeroconf[/dim]")
                
                elif command == "/discover-stop":
                    if self.auto_discovery:
                        self.auto_discovery.stop()
                        self.auto_discovery = None
                        self.console.print("[green]✅ Auto-discovery stopped[/green]")
                    else:
                        self.console.print("[dim]Auto-discovery not running[/dim]")
                
                elif command == "/discover-status":
                    if self.auto_discovery:
                        status = self.auto_discovery.status()
                        self.console.print(f"\n[bold]🔍 Auto-Discovery Status[/bold]")
                        self.console.print(f"  Running: {status['running']}")
                        self.console.print(f"  Advertising: {status['advertising']}")
                        self.console.print(f"  Discovered nodes: {status['discovered_nodes']}")
                        self.console.print(f"  Capabilities: {', '.join(status['capabilities'])}")
                        
                        nodes = self.auto_discovery.get_discovered_nodes()
                        if nodes:
                            self.console.print(f"\n[bold]Discovered Nodes:[/bold]")
                            for node in nodes:
                                self.console.print(f"  • {node.name} ({node.host}:{node.port})")
                                self.console.print(f"    Capabilities: {', '.join(node.capabilities)}")
                    else:
                        self.console.print("[dim]Auto-discovery not running[/dim]")
                        self.console.print("[dim]Run /discover-start to begin[/dim]")
                
                # ============ Feature 12: REST API Commands ============
                elif command == "/api-start":
                    if not self.api_server:
                        try:
                            self.api_server = CastleWyvernAPI(
                                host="0.0.0.0",
                                port=18791
                            )
                            # Start in background thread
                            import threading
                            api_thread = threading.Thread(
                                target=self.api_server.run,
                                kwargs={"debug": False},
                                daemon=True
                            )
                            api_thread.start()
                            self.console.print("[green]✅ REST API server started[/green]")
                            self.console.print("[dim]   Listening on http://0.0.0.0:18791[/dim]")
                            self.console.print("[dim]   Try: curl http://localhost:18791/health[/dim]")
                        except Exception as e:
                            self.console.print(f"[red]⚠️  Failed to start API: {e}[/red]")
                            self.console.print("[dim]   Run: pip install flask flask-cors[/dim]")
                    else:
                        self.console.print("[yellow]⚠️  API server already running[/yellow]")
                
                elif command == "/api-stop":
                    # Flask doesn't have a clean shutdown from outside
                    self.console.print("[yellow]⚠️  API server cannot be stopped gracefully[/yellow]")
                    self.console.print("[dim]   Restart Castle Wyvern to stop API[/dim]")
                    self.api_server = None
                
                elif command == "/api-status":
                    if self.api_server:
                        self.console.print("[green]✅ REST API is running[/green]")
                        self.console.print("[dim]   Endpoint: http://localhost:18791[/dim]")
                        self.console.print("\n[bold]Available Endpoints:[/bold]")
                        self.console.print("  GET  /health       - Health check")
                        self.console.print("  GET  /clan         - List clan members")
                        self.console.print("  POST /clan/ask     - Ask the clan")
                        self.console.print("  POST /clan/code    - Request code")
                        self.console.print("  GET  /nodes        - List nodes")
                        self.console.print("  POST /memory/search - Search memory")
                    else:
                        self.console.print("[dim]REST API not running[/dim]")
                        self.console.print("[dim]Run /api-start to begin[/dim]")
                
                # ============ Feature 13: Web Dashboard Commands ============
                elif command == "/web-start":
                    if not self.web_dashboard:
                        try:
                            self.web_dashboard = WebDashboard(
                                host="0.0.0.0",
                                port=18792
                            )
                            # Start in background thread
                            import threading
                            web_thread = threading.Thread(
                                target=self.web_dashboard.run,
                                kwargs={"debug": False},
                                daemon=True
                            )
                            web_thread.start()
                            self.console.print("[green]✅ Web Dashboard started[/green]")
                            self.console.print("[dim]   URL: http://localhost:18792[/dim]")
                            self.console.print("[dim]   Open your browser to view the dashboard[/dim]")
                        except Exception as e:
                            self.console.print(f"[red]⚠️  Failed to start Web Dashboard: {e}[/red]")
                            self.console.print("[dim]   Run: pip install flask flask-cors[/dim]")
                    else:
                        self.console.print("[yellow]⚠️  Web Dashboard already running[/yellow]")
                
                elif command == "/web-stop":
                    # Flask doesn't have clean shutdown from outside
                    self.console.print("[yellow]⚠️  Web Dashboard cannot be stopped gracefully[/yellow]")
                    self.console.print("[dim]   Restart Castle Wyvern to stop Web Dashboard[/dim]")
                    self.web_dashboard = None
                
                elif command == "/web-status":
                    if self.web_dashboard:
                        self.console.print("[green]✅ Web Dashboard is running[/green]")
                        self.console.print("[dim]   URL: http://localhost:18792[/dim]")
                        self.console.print("\n[bold]Dashboard Features:[/bold]")
                        self.console.print("  • Real-time clan status")
                        self.console.print("  • Chat interface with clan members")
                        self.console.print("  • Node monitoring")
                        self.console.print("  • Memory viewer")
                        self.console.print("  • System statistics")
                    else:
                        self.console.print("[dim]Web Dashboard not running[/dim]")
                        self.console.print("[dim]Run /web-start to begin[/dim]")
                
                # ============ Feature 14: Plugin System Commands ============
                elif command == "/plugins":
                    plugins = self.plugin_manager.list_plugins()
                    if plugins:
                        table = Table(title="🔌 Loaded Plugins")
                        table.add_column("Name", style="cyan")
                        table.add_column("Version")
                        table.add_column("Status")
                        table.add_column("Description", style="dim")
                        
                        for p in plugins:
                            status = "[green]enabled[/green]" if p["enabled"] else "[red]disabled[/red]"
                            table.add_row(p["name"], p["version"], status, p.get("description", "")[:40])
                        
                        self.console.print(table)
                        stats = self.plugin_manager.get_stats()
                        self.console.print(f"\n[dim]Total: {stats['total_loaded']} loaded, {stats['total_discovered']} discovered[/dim]")
                    else:
                        self.console.print("[dim]No plugins loaded. Place plugins in the plugins/ directory[/dim]")
                
                elif command == "/plugin-load":
                    if args:
                        success = self.plugin_manager.load_plugin(args)
                        if success:
                            self.console.print(f"[green]✅ Plugin '{args}' loaded[/green]")
                        else:
                            self.console.print(f"[red]⚠️  Failed to load plugin '{args}'[/red]")
                    else:
                        self.console.print("[yellow]⚠️  Usage: /plugin-load <name>[/yellow]")
                
                elif command == "/plugin-unload":
                    if args:
                        success = self.plugin_manager.unload_plugin(args)
                        if success:
                            self.console.print(f"[green]✅ Plugin '{args}' unloaded[/green]")
                        else:
                            self.console.print(f"[red]⚠️  Failed to unload plugin '{args}'[/red]")
                    else:
                        self.console.print("[yellow]⚠️  Usage: /plugin-unload <name>[/yellow]")
                
                elif command == "/plugin-reload":
                    if args:
                        success = self.plugin_manager.reload_plugin(args)
                        if success:
                            self.console.print(f"[green]✅ Plugin '{args}' reloaded[/green]")
                        else:
                            self.console.print(f"[red]⚠️  Failed to reload plugin '{args}'[/red]")
                    else:
                        self.console.print("[yellow]⚠️  Usage: /plugin-reload <name>[/yellow]")
                
                elif command == "/plugin-enable":
                    if args:
                        self.plugin_manager.enable_plugin(args)
                        self.console.print(f"[green]✅ Plugin '{args}' enabled[/green]")
                    else:
                        self.console.print("[yellow]⚠️  Usage: /plugin-enable <name>[/yellow]")
                
                elif command == "/plugin-disable":
                    if args:
                        self.plugin_manager.disable_plugin(args)
                        self.console.print(f"[yellow]⚠️  Plugin '{args}' disabled[/yellow]")
                    else:
                        self.console.print("[yellow]⚠️  Usage: /plugin-disable <name>[/yellow]")
                
                elif command == "/plugin-info":
                    if args:
                        info = self.plugin_manager.get_plugin_info(args)
                        if info:
                            self.console.print(f"\n[bold]🔌 {info['name']}[/bold]")
                            self.console.print(f"Version: {info['version']}")
                            self.console.print(f"Author: {info.get('author', 'Unknown')}")
                            self.console.print(f"Status: {'enabled' if info['enabled'] else 'disabled'}")
                            if info.get('description'):
                                self.console.print(f"Description: {info['description']}")
                        else:
                            self.console.print(f"[red]⚠️  Plugin '{args}' not found[/red]")
                    else:
                        self.console.print("[yellow]⚠️  Usage: /plugin-info <name>[/yellow]")
                
                elif command == "/hooks":
                    hooks = self.plugin_manager.hooks
                    if hooks:
                        table = Table(title="🪝 Available Hooks")
                        table.add_column("Name", style="cyan")
                        table.add_column("Callbacks")
                        table.add_column("Description", style="dim")
                        
                        for name, hook in sorted(hooks.items()):
                            table.add_row(name, str(len(hook.callbacks)), hook.description[:50])
                        
                        self.console.print(table)
                    else:
                        self.console.print("[dim]No hooks registered[/dim]")
                
                # ============ Feature 15: Monitoring Commands ============
                elif command == "/monitor-start":
                    if not self.monitoring._running:
                        self.monitoring.start(interval_seconds=30)
                        self.console.print("[green]✅ Monitoring service started[/green]")
                        self.console.print("[dim]   Collecting metrics every 30 seconds[/dim]")
                    else:
                        self.console.print("[yellow]⚠️  Monitoring service already running[/yellow]")
                
                elif command == "/monitor-stop":
                    if self.monitoring._running:
                        self.monitoring.stop()
                        self.console.print("[green]✅ Monitoring service stopped[/green]")
                    else:
                        self.console.print("[dim]Monitoring service not running[/dim]")
                
                elif command == "/monitor-status":
                    status = self.monitoring.get_status()
                    self.console.print(f"\n[bold]📊 Monitoring Status[/bold]")
                    self.console.print(f"Running: {status['running']}")
                    self.console.print(f"Overall Health: {status['overall_health']}")
                    self.console.print(f"Active Alerts: {status['active_alerts']}")
                    self.console.print(f"Total Alerts: {status['total_alerts']}")
                    self.console.print(f"Metrics Stored: {status['metrics_stored']}")
                    
                    if status['health_checks']:
                        self.console.print(f"\n[bold]Health Checks:[/bold]")
                        for name, check in status['health_checks'].items():
                            icon = "🟢" if check['status'] == 'healthy' else "🟡" if check['status'] == 'degraded' else "🔴"
                            self.console.print(f"  {icon} {name}: {check['message']}")
                
                elif command == "/health-check":
                    with self.console.status("[cyan]Running health checks...[/cyan]"):
                        results = self.monitoring.health.run_all_checks()
                    
                    table = Table(title="🏥 Health Check Results")
                    table.add_column("Component", style="cyan")
                    table.add_column("Status")
                    table.add_column("Message", style="dim")
                    
                    for name, status in results.items():
                        status_color = "green" if status.status == "healthy" else "yellow" if status.status == "degraded" else "red"
                        table.add_row(name, f"[{status_color}]{status.status}[/{status_color}]", status.message)
                    
                    self.console.print(table)
                
                elif command == "/alerts":
                    alerts = self.monitoring.get_active_alerts()
                    if alerts:
                        table = Table(title="🚨 Active Alerts")
                        table.add_column("ID", style="dim")
                        table.add_column("Severity")
                        table.add_column("Message")
                        table.add_column("Time", style="dim")
                        
                        for alert in alerts[:10]:  # Show last 10
                            sev_color = {
                                "critical": "red",
                                "error": "red",
                                "warning": "yellow",
                                "info": "blue"
                            }.get(alert.severity.value, "white")
                            
                            table.add_row(
                                alert.id[:20],
                                f"[{sev_color}]{alert.severity.value}[/{sev_color}]",
                                alert.message,
                                alert.timestamp[11:19]
                            )
                        
                        self.console.print(table)
                    else:
                        self.console.print("[green]✅ No active alerts[/green]")
                
                elif command == "/metrics":
                    metrics = self.monitoring.metrics
                    self.console.print(f"\n[bold]📈 System Metrics[/bold]\n")
                    
                    # Show latest values
                    for name in ["system.cpu.percent", "system.memory.percent", "system.disk.percent"]:
                        latest = metrics.get_latest(name)
                        if latest:
                            self.console.print(f"{name}: {latest.value:.1f}%")
                    
                    # Show stats
                    self.console.print(f"\n[bold]Last 5 Minutes:[/bold]")
                    for name in ["system.cpu.percent", "system.memory.percent"]:
                        stats = metrics.get_stats(name, minutes=5)
                        if stats:
                            self.console.print(f"\n{name}:")
                            self.console.print(f"  Mean: {stats.get('mean', 0):.1f}%")
                            self.console.print(f"  Max: {stats.get('max', 0):.1f}%")
                
                elif command == "/prometheus":
                    metrics_text = self.monitoring.metrics.export_prometheus()
                    self.console.print("\n[bold]# Prometheus Metrics Export[/bold]\n")
                    self.console.print(metrics_text)
                
                # ============ Feature 16: CLI Improvements Commands ============
                elif command == "/alias":
                    parts = args.split(maxsplit=1)
                    if len(parts) >= 2:
                        name, cmd = parts[0], parts[1]
                        if self.cli_improvements.aliases.add(name, cmd):
                            self.console.print(f"[green]✅ Alias '{name}' created[/green]")
                            self.console.print(f"[dim]   '{name}' -> '{cmd}'[/dim]")
                        else:
                            self.console.print("[red]⚠️  Failed to create alias[/red]")
                    else:
                        self.console.print("[yellow]⚠️  Usage: /alias <name> <command>[/yellow]")
                
                elif command == "/alias-list":
                    aliases = self.cli_improvements.aliases.list_all()
                    if aliases:
                        table = Table(title="⚡ Command Aliases")
                        table.add_column("Name", style="cyan")
                        table.add_column("Command", style="dim")
                        table.add_column("Description", style="dim")
                        
                        for alias in aliases:
                            table.add_row(alias.name, alias.command[:50], alias.description[:30])
                        
                        self.console.print(table)
                    else:
                        self.console.print("[dim]No aliases defined[/dim]")
                
                elif command == "/alias-remove":
                    if args:
                        if self.cli_improvements.aliases.remove(args):
                            self.console.print(f"[green]✅ Alias '{args}' removed[/green]")
                        else:
                            self.console.print(f"[red]⚠️  Alias '{args}' not found[/red]")
                    else:
                        self.console.print("[yellow]⚠️  Usage: /alias-remove <name>[/yellow]")
                
                elif command == "/session-save":
                    if args:
                        # Get recent commands from history
                        recent = self.cli_improvements.history.get_recent(20)
                        commands = [cmd["command"] for cmd in recent]
                        
                        self.cli_improvements.sessions.save(args, commands)
                        self.console.print(f"[green]✅ Session '{args}' saved ({len(commands)} commands)[/green]")
                    else:
                        self.console.print("[yellow]⚠️  Usage: /session-save <name>[/yellow]")
                
                elif command == "/session-load":
                    if args:
                        session = self.cli_improvements.sessions.load(args)
                        if session:
                            self.console.print(f"[green]✅ Loading session '{args}'[/green]")
                            self.console.print(f"[dim]   {len(session.commands)} commands[/dim]")
                            # Note: Actual execution would happen in main loop
                        else:
                            self.console.print(f"[red]⚠️  Session '{args}' not found[/red]")
                    else:
                        self.console.print("[yellow]⚠️  Usage: /session-load <name>[/yellow]")
                
                elif command == "/session-list":
                    sessions = self.cli_improvements.sessions.list_all()
                    if sessions:
                        table = Table(title="💾 Saved Sessions")
                        table.add_column("Name", style="cyan")
                        table.add_column("Commands")
                        table.add_column("Created", style="dim")
                        
                        for session in sessions:
                            table.add_row(
                                session.name,
                                str(len(session.commands)),
                                session.created_at[:10]
                            )
                        
                        self.console.print(table)
                    else:
                        self.console.print("[dim]No saved sessions[/dim]")
                
                elif command == "/history-search":
                    if args:
                        results = self.cli_improvements.history.search(args)
                        if results:
                            self.console.print(f"\n[bold]🔍 History search for '{args}':[/bold]\n")
                            for cmd in results[-10:]:
                                self.console.print(f"  {cmd['timestamp'][11:19]} {cmd['command'][:60]}")
                        else:
                            self.console.print("[dim]No matching commands found[/dim]")
                    else:
                        self.console.print("[yellow]⚠️  Usage: /history-search <query>[/yellow]")
                
                elif command == "/history-clear":
                    self.cli_improvements.history.clear()
                    self.console.print("[green]✅ Command history cleared[/green]")
                
                elif command == "/config":
                    self.cli_improvements.config.run_wizard(self.console)
                
                elif command == "/export":
                    if args:
                        if self.cli_improvements.export_import.export_all(args):
                            self.console.print(f"[green]✅ Data exported to {args}[/green]")
                        else:
                            self.console.print("[red]⚠️  Export failed[/red]")
                    else:
                        self.console.print("[yellow]⚠️  Usage: /export <file.json>[/yellow]")
                
                elif command == "/import":
                    if args:
                        if self.cli_improvements.export_import.import_all(args):
                            self.console.print(f"[green]✅ Data imported from {args}[/green]")
                        else:
                            self.console.print("[red]⚠️  Import failed[/red]")
                    else:
                        self.console.print("[yellow]⚠️  Usage: /import <file.json>[/yellow]")
                
                # ============ Feature 17: Integration Commands ============
                elif command == "/integrations":
                    status = self.integrations.get_status()
                    
                    table = Table(title="🔗 Integration Status")
                    table.add_column("Service", style="cyan")
                    table.add_column("Configured")
                    table.add_column("Status")
                    
                    for name, info in status.items():
                        if "configured" in info:
                            icon = "✅" if info["configured"] else "❌"
                            table.add_row(name, icon, "Ready" if info["configured"] else "Not configured")
                        elif "running" in info:
                            icon = "🟢" if info["running"] else "🔴"
                            table.add_row(name, "-", icon + " Running" if info["running"] else "Stopped")
                    
                    self.console.print(table)
                    
                    self.console.print("\n[dim]Configure integrations with:[/dim]")
                    self.console.print("  /slack-config <webhook_url>")
                    self.console.print("  /discord-config <webhook_url>")
                
                elif command == "/slack-config":
                    if args:
                        self.integrations.configure_slack(args)
                        self.console.print("[green]✅ Slack configured[/green]")
                        self.console.print("[dim]   Test with: /slack-test[/dim]")
                    else:
                        self.console.print("[yellow]⚠️  Usage: /slack-config <webhook_url>[/yellow]")
                        self.console.print("[dim]   Get webhook URL from: https://api.slack.com/messaging/webhooks[/dim]")
                
                elif command == "/discord-config":
                    if args:
                        self.integrations.configure_discord(args)
                        self.console.print("[green]✅ Discord configured[/green]")
                        self.console.print("[dim]   Test with: /discord-test[/dim]")
                    else:
                        self.console.print("[yellow]⚠️  Usage: /discord-config <webhook_url>[/yellow]")
                        self.console.print("[dim]   Get webhook URL from: Server Settings > Integrations > Webhooks[/dim]")
                
                elif command == "/slack-test":
                    success = self.integrations.slack.send_message(
                        "🏰 Castle Wyvern test message!",
                        username="Castle Wyvern"
                    )
                    if success:
                        self.console.print("[green]✅ Test message sent to Slack[/green]")
                    else:
                        self.console.print("[red]⚠️  Failed to send Slack message[/red]")
                        self.console.print("[dim]   Check your webhook URL with /integrations[/dim]")
                
                elif command == "/discord-test":
                    success = self.integrations.discord.send_message(
                        "🏰 Castle Wyvern test message!"
                    )
                    if success:
                        self.console.print("[green]✅ Test message sent to Discord[/green]")
                    else:
                        self.console.print("[red]⚠️  Failed to send Discord message[/red]")
                        self.console.print("[dim]   Check your webhook URL with /integrations[/dim]")
                
                elif command == "/alert":
                    if args:
                        results = self.integrations.send_alert(
                            "Manual Alert",
                            args,
                            severity="info"
                        )
                        
                        self.console.print("[bold]📤 Alert sent to:[/bold]")
                        for channel, success in results.items():
                            icon = "✅" if success else "❌"
                            self.console.print(f"  {icon} {channel}")
                    else:
                        self.console.print("[yellow]⚠️  Usage: /alert <message>[/yellow]")
                
                elif command == "/webhook-start":
                    if self.integrations.start_webhook_server():
                        self.console.print("[green]✅ Webhook server started[/green]")
                        self.console.print("[dim]   Listening on http://localhost:18793[/dim]")
                        self.console.print("[dim]   Endpoints:[/dim]")
                        self.console.print("[dim]     POST /webhook/alerts[/dim]")
                        self.console.print("[dim]     POST /webhook/commands[/dim]")
                        self.console.print("[dim]     POST /webhook/events[/dim]")
                    else:
                        self.console.print("[red]⚠️  Failed to start webhook server[/red]")
                
                elif command == "/webhook-stop":
                    self.console.print("[yellow]⚠️  Webhook server cannot be stopped gracefully[/yellow]")
                    self.console.print("[dim]   Restart Castle Wyvern to stop[/dim]")
                
                # ============ Feature 18: Security Commands ============
                elif command == "/security-status":
                    status = self.security.get_status()
                    
                    table = Table(title="🔒 Security Status")
                    table.add_column("Component", style="cyan")
                    table.add_column("Status")
                    
                    table.add_row("Audit Logging", "✅ Enabled" if status["audit_enabled"] else "❌ Disabled")
                    table.add_row("Encryption", "✅ Enabled" if status["encryption_enabled"] else "❌ Disabled")
                    table.add_row("Intrusion Detection", "✅ Enabled" if status["intrusion_detection"] else "❌ Disabled")
                    table.add_row("Audit Entries", str(status["audit_entries"]))
                    table.add_row("API Keys", str(status["api_keys"]))
                    
                    self.console.print(table)
                
                elif command == "/audit-log":
                    entries = self.security.audit.get_recent(20)
                    if entries:
                        table = Table(title="📋 Recent Audit Log")
                        table.add_column("Time", style="dim", width=10)
                        table.add_column("Level")
                        table.add_column("Category", style="dim")
                        table.add_column("Action")
                        table.add_column("User", style="cyan")
                        
                        for entry in entries:
                            time_str = entry.timestamp[11:19]
                            table.add_row(time_str, entry.level, entry.category, entry.action, entry.user)
                        
                        self.console.print(table)
                    else:
                        self.console.print("[dim]No audit entries[/dim]")
                
                elif command == "/audit-search":
                    if args:
                        results = self.security.audit.search(**json.loads(args))
                        self.console.print(f"\n[bold]🔍 Found {len(results)} matching entries[/bold]\n")
                        for entry in results[-10:]:
                            self.console.print(f"  {entry.timestamp[11:19]} [{entry.level}] {entry.category}: {entry.action}")
                    else:
                        self.console.print("[yellow]⚠️  Usage: /audit-search <json_filters>[/yellow]")
                
                elif command == "/audit-export":
                    if args:
                        if self.security.audit.export(args):
                            self.console.print(f"[green]✅ Audit log exported to {args}[/green]")
                        else:
                            self.console.print("[red]⚠️  Export failed[/red]")
                    else:
                        self.console.print("[yellow]⚠️  Usage: /audit-export <file.json>[/yellow]")
                
                elif command == "/apikey-create":
                    if args:
                        key = self.security.api_keys.generate_key(args)
                        self.console.print(f"[green]✅ API key created for: {args}[/green]")
                        self.console.print(f"[dim]   Key: {key}[/dim]")
                        self.console.print("\n[yellow]⚠️  Save this key - it won't be shown again![/yellow]")
                    else:
                        self.console.print("[yellow]⚠️  Usage: /apikey-create <name>[/yellow]")
                
                elif command == "/apikey-list":
                    keys = self.security.api_keys.list_keys()
                    if keys:
                        table = Table(title="🔑 API Keys")
                        table.add_column("Name", style="cyan")
                        table.add_column("Created")
                        table.add_column("Last Used", style="dim")
                        
                        for key in keys:
                            table.add_row(key["name"], key["created_at"][:10], key.get("last_used", "Never")[:10] if key.get("last_used") else "Never")
                        
                        self.console.print(table)
                    else:
                        self.console.print("[dim]No API keys[/dim]")
                
                elif command == "/apikey-revoke":
                    if args:
                        if self.security.api_keys.revoke_key(args):
                            self.console.print(f"[green]✅ API key revoked[/green]")
                        else:
                            self.console.print(f"[red]⚠️  API key not found[/red]")
                    else:
                        self.console.print("[yellow]⚠️  Usage: /apikey-revoke <key>[/yellow]")
                
                elif command == "/security-scan":
                    with self.console.status("[cyan]Running security scan...[/cyan]"):
                        results = self.security.run_security_scan()
                    
                    self.console.print(f"\n[bold]🔒 Security Scan Results[/bold]")
                    self.console.print(f"Issues found: {len(results['issues'])}")
                    
                    if results['issues']:
                        for issue in results['issues']:
                            icon = "🔴" if issue['severity'] == 'error' else "🟡" if issue['severity'] == 'warning' else "ℹ️"
                            self.console.print(f"  {icon} [{issue['severity']}] {issue['message']}")
                
                elif command == "/intrusion-check":
                    with self.console.status("[cyan]Checking for intrusions...[/cyan]"):
                        detections = self.security.check_intrusions()
                    
                    if detections:
                        self.console.print(f"\n[bold]🚨 {len(detections)} Potential Intrusions Detected[/bold]")
                        for detection in detections:
                            self.console.print(f"  🟡 {detection['pattern']}: {detection['count']} occurrences")
                    else:
                        self.console.print("[green]✅ No intrusions detected[/green]")
                
                # ============ Stretch Goals (Features 19-21) ============
                elif command == "/ai-optimize":
                    if args:
                        optimized = self.advanced_ai.optimize_prompt(args)
                        self.console.print(f"\n[bold]Original:[/bold] {args}")
                        self.console.print(f"\n[bold]Optimized:[/bold] {optimized}")
                    else:
                        self.console.print("[yellow]⚠️  Usage: /ai-optimize <prompt>[/yellow]")
                
                elif command == "/ai-stats":
                    stats = self.advanced_ai.get_stats()
                    table = Table(title="🧠 Advanced AI Stats")
                    table.add_column("Metric", style="cyan")
                    table.add_column("Value")
                    
                    table.add_row("Context Window Utilization", f"{stats['context_window'].get('utilization', 0):.1%}")
                    table.add_row("Cached Prompts", str(stats['cached_prompts']))
                    table.add_row("Code Executions", str(stats['executions']))
                    table.add_row("Ensemble Models", str(stats['ensemble_models']))
                    
                    self.console.print(table)
                
                elif command == "/perf-stats":
                    stats = self.performance.get_stats()
                    table = Table(title="⚡ Performance Stats")
                    table.add_column("Metric", style="cyan")
                    table.add_column("Value")
                    
                    table.add_row("Uptime", f"{stats['uptime_seconds'] // 3600}h {(stats['uptime_seconds'] % 3600) // 60}m")
                    table.add_row("Total Requests", str(stats['total_requests']))
                    table.add_row("Cache Hit Rate", stats['cache'].get('hit_rate', 'N/A'))
                    table.add_row("Cache Size", f"{stats['cache'].get('size', 0)}/{stats['cache'].get('max_size', 0)}")
                    
                    self.console.print(table)
                
                elif command == "/perf-optimize":
                    with self.console.status("[cyan]Optimizing memory...[/cyan]"):
                        result = self.performance.optimize_memory()
                    
                    self.console.print("[green]✅ Memory optimization complete[/green]")
                    self.console.print(f"[dim]   Cache cleared: {result['cache_cleared']}[/dim]")
                    self.console.print(f"[dim]   Pools cleared: {result['pools_cleared']}[/dim]")
                
                elif command == "/docs-generate":
                    with self.console.status("[cyan]Generating documentation...[/cyan]"):
                        output_file = self.documentation.export_markdown()
                    
                    self.console.print(f"[green]✅ Documentation generated[/green]")
                    self.console.print(f"[dim]   Location: {output_file}[/dim]")
                
                elif command == "/docs-export":
                    if args:
                        with self.console.status("[cyan]Exporting documentation...[/cyan]"):
                            output_file = self.documentation.export_markdown(args)
                        
                        self.console.print(f"[green]✅ Documentation exported to {args}[/green]")
                    else:
                        self.console.print("[yellow]⚠️  Usage: /docs-export <file.md>[/yellow]")
                
                # ============ MCP Protocol Commands ============
                elif command == "/mcp-start":
                    if not self.mcp_server:
                        self.mcp_server = CastleWyvernMCPServer(castle_wyvern_cli=self)
                        
                        # Start in background thread
                        import threading
                        mcp_thread = threading.Thread(
                            target=self.mcp_server.start,
                            daemon=True
                        )
                        mcp_thread.start()
                        
                        self.console.print("[green]✅ MCP Server started[/green]")
                        self.console.print("[dim]   The Manhattan Clan is now available via MCP![/dim]")
                        self.console.print("[dim]   Tools available:[/dim]")
                        for tool in self.mcp_server.list_tools():
                            self.console.print(f"[dim]     • {tool['name']}: {tool['description'][:50]}...[/dim]")
                    else:
                        self.console.print("[yellow]⚠️  MCP Server already running[/yellow]")
                
                elif command == "/mcp-stop":
                    if self.mcp_server:
                        self.mcp_server.stop()
                        self.mcp_server = None
                        self.console.print("[green]✅ MCP Server stopped[/green]")
                    else:
                        self.console.print("[dim]MCP Server not running[/dim]")
                
                elif command == "/mcp-tools":
                    if self.mcp_server:
                        table = Table(title="🔌 MCP Tools")
                        table.add_column("Tool Name", style="cyan")
                        table.add_column("Description")
                        
                        for tool in self.mcp_server.list_tools():
                            table.add_row(tool['name'], tool['description'][:60])
                        
                        self.console.print(table)
                    else:
                        # Show what tools would be available
                        temp_server = CastleWyvernMCPServer()
                        table = Table(title="🔌 Available MCP Tools (Start server with /mcp-start)")
                        table.add_column("Tool Name", style="cyan")
                        table.add_column("Description")
                        
                        for tool in temp_server.list_tools():
                            table.add_row(tool['name'], tool['description'][:60])
                        
                        self.console.print(table)
                
                elif command == "/mcp-install":
                    self.console.print("[bold]📦 MCP Installation Guide[/bold]\n")
                    self.console.print("To use Castle Wyvern with MCP clients:\n")
                    
                    self.console.print("[bold]1. Claude Desktop:[/bold]")
                    self.console.print("   - Open Claude Desktop")
                    self.console.print("   - Go to Settings > Developer > Edit Config")
                    self.console.print("   - Add Castle Wyvern to claude_desktop_config.json:")
                    self.console.print("""
   {
     "mcpServers": {
       "castle-wyvern": {
         "command": "python",
         "args": ["-m", "eyrie.mcp_server"],
         "cwd": "/path/to/castle-wyvern"
       }
     }
   }
""")
                    
                    self.console.print("[bold]2. Cursor:[/bold]")
                    self.console.print("   - Open Cursor Settings")
                    self.console.print("   - Find MCP settings")
                    self.console.print("   - Add the same configuration as above")
                    self.console.print("")
                    
                    self.console.print("[bold]3. Other MCP Clients:[/bold]")
                    self.console.print("   - Configure with stdio transport")
                    self.console.print("   - Command: python -m eyrie.mcp_server")
                    self.console.print("")
                    
                    self.console.print("[green]✅ After installation, restart your MCP client![/green]")
                
                # ============ A2A Protocol Commands ============
                elif command == "/a2a-start":
                    if not self.a2a:
                        self.a2a = A2AIntegration(castle_wyvern_cli=self)
                    
                    if self.a2a.start_server():
                        self.console.print("[green]✅ A2A Server started[/green]")
                        self.console.print("[dim]   The Manhattan Clan can now talk to other A2A agents![/dim]")
                        self.console.print("[dim]   Agent Card: http://localhost:18795/.well-known/agent.json[/dim]")
                        self.console.print("[dim]   Skills available:[/dim]")
                        for skill in ["goliath", "lexington", "brooklyn", "xanatos", "broadway"]:
                            self.console.print(f"[dim]     • {skill}[/dim]")
                    else:
                        self.console.print("[red]⚠️  Failed to start A2A server[/red]")
                
                elif command == "/a2a-stop":
                    self.console.print("[yellow]⚠️  A2A Server cannot be stopped gracefully[/yellow]")
                    self.console.print("[dim]   Restart Castle Wyvern to stop[/dim]")
                    self.a2a = None
                
                elif command == "/a2a-discover":
                    if args:
                        import asyncio
                        urls = args.split()
                        
                        with self.console.status("[cyan]Discovering A2A agents...[/cyan]"):
                            if not self.a2a:
                                self.a2a = A2AIntegration()
                            agents = asyncio.run(self.a2a.discover_agents(urls))
                        
                        if agents:
                            self.console.print(f"\n[green]✅ Discovered {len(agents)} A2A agent(s):[/green]")
                            for agent in agents:
                                self.console.print(f"  • {agent.name} ({agent.url})")
                                self.console.print(f"    {agent.description[:60]}...")
                        else:
                            self.console.print("[dim]No A2A agents found at provided URLs[/dim]")
                    else:
                        self.console.print("[yellow]⚠️  Usage: /a2a-discover <url1> [url2] ...[/yellow]")
                        self.console.print("[dim]   Example: /a2a-discover http://localhost:8080 http://localhost:9090[/dim]")
                
                elif command == "/a2a-agents":
                    if self.a2a:
                        agents = self.a2a.get_known_agents()
                        if agents:
                            table = Table(title="🔗 Known A2A Agents")
                            table.add_column("Agent", style="cyan")
                            table.add_column("Skills")
                            
                            for agent in agents:
                                skills = ", ".join([s['id'] for s in agent.get('skills', [])[:3]])
                                table.add_row(agent.get('name', 'Unknown'), skills)
                            
                            self.console.print(table)
                        else:
                            self.console.print("[dim]No known A2A agents[/dim]")
                            self.console.print("[dim]Use /a2a-discover to find agents[/dim]")
                    else:
                        self.console.print("[dim]A2A not initialized[/dim]")
                
                elif command == "/a2a-delegate":
                    parts = args.split(maxsplit=1)
                    if len(parts) >= 2:
                        agent_name, message = parts[0], parts[1]
                        
                        if self.a2a:
                            with self.console.status(f"[cyan]Delegating to {agent_name}...[/cyan]"):
                                import asyncio
                                response = asyncio.run(self.a2a.delegate_task(agent_name, message))
                            
                            if response:
                                self.console.print(f"\n[bold]Response from {agent_name}:[/bold]")
                                self.console.print(response)
                            else:
                                self.console.print(f"[red]⚠️  No response from {agent_name}[/red]")
                        else:
                            self.console.print("[red]⚠️  A2A not initialized. Start with /a2a-start[/red]")
                    else:
                        self.console.print("[yellow]⚠️  Usage: /a2a-delegate <agent_name> <message>[/yellow]")
                
                # ============ Enhanced Memory Commands ============
                elif command == "/memory-add":
                    if args:
                        mem_id = self.enhanced_memory.add(
                            content=args,
                            importance=4
                        )
                        self.console.print(f"[green]✅ Memory added with embedding[/green]")
                        self.console.print(f"[dim]   ID: {mem_id[:16]}...[/dim]")
                    else:
                        self.console.print("[yellow]⚠️  Usage: /memory-add <content>[/yellow]")
                
                elif command == "/memory-search":
                    if args:
                        results = self.enhanced_memory.search(args, use_semantic=True)
                        if results:
                            table = Table(title=f"🧠 Semantic Search: '{args}'")
                            table.add_column("Memory", style="cyan", max_width=60)
                            table.add_column("Similarity")
                            
                            for r in results:
                                sim_pct = f"{r['similarity']*100:.1f}%"
                                table.add_row(r['content'][:80], sim_pct)
                            
                            self.console.print(table)
                        else:
                            self.console.print("[dim]No similar memories found[/dim]")
                    else:
                        self.console.print("[yellow]⚠️  Usage: /memory-search <query>[/yellow]")
                
                elif command == "/memory-context":
                    if args:
                        context = self.enhanced_memory.get_context(args)
                        if context:
                            self.console.print(f"[bold]🧠 Context for:[/bold] {args}\n")
                            self.console.print(context)
                        else:
                            self.console.print("[dim]No relevant context found[/dim]")
                    else:
                        self.console.print("[yellow]⚠️  Usage: /memory-context <query>[/yellow]")
                
                elif command == "/memory-stats":
                    stats = self.enhanced_memory.get_stats()
                    table = Table(title="🧠 Enhanced Memory Statistics")
                    table.add_column("Metric", style="cyan")
                    table.add_column("Value")
                    
                    vector_stats = stats.get('vector_memory', {})
                    table.add_row("Total Memories", str(vector_stats.get('total_memories', 0)))
                    table.add_row("Vector Dimension", str(vector_stats.get('dimension', 0)))
                    table.add_row("High Importance", str(vector_stats.get('high_importance', 0)))
                    table.add_row("Total Accesses", str(vector_stats.get('total_accesses', 0)))
                    table.add_row("Consolidated", str(vector_stats.get('consolidated', 0)))
                    
                    self.console.print(table)
                    self.console.print("[dim]Enhanced with vector embeddings for semantic search[/dim]")
                
                elif command == "/memory-consolidate":
                    with self.console.status("[cyan]Consolidating old memories...[/cyan]"):
                        consolidated = self.enhanced_memory.vector_store.consolidate_memories()
                    
                    if consolidated > 0:
                        self.console.print(f"[green]✅ Consolidated {consolidated} memories[/green]")
                    else:
                        self.console.print("[dim]No memories needed consolidation[/dim]")
                
                # ============ Browser Agent Commands ============
                elif command == "/browse":
                    if args:
                        self.clan["jade"].set_busy(f"Browsing: {args[:40]}...")
                        with self.console.status(f"[cyan]🌐 Jade is browsing {args}...[/cyan]"):
                            page = self.browser.fetch(args)
                        
                        self.console.print(f"\n[bold]🌐 {page.title}[/bold]")
                        self.console.print(f"[dim]{page.url}[/dim]\n")
                        
                        # Show content (truncated)
                        content = page.content[:2000] if len(page.content) > 2000 else page.content
                        self.console.print(content)
                        
                        if len(page.content) > 2000:
                            self.console.print(f"\n[dim]... {len(page.content) - 2000} more characters[/dim]")
                        
                        self.console.print(f"\n[dim]🔗 Found {len(page.links)} links on page[/dim]")
                        self.clan["jade"].set_ready()
                    else:
                        self.console.print("[yellow]⚠️  Usage: /browse <url>[/yellow]")
                        self.console.print("[dim]   Example: /browse https://python.org[/dim]")
                
                elif command == "/search":
                    if args:
                        self.clan["jade"].set_busy(f"Searching: {args[:40]}...")
                        with self.console.status(f"[cyan]🔍 Jade is searching for '{args}'...[/cyan]"):
                            results = self.browser.search(args, num_results=5)
                        
                        table = Table(title=f"🔍 Search Results: '{args}'")
                        table.add_column("#", justify="right", style="cyan", width=3)
                        table.add_column("Title", style="bright_blue")
                        table.add_column("Snippet", style="dim", max_width=50)
                        
                        for i, result in enumerate(results, 1):
                            snippet = result.get('snippet', '')[:80] + '...' if len(result.get('snippet', '')) > 80 else result.get('snippet', '')
                            table.add_row(str(i), result.get('title', ''), snippet)
                        
                        self.console.print(table)
                        self.console.print(f"\n[dim]Use /browse <url> to fetch full page content[/dim]")
                        self.clan["jade"].set_ready()
                    else:
                        self.console.print("[yellow]⚠️  Usage: /search <query>[/yellow]")
                        self.console.print("[dim]   Example: /search Python tutorials[/dim]")
                
                elif command == "/research":
                    if args:
                        self.clan["jade"].set_busy(f"Researching: {args[:40]}...")
                        with self.console.status(f"[cyan]📚 Jade is researching '{args}'...[/cyan]"):
                            report = self.browser.research(args, depth=2)
                        
                        self.console.print(f"\n{report}")
                        self.clan["jade"].set_ready()
                    else:
                        self.console.print("[yellow]⚠️  Usage: /research <topic>[/yellow]")
                        self.console.print("[dim]   Example: /research machine learning basics[/dim]")
                
                elif command == "/browser-history":
                    history = self.browser.get_history()
                    if history:
                        table = Table(title="🌐 Browser History")
                        table.add_column("Time", style="dim", width=8)
                        table.add_column("Title", style="cyan")
                        table.add_column("URL", style="blue")
                        
                        for page in history[-10:]:  # Last 10
                            from datetime import datetime
                            time_str = datetime.fromtimestamp(page.timestamp).strftime("%H:%M")
                            title = page.title[:40] + '...' if len(page.title) > 40 else page.title
                            url = page.url[:50] + '...' if len(page.url) > 50 else page.url
                            table.add_row(time_str, title, url)
                        
                        self.console.print(table)
                        self.console.print(f"\n[dim]Total pages visited: {len(history)}[/dim]")
                    else:
                        self.console.print("[dim]No browsing history yet[/dim]")
                        self.console.print("[dim]Try /search or /browse to start exploring[/dim]")
                
                elif command == "/browser-clear":
                    self.browser.clear_history()
                    self.console.print("[green]✅ Browser history cleared[/green]")
                
                # ============ Clan Creator Commands ============
                elif command == "/clan-create":
                    if args:
                        self.console.print("[cyan]🎭 Generating clan member...[/cyan]")
                        
                        # Update existing members list
                        self.clan_creator.existing_members = list(self.clan.keys())
                        
                        # Generate preview
                        preview = self.clan_creator.preview_creation(args)
                        self.console.print(preview)
                        
                        # Store for confirmation
                        self.pending_clan_creation = self.clan_creator.create_from_description(args)
                        
                        if self.pending_clan_creation:
                            self.console.print(f"\n[cyan]Use /clan-create-confirm to add {self.pending_clan_creation.name} to the clan![/cyan]")
                        else:
                            self.console.print("[red]❌ Failed to generate clan member[/red]")
                    else:
                        self.console.print("[yellow]⚠️  Usage: /clan-create <description>[/yellow]")
                        self.console.print("[dim]   Example: /clan-create A DevOps expert who knows Kubernetes[/dim]")
                        self.console.print("[dim]   Example: /clan-create Security specialist for penetration testing[/dim]")
                
                elif command == "/clan-create-confirm":
                    if self.pending_clan_creation:
                        template = self.pending_clan_creation
                        
                        # Create the clan member
                        new_member = ClanMember(
                            name=template.name,
                            emoji=template.emoji,
                            role=template.role,
                            color=template.color
                        )
                        
                        # Add to clan (use lowercase name as key)
                        member_key = template.name.lower()
                        self.clan[member_key] = new_member
                        
                        self.console.print(f"\n[green]✅ {template.emoji} {template.name} has joined the clan![/green]")
                        self.console.print(f"[dim]   Role: {template.role}[/dim]")
                        self.console.print(f"[dim]   Specialty: {template.specialty.title()}[/dim]")
                        self.console.print("\n[bold]Example tasks:[/bold]")
                        for task in template.example_tasks:
                            self.console.print(f"  • {task}")
                        
                        # Clear pending
                        self.pending_clan_creation = None
                        
                        # Update clan creator's list
                        self.clan_creator.existing_members = list(self.clan.keys())
                        
                        self.console.print(f"\n[cyan]The clan now has {len(self.clan)} members! 🏰[/cyan]")
                    else:
                        self.console.print("[yellow]⚠️  No pending clan member creation[/yellow]")
                        self.console.print("[dim]   Use /clan-create first to preview a new member[/dim]")
                
                elif command == "/clan-create-cancel":
                    if self.pending_clan_creation:
                        name = self.pending_clan_creation.name
                        self.pending_clan_creation = None
                        self.console.print(f"[dim]❌ Cancelled creation of {name}[/dim]")
                    else:
                        self.console.print("[dim]No pending creation to cancel[/dim]")
                
                # ============ Docker Sandbox Commands ============
                elif command == "/sandbox-status":
                    status = self.sandbox.get_status()
                    
                    table = Table(title="🐳 Docker Sandbox Status")
                    table.add_column("Property", style="cyan")
                    table.add_column("Value")
                    
                    table.add_row("Enabled", "✅ Yes" if status['enabled'] else "❌ No")
                    table.add_row("Docker Available", "✅ Yes" if status['docker_available'] else "❌ No")
                    table.add_row("Supported Languages", ", ".join(status['supported_languages']))
                    table.add_row("Default Timeout", f"{status['default_timeout']}s")
                    table.add_row("Default Memory", status['default_memory'])
                    table.add_row("Default CPU", status['default_cpu'])
                    
                    self.console.print(table)
                    
                    if not status['enabled']:
                        self.console.print("\n[yellow]⚠️  Docker not available[/yellow]")
                        self.console.print("[dim]   Install Docker: https://docs.docker.com/get-docker/[/dim]")
                        self.console.print("[dim]   Then restart Castle Wyvern[/dim]")
                
                elif command == "/sandbox-exec":
                    if args:
                        language = getattr(self, '_sandbox_lang', 'python')
                        
                        self.console.print(f"[cyan]🐳 Executing {language} code in Docker sandbox...[/cyan]")
                        self.console.print("[dim]   (This may take a moment on first run to pull image)[/dim]")
                        
                        with self.console.status("[cyan]Running in sandbox...[/cyan]"):
                            result = self.sandbox.execute(args, language=language)
                        
                        if result.success:
                            self.console.print(f"\n[green]✅ Execution successful ({result.execution_time:.2f}s)[/green]")
                            if result.stdout:
                                self.console.print("\n[bold]Output:[/bold]")
                                self.console.print(result.stdout)
                        else:
                            self.console.print(f"\n[red]❌ Execution failed[/red]")
                            if result.error_message:
                                self.console.print(f"[red]{result.error_message}[/red]")
                            if result.stderr:
                                self.console.print("\n[bold]Error output:[/bold]")
                                self.console.print(result.stderr)
                    else:
                        self.console.print("[yellow]⚠️  Usage: /sandbox-exec <code>[/yellow]")
                        self.console.print("[dim]   Example: /sandbox-exec print('Hello World')[/dim]")
                        self.console.print(f"[dim]   Current language: {getattr(self, '_sandbox_lang', 'python')}[/dim]")
                
                elif command == "/sandbox-lang":
                    if args:
                        lang = args.lower()
                        supported = self.sandbox.IMAGES.keys()
                        
                        if lang in supported:
                            self._sandbox_lang = lang
                            self.console.print(f"[green]✅ Sandbox language set to: {lang}[/green]")
                        else:
                            self.console.print(f"[red]❌ Unsupported language: {lang}[/red]")
                            self.console.print(f"[dim]   Supported: {', '.join(supported)}[/dim]")
                    else:
                        current = getattr(self, '_sandbox_lang', 'python')
                        self.console.print(f"[dim]Current language: {current}[/dim]")
                        self.console.print(f"[dim]Supported: {', '.join(self.sandbox.IMAGES.keys())}[/dim]")
                
                elif command == "/sandbox-list":
                    containers = self.sandbox.list_running_containers()
                    
                    if containers:
                        table = Table(title="🐳 Running Sandbox Containers")
                        table.add_column("ID", style="cyan", width=12)
                        table.add_column("Image", style="blue")
                        table.add_column("Status")
                        
                        for c in containers:
                            table.add_row(c['id'], c['image'], c['status'])
                        
                        self.console.print(table)
                    else:
                        self.console.print("[dim]No sandbox containers running[/dim]")
                
                elif command == "/sandbox-cleanup":
                    with self.console.status("[cyan]Cleaning up sandbox containers...[/cyan]"):
                        removed = self.sandbox.cleanup_all()
                    
                    if removed > 0:
                        self.console.print(f"[green]✅ Removed {removed} container(s)[/green]")
                    else:
                        self.console.print("[dim]No containers to clean up[/dim]")
                
                # ============ Goal-Based Agent Commands ============
                elif command == "/goal":
                    if args:
                        # Initialize goal agent if needed
                        if not self.goal_agent:
                            clan_funcs = {
                                name: lambda task, n=name: f"[{n}] Would execute: {task}"
                                for name in self.clan.keys()
                            }
                            self.goal_agent = GoalBasedAgent(clan_funcs)
                        
                        self.console.print(f"[cyan]🎯 Creating goal: {args}[/cyan]")
                        
                        # Create the goal
                        goal = self.goal_agent.create_goal(args)
                        
                        self.console.print(f"\n[bold]Goal Plan:[/bold]")
                        for st in goal.subtasks:
                            self.console.print(f"  {st.id}. [{st.assigned_to}] {st.description}")
                        
                        self.console.print(f"\n[cyan]Execute with /goal-execute {goal.id}[/cyan]")
                        self.console.print("[dim]Or check with /goal-status {goal.id}[/dim]")
                    else:
                        self.console.print("[yellow]⚠️  Usage: /goal <description>[/yellow]")
                        self.console.print("[dim]   Example: /goal Build a REST API for a todo app[/dim]")
                        self.console.print("[dim]   Example: /goal Create a Python script to analyze CSV data[/dim]")
                
                elif command == "/goal-execute":
                    if args:
                        if not self.goal_agent:
                            self.console.print("[red]❌ No goals created yet[/red]")
                            return
                        
                        goal = self.goal_agent.active_goals.get(args)
                        if not goal:
                            self.console.print(f"[red]❌ Goal {args} not found[/red]")
                            return
                        
                        self.console.print(f"[cyan]🎯 Executing goal: {goal.description}[/cyan]")
                        self.console.print(f"[dim]This will run {len(goal.subtasks)} subtasks...[/dim]\n")
                        
                        def progress(current, total, status):
                            self.console.print(f"[{current}/{total}] {status}")
                        
                        completed = self.goal_agent.execute_goal(args, progress)
                        
                        self.console.print(f"\n[green]✅ Goal completed![/green]")
                        self.console.print(f"[dim]Completed {len(completed.subtasks)} subtasks in {(completed.completed_at - completed.created_at):.1f}s[/dim]")
                    else:
                        self.console.print("[yellow]⚠️  Usage: /goal-execute <goal_id>[/yellow]")
                        self.console.print("[dim]   Use /goal-list to see active goals[/dim]")
                
                elif command == "/goal-status":
                    if args:
                        if not self.goal_agent:
                            self.console.print("[red]❌ No goals created yet[/red]")
                            return
                        
                        summary = self.goal_agent.get_goal_summary(args)
                        self.console.print(summary)
                    else:
                        if self.goal_agent:
                            active = self.goal_agent.list_active_goals()
                            if active:
                                self.console.print("[bold]Active Goals:[/bold]")
                                for goal in active:
                                    completed = sum(1 for st in goal.subtasks if st.status.value == "completed")
                                    self.console.print(f"  {goal.id}: {goal.description[:50]}... ({completed}/{len(goal.subtasks)})")
                            else:
                                self.console.print("[dim]No active goals[/dim]")
                        else:
                            self.console.print("[dim]No goals created yet[/dim]")
                
                elif command == "/goal-list":
                    if not self.goal_agent:
                        self.console.print("[dim]No goals created yet[/dim]")
                        return
                    
                    active = self.goal_agent.list_active_goals()
                    completed = self.goal_agent.list_completed_goals()
                    
                    if active:
                        self.console.print("[bold]🎯 Active Goals:[/bold]")
                        for goal in active:
                            self.console.print(f"  {goal.id}: {goal.description[:60]}")
                    
                    if completed:
                        self.console.print("\n[bold]✅ Completed Goals:[/bold]")
                        for goal in completed[-5:]:  # Last 5
                            self.console.print(f"  {goal.id}: {goal.description[:60]}")
                    
                    if not active and not completed:
                        self.console.print("[dim]No goals yet. Create one with /goal[/dim]")
                
                elif command in ["ask", "code", "review", "summarize", "plan"]:
                    if args:
                        self.route_and_respond(args)
                    else:
                        self.console.print(f"[yellow]⚠️  Please provide a {command} request.[/yellow]")
                
                else:
                    # Treat as general ask
                    self.route_and_respond(user_input)
                
                self.console.print()  # Empty line for spacing
                
            except KeyboardInterrupt:
                self.console.print("\n\n[dim]🏰 Castle Wyvern sleeps...[/dim]")
                break
            except Exception as e:
                self.console.print(f"\n[red]⚠️  Error: {str(e)}[/red]\n")


def main():
    """Entry point for Castle Wyvern CLI."""
    cli = CastleWyvernCLI()
    cli.run()


if __name__ == "__main__":
    main()