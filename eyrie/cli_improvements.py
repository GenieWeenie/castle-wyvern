"""
Castle Wyvern CLI Improvements
Feature 16: Enhanced command-line experience

Provides:
- Command history persistence (across sessions)
- Intelligent autocomplete
- Batch/scripting mode
- Configuration wizard
- Command aliases
- Session management
- Export/import functionality
"""

import os
import sys
import json
import readline
import atexit
from typing import Dict, List, Optional, Callable, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import re


@dataclass
class CommandAlias:
    """A command alias."""
    name: str
    command: str
    description: str = ""
    created_at: str = ""
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> "CommandAlias":
        return cls(**data)


@dataclass
class CLISession:
    """A saved CLI session."""
    name: str
    commands: List[str]
    created_at: str
    description: str = ""
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> "CLISession":
        return cls(**data)


class HistoryManager:
    """
    Manages persistent command history across sessions.
    """
    
    def __init__(self, history_file: str = None):
        if history_file is None:
            base_dir = Path.home() / ".castle_wyvern"
            base_dir.mkdir(exist_ok=True)
            history_file = str(base_dir / "history.json")
        
        self.history_file = history_file
        self.commands: List[Dict] = []
        self._load_history()
        
        # Setup readline
        self._setup_readline()
    
    def _load_history(self):
        """Load history from file."""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r") as f:
                    self.commands = json.load(f)
            except Exception:
                self.commands = []
    
    def _save_history(self):
        """Save history to file."""
        try:
            with open(self.history_file, "w") as f:
                json.dump(self.commands[-1000:], f, indent=2)  # Keep last 1000
        except Exception as e:
            print(f"[History] Error saving: {e}")
    
    def _setup_readline(self):
        """Setup readline for history navigation."""
        # Enable tab completion
        readline.parse_and_bind("tab: complete")
        
        # Load previous readline history if available
        readline_history = self.history_file.replace(".json", "_readline.txt")
        if os.path.exists(readline_history):
            try:
                readline.read_history_file(readline_history)
            except Exception:
                pass
        
        # Save readline history on exit
        atexit.register(self._save_readline_history, readline_history)
    
    def _save_readline_history(self, history_file: str):
        """Save readline history."""
        try:
            readline.write_history_file(history_file)
        except Exception:
            pass
    
    def record(self, command: str, success: bool = True, result: str = ""):
        """Record a command execution."""
        entry = {
            "command": command,
            "timestamp": datetime.now().isoformat(),
            "success": success,
            "result_preview": result[:100] if result else ""
        }
        self.commands.append(entry)
        
        # Auto-save every 10 commands
        if len(self.commands) % 10 == 0:
            self._save_history()
    
    def get_recent(self, limit: int = 50) -> List[Dict]:
        """Get recent commands."""
        return self.commands[-limit:]
    
    def search(self, query: str) -> List[Dict]:
        """Search command history."""
        query_lower = query.lower()
        return [
            cmd for cmd in self.commands
            if query_lower in cmd["command"].lower()
        ]
    
    def get_stats(self) -> Dict:
        """Get history statistics."""
        if not self.commands:
            return {"total": 0, "unique": 0}
        
        unique_commands = set(cmd["command"].split()[0] for cmd in self.commands)
        
        return {
            "total": len(self.commands),
            "unique": len(unique_commands),
            "successful": sum(1 for cmd in self.commands if cmd.get("success", True)),
            "failed": sum(1 for cmd in self.commands if not cmd.get("success", True)),
            "most_used": self._get_most_used()
        }
    
    def _get_most_used(self, limit: int = 5) -> List[Tuple[str, int]]:
        """Get most frequently used commands."""
        from collections import Counter
        
        command_names = [cmd["command"].split()[0] for cmd in self.commands]
        return Counter(command_names).most_common(limit)
    
    def clear(self):
        """Clear history."""
        self.commands = []
        self._save_history()


