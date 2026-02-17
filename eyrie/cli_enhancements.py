"""
Castle Wyvern CLI Enhancements
================================
Provides tab completion, command history persistence, and better error messages.

Features:
- Auto-complete for all 37+ commands
- Better error messages with suggestions using difflib
- Persistent command history between sessions
- Tab completion for clan member names
"""

import os
import sys
import difflib
from pathlib import Path
from typing import Generator, List, Optional, Set, Dict, Any, Tuple, cast

# Try to import prompt_toolkit, fall back to basic implementation
try:
    from prompt_toolkit import PromptSession
    from prompt_toolkit.completion import Completer, Completion
    from prompt_toolkit.history import FileHistory
    from prompt_toolkit.key_binding import KeyBindings

    PROMPT_TOOLKIT_AVAILABLE = True
except ImportError:
    PROMPT_TOOLKIT_AVAILABLE = False
    Completer = object  # Base class fallback
    Completion = object  # Type fallback
    # We'll use a basic readline fallback
    import readline


class CommandCompleter(Completer):
    """Custom completer for Castle Wyvern CLI commands."""

    # All available commands
    COMMANDS: List[str] = [
        # Basic commands
        "help",
        "status",
        "health",
        "members",
        "history",
        "memory",
        "quit",
        "exit",
        "bye",
        # Direct clan access
        "ask",
        "code",
        "review",
        "summarize",
        "plan",
        # BMAD Workflow
        "/spec",
        "/build",
        "/brief",
        # Document commands
        "/ingest",
        "/docs",
        "/search",
        # Node commands
        "/nodes",
        "/node-add",
        "/tasks",
        # Auto-discovery
        "/discover-start",
        "/discover-stop",
        "/discover-status",
        # REST API
        "/api-start",
        "/api-stop",
        "/api-status",
        # Web Dashboard
        "/web-start",
        "/web-stop",
        "/web-status",
        # Plugin System
        "/plugins",
        "/plugin-load",
        "/plugin-unload",
        "/plugin-reload",
        "/plugin-enable",
        "/plugin-disable",
        "/plugin-info",
        "/hooks",
        # Monitoring
        "/monitor-start",
        "/monitor-stop",
        "/monitor-status",
        "/health-check",
        "/alerts",
        "/metrics",
        "/prometheus",
        # CLI Improvements
        "/alias",
        "/alias-list",
        "/alias-remove",
        "/session-save",
        "/session-load",
        "/session-list",
        "/history-search",
        "/history-clear",
        "/config",
        "/export",
        "/import",
        # Integrations
        "/integrations",
        "/slack-config",
        "/discord-config",
        "/slack-test",
        "/discord-test",
        "/alert",
        "/webhook-start",
        "/webhook-stop",
        # Security
        "/security-status",
        "/audit-log",
        "/audit-search",
        "/audit-export",
        "/apikey-create",
        "/apikey-list",
        "/apikey-revoke",
        "/security-scan",
        "/intrusion-check",
        # Enhanced Memory
        "/memory-add",
        "/memory-search",
        "/memory-context",
        "/memory-stats",
        "/memory-consolidate",
        # Browser Agent
        "/browse",
        "/research",
        "/browser-history",
        "/browser-clear",
        # Clan Creator
        "/clan-create",
        "/clan-create-confirm",
        "/clan-create-cancel",
        # Docker Sandbox
        "/sandbox-status",
        "/sandbox-exec",
        "/sandbox-lang",
        "/sandbox-list",
        "/sandbox-cleanup",
        # Goal-Based Agent
        "/goal",
        "/goal-status",
        "/goal-list",
        "/goal-execute",
        # Function Builder
        "/function-create",
        "/function-list",
        "/function-packs",
        "/function-search",
        "/function-show",
        # llama.cpp
        "/llama-status",
        "/llama-models",
        # Clan Backstories
        "/backstory",
        "/personalities",
        # nanoGPT
        "/nanogpt-create",
        "/nanogpt-train",
        "/nanogpt-list",
        "/nanogpt-sample",
        # Knowledge Graph
        "/kg-status",
        "/kg-add-entity",
        "/kg-add-rel",
        "/kg-query",
        "/kg-reason",
        "/kg-extract",
        "/kg-visualize",
        "/kg-export",
        "/kg-path",
        "/kg-report",
        # Visual Automation
        "/visual-status",
        "/visual-scan",
        "/visual-click",
        "/visual-type",
        "/visual-browser-start",
        "/visual-browser-task",
        "/visual-browser-end",
        "/visual-macro-login",
        "/visual-debug",
        "/visual-sessions",
        "/visual-replay",
        # Agent Coordination
        "/coord-status",
        "/coord-team",
        "/coord-run",
        "/coord-agents",
        "/coord-agent",
        "/coord-analytics",
        "/coord-optimize",
        "/coord-report",
        "/coord-compare",
        # Stretch Goals
        "/ai-optimize",
        "/ai-stats",
        "/perf-stats",
        "/perf-optimize",
        "/docs-generate",
        "/docs-export",
        # Visual Workflow Builder
        "/workflow-list",
        "/workflow-create",
        "/workflow-open",
        "/workflow-run",
        "/workflow-delete",
        "/workflow-export",
        "/workflow-import",
        "/workflow-template",
        # MCP Protocol
        "/mcp-start",
        "/mcp-stop",
        "/mcp-tools",
        "/mcp-install",
        # A2A Protocol
        "/a2a-start",
        "/a2a-stop",
        "/a2a-discover",
        "/a2a-agents",
        "/a2a-delegate",
    ]

    # Clan member names for tab completion
    CLAN_MEMBERS: List[str] = [
        "goliath",
        "lexington",
        "brooklyn",
        "broadway",
        "hudson",
        "bronx",
        "elisa",
        "xanatos",
        "demona",
        "jade",
    ]

    # Commands that accept member names as arguments
    MEMBER_COMMANDS: Set[str] = {"/clan", "/coord-agent", "/backstory", "/nanogpt-create"}

    def __init__(self):
        self.commands = self.COMMANDS
        self.members = self.CLAN_MEMBERS
        self.member_commands = self.MEMBER_COMMANDS

    def get_completions(self, document: Any, complete_event: Any) -> Generator[Completion, None, None]:
        """Generate completions based on current input."""
        text = document.text_before_cursor
        words = text.split()

        if not words:
            # No input yet, show all commands
            for cmd in self.commands:
                yield Completion(cmd, start_position=0)
            return

        # Check if we're completing a command or an argument
        if len(words) == 1 and not text.endswith(" "):
            # Completing the first word (command)
            for cmd in self.commands:
                if cmd.startswith(words[0]):
                    yield Completion(
                        cmd,
                        start_position=-len(words[0]),
                        display_meta=self._get_command_description(cmd),
                    )
        else:
            # Completing arguments - check for member name completion
            command = words[0] if words else ""
            current_word = words[-1] if words and not text.endswith(" ") else ""

            # Check if this command might take a member name
            if any(command.startswith(cmd) for cmd in self.member_commands):
                for member in self.members:
                    if member.startswith(current_word.lower()):
                        yield Completion(
                            member, start_position=-len(current_word), display_meta="Clan Member"
                        )

            # Also complete command if we're on the first word with a space after
            if text.endswith(" ") and len(words) == 1:
                # Show all members as possible completions for member commands
                if any(command.startswith(cmd) for cmd in self.member_commands):
                    for member in self.members:
                        yield Completion(member, start_position=0, display_meta="Clan Member")

    def _get_command_description(self, command: str) -> Optional[str]:
        """Get a short description for a command."""
        descriptions = {
            "help": "Show help information",
            "status": "Show full dashboard",
            "health": "Check Phoenix Gate status",
            "members": "List all clan members",
            "history": "Show conversation history",
            "quit": "Leave Castle Wyvern",
            "ask": "Ask the clan a question",
            "code": "Request code from Lexington",
            "review": "Request code review from Xanatos",
            "summarize": "Request summary from Broadway",
            "plan": "Request architecture from Brooklyn",
            "/spec": "Quick technical spec",
            "/build": "Implementation workflow",
            "/kg-status": "Knowledge graph statistics",
            "/coord-status": "Coordination system status",
            "/mcp-start": "Start MCP server",
            "/a2a-start": "Start A2A server",
        }
        return descriptions.get(command)


