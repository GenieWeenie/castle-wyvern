"""
Castle Wyvern REST API Server
Feature 12: Expose Castle Wyvern functionality via REST API

Provides HTTP endpoints for:
- Clan member interactions
- Task management
- Node status
- BMAD workflow execution
- Memory access
"""

import json
import logging
import os
import sys
from typing import Dict, Any, Optional
from datetime import datetime
from functools import wraps

logger = logging.getLogger("castle_wyvern.api")

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from flask import Flask, request, jsonify, Response
    from flask_cors import CORS

    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

from eyrie.phoenix_gate import PhoenixGate
from eyrie.intent_router import IntentRouter, IntentType
from eyrie.document_ingestion import DocumentIngestion
from eyrie.node_manager import NodeManager
from eyrie.knowledge_graph import KnowledgeGraph
from eyrie.agent_coordination import ClanCoordinationManager
from grimoorum.memory_manager import GrimoorumV2
from bmad.bmad_workflow import BMADWorkflow


class CastleWyvernAPI:
    """
    REST API server for Castle Wyvern.

    Endpoints:
    - GET  /health          - Health check
    - GET  /status          - Full system status
    - GET  /clan            - List clan members
    - POST /clan/ask        - Ask the clan a question
    - POST /clan/code       - Request code from Lexington
    - POST /clan/review     - Request code review from Xanatos
    - POST /clan/plan       - Request architecture from Brooklyn
    - GET  /nodes           - List connected nodes
    - POST /nodes/discover  - Trigger node discovery
    - GET  /memory          - Search memory (Grimoorum)
    - POST /memory/ingest   - Ingest document into memory
    - POST /bmad/spec       - Create quick spec
    - POST /bmad/story      - Create dev story
    - POST /bmad/review     - Run code review
    """

    def __init__(self, host: str = "0.0.0.0", port: int = 18791, api_key: Optional[str] = None):
        if not FLASK_AVAILABLE:
            raise ImportError("Flask not installed. Run: pip install flask flask-cors")

        self.host = host
        self.port = port
        self.api_key = api_key

        # Initialize Castle Wyvern components
        self.phoenix_gate = PhoenixGate()
        self.intent_router = IntentRouter(use_ai_classification=True)
        self.grimoorum = GrimoorumV2()
        self.node_manager = NodeManager()
        self.knowledge_graph = KnowledgeGraph()
        self.coordination = ClanCoordinationManager()

        # Create Flask app
        self.app = Flask("CastleWyvern")
        CORS(self.app)  # Enable CORS for all routes
        # Request size limit (5MB) to avoid huge payloads
        self.app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

        # Light observability: request count, start time, access log
        self._request_count = 0
        self._started_at = datetime.now()

        @self.app.after_request
        def _log_request(response):
            self._request_count += 1
            logger.info("%s %s %s", request.method, request.path, response.status_code)
            return response

        # Register routes
        self._register_routes()

        @self.app.errorhandler(413)
        def _payload_too_large(_e):
            return self._error("Request body too large (max 5MB)", "payload_too_large", 413)

    def _require_api_key(self, f):
        """Decorator to require API key for protected endpoints."""

        @wraps(f)
        def decorated(*args, **kwargs):
            if not self.api_key:
                return f(*args, **kwargs)

            provided_key = request.headers.get("X-API-Key") or request.args.get("api_key")
            if provided_key != self.api_key:
                return (
                    jsonify({"error": "Invalid or missing API key", "code": "invalid_api_key"}),
                    401,
                )

            return f(*args, **kwargs)

        return decorated

    def _error(self, message: str, code: str, status_code: int = 400):
        """Return a consistent JSON error response."""
        return jsonify({"error": message, "code": code}), status_code

    def _register_routes(self):
        """Register all API routes."""

        # ============ Health & Status ============

        @self.app.route("/health", methods=["GET"])
        def health():
            """Health check endpoint."""
            return jsonify(
                {
                    "status": "healthy",
                    "timestamp": datetime.now().isoformat(),
                    "version": "0.2.1",
                    "services": {
                        "phoenix_gate": self.phoenix_gate.circuit_breakers["primary"].state,
                        "grimoorum": "active",
                        "intent_router": "active",
                    },
                }
            )

        @self.app.route("/metrics", methods=["GET"])
        def metrics():
            """Light observability: request count and uptime (no auth for easy scraping)."""
            uptime_seconds = (datetime.now() - self._started_at).total_seconds()
            return jsonify(
                {
                    "requests_total": self._request_count,
                    "started_at": self._started_at.isoformat(),
                    "uptime_seconds": round(uptime_seconds, 1),
                }
            )

        @self.app.route("/status", methods=["GET"])
        @self._require_api_key
        def status():
            """Full system status."""
            return jsonify(
                {
                    "castle_wyvern": {
                        "version": "0.2.1",
                        "timestamp": datetime.now().isoformat(),
                        "phoenix_gate": {
                            "primary": {
                                "provider": "z.ai",
                                "circuit_state": self.phoenix_gate.circuit_breakers[
                                    "primary"
                                ].state,
                            },
                            "fallback": {
                                "provider": "openai",
                                "circuit_state": self.phoenix_gate.circuit_breakers[
                                    "fallback"
                                ].state,
                            },
                        },
                        "clan": {
                            "total_members": 9,
                            "members": [
                                {"name": "Goliath", "role": "Leader", "emoji": "🦁"},
                                {"name": "Lexington", "role": "Technician", "emoji": "🔧"},
                                {"name": "Brooklyn", "role": "Strategist", "emoji": "🎯"},
                                {"name": "Broadway", "role": "Chronicler", "emoji": "📜"},
                                {"name": "Hudson", "role": "Archivist", "emoji": "📚"},
                                {"name": "Bronx", "role": "Watchdog", "emoji": "🐕"},
                                {"name": "Elisa", "role": "Bridge", "emoji": "🌉"},
                                {"name": "Xanatos", "role": "Red Team", "emoji": "🎭"},
                                {"name": "Demona", "role": "Failsafe", "emoji": "🔥"},
                            ],
                        },
                        "nodes": {
                            "count": len(self.node_manager.list_nodes()),
                            "nodes": [
                                {"id": n.id, "name": n.name, "status": n.status}
                                for n in self.node_manager.list_nodes()
                            ],
                        },
                    }
                }
            )

        # ============ Clan Interactions ============

        @self.app.route("/clan", methods=["GET"])
        def list_clan():
            """List all clan members."""
            return jsonify(
                {
                    "clan": "Manhattan Clan",
                    "members": [
                        {
                            "id": "goliath",
                            "name": "Goliath",
                            "role": "Leader",
                            "emoji": "🦁",
                            "specialty": "High-level reasoning, orchestration",
                        },
                        {
                            "id": "lexington",
                            "name": "Lexington",
                            "role": "Technician",
                            "emoji": "🔧",
                            "specialty": "Code, automation, technical execution",
                        },
                        {
                            "id": "brooklyn",
                            "name": "Brooklyn",
                            "role": "Strategist",
                            "emoji": "🎯",
                            "specialty": "Multi-path planning, architecture",
                        },
                        {
                            "id": "broadway",
                            "name": "Broadway",
                            "role": "Chronicler",
                            "emoji": "📜",
                            "specialty": "Documentation, summarization",
                        },
                        {
                            "id": "hudson",
                            "name": "Hudson",
                            "role": "Archivist",
                            "emoji": "📚",
                            "specialty": "Historical context, long-term memory",
                        },
                        {
                            "id": "bronx",
                            "name": "Bronx",
                            "role": "Watchdog",
                            "emoji": "🐕",
                            "specialty": "Security monitoring, alerts",
                        },
                        {
                            "id": "elisa",
                            "name": "Elisa",
                            "role": "Bridge",
                            "emoji": "🌉",
                            "specialty": "Human context, ethics, legal",
                        },
                        {
                            "id": "xanatos",
                            "name": "Xanatos",
                            "role": "Red Team",
                            "emoji": "🎭",
                            "specialty": "Adversarial testing, vulnerabilities",
                        },
                        {
                            "id": "demona",
                            "name": "Demona",
                            "role": "Failsafe",
                            "emoji": "🔥",
                            "specialty": "Error prediction, worst-case scenarios",
                        },
                    ],
                }
            )

        @self.app.route("/clan/ask", methods=["POST"])
        @self._require_api_key
        def clan_ask():
            """Ask the clan a question - routes to appropriate member."""
            data = request.get_json() or {}
            question = data.get("question") or data.get("prompt") or data.get("message")

            if not question:
                return self._error("Question is required", "missing_field", 400)

            try:
                # Classify intent
                intent_result = self.intent_router.classify_intent(question)
                intent = intent_result.intent
                confidence = intent_result.confidence

                # Route to appropriate agent
                member = self._get_member_for_intent(intent)

                # Generate response via Phoenix Gate
                system_prompt = self._get_system_prompt(member)
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question},
                ]

                response = self.phoenix_gate.chat_completion(messages)

                return jsonify(
                    {
                        "question": question,
                        "routing": {
                            "intent": intent.value,
                            "confidence": confidence,
                            "member": member,
                        },
                        "response": response,
                        "timestamp": datetime.now().isoformat(),
                    }
                )

            except Exception as e:
                return self._error(str(e), "server_error", 500)

        @self.app.route("/clan/code", methods=["POST"])
        @self._require_api_key
        def clan_code():
            """Request code from Lexington."""
            data = request.get_json() or {}
            description = data.get("description") or data.get("prompt")
            language = data.get("language", "python")

            if not description:
                return self._error("Description is required", "missing_field", 400)

            try:
                system_prompt = """You are Lexington, the technician of the Manhattan Clan.
You write clean, efficient, well-documented code.
Always include comments explaining the logic.
Provide example usage when appropriate."""

                prompt = f"Write {language} code for: {description}"
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ]

                response = self.phoenix_gate.chat_completion(messages)

                return jsonify(
                    {
                        "member": "Lexington",
                        "language": language,
                        "description": description,
                        "code": response,
                        "timestamp": datetime.now().isoformat(),
                    }
                )

            except Exception as e:
                return self._error(str(e), "server_error", 500)

        @self.app.route("/clan/review", methods=["POST"])
        @self._require_api_key
        def clan_review():
            """Request code review from Xanatos."""
            data = request.get_json() or {}
            code = data.get("code") or data.get("content")

            if not code:
                return self._error("Code is required", "missing_field", 400)

            try:
                system_prompt = """You are Xanatos, the red team specialist.
Review code for security vulnerabilities, bugs, and improvements.
Be thorough but constructive. Identify issues and suggest fixes."""

                prompt = f"Review this code:\n\n```\n{code}\n```"
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ]

                response = self.phoenix_gate.chat_completion(messages)

                return jsonify(
                    {
                        "member": "Xanatos",
                        "code_length": len(code),
                        "review": response,
                        "timestamp": datetime.now().isoformat(),
                    }
                )

            except Exception as e:
                return self._error(str(e), "server_error", 500)

        @self.app.route("/clan/plan", methods=["POST"])
        @self._require_api_key
        def clan_plan():
            """Request architecture/plan from Brooklyn."""
            data = request.get_json() or {}
            description = data.get("description") or data.get("prompt")

            if not description:
                return self._error("Description is required", "missing_field", 400)

            try:
                system_prompt = """You are Brooklyn, the strategist.
Create clear, actionable architecture plans and technical designs.
Break complex problems into manageable components.
Consider trade-offs and provide reasoning."""

                prompt = f"Create an architecture plan for: {description}"
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ]

                response = self.phoenix_gate.chat_completion(messages)

                return jsonify(
                    {
                        "member": "Brooklyn",
                        "description": description,
                        "plan": response,
                        "timestamp": datetime.now().isoformat(),
                    }
                )

            except Exception as e:
                return self._error(str(e), "server_error", 500)

        @self.app.route("/clan/summarize", methods=["POST"])
        @self._require_api_key
        def clan_summarize():
            """Request summary from Broadway."""
            data = request.get_json() or {}
            text = data.get("text") or data.get("content")
            max_length = data.get("max_length", "medium")  # short, medium, long

            if not text:
                return self._error("Text is required", "missing_field", 400)

            try:
                length_prompt = {
                    "short": "Provide a brief 1-2 sentence summary.",
                    "medium": "Provide a concise paragraph summary.",
                    "long": "Provide a detailed summary covering all key points.",
                }.get(max_length, "Provide a concise summary.")

                system_prompt = f"""You are Broadway, the chronicler.
Summarize content clearly and accurately.
{length_prompt}
Maintain the original meaning and key details."""

                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Summarize this:\n\n{text}"},
                ]

                response = self.phoenix_gate.chat_completion(messages)

                return jsonify(
                    {
                        "member": "Broadway",
                        "original_length": len(text),
                        "summary": response,
                        "timestamp": datetime.now().isoformat(),
                    }
                )

            except Exception as e:
                return self._error(str(e), "server_error", 500)

        # ============ Node Management ============

        @self.app.route("/nodes", methods=["GET"])
        @self._require_api_key
        def list_nodes():
            """List all connected Stone nodes."""
            nodes = self.node_manager.list_nodes()
            return jsonify(
                {
                    "count": len(nodes),
                    "nodes": [
                        {
                            "id": n.id,
                            "name": n.name,
                            "host": n.host,
                            "port": n.port,
                            "status": n.status,
                            "capabilities": n.capabilities,
                            "load": n.load,
                            "last_seen": n.last_seen,
                        }
                        for n in nodes
                    ],
                }
            )

        @self.app.route("/nodes", methods=["POST"])
        @self._require_api_key
        def add_node():
            """Add a new Stone node."""
            data = request.get_json() or {}

            name = data.get("name")
            host = data.get("host")
            port = data.get("port", 18790)
            capabilities = data.get("capabilities", ["cpu"])

            if not name or not host:
                return self._error("Name and host are required", "missing_field", 400)

            try:
                node = self.node_manager.add_node(name, host, port, capabilities)
                return (
                    jsonify(
                        {
                            "message": "Node added successfully",
                            "node": {
                                "id": node.id,
                                "name": node.name,
                                "host": node.host,
                                "port": node.port,
                                "status": node.status,
                            },
                        }
                    ),
                    201,
                )
            except Exception as e:
                return self._error(str(e), "server_error", 500)

        @self.app.route("/nodes/discover", methods=["POST"])
        @self._require_api_key
        def discover_nodes():
            """Trigger node discovery."""
            try:
                # This would trigger the auto-discovery service
                return jsonify(
                    {
                        "message": "Node discovery triggered",
                        "note": "Auto-discovery service will populate nodes",
                        "timestamp": datetime.now().isoformat(),
                    }
                )
            except Exception as e:
                return self._error(str(e), "server_error", 500)

        # ============ Memory (Grimoorum) ============

        @self.app.route("/memory/search", methods=["POST"])
        @self._require_api_key
        def search_memory():
            """Search Grimoorum memory."""
            data = request.get_json() or {}
            query = data.get("query")
            limit = data.get("limit", 10)

            if not query:
                return self._error("Query is required", "missing_field", 400)

            try:
                results = self.grimoorum.search(query, limit=limit)
                return jsonify({"query": query, "results_count": len(results), "results": results})
            except Exception as e:
                return self._error(str(e), "server_error", 500)

        @self.app.route("/memory/ingest", methods=["POST"])
        @self._require_api_key
        def ingest_document():
            """Ingest a document into memory."""
            data = request.get_json() or {}
            content = data.get("content")
            doc_type = data.get("type", "note")
            metadata = data.get("metadata", {})

            if not content:
                return self._error("Content is required", "missing_field", 400)

            try:
                doc_id = self.grimoorum.add(content, doc_type=doc_type, metadata=metadata)
                return (
                    jsonify(
                        {
                            "message": "Document ingested successfully",
                            "document_id": doc_id,
                            "type": doc_type,
                            "content_length": len(content),
                        }
                    ),
                    201,
                )
            except Exception as e:
                return self._error(str(e), "server_error", 500)

        @self.app.route("/memory/conversations", methods=["GET"])
        @self._require_api_key
        def list_conversations():
            """List recent conversations."""
            try:
                conversations = self.grimoorum.get_recent_conversations(limit=50)
                return jsonify({"count": len(conversations), "conversations": conversations})
            except Exception as e:
                return self._error(str(e), "server_error", 500)

        # ============ Knowledge Graph (KAG) ============

        @self.app.route("/kg/status", methods=["GET"])
        @self._require_api_key
        def kg_status():
            """Get knowledge graph statistics."""
            try:
                stats = self.knowledge_graph.get_stats()
                return jsonify({"knowledge_graph": stats})
            except Exception as e:
                return self._error(str(e), "server_error", 500)

        @self.app.route("/kg/reason", methods=["POST"])
        @self._require_api_key
        def kg_reason():
            """Run logical reasoning over the knowledge graph."""
            data = request.get_json() or {}
            query = data.get("query")

            if not query:
                return self._error("query is required", "missing_field", 400)

            try:
                result = self.knowledge_graph.logical_reasoning(query)
                return jsonify(result)
            except Exception as e:
                return self._error(str(e), "server_error", 500)

        # ============ Agent Coordination ============

        @self.app.route("/coord/status", methods=["GET"])
        @self._require_api_key
        def coord_status():
            """Get coordination system status."""
            try:
                stats = self.coordination.coordination.get_coordination_stats()
                return jsonify({"coordination": stats})
            except Exception as e:
                return self._error(str(e), "server_error", 500)

        @self.app.route("/coord/team", methods=["POST"])
        @self._require_api_key
        def coord_team():
            """Get optimal team for a task (no execution)."""
            data = request.get_json() or {}
            task = data.get("task") or data.get("description")
            requirements = data.get("requirements", ["general"])
            if isinstance(requirements, str):
                requirements = [r.strip() for r in requirements.split(",")]

            if not task:
                return self._error("task (or description) is required", "missing_field", 400)

            try:
                team_ids = self.coordination.get_optimal_team(task, requirements)
                team = []
                for agent_id in team_ids:
                    perf = self.coordination.get_agent_performance(agent_id)
                    team.append(
                        {
                            "id": agent_id,
                            "name": (perf or {}).get("name", agent_id),
                            "specialization": (perf or {}).get("specialization", ""),
                            "performance_score": (perf or {}).get("performance_score", 0),
                        }
                    )
                return jsonify({"task": task, "requirements": requirements, "team": team})
            except Exception as e:
                return self._error(str(e), "server_error", 500)

        # ============ BMAD Workflows ============

        @self.app.route("/bmad/spec", methods=["POST"])
        @self._require_api_key
        def bmad_spec():
            """Create a quick spec via BMAD."""
            data = request.get_json() or {}
            description = data.get("description") or data.get("prompt")

            if not description:
                return self._error("Description is required", "missing_field", 400)

            try:
                # Use Lexington for spec generation
                system_prompt = """You are Lexington. Create a concise technical specification.
Include: Overview, Requirements, and Implementation approach."""

                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Create a spec for: {description}"},
                ]

                response = self.phoenix_gate.chat_completion(messages)

                return jsonify(
                    {
                        "workflow": "BMAD - Quick Spec",
                        "description": description,
                        "spec": response,
                        "timestamp": datetime.now().isoformat(),
                    }
                )

            except Exception as e:
                return self._error(str(e), "server_error", 500)

        @self.app.route("/bmad/review", methods=["POST"])
        @self._require_api_key
        def bmad_review():
            """Run code review via BMAD."""
            data = request.get_json() or {}
            code = data.get("code") or data.get("content")

            if not code:
                return self._error("Code is required", "missing_field", 400)

            try:
                system_prompt = """You are Xanatos. Conduct a thorough code review.
Check for: Security issues, Bugs, Performance problems, Style violations.
Provide specific line-by-line feedback."""

                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Review this code:\n\n```\n{code}\n```"},
                ]

                response = self.phoenix_gate.chat_completion(messages)

                return jsonify(
                    {
                        "workflow": "BMAD - Code Review",
                        "code_length": len(code),
                        "review": response,
                        "timestamp": datetime.now().isoformat(),
                    }
                )

            except Exception as e:
                return self._error(str(e), "server_error", 500)

    def _get_member_for_intent(self, intent: IntentType) -> str:
        """Map intent to clan member."""
        mapping = {
            IntentType.CODE: "Lexington",
            IntentType.REVIEW: "Xanatos",
            IntentType.PLAN: "Brooklyn",
            IntentType.SUMMARIZE: "Broadway",
            IntentType.RESEARCH: "Hudson",
            IntentType.SECURITY: "Bronx",
            IntentType.CHAT: "Goliath",
        }
        return mapping.get(intent, "Goliath")

    def _get_system_prompt(self, member: str) -> str:
        """Get system prompt for a clan member."""
        prompts = {
            "Goliath": "You are Goliath, leader of the Manhattan Clan. Provide wise, thoughtful responses with leadership perspective.",
            "Lexington": "You are Lexington, the technician. Focus on practical, technical solutions with clean implementation details.",
            "Brooklyn": "You are Brooklyn, the strategist. Think through multiple approaches and recommend the best path forward.",
            "Broadway": "You are Broadway, the chronicler. Be clear, thorough, and document everything well.",
            "Hudson": "You are Hudson, the archivist. Draw on historical knowledge and provide context.",
            "Bronx": "You are Bronx, the watchdog. Focus on security, threats, and protection.",
            "Elisa": "You are Elisa, the bridge to humanity. Connect technical concepts to human understanding and consider ethical implications.",
            "Xanatos": "You are Xanatos, the red team. Challenge assumptions and find weaknesses.",
            "Demona": "You are Demona, the failsafe. Consider edge cases and failure modes.",
        }
        return prompts.get(member, prompts["Goliath"])

    def run(self, debug: bool = False):
        """Start the API server."""
        print(f"🏰 Castle Wyvern API Server")
        print(f"   Host: {self.host}:{self.port}")
        print(f"   API Key Required: {bool(self.api_key)}")
        print(f"   CORS: Enabled")
        print()
        print("   Endpoints:")
        print("   - GET  /health              Health check")
        print("   - GET  /status              System status")
        print("   - GET  /clan                List clan members")
        print("   - POST /clan/ask            Ask the clan")
        print("   - POST /clan/code           Request code (Lexington)")
        print("   - POST /clan/review         Code review (Xanatos)")
        print("   - POST /clan/plan           Architecture (Brooklyn)")
        print("   - POST /clan/summarize      Summarize (Broadway)")
        print("   - GET  /nodes               List nodes")
        print("   - POST /nodes               Add node")
        print("   - POST /memory/search       Search memory")
        print("   - POST /memory/ingest       Ingest document")
        print("   - POST /bmad/spec           Quick spec")
        print("   - POST /bmad/review         Code review")
        print()

        self.app.run(host=self.host, port=self.port, debug=debug)


# Standalone usage
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Castle Wyvern REST API Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=18791, help="Port to listen on")
    parser.add_argument("--api-key", help="API key for authentication")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")

    args = parser.parse_args()

    if not FLASK_AVAILABLE:
        print("⚠️  Flask not installed. Run: pip install flask flask-cors")
        exit(1)

    api = CastleWyvernAPI(host=args.host, port=args.port, api_key=args.api_key)
    api.run(debug=args.debug)
