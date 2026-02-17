"""
Tests for eyrie.plugin_system: PluginManager, hooks, and example plugin loading.
"""

import os
import sys
import pytest

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eyrie.plugin_system import (
    PluginHook,
    PluginManager,
    PluginAPI,
    BasePlugin,
)


class MockGrimoorum:
    def record(self, user_input, agent_name="", agent_response="", importance=3, tags=None):
        return "mock_memory_id"

    def search_by_keyword(self, query, limit=10):
        return []


class MockPhoenixGate:
    def chat_completion(self, messages):
        return "mock response"


@pytest.fixture
def plugins_dir(tmp_path):
    """Use a temp plugins dir so we don't rely on repo plugins/ at collect time."""
    return str(tmp_path)


class TestPluginHook:
    def test_register_and_execute(self):
        hook = PluginHook("test_hook", "Test")
        results = []

        def cb1(x):
            results.append(("cb1", x))
            return 1

        def cb2(x):
            results.append(("cb2", x))
            return 2

        hook.register(cb1)
        hook.register(cb2)
        out = hook.execute(42)
        assert out == [1, 2]
        assert results == [("cb1", 42), ("cb2", 42)]


class TestPluginManagerWithoutPlugins:
    def test_register_hook_and_trigger(self, tmp_path):
        pm = PluginManager(
            plugins_dir=str(tmp_path),
            phoenix_gate=MockPhoenixGate(),
            grimoorum=MockGrimoorum(),
        )
        received = []

        def my_callback(arg):
            received.append(arg)
            return "ok"

        pm.register_hook("custom_hook", "Custom")
        pm.register_hook_callback("custom_hook", my_callback)
        results = pm.trigger_hook("custom_hook", "hello")
        assert results == ["ok"]
        assert received == ["hello"]

    def test_load_example_plugin_from_repo(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        repo_plugins = os.path.join(base_dir, "plugins")
        if not os.path.isdir(repo_plugins) or "example_plugin" not in os.listdir(repo_plugins):
            pytest.skip("plugins/example_plugin not found")

        pm = PluginManager(
            plugins_dir=repo_plugins,
            phoenix_gate=MockPhoenixGate(),
            grimoorum=MockGrimoorum(),
        )
        ok = pm.load_plugin("example_plugin")
        assert ok is True
        assert "example_plugin" in pm.plugins
        plugin = pm.plugins["example_plugin"]
        assert plugin.name == "example_plugin"
        assert plugin.enabled is True
        assert plugin._initialized is True
        # post_command hook should be registered by the plugin
        results = pm.trigger_hook("post_command", "ask", result=None)
        assert isinstance(results, list)
        pm.unload_plugin("example_plugin")
        assert "example_plugin" not in pm.plugins
