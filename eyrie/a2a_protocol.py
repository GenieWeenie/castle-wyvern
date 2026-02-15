"""
Castle Wyvern A2A (Agent-to-Agent) Protocol
Implements Google's A2A protocol for inter-framework communication

Provides:
- A2A server for receiving agent requests
- A2A client for connecting to other agents
- Task management across agent boundaries
- Streaming responses between agents
"""

import os
import sys
import json
import uuid
import asyncio
import aiohttp
from typing import Dict, List, Optional, Callable, Any, AsyncGenerator
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from urllib.parse import urljoin
import traceback

try:
    from flask import Flask, request, jsonify, Response, stream_with_context
    from flask_cors import CORS
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False


class A2ATaskState(Enum):
    """A2A task states."""
    SUBMITTED = "submitted"
    WORKING = "working"
    INPUT_REQUIRED = "input-required"
    COMPLETED = "completed"
    CANCELED = "canceled"
    FAILED = "failed"
    UNKNOWN = "unknown"


class A2AMessageRole(Enum):
    """A2A message roles."""
    USER = "user"
    AGENT = "agent"


@dataclass
class A2AArtifact:
    """An artifact produced by an agent."""
    name: str
    description: Optional[str] = None
    parts: List[Dict] = None
    index: int = 0
    append: Optional[bool] = None
    last_chunk: Optional[bool] = None
    metadata: Optional[Dict] = None
    
    def to_dict(self) -> Dict:
        result = {"name": self.name}
        if self.description:
            result["description"] = self.description
        if self.parts:
            result["parts"] = self.parts
        if self.metadata:
            result["metadata"] = self.metadata
        return result


@dataclass
class A2AMessage:
    """A message in an A2A conversation."""
    role: str
    parts: List[Dict]
    metadata: Optional[Dict] = None
    
    def to_dict(self) -> Dict:
        result = {
            "role": self.role,
            "parts": self.parts
        }
        if self.metadata:
            result["metadata"] = self.metadata
        return result
    
    @classmethod
    def from_dict(cls, data: Dict) -> "A2AMessage":
        return cls(
            role=data.get("role", "user"),
            parts=data.get("parts", []),
            metadata=data.get("metadata")
        )


@dataclass
class A2ATask:
    """An A2A task."""
    id: str
    session_id: str
    state: str
    messages: List[A2AMessage]
    artifacts: List[A2AArtifact]
    history: List[Dict]
    metadata: Optional[Dict] = None
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "sessionId": self.session_id,
            "state": self.state,
            "messages": [m.to_dict() for m in self.messages],
            "artifacts": [a.to_dict() for a in self.artifacts],
            "history": self.history,
            "metadata": self.metadata or {}
        }
    
    @classmethod
    def create(cls, session_id: str, message: A2AMessage, 
               task_id: str = None) -> "A2ATask":
        """Create a new task."""
        return cls(
            id=task_id or str(uuid.uuid4()),
            session_id=session_id,
            state=A2ATaskState.SUBMITTED.value,
            messages=[message],
            artifacts=[],
            history=[],
            metadata={"created_at": datetime.now().isoformat()}
        )


@dataclass
class A2AAgentCard:
    """An A2A agent card describing capabilities."""
    name: str
    description: str
    url: str
    version: str
    capabilities: Dict[str, bool]
    default_input_modes: List[str]
    default_output_modes: List[str]
    skills: List[Dict]
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "url": self.url,
            "version": self.version,
            "capabilities": self.capabilities,
            "defaultInputModes": self.default_input_modes,
            "defaultOutputModes": self.default_output_modes,
            "skills": self.skills
        }
    
    @classmethod
    def for_castle_wyvern(cls, base_url: str) -> "A2AAgentCard":
        """Create Castle Wyvern's agent card."""
        return cls(
            name="Castle Wyvern",
            description="The Manhattan Clan - A multi-agent AI infrastructure with 9 specialized agents",
            url=base_url,
            version="1.0.0",
            capabilities={
                "streaming": True,
                "pushNotifications": False
            },
            default_input_modes=["text"],
            default_output_modes=["text"],
            skills=[
                {
                    "id": "goliath",
                    "name": "Strategic Leadership",
                    "description": "High-level reasoning, strategy, and leadership",
                    "tags": ["strategy", "leadership", "reasoning"],
                    "examples": ["Help me plan a product roadmap", "What's the best approach to this problem?"]
                },
                {
                    "id": "lexington",
                    "name": "Technical Implementation",
                    "description": "Coding, automation, and technical execution",
                    "tags": ["coding", "programming", "automation"],
                    "examples": ["Write a Python function to...", "Debug this code"]
                },
                {
                    "id": "brooklyn",
                    "name": "Architecture Planning",
                    "description": "System architecture and design patterns",
                    "tags": ["architecture", "design", "planning"],
                    "examples": ["Design a microservices architecture", "How should I structure this?"]
                },
                {
                    "id": "xanatos",
                    "name": "Security Review",
                    "description": "Security analysis and adversarial testing",
                    "tags": ["security", "review", "testing"],
                    "examples": ["Review this code for vulnerabilities", "Security audit"]
                },
                {
                    "id": "broadway",
                    "name": "Documentation",
                    "description": "Documentation, summarization, and explanations",
                    "tags": ["documentation", "writing", "summarization"],
                    "examples": ["Summarize this document", "Write documentation for..."]
                }
            ]
        )


