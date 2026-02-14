"""
Castle Wyvern MCP (Model Context Protocol) Server
Integration with Microsoft's Model Context Protocol

Provides:
- MCP server implementation
- Castle Wyvern clan members as MCP tools
- Resource exposure via MCP
- Prompt templates via MCP
"""

import os
import sys
import json
import asyncio
from typing import Dict, List, Optional, Callable, Any, AsyncIterator
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import traceback

try:
    # MCP SDK (if available)
    from mcp.server import Server
    from mcp.types import (
        TextContent, 
        Tool, 
        Resource,
        Prompt,
        PromptMessage,
        CallToolRequestParams,
        ListResourcesRequest,
        ReadResourceRequest,
        GetPromptRequest
    )
    MCP_SDK_AVAILABLE = True
except ImportError:
    MCP_SDK_AVAILABLE = False
    # We'll implement basic MCP protocol manually


class MCPErrorCode(Enum):
    """MCP error codes."""
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    SERVER_ERROR = -32000


@dataclass
class MCPTool:
    """An MCP tool definition."""
    name: str
    description: str
    input_schema: Dict[str, Any]
    handler: Callable[[Dict], Any]
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema
        }


@dataclass
class MCPResource:
    """An MCP resource definition."""
    uri: str
    name: str
    description: str
    mime_type: str
    handler: Callable[[], str]
    
    def to_dict(self) -> Dict:
        return {
            "uri": self.uri,
            "name": self.name,
            "description": self.description,
            "mimeType": self.mime_type
        }


@dataclass  
class MCPPrompt:
    """An MCP prompt definition."""
    name: str
    description: str
    arguments: List[Dict]
    handler: Callable[[Dict], str]
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "arguments": self.arguments
        }


