"""
Castle Wyvern Web Dashboard
Feature 13: Browser-based UI for the Manhattan Clan

Provides:
- Real-time clan status
- Chat interface with clan members
- Node monitoring
- Memory viewer
- API console
"""

import os
import sys
import json
import threading
from datetime import datetime
from typing import Dict, Any, Optional

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from flask import Flask, render_template, jsonify, request, Response, send_from_directory
    from flask_cors import CORS
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

from eyrie.phoenix_gate import PhoenixGate
from eyrie.intent_router import IntentRouter, IntentType
from eyrie.node_manager import NodeManager
from eyrie.auto_discovery import AutoDiscoveryService
from grimoorum.memory_manager import GrimoorumV2


class WebDashboard:
    """
    Castle Wyvern Web Dashboard.
    
    Serves a beautiful web interface for interacting with
    the Manhattan Clan, monitoring nodes, and viewing memory.
    """
    
    def __init__(self, host: str = "0.0.0.0", port: int = 18792):
        if not FLASK_AVAILABLE:
            raise ImportError("Flask not installed. Run: pip install flask flask-cors")
        
        self.host = host
        self.port = port
        
        # Initialize components
        self.phoenix_gate = PhoenixGate()
        self.intent_router = IntentRouter(use_ai_classification=True)
        self.grimoorum = GrimoorumV2()
        self.node_manager = NodeManager()
        
        # Create Flask app
        self.app = Flask(__name__, 
                        template_folder=self._get_template_dir(),
                        static_folder=self._get_static_dir())
        CORS(self.app)
        
        # Register routes
        self._register_routes()
    
    def _get_template_dir(self) -> str:
        """Get or create template directory."""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        template_dir = os.path.join(base_dir, "templates")
        os.makedirs(template_dir, exist_ok=True)
        return template_dir
    
    def _get_static_dir(self) -> str:
        """Get or create static directory."""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        static_dir = os.path.join(base_dir, "static")
        os.makedirs(static_dir, exist_ok=True)
        return static_dir
    
    def _register_routes(self):
        """Register all web routes."""
        
        @self.app.route("/")
        def index():
            """Main dashboard page."""
            return render_template("dashboard.html")
        
        @self.app.route("/api/status")
        def api_status():
            """Get current system status."""
            return jsonify({
                "castle_wyvern": {
                    "version": "0.2.0",
                    "timestamp": datetime.now().isoformat(),
                    "phoenix_gate": {
                        "primary": {
                            "provider": "z.ai",
                            "state": self.phoenix_gate.circuit_breakers["primary"].state.value
                        },
                        "fallback": {
                            "provider": "openai",
                            "state": self.phoenix_gate.circuit_breakers["fallback"].state.value
                        }
                    }
                }
            })
        
        @self.app.route("/api/clan")
        def api_clan():
            """Get clan member information."""
            clan = [
                {"id": "goliath", "name": "Goliath", "role": "Leader", 
                 "emoji": "🦁", "color": "#FFD700", "specialty": "High-level reasoning",
                 "status": "Ready", "current_task": "Standing by"},
                {"id": "lexington", "name": "Lexington", "role": "Technician", 
                 "emoji": "🔧", "color": "#00CED1", "specialty": "Code & automation",
                 "status": "Ready", "current_task": "Standing by"},
                {"id": "brooklyn", "name": "Brooklyn", "role": "Strategist", 
                 "emoji": "🎯", "color": "#FF6347", "specialty": "Architecture & planning",
                 "status": "Ready", "current_task": "Standing by"},
                {"id": "broadway", "name": "Broadway", "role": "Chronicler", 
                 "emoji": "📜", "color": "#32CD32", "specialty": "Documentation",
                 "status": "Ready", "current_task": "Standing by"},
                {"id": "hudson", "name": "Hudson", "role": "Archivist", 
                 "emoji": "📚", "color": "#4169E1", "specialty": "Historical context",
                 "status": "Ready", "current_task": "Standing by"},
                {"id": "bronx", "name": "Bronx", "role": "Watchdog", 
                 "emoji": "🐕", "color": "#8B4513", "specialty": "Security monitoring",
                 "status": "Ready", "current_task": "Standing by"},
                {"id": "elisa", "name": "Elisa", "role": "Bridge", 
                 "emoji": "🌉", "color": "#F0F8FF", "specialty": "Human context",
                 "status": "Ready", "current_task": "Standing by"},
                {"id": "xanatos", "name": "Xanatos", "role": "Red Team", 
                 "emoji": "🎭", "color": "#2F4F4F", "specialty": "Adversarial testing",
                 "status": "Ready", "current_task": "Standing by"},
                {"id": "demona", "name": "Demona", "role": "Failsafe", 
                 "emoji": "🔥", "color": "#DC143C", "specialty": "Error prediction",
                 "status": "Ready", "current_task": "Standing by"}
            ]
            return jsonify({"clan": clan})
        
        @self.app.route("/api/chat", methods=["POST"])
        def api_chat():
            """Chat with the clan via web interface."""
            data = request.get_json() or {}
            message = data.get("message", "")
            
            if not message:
                return jsonify({"error": "Message is required"}), 400
            
            try:
                # Classify intent
                intent_result = self.intent_router.classify_intent(message)
                member = self._get_member_for_intent(intent_result.intent)
                
                # Get response from AI
                system_prompt = self._get_system_prompt(member)
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ]
                
                response = self.phoenix_gate.chat_completion(messages)
                
                # Save to memory
                self.grimoorum.record(
                    user_input=message,
                    agent_name=member.lower(),
                    agent_response=response,
                    intent=intent_result.intent.value,
                    importance=2,
                    session_id="web_dashboard"
                )
                
                return jsonify({
                    "message": message,
                    "response": response,
                    "member": member,
                    "intent": intent_result.intent.value,
                    "confidence": intent_result.confidence,
                    "timestamp": datetime.now().isoformat()
                })
                
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route("/api/nodes")
        def api_nodes():
            """Get all connected nodes."""
            nodes = self.node_manager.list_nodes()
            return jsonify({
                "count": len(nodes),
                "nodes": [
                    {
                        "id": n.id,
                        "name": n.name,
                        "host": n.host,
                        "port": n.port,
                        "status": n.status,
                        "capabilities": n.capabilities,
                        "load": n.load
                    }
                    for n in nodes
                ]
            })
        
        @self.app.route("/api/memory/recent")
        def api_memory_recent():
            """Get recent conversations."""
            try:
                conversations = self.grimoorum.get_recent_conversations(limit=20)
                return jsonify({
                    "count": len(conversations),
                    "conversations": conversations
                })
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route("/api/memory/search", methods=["POST"])
        def api_memory_search():
            """Search memory."""
            data = request.get_json() or {}
            query = data.get("query", "")
            
            if not query:
                return jsonify({"error": "Query is required"}), 400
            
            try:
                results = self.grimoorum.search(query, limit=10)
                return jsonify({
                    "query": query,
                    "results": results
                })
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route("/api/stats")
        def api_stats():
            """Get system statistics."""
            try:
                stats = self.grimoorum.get_stats()
                return jsonify(stats)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
    
    def _get_member_for_intent(self, intent: IntentType) -> str:
        """Map intent to clan member."""
        mapping = {
            IntentType.CODE: "Lexington",
            IntentType.REVIEW: "Xanatos",
            IntentType.PLAN: "Brooklyn",
            IntentType.SUMMARIZE: "Broadway",
            IntentType.RESEARCH: "Hudson",
            IntentType.SECURITY: "Bronx",
            IntentType.CHAT: "Goliath"
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
            "Elisa": "You are Elisa, the bridge to humanity. Connect technical concepts to human understanding.",
            "Xanatos": "You are Xanatos, the red team. Challenge assumptions and find weaknesses.",
            "Demona": "You are Demona, the failsafe. Consider edge cases and failure modes."
        }
        return prompts.get(member, prompts["Goliath"])
    
    def create_templates(self):
        """Create HTML template files."""
        template_dir = self._get_template_dir()
        
        # Main dashboard HTML
        dashboard_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Castle Wyvern Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            min-height: 100vh;
            color: #eee;
        }
        
        .header {
            background: rgba(0, 0, 0, 0.3);
            padding: 20px;
            text-align: center;
            border-bottom: 2px solid #e94560;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 5px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }
        
        .header p {
            color: #aaa;
            font-style: italic;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .grid {
            display: grid;
            grid-template-columns: 1fr 2fr 1fr;
            gap: 20px;
            margin-top: 20px;
        }
        
        .panel {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            padding: 20px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .panel h2 {
            margin-bottom: 15px;
            color: #e94560;
            border-bottom: 1px solid rgba(233, 69, 96, 0.3);
            padding-bottom: 10px;
        }
        
        /* Clan Members */
        .clan-member {
            display: flex;
            align-items: center;
            padding: 10px;
            margin: 8px 0;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            transition: all 0.3s;
            cursor: pointer;
        }
        
        .clan-member:hover {
            background: rgba(255, 255, 255, 0.1);
            transform: translateX(5px);
        }
        
        .clan-member .emoji {
            font-size: 1.5em;
            margin-right: 10px;
        }
        
        .clan-member .info {
            flex: 1;
        }
        
        .clan-member .name {
            font-weight: bold;
        }
        
        .clan-member .role {
            font-size: 0.8em;
            color: #aaa;
        }
        
        .status-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #00ff88;
            box-shadow: 0 0 10px #00ff88;
        }
        
        /* Chat Area */
        .chat-container {
            display: flex;
            flex-direction: column;
            height: 600px;
        }
        
        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 10px;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 8px;
            margin-bottom: 15px;
        }
        
        .message {
            margin: 10px 0;
            padding: 12px;
            border-radius: 8px;
            max-width: 80%;
        }
        
        .message.user {
            background: rgba(233, 69, 96, 0.3);
            margin-left: auto;
            border-left: 3px solid #e94560;
        }
        
        .message.bot {
            background: rgba(0, 206, 209, 0.2);
            border-left: 3px solid #00ced1;
        }
        
        .message-header {
            font-size: 0.8em;
            color: #aaa;
            margin-bottom: 5px;
        }
        
        .chat-input {
            display: flex;
            gap: 10px;
        }
        
        .chat-input input {
            flex: 1;
            padding: 12px;
            border: none;
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.1);
            color: #fff;
            font-size: 1em;
        }
        
        .chat-input input::placeholder {
            color: #888;
        }
        
        .chat-input button {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            background: #e94560;
            color: #fff;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s;
        }
        
        .chat-input button:hover {
            background: #ff6b6b;
            transform: scale(1.05);
        }
        
        /* Stats */
        .stat-item {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .stat-value {
            color: #00ff88;
            font-weight: bold;
        }
        
        /* Phoenix Gate */
        .phoenix-gate {
            background: rgba(255, 100, 0, 0.1);
            border: 1px solid rgba(255, 100, 0, 0.3);
            border-radius: 8px;
            padding: 15px;
            margin-top: 20px;
        }
        
        .phoenix-gate h3 {
            color: #ff8c00;
            margin-bottom: 10px;
        }
        
        .circuit {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
        }
        
        .circuit-state {
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 0.85em;
        }
        
        .circuit-state.closed {
            background: rgba(0, 255, 136, 0.2);
            color: #00ff88;
        }
        
        .circuit-state.open {
            background: rgba(255, 0, 0, 0.2);
            color: #ff4444;
        }
        
        /* Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: rgba(0, 0, 0, 0.2);
        }
        
        ::-webkit-scrollbar-thumb {
            background: rgba(255, 255, 255, 0.2);
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: rgba(255, 255, 255, 0.3);
        }
        
        /* Loading */
        .typing {
            display: none;
            align-items: center;
            gap: 5px;
            padding: 10px;
            color: #aaa;
        }
        
        .typing.active {
            display: flex;
        }
        
        .dot {
            width: 8px;
            height: 8px;
            background: #00ced1;
            border-radius: 50%;
            animation: bounce 1.4s infinite ease-in-out;
        }
        
        .dot:nth-child(1) { animation-delay: -0.32s; }
        .dot:nth-child(2) { animation-delay: -0.16s; }
        
        @keyframes bounce {
            0%, 80%, 100% { transform: scale(0); }
            40% { transform: scale(1); }
        }
        
        /* Responsive */
        @media (max-width: 1024px) {
            .grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🏰 Castle Wyvern</h1>
        <p>"We are defenders of the night! We are gargoyles!"</p>
    </div>
    
    <div class="container">
        <div class="grid">
            <!-- Left Panel: Clan Members -->
            <div class="panel">
                <h2>👥 The Manhattan Clan</h2>
                <div id="clan-list">
                    <!-- Clan members loaded via JS -->
                </div>
                
                <div class="phoenix-gate">
                    <h3>🔥 Phoenix Gate</h3>
                    <div id="phoenix-status">
                        <div class="circuit">
                            <span>Primary (Z.ai)</span>
                            <span class="circuit-state closed">CLOSED</span>
                        </div>
                        <div class="circuit">
                            <span>Fallback (OpenAI)</span>
                            <span class="circuit-state closed">CLOSED</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Center Panel: Chat -->
            <div class="panel">
                <h2>💬 Clan Council</h2>
                <div class="chat-container">
                    <div class="chat-messages" id="chat-messages">
                        <div class="message bot">
                            <div class="message-header">🦁 Goliath</div>
                            <div>Welcome to Castle Wyvern. How may the clan serve you today?</div>
                        </div>
                    </div>
                    
                    <div class="typing" id="typing">
                        <div class="dot"></div>
                        <div class="dot"></div>
                        <div class="dot"></div>
                        <span>The clan is consulting...</span>
                    </div>
                    
                    <div class="chat-input">
                        <input type="text" id="message-input" 
                               placeholder="Ask the clan anything..."
                               onkeypress="if(event.key==='Enter') sendMessage()">
                        <button onclick="sendMessage()">Send</button>
                    </div>
                </div>
            </div>
            
            <!-- Right Panel: Stats -->
            <div class="panel">
                <h2>📊 System Status</h2>
                <div id="stats">
                    <div class="stat-item">
                        <span>Total Memories</span>
                        <span class="stat-value" id="stat-memories">-</span>
                    </div>
                    <div class="stat-item">
                        <span>Active Nodes</span>
                        <span class="stat-value" id="stat-nodes">-</span>
                    </div>
                    <div class="stat-item">
                        <span>Version</span>
                        <span class="stat-value">v0.2.0</span>
                    </div>
                </div>
                
                <h2 style="margin-top: 30px;">🌐 Recent Activity</h2>
                <div id="recent-activity">
                    <!-- Recent conversations -->
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Load clan members
        async function loadClan() {
            try {
                const response = await fetch("/api/clan");
                const data = await response.json();
                const clanList = document.getElementById("clan-list");
                
                clanList.innerHTML = data.clan.map(member => `
                    <div class="clan-member" onclick="selectMember('${member.name}')">
                        <span class="emoji">${member.emoji}</span>
                        <div class="info">
                            <div class="name" style="color: ${member.color}">${member.name}</div>
                            <div class="role">${member.role}</div>
                        </div>
                        <div class="status-dot"></div>
                    </div>
                `).join("");
            } catch (e) {
                console.error("Failed to load clan:", e);
            }
        }
        
        // Load stats
        async function loadStats() {
            try {
                const response = await fetch("/api/stats");
                const data = await response.json();
                document.getElementById("stat-memories").textContent = data.total_memories || 0;
                
                const nodesResponse = await fetch("/api/nodes");
                const nodesData = await nodesResponse.json();
                document.getElementById("stat-nodes").textContent = nodesData.count || 0;
            } catch (e) {
                console.error("Failed to load stats:", e);
            }
        }
        
        // Send message
        async function sendMessage() {
            const input = document.getElementById("message-input");
            const message = input.value.trim();
            
            if (!message) return;
            
            // Add user message
            addMessage(message, "user", "You");
            input.value = "";
            
            // Show typing
            document.getElementById("typing").classList.add("active");
            
            try {
                const response = await fetch("/api/chat", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ message })
                });
                
                const data = await response.json();
                
                // Hide typing
                document.getElementById("typing").classList.remove("active");
                
                // Add bot response
                const emoji = getEmojiForMember(data.member);
                addMessage(data.response, "bot", `${emoji} ${data.member}`);
                
            } catch (e) {
                document.getElementById("typing").classList.remove("active");
                addMessage("Sorry, there was an error processing your request.", "bot", "⚠️ Error");
            }
        }
        
        function addMessage(text, type, sender) {
            const container = document.getElementById("chat-messages");
            const messageDiv = document.createElement("div");
            messageDiv.className = `message ${type}`;
            messageDiv.innerHTML = `
                <div class="message-header">${sender}</div>
                <div>${escapeHtml(text).replace(/\\n/g, "<br>")}</div>
            `;
            container.appendChild(messageDiv);
            container.scrollTop = container.scrollHeight;
        }
        
        function getEmojiForMember(member) {
            const emojis = {
                "Goliath": "🦁", "Lexington": "🔧", "Brooklyn": "🎯",
                "Broadway": "📜", "Hudson": "📚", "Bronx": "🐕",
                "Elisa": "🌉", "Xanatos": "🎭", "Demona": "🔥"
            };
            return emojis[member] || "🎭";
        }
        
        function escapeHtml(text) {
            const div = document.createElement("div");
            div.textContent = text;
            return div.innerHTML;
        }
        
        function selectMember(member) {
            const input = document.getElementById("message-input");
            input.value = `@${member} `;
            input.focus();
        }
        
        // Initialize
        loadClan();
        loadStats();
        setInterval(loadStats, 30000); // Refresh stats every 30s
    </script>
</body>
</html>
'''
        
        with open(os.path.join(template_dir, "dashboard.html"), "w") as f:
            f.write(dashboard_html.strip())
    
    def run(self, debug: bool = False):
        """Start the web dashboard server."""
        # Create templates
        self.create_templates()
        
        print(f"🏰 Castle Wyvern Web Dashboard")
        print(f"   URL: http://{self.host}:{self.port}")
        print(f"   Open your browser and navigate to the URL above")
        print()
        
        self.app.run(host=self.host, port=self.port, debug=debug)


# Standalone usage
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Castle Wyvern Web Dashboard")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=18792, help="Port to listen on")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    if not FLASK_AVAILABLE:
        print("⚠️  Flask not installed. Run: pip install flask flask-cors")
        exit(1)
    
    dashboard = WebDashboard(host=args.host, port=args.port)
    dashboard.run(debug=args.debug)
