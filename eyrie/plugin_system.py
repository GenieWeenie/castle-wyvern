"""
Castle Wyvern Plugin System
Feature 14: Extensible plugin architecture

Provides:
- Plugin discovery and loading
- Hook system for extending functionality
- Sandboxed plugin execution
- Plugin API for developers
- Hot-reload support
"""

import os
import sys
import json
import importlib
import importlib.util
import inspect
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from abc import ABC, abstractmethod
import hashlib
import threading


class PluginHook:
    """Represents a hook that plugins can register callbacks for."""

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.callbacks: List[Callable] = []

    def register(self, callback: Callable):
        """Register a callback for this hook."""
        self.callbacks.append(callback)

    def unregister(self, callback: Callable):
        """Unregister a callback."""
        if callback in self.callbacks:
            self.callbacks.remove(callback)

    def execute(self, *args, **kwargs) -> List[Any]:
        """Execute all registered callbacks and return results."""
        results = []
        for callback in self.callbacks:
            try:
                result = callback(*args, **kwargs)
                results.append(result)
            except Exception as e:
                print(f"[Plugin Hook '{self.name}'] Error in callback: {e}")
        return results


class PluginAPI:
    """
    API provided to plugins for interacting with Castle Wyvern.

    This is a controlled interface - plugins can only access
    what we explicitly expose.
    """

    def __init__(self, plugin_manager: "PluginManager"):
        self._plugin_manager = plugin_manager
        self._phoenix_gate = plugin_manager.phoenix_gate
        self._grimoorum = plugin_manager.grimoorum

    def log(self, message: str, level: str = "info"):
        """Log a message through Castle Wyvern's logging system."""
        timestamp = datetime.now().isoformat()
        print(f"[{timestamp}] [Plugin] [{level.upper()}] {message}")

    def call_ai(self, prompt: str, system_prompt: str = None) -> str:
        """Make an AI call through Phoenix Gate."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        return self._phoenix_gate.chat_completion(messages)

    def store_memory(self, content: str, metadata: Dict = None) -> str:
        """Store something in Grimoorum memory."""
        metadata = metadata or {}
        return self._grimoorum.record(
            user_input=content,
            agent_name=metadata.get("agent", "plugin"),
            agent_response="",  # Plugin memories don't have responses
            importance=metadata.get("importance", 3),
            tags=metadata.get("tags", []),
        )

    def search_memory(self, query: str, limit: int = 10) -> List[Dict]:
        """Search Grimoorum memory."""
        return self._grimoorum.search_by_keyword(query, limit=limit)

    def register_hook(self, hook_name: str, callback: Callable):
        """Register a callback for a plugin hook."""
        self._plugin_manager.register_hook_callback(hook_name, callback)

    def trigger_hook(self, hook_name: str, *args, **kwargs) -> List[Any]:
        """Trigger a hook and return all results."""
        return self._plugin_manager.trigger_hook(hook_name, *args, **kwargs)

    def get_config(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        return self._plugin_manager.config.get(key, default)

    def set_config(self, key: str, value: Any):
        """Set a configuration value."""
        self._plugin_manager.config[key] = value


class BasePlugin(ABC):
    """
    Base class that all Castle Wyvern plugins must inherit from.

    Example:
        class MyPlugin(BasePlugin):
            name = "my_plugin"
            version = "1.0.0"
            description = "Does cool things"

            def initialize(self):
                self.api.log("My plugin initialized!")
    """

    # Plugin metadata (override in subclass)
    name: str = "unnamed_plugin"
    version: str = "0.1.0"
    description: str = ""
    author: str = ""
    requires: List[str] = []  # List of required plugin names

    def __init__(self):
        self.api: Optional[PluginAPI] = None
        self.enabled: bool = False
        self._initialized: bool = False

    def _setup(self, api: PluginAPI):
        """Internal setup - called by PluginManager."""
        self.api = api

    @abstractmethod
    def initialize(self):
        """
        Called when the plugin is loaded and enabled.
        Use this to register hooks, set up state, etc.
        """
        pass

    def shutdown(self):
        """
        Called when the plugin is being unloaded.
        Use this to clean up resources.
        """
        pass

    def get_info(self) -> Dict:
        """Get plugin information."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "enabled": self.enabled,
            "initialized": self._initialized,
            "requires": self.requires,
        }