class AutocompleteEngine:
    """
    Intelligent autocomplete for Castle Wyvern CLI.
    """
    
    def __init__(self):
        self.commands = [
            # Basic commands
            "ask", "code", "review", "summarize", "plan",
            "status", "health", "members", "history", "memory", "help", "quit", "exit",
            
            # BMAD commands
            "/spec", "/build", "/review", "/brief",
            
            # Document commands
            "/ingest", "/docs", "/search",
            
            # Node commands
            "/nodes", "/node-add", "/tasks",
            
            # Auto-discovery
            "/discover-start", "/discover-stop", "/discover-status",
            
            # REST API
            "/api-start", "/api-stop", "/api-status",
            
            # Web Dashboard
            "/web-start", "/web-stop", "/web-status",
            
            # Plugin System
            "/plugins", "/plugin-load", "/plugin-unload", "/plugin-reload",
            "/plugin-enable", "/plugin-disable", "/plugin-info", "/hooks",
            
            # Monitoring
            "/monitor-start", "/monitor-stop", "/monitor-status",
            "/health-check", "/alerts", "/metrics", "/prometheus",
            
            # CLI Improvements (this feature)
            "/alias", "/alias-list", "/alias-remove",
            "/session-save", "/session-load", "/session-list",
            "/history", "/history-search", "/history-clear",
            "/config", "/export", "/import",
        ]
        
        self.custom_completions: List[str] = []
    
    def get_completions(self, text: str) -> List[str]:
        """Get completions for partial text."""
        if not text:
            return []
        
        text_lower = text.lower()
        
        # Match against known commands
        matches = [
            cmd for cmd in self.commands + self.custom_completions
            if cmd.lower().startswith(text_lower)
        ]
        
        return sorted(matches)
    
    def add_completion(self, text: str):
        """Add a custom completion."""
        if text not in self.custom_completions:
            self.custom_completions.append(text)
    
    def setup_readline(self, completer_func: Callable[[str, int], Optional[str]] = None):
        """Setup readline with tab completion."""
        if completer_func is None:
            def completer(text: str, state: int) -> Optional[str]:
                matches = self.get_completions(text)
                if state < len(matches):
                    return matches[state]
                return None
        
        readline.set_completer(completer_func)
        readline.parse_and_bind("tab: complete")


class AliasManager:
    """
    Manages command aliases.
    """
    
    def __init__(self, aliases_file: str = None):
        if aliases_file is None:
            base_dir = Path.home() / ".castle_wyvern"
            base_dir.mkdir(exist_ok=True)
            aliases_file = str(base_dir / "aliases.json")
        
        self.aliases_file = aliases_file
        self.aliases: Dict[str, CommandAlias] = {}
        self._load_aliases()
        
        # Add default aliases
        self._add_defaults()
    
    def _load_aliases(self):
        """Load aliases from file."""
        if os.path.exists(self.aliases_file):
            try:
                with open(self.aliases_file, "r") as f:
                    data = json.load(f)
                    self.aliases = {
                        name: CommandAlias.from_dict(alias_data)
                        for name, alias_data in data.items()
                    }
            except Exception:
                self.aliases = {}
    
    def _save_aliases(self):
        """Save aliases to file."""
        try:
            with open(self.aliases_file, "w") as f:
                data = {name: alias.to_dict() for name, alias in self.aliases.items()}
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[Aliases] Error saving: {e}")
    
    def _add_defaults(self):
        """Add default aliases if not present."""
        defaults = {
            "h": CommandAlias("h", "help", "Shortcut for help", datetime.now().isoformat()),
            "q": CommandAlias("q", "quit", "Shortcut for quit", datetime.now().isoformat()),
            "s": CommandAlias("s", "status", "Shortcut for status", datetime.now().isoformat()),
            "c": CommandAlias("c", "code", "Shortcut for code", datetime.now().isoformat()),
            "a": CommandAlias("a", "ask", "Shortcut for ask", datetime.now().isoformat()),
        }
        
        for name, alias in defaults.items():
            if name not in self.aliases:
                self.aliases[name] = alias
        
        self._save_aliases()
    
    def add(self, name: str, command: str, description: str = "") -> bool:
        """Add a new alias."""
        if not name or not command:
            return False
        
        # Validate alias name (no spaces, no special chars)
        if not re.match(r'^[a-zA-Z0-9_-]+$', name):
            return False
        
        self.aliases[name] = CommandAlias(
            name=name,
            command=command,
            description=description,
            created_at=datetime.now().isoformat()
        )
        self._save_aliases()
        return True
    
    def remove(self, name: str) -> bool:
        """Remove an alias."""
        if name in self.aliases:
            del self.aliases[name]
            self._save_aliases()
            return True
        return False
    
    def get(self, name: str) -> Optional[CommandAlias]:
        """Get an alias by name."""
        return self.aliases.get(name)
    
    def expand(self, command: str) -> str:
        """Expand an alias in a command string."""
        parts = command.split(maxsplit=1)
        if not parts:
            return command
        
        alias_name = parts[0]
        alias = self.get(alias_name)
        
        if alias:
            if len(parts) > 1:
                return f"{alias.command} {parts[1]}"
            return alias.command
        
        return command
    
    def list_all(self) -> List[CommandAlias]:
        """List all aliases."""
        return sorted(self.aliases.values(), key=lambda a: a.name)