class CLIHistoryManager:
    """Manages persistent command history."""

    def __init__(self, history_dir: str = "~/.castle_wyvern"):
        self.history_dir = Path(history_dir).expanduser()
        self.history_file = self.history_dir / "history.txt"
        self._ensure_history_dir()

    def _ensure_history_dir(self):
        """Ensure the history directory exists."""
        self.history_dir.mkdir(parents=True, exist_ok=True)

    def get_history_file(self) -> str:
        """Get the path to the history file."""
        return str(self.history_file)

    def add_command(self, command: str):
        """Add a command to history."""
        if command.strip():
            with open(self.history_file, "a") as f:
                f.write(f"{command}\n")

    def load_history(self) -> List[str]:
        """Load all history entries."""
        if not self.history_file.exists():
            return []

        try:
            with open(self.history_file, "r") as f:
                return [line.strip() for line in f if line.strip()]
        except Exception:
            return []

    def clear_history(self):
        """Clear all history."""
        if self.history_file.exists():
            self.history_file.write_text("")


class ErrorSuggester:
    """Provides intelligent error suggestions using difflib."""

    def __init__(self, valid_commands: List[str]):
        self.valid_commands = valid_commands

    def suggest(self, invalid_command: str, cutoff: float = 0.6) -> Optional[str]:
        """
        Suggest the closest matching valid command.

        Args:
            invalid_command: The command the user typed
            cutoff: Minimum similarity ratio (0.0 to 1.0)

        Returns:
            The closest matching command or None
        """
        matches = difflib.get_close_matches(
            invalid_command, self.valid_commands, n=1, cutoff=cutoff
        )
        return matches[0] if matches else None

    def get_suggestions(self, invalid_command: str, n: int = 3, cutoff: float = 0.4) -> List[str]:
        """
        Get multiple suggestions for an invalid command.

        Args:
            invalid_command: The command the user typed
            n: Maximum number of suggestions
            cutoff: Minimum similarity ratio

        Returns:
            List of suggested commands
        """
        return difflib.get_close_matches(invalid_command, self.valid_commands, n=n, cutoff=cutoff)

    def format_error_message(self, invalid_command: str) -> str:
        """
        Format a helpful error message with suggestions.

        Args:
            invalid_command: The command the user typed

        Returns:
            Formatted error message
        """
        suggestions = self.get_suggestions(invalid_command, n=3, cutoff=0.4)

        if not suggestions:
            return f"Unknown command: '{invalid_command}'. Type 'help' for available commands."

        if len(suggestions) == 1:
            return f"Unknown command: '{invalid_command}'. Did you mean '{suggestions[0]}'?"

        suggestions_str = "', '".join(suggestions)
        return f"Unknown command: '{invalid_command}'. Did you mean one of: '{suggestions_str}'?"