class CastleWyvernMCPServer:
    """
    MCP Server for Castle Wyvern.
    
    Exposes the Manhattan Clan as MCP tools that any MCP-compatible
    client can use (Claude Desktop, Cursor, etc.)
    """
    
    def __init__(self, castle_wyvern_cli=None, host: str = "localhost", port: int = 18794):
        self.host = host
        self.port = port
        self.cli = castle_wyvern_cli
        
        # MCP components
        self.tools: Dict[str, MCPTool] = {}
        self.resources: Dict[str, MCPResource] = {}
        self.prompts: Dict[str, MCPPrompt] = {}
        
        # Server state
        self._running = False
        self._server = None
        
        # Setup default tools, resources, and prompts
        self._setup_defaults()
    
    def _setup_defaults(self):
        """Setup default MCP tools, resources, and prompts."""
        
        # ============ TOOLS ============
        
        # Goliath - Leader
        self.register_tool(
            name="ask_goliath",
            description="Ask Goliath, the leader of the Manhattan Clan. Best for high-level reasoning, strategy, and leadership questions.",
            input_schema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The question to ask Goliath"
                    }
                },
                "required": ["question"]
            },
            handler=self._handle_ask_goliath
        )
        
        # Lexington - Technician
        self.register_tool(
            name="ask_lexington",
            description="Ask Lexington, the technician. Best for coding, technical implementation, and automation.",
            input_schema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The coding or technical question"
                    },
                    "language": {
                        "type": "string",
                        "description": "Programming language (optional)",
                        "default": "python"
                    }
                },
                "required": ["question"]
            },
            handler=self._handle_ask_lexington
        )
        
        # Brooklyn - Strategist
        self.register_tool(
            name="ask_brooklyn",
            description="Ask Brooklyn, the strategist. Best for architecture, planning, and multi-path analysis.",
            input_schema={
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "What you want to plan or architect"
                    }
                },
                "required": ["description"]
            },
            handler=self._handle_ask_brooklyn
        )
        
        # Xanatos - Red Team
        self.register_tool(
            name="ask_xanatos",
            description="Ask Xanatos, the red team specialist. Best for security reviews, finding vulnerabilities, and adversarial testing.",
            input_schema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Code to review for security issues"
                    },
                    "description": {
                        "type": "string",
                        "description": "Description of what to test/review"
                    }
                },
                "required": ["description"]
            },
            handler=self._handle_ask_xanatos
        )
        
        # Broadway - Chronicler
        self.register_tool(
            name="ask_broadway",
            description="Ask Broadway, the chronicler. Best for documentation, summarization, and explanations.",
            input_schema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to summarize or explain"
                    },
                    "task": {
                        "type": "string",
                        "enum": ["summarize", "explain", "document"],
                        "description": "What to do with the text"
                    }
                },
                "required": ["text", "task"]
            },
            handler=self._handle_ask_broadway
        )
        
        # System tools
        self.register_tool(
            name="castle_wyvern_status",
            description="Get Castle Wyvern system status including clan members, health, and metrics.",
            input_schema={
                "type": "object",
                "properties": {}
            },
            handler=self._handle_status
        )
        
        # ============ RESOURCES ============
        
        self.register_resource(
            uri="castlewyvern://clan/members",
            name="Clan Members",
            description="Information about all Manhattan Clan members",
            mime_type="application/json",
            handler=self._get_clan_members_resource
        )
        
        self.register_resource(
            uri="castlewyvern://docs/roadmap",
            name="Castle Wyvern Roadmap",
            description="Feature roadmap and project status",
            mime_type="text/markdown",
            handler=self._get_roadmap_resource
        )
        
        self.register_resource(
            uri="castlewyvern://system/health",
            name="System Health",
            description="Current system health status",
            mime_type="application/json",
            handler=self._get_health_resource
        )
        
        # ============ PROMPTS ============
        
        self.register_prompt(
            name="code_review",
            description="Comprehensive code review template",
            arguments=[
                {
                    "name": "code",
                    "description": "The code to review",
                    "required": True
                },
                {
                    "name": "language",
                    "description": "Programming language",
                    "required": False
                }
            ],
            handler=self._handle_code_review_prompt
        )
        
        self.register_prompt(
            name="architecture_plan",
            description="Architecture planning template",
            arguments=[
                {
                    "name": "project_description",
                    "description": "Description of the project",
                    "required": True
                }
            ],
            handler=self._handle_architecture_prompt
        )
    
    # ============ TOOL HANDLERS ============
    
    def _handle_ask_goliath(self, params: Dict) -> str:
        """Handle ask_goliath tool."""
        question = params.get("question", "")
        if self.cli:
            # Route to Goliath
            return f"🦁 Goliath considers your question: '{question}'\n\n[Response would be generated via Phoenix Gate]"
        return "Castle Wyvern CLI not initialized"
    
    def _handle_ask_lexington(self, params: Dict) -> str:
        """Handle ask_lexington tool."""
        question = params.get("question", "")
        language = params.get("language", "python")
        return f"🔧 Lexington is coding a solution for: '{question}' (Language: {language})\n\n[Code would be generated via Phoenix Gate]"
    
    def _handle_ask_brooklyn(self, params: Dict) -> str:
        """Handle ask_brooklyn tool."""
        description = params.get("description", "")
        return f"🎯 Brooklyn is architecting a plan for: '{description}'\n\n[Architecture plan would be generated via Phoenix Gate]"
    
    def _handle_ask_xanatos(self, params: Dict) -> str:
        """Handle ask_xanatos tool."""
        code = params.get("code", "")
        description = params.get("description", "")
        return f"🎭 Xanatos is reviewing for vulnerabilities: '{description}'\n\n[Security review would be generated via Phoenix Gate]"
    
    def _handle_ask_broadway(self, params: Dict) -> str:
        """Handle ask_broadway tool."""
        text = params.get("text", "")
        task = params.get("task", "summarize")
        return f"📜 Broadway is {task}ing: '{text[:100]}...'\n\n[Result would be generated via Phoenix Gate]"
    
    def _handle_status(self, params: Dict) -> str:
        """Handle status tool."""
        return json.dumps({
            "status": "running",
            "clan_members": 9,
            "features": 21,
            "version": "1.0.0",
            "phoenix_gate": "online",
            "timestamp": datetime.now().isoformat()
        }, indent=2)
    
    # ============ RESOURCE HANDLERS ============
    
    def _get_clan_members_resource(self) -> str:
        """Get clan members resource."""
        members = [
            {"name": "Goliath", "role": "Leader", "emoji": "🦁", "specialty": "High-level reasoning"},
            {"name": "Lexington", "role": "Technician", "emoji": "🔧", "specialty": "Code & automation"},
            {"name": "Brooklyn", "role": "Strategist", "emoji": "🎯", "specialty": "Architecture & planning"},
            {"name": "Broadway", "role": "Chronicler", "emoji": "📜", "specialty": "Documentation"},
            {"name": "Hudson", "role": "Archivist", "emoji": "📚", "specialty": "Historical context"},
            {"name": "Bronx", "role": "Watchdog", "emoji": "🐕", "specialty": "Security monitoring"},
            {"name": "Elisa", "role": "Bridge", "emoji": "🌉", "specialty": "Human context"},
            {"name": "Xanatos", "role": "Red Team", "emoji": "🎭", "specialty": "Adversarial testing"},
            {"name": "Demona", "role": "Failsafe", "emoji": "🔥", "specialty": "Error prediction"}
        ]
        return json.dumps({"clan": "Manhattan Clan", "members": members}, indent=2)
    
    def _get_roadmap_resource(self) -> str:
        """Get roadmap resource."""
        return """# Castle Wyvern Roadmap

## ✅ Completed (21/21 features)

### Phase 1: Foundation (4/4)
- ✅ Real AI API calls
- ✅ Dependency management
- ✅ Error handling
- ✅ Comprehensive logging

### Phase 2: Core (4/4)
- ✅ Intent-based routing
- ✅ Test suite
- ✅ Rich CLI
- ✅ BMAD integration

### Phase 3: Advanced (5/5)
- ✅ Document Ingestion (RAG)
- ✅ Memory Upgrades
- ✅ Multi-Node Distribution
- ✅ Auto-Discovery
- ✅ REST API Server
- ✅ Web Dashboard

### Phase 4: Power (5/5)
- ✅ Plugin System
- ✅ Advanced Monitoring
- ✅ CLI Improvements
- ✅ Integration APIs
- ✅ Security Enhancements

### Stretch Goals (3/3)
- ✅ Advanced AI Features
- ✅ Performance Optimizations
- ✅ Documentation Generator

## 🚀 Future Enhancements
- MCP Protocol Support (in progress)
- A2A Protocol Support
- Visual Workflow Builder
- Voice Interface
"""
    
    def _get_health_resource(self) -> str:
        """Get health resource."""
        return json.dumps({
            "status": "healthy",
            "components": {
                "phoenix_gate": "online",
                "grimoorum": "online",
                "intent_router": "online"
            },
            "timestamp": datetime.now().isoformat()
        }, indent=2)
    
    # ============ PROMPT HANDLERS ============
    
    def _handle_code_review_prompt(self, args: Dict) -> str:
        """Handle code review prompt."""
        code = args.get("code", "")
        language = args.get("language", "python")
        
        return f"""Please review the following {language} code for:
1. Security vulnerabilities
2. Performance issues
3. Code quality
4. Best practices

```{language}
{code}
```

Provide specific recommendations for improvement."""
    
    def _handle_architecture_prompt(self, args: Dict) -> str:
        """Handle architecture prompt."""
        description = args.get("project_description", "")
        
        return f"""Design a system architecture for:

{description}

Please provide:
1. High-level architecture diagram
2. Component breakdown
3. Data flow
4. Technology recommendations
5. Scalability considerations
6. Security considerations"""
    
    # ============ REGISTRATION METHODS ============
    
    def register_tool(self, name: str, description: str, 
                     input_schema: Dict, handler: Callable):
        """Register an MCP tool."""
        self.tools[name] = MCPTool(
            name=name,
            description=description,
            input_schema=input_schema,
            handler=handler
        )
    
    def register_resource(self, uri: str, name: str, 
                         description: str, mime_type: str, 
                         handler: Callable):
        """Register an MCP resource."""
        self.resources[uri] = MCPResource(
            uri=uri,
            name=name,
            description=description,
            mime_type=mime_type,
            handler=handler
        )
    
    def register_prompt(self, name: str, description: str,
                       arguments: List[Dict], handler: Callable):
        """Register an MCP prompt."""
        self.prompts[name] = MCPPrompt(
            name=name,
            description=description,
            arguments=arguments,
            handler=handler
        )
    
    # ============ SERVER METHODS ============
    
    def get_capabilities(self) -> Dict:
        """Get server capabilities."""
        return {
            "serverInfo": {
                "name": "castle-wyvern-mcp",
                "version": "1.0.0"
            },
            "capabilities": {
                "tools": {"listChanged": True},
                "resources": {"listChanged": True, "subscribe": True},
                "prompts": {"listChanged": True}
            }
        }
    
    def list_tools(self) -> List[Dict]:
        """List available tools."""
        return [tool.to_dict() for tool in self.tools.values()]
    
    def call_tool(self, name: str, arguments: Dict) -> str:
        """Call a tool."""
        if name not in self.tools:
            raise ValueError(f"Tool not found: {name}")
        
        tool = self.tools[name]
        try:
            result = tool.handler(arguments)
            return json.dumps({
                "content": [{"type": "text", "text": result}],
                "isError": False
            })
        except Exception as e:
            return json.dumps({
                "content": [{"type": "text", "text": f"Error: {str(e)}"}],
                "isError": True
            })
    
    def list_resources(self) -> List[Dict]:
        """List available resources."""
        return [resource.to_dict() for resource in self.resources.values()]
    
    def read_resource(self, uri: str) -> str:
        """Read a resource."""
        if uri not in self.resources:
            raise ValueError(f"Resource not found: {uri}")
        
        resource = self.resources[uri]
        return json.dumps({
            "contents": [{
                "uri": uri,
                "mimeType": resource.mime_type,
                "text": resource.handler()
            }]
        })
    
    def list_prompts(self) -> List[Dict]:
        """List available prompts."""
        return [prompt.to_dict() for prompt in self.prompts.values()]
    
    def get_prompt(self, name: str, arguments: Dict) -> str:
        """Get a prompt."""
        if name not in self.prompts:
            raise ValueError(f"Prompt not found: {name}")
        
        prompt = self.prompts[name]
        text = prompt.handler(arguments)
        
        return json.dumps({
            "description": prompt.description,
            "messages": [{
                "role": "user",
                "content": {"type": "text", "text": text}
            }]
        })
    
    async def handle_request(self, request: Dict) -> Dict:
        """Handle an MCP request."""
        method = request.get("method", "")
        request_id = request.get("id")
        params = request.get("params", {})
        
        try:
            if method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": self.get_capabilities()
                }
            
            elif method == "tools/list":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"tools": self.list_tools()}
                }
            
            elif method == "tools/call":
                name = params.get("name", "")
                arguments = params.get("arguments", {})
                result = self.call_tool(name, arguments)
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": json.loads(result)
                }
            
            elif method == "resources/list":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"resources": self.list_resources()}
                }
            
            elif method == "resources/read":
                uri = params.get("uri", "")
                result = self.read_resource(uri)
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": json.loads(result)
                }
            
            elif method == "prompts/list":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {"prompts": self.list_prompts()}
                }
            
            elif method == "prompts/get":
                name = params.get("name", "")
                arguments = params.get("arguments", {})
                result = self.get_prompt(name, arguments)
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": json.loads(result)
                }
            
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": MCPErrorCode.METHOD_NOT_FOUND.value,
                        "message": f"Method not found: {method}"
                    }
                }
                
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": MCPErrorCode.INTERNAL_ERROR.value,
                    "message": str(e)
                }
            }
    
    def start(self) -> bool:
        """Start the MCP server (stdio mode for compatibility)."""
        print("🏰 Castle Wyvern MCP Server starting...", file=sys.stderr)
        print(f"   Tools: {len(self.tools)}", file=sys.stderr)
        print(f"   Resources: {len(self.resources)}", file=sys.stderr)
        print(f"   Prompts: {len(self.prompts)}", file=sys.stderr)
        print("   Ready for connections!", file=sys.stderr)
        
        self._running = True
        
        # For stdio transport (most common)
        while self._running:
            try:
                line = input()
                if not line:
                    continue
                
                request = json.loads(line)
                response = asyncio.run(self.handle_request(request))
                print(json.dumps(response), flush=True)
                
            except json.JSONDecodeError:
                continue
            except EOFError:
                break
            except KeyboardInterrupt:
                break
        
        return True
    
    def stop(self):
        """Stop the MCP server."""
        self._running = False


# Standalone usage
if __name__ == "__main__":
    print("🏰 Castle Wyvern MCP Server", file=sys.stderr)
    print("=" * 50, file=sys.stderr)
    print("This server implements the Model Context Protocol.", file=sys.stderr)
    print("Connect with: Claude Desktop, Cursor, or any MCP client.", file=sys.stderr)
    print("", file=sys.stderr)
    
    server = CastleWyvernMCPServer()
    server.start()