class SessionManager:
    """
    Manages saved CLI sessions (sequences of commands).
    """
    
    def __init__(self, sessions_dir: str = None):
        if sessions_dir is None:
            base_dir = Path.home() / ".castle_wyvern"
            base_dir.mkdir(exist_ok=True)
            sessions_dir = str(base_dir / "sessions")
        
        self.sessions_dir = sessions_dir
        os.makedirs(sessions_dir, exist_ok=True)
    
    def _get_session_file(self, name: str) -> str:
        """Get file path for a session."""
        # Sanitize name
        safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', name)
        return os.path.join(self.sessions_dir, f"{safe_name}.json")
    
    def save(self, name: str, commands: List[str], description: str = ""):
        """Save a session."""
        session = CLISession(
            name=name,
            commands=commands,
            description=description,
            created_at=datetime.now().isoformat()
        )
        
        filepath = self._get_session_file(name)
        with open(filepath, "w") as f:
            json.dump(session.to_dict(), f, indent=2)
    
    def load(self, name: str) -> Optional[CLISession]:
        """Load a session."""
        filepath = self._get_session_file(name)
        
        if not os.path.exists(filepath):
            return None
        
        with open(filepath, "r") as f:
            data = json.load(f)
            return CLISession.from_dict(data)
    
    def delete(self, name: str) -> bool:
        """Delete a session."""
        filepath = self._get_session_file(name)
        
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False
    
    def list_all(self) -> List[CLISession]:
        """List all saved sessions."""
        sessions = []
        
        for filename in os.listdir(self.sessions_dir):
            if filename.endswith(".json"):
                name = filename[:-5]
                session = self.load(name)
                if session:
                    sessions.append(session)
        
        return sorted(sessions, key=lambda s: s.name)


class ConfigWizard:
    """
    Interactive configuration wizard.
    """
    
    def __init__(self, config_file: str = None):
        if config_file is None:
            base_dir = Path.home() / ".castle_wyvern"
            base_dir.mkdir(exist_ok=True)
            config_file = str(base_dir / "config.json")
        
        self.config_file = config_file
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """Load configuration."""
        defaults = {
            "ai": {
                "primary_provider": "z.ai",
                "fallback_provider": "openai",
                "timeout_seconds": 60
            },
            "ui": {
                "theme": "dark",
                "show_emojis": True,
                "compact_mode": False
            },
            "monitoring": {
                "enabled": True,
                "interval_seconds": 30,
                "alerts_enabled": True
            },
            "memory": {
                "max_entries": 10000,
                "auto_summarize": True
            }
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    loaded = json.load(f)
                    # Merge with defaults
                    for key, value in defaults.items():
                        if key not in loaded:
                            loaded[key] = value
                        elif isinstance(value, dict):
                            for subkey, subvalue in value.items():
                                if subkey not in loaded[key]:
                                    loaded[key][subkey] = subvalue
                    return loaded
            except Exception:
                pass
        
        return defaults
    
    def save_config(self):
        """Save configuration."""
        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=2)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a config value using dot notation."""
        keys = key.split(".")
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Set a config value using dot notation."""
        keys = key.split(".")
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        self.save_config()
    
    def run_wizard(self, console):
        """Run interactive configuration wizard."""
        from rich.panel import Panel
        from rich.prompt import Prompt, Confirm
        
        console.print(Panel.fit("⚙️  Castle Wyvern Configuration Wizard", style="cyan"))
        console.print()
        
        # AI Provider settings
        console.print("[bold]AI Provider Settings[/bold]")
        providers = ["z.ai", "openai", "ollama", "anthropic"]
        current = self.get("ai.primary_provider")
        console.print(f"Current primary provider: {current}")
        
        if Confirm.ask("Change primary AI provider?", default=False):
            for i, provider in enumerate(providers, 1):
                console.print(f"  {i}. {provider}")
            
            choice = Prompt.ask("Select provider", choices=[str(i) for i in range(1, len(providers)+1)])
            self.set("ai.primary_provider", providers[int(choice)-1])
            console.print(f"[green]✅ Primary provider set to: {providers[int(choice)-1]}[/green]")
        
        # UI settings
        console.print("\n[bold]UI Settings[/bold]")
        
        if Confirm.ask("Enable compact mode?", default=self.get("ui.compact_mode")):
            self.set("ui.compact_mode", True)
        else:
            self.set("ui.compact_mode", False)
        
        # Monitoring settings
        console.print("\n[bold]Monitoring Settings[/bold]")
        
        if Confirm.ask("Enable monitoring?", default=self.get("monitoring.enabled")):
            self.set("monitoring.enabled", True)
            
            interval = Prompt.ask(
                "Monitoring interval (seconds)",
                default=str(self.get("monitoring.interval_seconds")),
                show_default=True
            )
            self.set("monitoring.interval_seconds", int(interval))
        else:
            self.set("monitoring.enabled", False)
        
        console.print("\n[green]✅ Configuration saved![/green]")