class EnhancedPrompt:
    """
    Enhanced prompt session with tab completion and history.
    Falls back to basic input if prompt_toolkit is not available.
    """

    def __init__(self, console=None):
        self.console = console
        self.history_manager = CLIHistoryManager()
        self.completer = CommandCompleter()
        self.error_suggester = ErrorSuggester(self.completer.commands)

        self.session = None
        self._init_session()

    def _init_session(self):
        """Initialize the prompt session."""
        if PROMPT_TOOLKIT_AVAILABLE:
            try:
                history = FileHistory(self.history_manager.get_history_file())
                self.session = PromptSession(
                    history=history,
                    completer=self.completer,
                    complete_while_typing=True,
                    enable_history_search=True,
                )
            except Exception as e:
                print(f"Warning: Could not initialize prompt_toolkit: {e}")
                self.session = None

        # Fallback to readline if prompt_toolkit is not available
        if self.session is None and not PROMPT_TOOLKIT_AVAILABLE:
            self._setup_readline()

    def _setup_readline(self):
        """Setup readline for basic tab completion and history."""
        try:
            # Load history
            history_file = self.history_manager.get_history_file()
            if os.path.exists(history_file):
                readline.read_history_file(history_file)

            # Set history length
            readline.set_history_length(1000)

            # Enable tab completion
            readline.parse_and_bind("tab: complete")

            # Set up completer
            def completer(text, state):
                options = [cmd for cmd in self.completer.commands if cmd.startswith(text)]
                if state < len(options):
                    return options[state]
                return None

            readline.set_completer(completer)

        except Exception as e:
            print(f"Warning: Could not setup readline: {e}")

    def prompt(self, message: str = "> ") -> str:
        """
        Show prompt and get user input.

        Args:
            message: The prompt message to display

        Returns:
            User input string
        """
        if self.session and PROMPT_TOOLKIT_AVAILABLE:
            try:
                return cast(str, self.session.prompt(message))
            except KeyboardInterrupt:
                raise
            except EOFError:
                raise
            except Exception as e:
                # Fall back to basic input on error
                if self.console:
                    self.console.print(f"[dim]Prompt error: {e}. Using basic input.[/dim]")
                return cast(str, input(message))
        else:
            return cast(str, input(message))

    def save_history(self):
        """Save command history to file (readline fallback)."""
        if not PROMPT_TOOLKIT_AVAILABLE:
            try:
                history_file = self.history_manager.get_history_file()
                readline.write_history_file(history_file)
            except Exception:
                pass

    def get_error_suggestion(self, invalid_command: str) -> str:
        """
        Get a helpful error message for an invalid command.

        Args:
            invalid_command: The command the user typed

        Returns:
            Formatted error message with suggestions
        """
        return cast(str, self.error_suggester.format_error_message(invalid_command))

    def is_valid_command(self, command: str) -> bool:
        """
        Check if a command is valid.

        Args:
            command: The command to check

        Returns:
            True if valid, False otherwise
        """
        if not command:
            return True  # Empty is fine (will just show prompt again)

        cmd_lower = command.lower().split()[0]
        return cmd_lower in [c.lower() for c in self.completer.commands]


def create_enhanced_prompt(console=None) -> EnhancedPrompt:
    """
    Factory function to create an enhanced prompt session.

    Args:
        console: Optional Rich console for styled output

    Returns:
        EnhancedPrompt instance
    """
    return EnhancedPrompt(console)


# Export the main classes and functions
__all__ = [
    "CommandCompleter",
    "CLIHistoryManager",
    "ErrorSuggester",
    "EnhancedPrompt",
    "create_enhanced_prompt",
    "PROMPT_TOOLKIT_AVAILABLE",
]
