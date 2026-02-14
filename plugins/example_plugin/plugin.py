"""
Example Castle Wyvern Plugin

This demonstrates the plugin system capabilities.
"""

from eyrie.plugin_system import BasePlugin


class ExamplePlugin(BasePlugin):
    """
    Example plugin that demonstrates:
    - Hook registration
    - API usage
    - Memory storage
    - AI calls
    """
    
    name = "example_plugin"
    version = "1.0.0"
    description = "Example plugin demonstrating Castle Wyvern plugin system"
    author = "Castle Wyvern Team"
    requires = []
    
    def initialize(self):
        """Called when the plugin is loaded."""
        self.api.log(f"🎉 {self.name} v{self.version} initialized!", "info")
        
        # Register for hooks
        self.api.register_hook("post_command", self.on_command)
        self.api.register_hook("memory_added", self.on_memory_added)
        
        # Store initialization in memory
        self.api.store_memory(
            f"Plugin {self.name} initialized at startup",
            {"source": "plugin", "plugin_name": self.name}
        )
    
    def on_command(self, command: str, result=None):
        """Called after each command is executed."""
        self.api.log(f"📋 Command executed: {command}", "debug")
    
    def on_memory_added(self, content: str, metadata: dict = None):
        """Called when a memory is added."""
        self.api.log(f"🧠 Memory added: {content[:50]}...", "debug")
    
    def shutdown(self):
        """Called when the plugin is unloaded."""
        self.api.log(f"👋 {self.name} shutting down...", "info")