class ExportImportManager:
    """
    Handles export and import of Castle Wyvern data.
    """
    
    def __init__(self, base_dir: str = None):
        if base_dir is None:
            base_dir = str(Path.home() / ".castle_wyvern")
        
        self.base_dir = base_dir
    
    def export_all(self, output_file: str) -> bool:
        """Export all data to a JSON file."""
        try:
            export_data = {
                "version": "0.2.0",
                "exported_at": datetime.now().isoformat(),
                "data": {}
            }
            
            # Export config
            config_file = os.path.join(self.base_dir, "config.json")
            if os.path.exists(config_file):
                with open(config_file, "r") as f:
                    export_data["data"]["config"] = json.load(f)
            
            # Export aliases
            aliases_file = os.path.join(self.base_dir, "aliases.json")
            if os.path.exists(aliases_file):
                with open(aliases_file, "r") as f:
                    export_data["data"]["aliases"] = json.load(f)
            
            # Export history
            history_file = os.path.join(self.base_dir, "history.json")
            if os.path.exists(history_file):
                with open(history_file, "r") as f:
                    export_data["data"]["history"] = json.load(f)
            
            # Export sessions
            sessions_dir = os.path.join(self.base_dir, "sessions")
            if os.path.exists(sessions_dir):
                export_data["data"]["sessions"] = {}
                for filename in os.listdir(sessions_dir):
                    if filename.endswith(".json"):
                        filepath = os.path.join(sessions_dir, filename)
                        with open(filepath, "r") as f:
                            export_data["data"]["sessions"][filename[:-5]] = json.load(f)
            
            # Write export file
            with open(output_file, "w") as f:
                json.dump(export_data, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"[Export] Error: {e}")
            return False
    
    def import_all(self, input_file: str, merge: bool = True) -> bool:
        """Import data from a JSON file."""
        try:
            with open(input_file, "r") as f:
                import_data = json.load(f)
            
            if "data" not in import_data:
                print("[Import] Invalid export file format")
                return False
            
            data = import_data["data"]
            
            # Import config
            if "config" in data:
                config_file = os.path.join(self.base_dir, "config.json")
                with open(config_file, "w") as f:
                    json.dump(data["config"], f, indent=2)
            
            # Import aliases
            if "aliases" in data:
                aliases_file = os.path.join(self.base_dir, "aliases.json")
                if merge and os.path.exists(aliases_file):
                    with open(aliases_file, "r") as f:
                        existing = json.load(f)
                    existing.update(data["aliases"])
                    data["aliases"] = existing
                
                with open(aliases_file, "w") as f:
                    json.dump(data["aliases"], f, indent=2)
            
            # Import history (append if merging)
            if "history" in data:
                history_file = os.path.join(self.base_dir, "history.json")
                if merge and os.path.exists(history_file):
                    with open(history_file, "r") as f:
                        existing = json.load(f)
                    existing.extend(data["history"])
                    data["history"] = existing[-1000:]  # Keep last 1000
                
                with open(history_file, "w") as f:
                    json.dump(data["history"], f, indent=2)
            
            # Import sessions
            if "sessions" in data:
                sessions_dir = os.path.join(self.base_dir, "sessions")
                os.makedirs(sessions_dir, exist_ok=True)
                
                for name, session_data in data["sessions"].items():
                    filepath = os.path.join(sessions_dir, f"{name}.json")
                    with open(filepath, "w") as f:
                        json.dump(session_data, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"[Import] Error: {e}")
            return False


class CLIImprovements:
    """
    Main class integrating all CLI improvements.
    """
    
    def __init__(self):
        self.history = HistoryManager()
        self.autocomplete = AutocompleteEngine()
        self.aliases = AliasManager()
        self.sessions = SessionManager()
        self.config = ConfigWizard()
        self.export_import = ExportImportManager()
        
        # Setup autocomplete
        self.autocomplete.setup_readline()
    
    def expand_command(self, command: str) -> str:
        """Expand aliases in a command."""
        return self.aliases.expand(command)
    
    def record_command(self, command: str, success: bool = True, result: str = ""):
        """Record a command execution."""
        self.history.record(command, success, result)


# Standalone test
if __name__ == "__main__":
    print("🏰 Castle Wyvern CLI Improvements Test")
    print("=" * 50)
    
    cli = CLIImprovements()
    
    print("\n✅ CLI Improvements initialized!")
    print(f"History entries: {len(cli.history.commands)}")
    print(f"Aliases: {len(cli.aliases.aliases)}")
    print(f"Config keys: {list(cli.config.config.keys())}")