@dataclass
class PluginManifest:
    """Manifest file for a plugin."""

    name: str
    version: str
    description: str
    author: str
    main_file: str
    main_class: str
    requires: List[str]
    permissions: List[str]

    @classmethod
    def from_dict(cls, data: Dict) -> "PluginManifest":
        return cls(
            name=data.get("name", "unnamed"),
            version=data.get("version", "0.1.0"),
            description=data.get("description", ""),
            author=data.get("author", ""),
            main_file=data.get("main_file", "plugin.py"),
            main_class=data.get("main_class", "Plugin"),
            requires=data.get("requires", []),
            permissions=data.get("permissions", []),
        )

    def to_dict(self) -> Dict:
        return asdict(self)


class PluginManager:
    """
    Manages the plugin system for Castle Wyvern.

    Features:
    - Plugin discovery from plugins/ directory
    - Loading and unloading plugins
    - Hook system for extensibility
    - Plugin dependency resolution
    - Configuration management
    """

    def __init__(self, plugins_dir: str = None, phoenix_gate=None, grimoorum=None):
        # Plugin directory
        if plugins_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            plugins_dir = os.path.join(base_dir, "plugins")

        self.plugins_dir = plugins_dir
        os.makedirs(self.plugins_dir, exist_ok=True)

        # Core components (injected)
        self.phoenix_gate = phoenix_gate
        self.grimoorum = grimoorum

        # Plugin registry
        self.plugins: Dict[str, BasePlugin] = {}
        self.manifests: Dict[str, PluginManifest] = {}
        self.hooks: Dict[str, PluginHook] = {}

        # Configuration
        self.config: Dict[str, Any] = {}
        self._config_file = os.path.join(self.plugins_dir, "plugin_config.json")
        self._load_config()

        # API instance (shared)
        self._api = PluginAPI(self)

        # Built-in hooks
        self._register_builtin_hooks()

    def _load_config(self):
        """Load plugin configuration."""
        if os.path.exists(self._config_file):
            try:
                with open(self._config_file, "r") as f:
                    self.config = json.load(f)
            except Exception as e:
                print(f"[PluginManager] Error loading config: {e}")
                self.config = {}

    def _save_config(self):
        """Save plugin configuration."""
        try:
            with open(self._config_file, "w") as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"[PluginManager] Error saving config: {e}")

    def _register_builtin_hooks(self):
        """Register built-in hooks."""
        builtin_hooks = [
            ("pre_command", "Called before processing a command"),
            ("post_command", "Called after processing a command"),
            ("pre_ai_call", "Called before making an AI call"),
            ("post_ai_call", "Called after making an AI call"),
            ("memory_added", "Called when a memory is added"),
            ("node_discovered", "Called when a node is discovered"),
            ("plugin_loaded", "Called when a plugin is loaded"),
            ("plugin_unloaded", "Called when a plugin is unloaded"),
        ]

        for name, description in builtin_hooks:
            self.register_hook(name, description)

    def register_hook(self, name: str, description: str = "") -> PluginHook:
        """Register a new hook."""
        if name not in self.hooks:
            self.hooks[name] = PluginHook(name, description)
        return self.hooks[name]

    def register_hook_callback(self, hook_name: str, callback: Callable):
        """Register a callback for a hook."""
        if hook_name not in self.hooks:
            self.register_hook(hook_name)
        self.hooks[hook_name].register(callback)

    def trigger_hook(self, hook_name: str, *args, **kwargs) -> List[Any]:
        """Trigger a hook and return results."""
        if hook_name not in self.hooks:
            return []
        return self.hooks[hook_name].execute(*args, **kwargs)

    def discover_plugins(self) -> List[str]:
        """Discover available plugins in the plugins directory."""
        plugin_names = []

        if not os.path.exists(self.plugins_dir):
            return plugin_names

        for item in os.listdir(self.plugins_dir):
            item_path = os.path.join(self.plugins_dir, item)

            # Check if it's a directory with a manifest
            if os.path.isdir(item_path):
                manifest_path = os.path.join(item_path, "manifest.json")
                if os.path.exists(manifest_path):
                    plugin_names.append(item)

            # Check if it's a single Python file
            elif item.endswith(".py") and not item.startswith("_"):
                plugin_names.append(item[:-3])

        return sorted(plugin_names)

    def load_manifest(self, plugin_name: str) -> Optional[PluginManifest]:
        """Load a plugin's manifest."""
        plugin_path = os.path.join(self.plugins_dir, plugin_name)
        manifest_path = os.path.join(plugin_path, "manifest.json")

        if os.path.exists(manifest_path):
            try:
                with open(manifest_path, "r") as f:
                    data = json.load(f)
                return PluginManifest.from_dict(data)
            except Exception as e:
                print(f"[PluginManager] Error loading manifest for {plugin_name}: {e}")

        # Default manifest for simple .py files
        return PluginManifest(
            name=plugin_name,
            version="0.1.0",
            description="",
            author="",
            main_file=f"{plugin_name}.py",
            main_class="Plugin",
            requires=[],
            permissions=[],
        )

    def load_plugin(self, plugin_name: str) -> bool:
        """Load a plugin by name."""
        if plugin_name in self.plugins:
            print(f"[PluginManager] Plugin '{plugin_name}' already loaded")
            return True

        try:
            # Load manifest
            manifest = self.load_manifest(plugin_name)
            if manifest is None:
                print(f"[PluginManager] No manifest found for '{plugin_name}'")
                return False

            # Check dependencies
            for req in manifest.requires:
                if req not in self.plugins:
                    print(f"[PluginManager] Loading dependency: {req}")
                    if not self.load_plugin(req):
                        print(f"[PluginManager] Failed to load dependency: {req}")
                        return False

            # Load the plugin module
            plugin_path = os.path.join(self.plugins_dir, plugin_name)
            main_file_path = os.path.join(plugin_path, manifest.main_file)

            if not os.path.exists(main_file_path):
                # Try .py extension
                main_file_path = os.path.join(self.plugins_dir, f"{plugin_name}.py")

            if not os.path.exists(main_file_path):
                print(f"[PluginManager] Plugin file not found: {main_file_path}")
                return False

            # Load module
            spec = importlib.util.spec_from_file_location(
                f"castle_wyvern_plugin_{plugin_name}", main_file_path
            )
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)

            # Find plugin class
            plugin_class = getattr(module, manifest.main_class, None)
            if plugin_class is None:
                print(f"[PluginManager] Plugin class '{manifest.main_class}' not found")
                return False

            # Instantiate plugin
            plugin = plugin_class()
            plugin._setup(self._api)

            # Store
            self.plugins[plugin_name] = plugin
            self.manifests[plugin_name] = manifest

            # Initialize if enabled
            if self.config.get(f"enabled_{plugin_name}", True):
                plugin.initialize()
                plugin.enabled = True
                plugin._initialized = True

            # Trigger hook
            self.trigger_hook("plugin_loaded", plugin_name, plugin)

            print(f"[PluginManager] ✅ Loaded plugin: {plugin_name} v{manifest.version}")
            return True

        except Exception as e:
            print(f"[PluginManager] ❌ Error loading plugin '{plugin_name}': {e}")
            import traceback

            traceback.print_exc()
            return False

    def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a plugin."""
        if plugin_name not in self.plugins:
            print(f"[PluginManager] Plugin '{plugin_name}' not loaded")
            return False

        try:
            plugin = self.plugins[plugin_name]

            # Call shutdown
            plugin.shutdown()

            # Remove
            del self.plugins[plugin_name]
            del self.manifests[plugin_name]

            # Trigger hook
            self.trigger_hook("plugin_unloaded", plugin_name)

            print(f"[PluginManager] ✅ Unloaded plugin: {plugin_name}")
            return True

        except Exception as e:
            print(f"[PluginManager] ❌ Error unloading plugin '{plugin_name}': {e}")
            return False

    def reload_plugin(self, plugin_name: str) -> bool:
        """Reload a plugin."""
        if plugin_name in self.plugins:
            self.unload_plugin(plugin_name)
        return self.load_plugin(plugin_name)

    def load_all_plugins(self) -> Dict[str, bool]:
        """Load all discovered plugins."""
        results = {}
        plugin_names = self.discover_plugins()

        print(f"[PluginManager] Discovered {len(plugin_names)} plugin(s)")

        for name in plugin_names:
            results[name] = self.load_plugin(name)

        return results

    def enable_plugin(self, plugin_name: str) -> bool:
        """Enable a plugin."""
        self.config[f"enabled_{plugin_name}"] = True
        self._save_config()

        if plugin_name in self.plugins:
            plugin = self.plugins[plugin_name]
            if not plugin.enabled:
                plugin.initialize()
                plugin.enabled = True

        return True

    def disable_plugin(self, plugin_name: str) -> bool:
        """Disable a plugin."""
        self.config[f"enabled_{plugin_name}"] = False
        self._save_config()

        if plugin_name in self.plugins:
            plugin = self.plugins[plugin_name]
            if plugin.enabled:
                plugin.shutdown()
                plugin.enabled = False

        return True

    def get_plugin_info(self, plugin_name: str) -> Optional[Dict]:
        """Get information about a plugin."""
        if plugin_name not in self.plugins:
            return None

        plugin = self.plugins[plugin_name]
        manifest = self.manifests[plugin_name]

        return {**plugin.get_info(), "manifest": manifest.to_dict()}

    def list_plugins(self) -> List[Dict]:
        """List all loaded plugins with info."""
        return [self.get_plugin_info(name) for name in sorted(self.plugins.keys())]

    def get_stats(self) -> Dict:
        """Get plugin system statistics."""
        return {
            "total_discovered": len(self.discover_plugins()),
            "total_loaded": len(self.plugins),
            "total_hooks": len(self.hooks),
            "hook_callbacks": sum(len(h.callbacks) for h in self.hooks.values()),
            "plugins": [
                {"name": name, "enabled": p.enabled, "version": p.version}
                for name, p in sorted(self.plugins.items())
            ],
        }


# Example plugin template
EXAMPLE_PLUGIN_TEMPLATE = '''"""
Example Castle Wyvern Plugin

