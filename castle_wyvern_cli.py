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