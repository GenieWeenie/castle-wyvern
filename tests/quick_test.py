"""
Quick tests for Castle Wyvern core functionality.
Run with: python tests/quick_test.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        from eyrie.phoenix_gate import PhoenixGate
        from eyrie.intent_router import IntentRouter
        from eyrie.workflow_builder import WorkflowManager
        from eyrie.mcp_server import CastleWyvernMCPServer
        from eyrie.a2a_protocol import A2AIntegration
        from eyrie.enhanced_memory import EnhancedGrimoorum
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_workflow_templates():
    """Test workflow template creation."""
    print("\nTesting workflow templates...")
    
    from eyrie.workflow_builder import WorkflowManager
    
    manager = WorkflowManager(storage_dir="/tmp/test_workflows")
    
    templates = manager.get_templates()
    print(f"  Found {len(templates)} templates")
    
    # Create from template
    wf = manager.create_from_template("bmad_full")
    if wf:
        print(f"  ✅ Created BMAD workflow: {len(wf.nodes)} nodes, {len(wf.edges)} edges")
        return True
    else:
        print("  ❌ Failed to create workflow")
        return False

def test_enhanced_memory():
    """Test enhanced memory."""
    print("\nTesting enhanced memory...")
    
    from eyrie.enhanced_memory import EnhancedGrimoorum
    
    memory = EnhancedGrimoorum()
    
    # Add test memories
    memory.add("Python is a programming language", importance=4)
    memory.add("Machine learning is a subset of AI", importance=4)
    memory.add("Flask is a Python web framework", importance=3)
    
    # Search
    results = memory.search("What is AI?", use_semantic=True)
    print(f"  ✅ Search returned {len(results)} results")
    
    stats = memory.get_stats()
    print(f"  ✅ Vector memories: {stats['vector_memory']['total_memories']}")
    
    return True

def test_mcp_server():
    """Test MCP server initialization."""
    print("\nTesting MCP server...")
    
    from eyrie.mcp_server import CastleWyvernMCPServer
    
    server = CastleWyvernMCPServer()
    tools = server.list_tools()
    
    print(f"  ✅ MCP server initialized with {len(tools)} tools")
    return True

def test_a2a_protocol():
    """Test A2A protocol."""
    print("\nTesting A2A protocol...")
    
    from eyrie.a2a_protocol import A2AAgentCard
    
    card = A2AAgentCard.for_castle_wyvern("http://localhost:18795")
    
    print(f"  ✅ Agent card created: {card.name}")
    print(f"  ✅ Skills: {len(card.skills)}")
    return True

def main():
    """Run all tests."""
    print("🏰 Castle Wyvern Quick Tests")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("Workflow Templates", test_workflow_templates),
        ("Enhanced Memory", test_enhanced_memory),
        ("MCP Server", test_mcp_server),
        ("A2A Protocol", test_a2a_protocol),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"  ❌ Error: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 50)
    print("Test Results:")
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {name}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
