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
        self.bmad = BMADWorkflow(self.console, self.phoenix_gate, self.grimoorum)
        self.documents = DocumentIngestion()
        self.nodes = NodeManager()
        
        # Feature 11: Auto-Discovery
        self.auto_discovery = None
        
        # Feature 12: REST API
        self.api_server = None
        
        # Feature 13: Web Dashboard
        self.web_dashboard = None
        
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