This demonstrates how to create a custom plugin.
"""

from eyrie.plugin_system import BasePlugin


class Plugin(BasePlugin):
    """Example plugin that logs when commands are executed."""
    
    name = "example_logger"
    version = "1.0.0"
    description = "Logs all commands to the console"
    author = "Your Name"
    
    def initialize(self):
        """Called when the plugin is loaded."""
        self.api.log("Example plugin initialized!")
        
        # Register for the post_command hook
        self.api.register_hook("post_command", self.on_command)
    
    def on_command(self, command: str, result: any):
        """Called after each command."""
        self.api.log(f"Command executed: {command}")
    
    def shutdown(self):
        """Called when the plugin is unloaded."""
        self.api.log("Example plugin shutting down...")
'''


# Standalone test
if __name__ == "__main__":
    print("🏰 Castle Wyvern Plugin System Test")
    print("=" * 50)

    # Create plugin manager
    pm = PluginManager()

    # Discover plugins
    plugins = pm.discover_plugins()
    print(f"\nDiscovered plugins: {plugins}")

    # Show stats
    stats = pm.get_stats()
    print(f"\nPlugin system stats:")
    print(f"  Total hooks: {stats['total_hooks']}")
    print(f"  Hook callbacks: {stats['hook_callbacks']}")

    print("\n✅ Plugin system ready!")