class A2AServer:
    """
    A2A Server for Castle Wyvern.
    
    Exposes the Manhattan Clan as an A2A-compatible agent
    that other frameworks can communicate with.
    """
    
    def __init__(self, castle_wyvern_cli=None, host: str = "0.0.0.0", port: int = 18795):
        if not FLASK_AVAILABLE:
            raise ImportError("Flask required for A2A server")
        
        self.host = host
        self.port = port
        self.cli = castle_wyvern_cli
        
        self.app = Flask("CastleWyvernA2A")
        CORS(self.app)
        
        # Task storage
        self.tasks: Dict[str, A2ATask] = {}
        
        # Agent card
        self.agent_card = A2AAgentCard.for_castle_wyvern(f"http://{host}:{port}")
        
        # Setup routes
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup Flask routes for A2A protocol."""
        
        @self.app.route("/.well-known/agent.json", methods=["GET"])
        def get_agent_card():
            """Return agent card (A2A discovery)."""
            return jsonify(self.agent_card.to_dict())
        
        @self.app.route("/a2a/tasks/send", methods=["POST"])
        def send_task():
            """Send a task (non-streaming)."""
            try:
                data = request.get_json()
                task = self._process_task_request(data)
                
                # Process task (would call actual Castle Wyvern)
                result = self._execute_task(task)
                
                return jsonify(result.to_dict())
                
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route("/a2a/tasks/sendSubscribe", methods=["POST"])
        def send_task_subscribe():
            """Send a task with streaming updates."""
            try:
                data = request.get_json()
                
                def generate():
                    # Simulate streaming responses
                    yield f"data: {json.dumps({'state': 'working'})}\n\n"
                    
                    task = self._process_task_request(data)
                    result = self._execute_task(task)
                    
                    yield f"data: {json.dumps(result.to_dict())}\n\n"
                
                return Response(
                    stream_with_context(generate()),
                    mimetype='text/event-stream'
                )
                
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route("/a2a/tasks/get", methods=["POST"])
        def get_task():
            """Get task status."""
            try:
                data = request.get_json()
                task_id = data.get("id")
                
                if task_id in self.tasks:
                    return jsonify(self.tasks[task_id].to_dict())
                else:
                    return jsonify({"error": "Task not found"}), 404
                    
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route("/a2a/tasks/cancel", methods=["POST"])
        def cancel_task():
            """Cancel a task."""
            try:
                data = request.get_json()
                task_id = data.get("id")
                
                if task_id in self.tasks:
                    self.tasks[task_id].state = A2ATaskState.CANCELED.value
                    return jsonify(self.tasks[task_id].to_dict())
                else:
                    return jsonify({"error": "Task not found"}), 404
                    
            except Exception as e:
                return jsonify({"error": str(e)}), 500
    
    def _process_task_request(self, data: Dict) -> A2ATask:
        """Process an incoming task request."""
        session_id = data.get("sessionId", str(uuid.uuid4()))
        message_data = data.get("message", {})
        task_id = data.get("id")
        
        message = A2AMessage.from_dict(message_data)
        task = A2ATask.create(session_id, message, task_id)
        
        # Store task
        self.tasks[task.id] = task
        
        return task
    
    def _execute_task(self, task: A2ATask) -> A2ATask:
        """Execute a task using Castle Wyvern."""
        task.state = A2ATaskState.WORKING.value
        
        # Get the message content
        last_message = task.messages[-1] if task.messages else None
        if not last_message:
            task.state = A2ATaskState.FAILED.value
            return task
        
        # Extract text from parts
        text_parts = [p.get("text", "") for p in last_message.parts if p.get("type") == "text"]
        query = " ".join(text_parts)
        
        # Route to appropriate clan member based on query
        # This is simplified - would use actual intent routing
        skill_id = self._determine_skill(query)
        
        # Simulate response (in real implementation, would call Phoenix Gate)
        response_text = self._generate_response(query, skill_id)
        
        # Add response message
        response_message = A2AMessage(
            role=A2AMessageRole.AGENT.value,
            parts=[{"type": "text", "text": response_text}]
        )
        task.messages.append(response_message)
        
        # Add artifact
        artifact = A2AArtifact(
            name="response",
            parts=[{"type": "text", "text": response_text}]
        )
        task.artifacts.append(artifact)
        
        task.state = A2ATaskState.COMPLETED.value
        task.metadata["completed_at"] = datetime.now().isoformat()
        task.metadata["skill_used"] = skill_id
        
        return task
    
    def _determine_skill(self, query: str) -> str:
        """Determine which skill to use based on query."""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["code", "function", "bug", "debug", "python", "javascript"]):
            return "lexington"
        elif any(word in query_lower for word in ["architecture", "design", "structure", "system"]):
            return "brooklyn"
        elif any(word in query_lower for word in ["security", "vulnerability", "hack", "exploit"]):
            return "xanatos"
        elif any(word in query_lower for word in ["document", "summary", "explain", "write"]):
            return "broadway"
        else:
            return "goliath"
    
    def _generate_response(self, query: str, skill_id: str) -> str:
        """Generate a response (simulated)."""
        responses = {
            "goliath": f"🦁 Goliath has considered your request: '{query[:50]}...' and offers strategic guidance.",
            "lexington": f"🔧 Lexington is implementing a solution for: '{query[:50]}...'",
            "brooklyn": f"🎯 Brooklyn has architected a plan for: '{query[:50]}...'",
            "xanatos": f"🎭 Xanatos has reviewed: '{query[:50]}...' and found potential improvements.",
            "broadway": f"📜 Broadway has documented: '{query[:50]}...'"
        }
        
        return responses.get(skill_id, responses["goliath"])
    
    def run(self, debug: bool = False):
        """Start the A2A server."""
        print(f"🔗 Castle Wyvern A2A Server starting on http://{self.host}:{self.port}")
        print(f"   Agent Card: http://{self.host}:{self.port}/.well-known/agent.json")
        print(f"   Skills: {len(self.agent_card.skills)}")
        self.app.run(host=self.host, port=self.port, debug=debug)


class A2AClient:
    """
    A2A Client for connecting to other A2A agents.
    
    Allows Castle Wyvern to delegate tasks to other A2A-compatible
    agents (CrewAI, LangGraph, etc.)
    """
    
    def __init__(self):
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def discover_agent(self, url: str) -> Optional[A2AAgentCard]:
        """Discover an A2A agent at a URL."""
        try:
            agent_card_url = urljoin(url, "/.well-known/agent.json")
            
            async with self.session.get(agent_card_url) as response:
                if response.status == 200:
                    data = await response.json()
                    return A2AAgentCard(
                        name=data.get("name", "Unknown"),
                        description=data.get("description", ""),
                        url=data.get("url", url),
                        version=data.get("version", "1.0.0"),
                        capabilities=data.get("capabilities", {}),
                        default_input_modes=data.get("defaultInputModes", ["text"]),
                        default_output_modes=data.get("defaultOutputModes", ["text"]),
                        skills=data.get("skills", [])
                    )
                return None
        except Exception as e:
            print(f"[A2A] Discovery error: {e}")
            return None
    
    async def send_task(self, agent_url: str, message: str, 
                       session_id: str = None) -> Optional[A2ATask]:
        """Send a task to an A2A agent."""
        try:
            task_url = urljoin(agent_url, "/a2a/tasks/send")
            
            payload = {
                "sessionId": session_id or str(uuid.uuid4()),
                "message": {
                    "role": "user",
                    "parts": [{"type": "text", "text": message}]
                }
            }
            
            async with self.session.post(task_url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return A2ATask(
                        id=data.get("id"),
                        session_id=data.get("sessionId"),
                        state=data.get("state"),
                        messages=[A2AMessage.from_dict(m) for m in data.get("messages", [])],
                        artifacts=[A2AArtifact(**a) for a in data.get("artifacts", [])],
                        history=data.get("history", []),
                        metadata=data.get("metadata", {})
                    )
                return None
        except Exception as e:
            print(f"[A2A] Send task error: {e}")
            return None
    
    async def send_task_stream(self, agent_url: str, message: str,
                               session_id: str = None) -> AsyncGenerator[Dict, None]:
        """Send a task with streaming updates."""
        try:
            task_url = urljoin(agent_url, "/a2a/tasks/sendSubscribe")
            
            payload = {
                "sessionId": session_id or str(uuid.uuid4()),
                "message": {
                    "role": "user",
                    "parts": [{"type": "text", "text": message}]
                }
            }
            
            async with self.session.post(task_url, json=payload) as response:
                async for line in response.content:
                    line = line.decode().strip()
                    if line.startswith("data: "):
                        data = json.loads(line[6:])
                        yield data
                        
        except Exception as e:
            print(f"[A2A] Stream error: {e}")
            yield {"error": str(e)}


class A2AIntegration:
    """
    Central A2A integration for Castle Wyvern.
    """
    
    def __init__(self, castle_wyvern_cli=None):
        self.cli = castle_wyvern_cli
        self.server: Optional[A2AServer] = None
        self.known_agents: Dict[str, A2AAgentCard] = {}
    
    def start_server(self, host: str = "0.0.0.0", port: int = 18795) -> bool:
        """Start the A2A server."""
        if not FLASK_AVAILABLE:
            print("[A2A] Flask not available, cannot start server")
            return False
        
        try:
            self.server = A2AServer(self.cli, host, port)
            
            # Start in background thread
            import threading
            server_thread = threading.Thread(
                target=self.server.run,
                kwargs={"debug": False},
                daemon=True
            )
            server_thread.start()
            
            return True
        except Exception as e:
            print(f"[A2A] Failed to start server: {e}")
            return False
    
    async def discover_agents(self, urls: List[str]) -> List[A2AAgentCard]:
        """Discover A2A agents at given URLs."""
        discovered = []
        
        async with A2AClient() as client:
            for url in urls:
                agent = await client.discover_agent(url)
                if agent:
                    self.known_agents[agent.name] = agent
                    discovered.append(agent)
        
        return discovered
    
    async def delegate_task(self, agent_name: str, message: str) -> Optional[str]:
        """Delegate a task to another A2A agent."""
        if agent_name not in self.known_agents:
            return None
        
        agent = self.known_agents[agent_name]
        
        async with A2AClient() as client:
            task = await client.send_task(agent.url, message)
            if task and task.artifacts:
                # Extract text from first artifact
                parts = task.artifacts[0].parts
                text_parts = [p.get("text", "") for p in parts if p.get("type") == "text"]
                return " ".join(text_parts)
        
        return None
    
    def get_known_agents(self) -> List[Dict]:
        """Get list of known A2A agents."""
        return [agent.to_dict() for agent in self.known_agents.values()]


# Standalone test
if __name__ == "__main__":
    print("🏰 Castle Wyvern A2A Protocol Test")
    print("=" * 50)
    
    # Test agent card
    card = A2AAgentCard.for_castle_wyvern("http://localhost:18795")
    print(f"\n1. Agent Card: {card.name}")
    print(f"   Skills: {len(card.skills)}")
    for skill in card.skills:
        print(f"   - {skill['id']}: {skill['name']}")
    
    # Test task creation
    print("\n2. Task Creation:")
    message = A2AMessage(
        role="user",
        parts=[{"type": "text", "text": "Write a Python function"}]
    )
    task = A2ATask.create("session-123", message)
    print(f"   Task ID: {task.id}")
    print(f"   State: {task.state}")
    
    # Test server (if Flask available)
    if FLASK_AVAILABLE:
        print("\n3. A2A Server:")
        print("   Flask available - server can start")
        print("   Would run on http://localhost:18795")
    else:
        print("\n3. A2A Server:")
        print("   Flask not available")
    
    print("\n✅ A2A Protocol ready!")
