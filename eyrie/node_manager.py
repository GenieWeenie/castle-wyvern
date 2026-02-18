"""
Castle Wyvern Multi-Node Distribution
Feature 10: Distribute workloads across multiple Stone nodes
"""

import json
import socket
import threading
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import hashlib
import uuid


class NodeStatus(Enum):
    """Status of a Stone node."""

    ONLINE = "online"
    OFFLINE = "offline"
    BUSY = "busy"
    DEGRADED = "degraded"


class TaskStatus(Enum):
    """Status of a distributed task."""

    PENDING = "pending"
    ASSIGNED = "assigned"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class StoneNode:
    """A Stone node (computing resource) in the Castle Wyvern network."""

    id: str
    name: str
    host: str
    port: int
    status: str
    capabilities: List[str]  # e.g., ["cpu", "gpu", "ollama"]
    load: float  # 0.0 to 1.0
    last_seen: str
    metadata: Dict[str, Any]

    @classmethod
    def create(
        cls,
        name: str,
        host: str,
        port: int = 18790,
        capabilities: Optional[List[str]] = None,
    ) -> "StoneNode":
        """Create a new Stone node."""
        node_id = str(uuid.uuid4())[:8]
        return cls(
            id=node_id,
            name=name,
            host=host,
            port=port,
            status=NodeStatus.ONLINE.value,
            capabilities=capabilities or ["cpu"],
            load=0.0,
            last_seen=datetime.now().isoformat(),
            metadata={},
        )


@dataclass
class DistributedTask:
    """A task that can be distributed across nodes."""

    id: str
    type: str  # "ai_call", "document_process", "code_review", etc.
    payload: Dict[str, Any]
    status: str
    assigned_node: Optional[str]
    created_at: str
    started_at: Optional[str]
    completed_at: Optional[str]
    result: Optional[Any]
    error: Optional[str]
    priority: int  # 1-5, higher = more important


class NodeManager:
    """
    Manages Stone nodes in the Castle Wyvern network.

    Features:
    - Node registration and discovery
    - Health monitoring
    - Load balancing
    - Task distribution
    """

    def __init__(self, storage_dir: str = "grimoorum/nodes"):
        self.storage_dir = storage_dir
        self.nodes: Dict[str, StoneNode] = {}
        self.tasks: Dict[str, DistributedTask] = {}
        self.local_node_id: Optional[str] = None

        self._initialize_storage()
        self._load_nodes()

        # Register self as local node
        self._register_local_node()

    def _initialize_storage(self):
        """Create storage directory."""
        import os

        os.makedirs(self.storage_dir, exist_ok=True)

    def _load_nodes(self):
        """Load known nodes from storage."""
        import os

        nodes_file = os.path.join(self.storage_dir, "nodes.json")
        tasks_file = os.path.join(self.storage_dir, "tasks.json")

        try:
            with open(nodes_file, "r") as f:
                data: Dict[str, Any] = json.load(f)
                self.nodes = {k: StoneNode(**v) for k, v in data.items()}  # type: ignore[arg-type]
        except (FileNotFoundError, json.JSONDecodeError):
            self.nodes = {}

        try:
            with open(tasks_file, "r") as f:
                data = json.load(f)
                self.tasks = {
                    k: DistributedTask(**v) for k, v in data.items()  # type: ignore[arg-type]
                }
        except (FileNotFoundError, json.JSONDecodeError):
            self.tasks = {}

    def _save_nodes(self):
        """Save nodes to storage."""
        import os

        nodes_file = os.path.join(self.storage_dir, "nodes.json")
        tasks_file = os.path.join(self.storage_dir, "tasks.json")

        with open(nodes_file, "w") as f:
            json.dump({k: asdict(v) for k, v in self.nodes.items()}, f, indent=2)

        with open(tasks_file, "w") as f:
            json.dump({k: asdict(v) for k, v in self.tasks.items()}, f, indent=2)

    def _register_local_node(self):
        """Register this machine as a Stone node."""
        hostname = socket.gethostname()
        local_ip = self._get_local_ip()

        # Check if we already have a local node
        for node in self.nodes.values():
            if node.host == local_ip and node.name == hostname:
                self.local_node_id = node.id
                # Update status
                node.status = NodeStatus.ONLINE.value
                node.last_seen = datetime.now().isoformat()
                self._save_nodes()
                return

        # Create new local node
        node = StoneNode.create(
            name=hostname,
            host=local_ip,
            capabilities=["cpu", "ollama"],  # Assume ollama might be available
        )

        self.nodes[node.id] = node
        self.local_node_id = node.id
        self._save_nodes()

    def _get_local_ip(self) -> str:
        """Get the local IP address."""
        try:
            # Connect to a remote address to determine local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return str(ip)
        except Exception:
            return "127.0.0.1"

    def register_node(
        self,
        name: str,
        host: str,
        port: int = 18790,
        capabilities: Optional[List[str]] = None,
    ) -> str:
        """
        Register a new Stone node.

        Returns:
            Node ID
        """
        # Check if node already exists
        for node in self.nodes.values():
            if node.host == host and node.port == port:
                # Update existing
                node.name = name
                node.capabilities = capabilities or ["cpu"]
                node.status = NodeStatus.ONLINE.value
                node.last_seen = datetime.now().isoformat()
                self._save_nodes()
                return node.id

        # Create new node
        node = StoneNode.create(name, host, port, capabilities)
        self.nodes[node.id] = node
        self._save_nodes()

        return node.id

    def unregister_node(self, node_id: str) -> bool:
        """Remove a node from the network."""
        if node_id not in self.nodes:
            return False

        del self.nodes[node_id]
        self._save_nodes()
        return True

    def get_node(self, node_id: str) -> Optional[StoneNode]:
        """Get a node by ID."""
        return self.nodes.get(node_id)

    def list_nodes(self) -> List[Dict]:
        """List all registered nodes."""
        return [asdict(node) for node in self.nodes.values()]

    def get_online_nodes(self) -> List[StoneNode]:
        """Get all online nodes."""
        return [node for node in self.nodes.values() if node.status == NodeStatus.ONLINE.value]

    def update_node_status(
        self, node_id: str, status: NodeStatus, load: Optional[float] = None
    ) -> bool:
        """Update a node's status."""
        if node_id not in self.nodes:
            return False

        node = self.nodes[node_id]
        node.status = status.value
        node.last_seen = datetime.now().isoformat()

        if load is not None:
            node.load = max(0.0, min(1.0, load))

        self._save_nodes()
        return True

    def check_node_health(self, node_id: str) -> bool:
        """
        Check if a node is reachable.
        Simple ping test - in production would check actual service.
        """
        node = self.nodes.get(node_id)
        if not node:
            return False

        try:
            # Try to connect to the node's port
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((node.host, node.port))
            sock.close()

            is_healthy = result == 0

            if is_healthy:
                self.update_node_status(node_id, NodeStatus.ONLINE)
            else:
                self.update_node_status(node_id, NodeStatus.OFFLINE)

            return is_healthy
        except Exception:
            self.update_node_status(node_id, NodeStatus.OFFLINE)
            return False

    def select_best_node(self, required_capabilities: Optional[List[str]] = None) -> Optional[str]:
        """
        Select the best node for a task using load balancing.

        Strategy:
        1. Filter by required capabilities
        2. Prefer nodes with lower load
        3. Fall back to local node
        """
        candidates = self.get_online_nodes()

        # Filter by capabilities
        if required_capabilities:
            candidates = [
                n for n in candidates if all(cap in n.capabilities for cap in required_capabilities)
            ]

        if not candidates:
            # Fall back to local node
            return self.local_node_id

        # Sort by load (lowest first)
        candidates.sort(key=lambda n: n.load)

        return candidates[0].id

    def create_task(self, task_type: str, payload: Dict[str, Any], priority: int = 3) -> str:
        """
        Create a new distributed task.

        Args:
            task_type: Type of task (ai_call, document_process, etc.)
            payload: Task data
            priority: 1-5, higher = more important

        Returns:
            Task ID
        """
        task_id = str(uuid.uuid4())[:12]

        task = DistributedTask(
            id=task_id,
            type=task_type,
            payload=payload,
            status=TaskStatus.PENDING.value,
            assigned_node=None,
            created_at=datetime.now().isoformat(),
            started_at=None,
            completed_at=None,
            result=None,
            error=None,
            priority=priority,
        )

        self.tasks[task_id] = task
        self._save_nodes()

        return task_id

    def assign_task(self, task_id: str, node_id: Optional[str] = None) -> bool:
        """
        Assign a pending task to a node.
        If node_id not provided, selects best available node.
        """
        if task_id not in self.tasks:
            return False

        task = self.tasks[task_id]

        if task.status != TaskStatus.PENDING.value:
            return False

        # Select node if not provided
        if node_id is None:
            node_id = self.select_best_node()

        if not node_id or node_id not in self.nodes:
            return False

        task.assigned_node = node_id
        task.status = TaskStatus.ASSIGNED.value
        task.started_at = datetime.now().isoformat()

        self._save_nodes()
        return True

    def complete_task(
        self,
        task_id: str,
        result: Any = None,
        error: Optional[str] = None,
    ) -> bool:
        """Mark a task as completed."""
        if task_id not in self.tasks:
            return False

        task = self.tasks[task_id]

        if error:
            task.status = TaskStatus.FAILED.value
            task.error = error
        else:
            task.status = TaskStatus.COMPLETED.value
            task.result = result

        task.completed_at = datetime.now().isoformat()
        self._save_nodes()

        return True

    def get_task(self, task_id: str) -> Optional[Dict]:
        """Get task details."""
        if task_id not in self.tasks:
            return None
        return asdict(self.tasks[task_id])

    def list_tasks(self, status: Optional[str] = None) -> List[Dict]:
        """List tasks, optionally filtered by status."""
        task_list = list(self.tasks.values())

        if status:
            task_list = [t for t in task_list if t.status == status]

        return [asdict(t) for t in task_list]

    def get_stats(self) -> Dict:
        """Get node network statistics."""
        total_nodes = len(self.nodes)
        online_nodes = len(self.get_online_nodes())

        status_counts: Dict[str, int] = {}
        for node in self.nodes.values():
            status_counts[node.status] = status_counts.get(node.status, 0) + 1

        task_counts: Dict[str, int] = {}
        for task in self.tasks.values():
            task_counts[task.status] = task_counts.get(task.status, 0) + 1

        return {
            "total_nodes": total_nodes,
            "online_nodes": online_nodes,
            "offline_nodes": total_nodes - online_nodes,
            "node_status": status_counts,
            "total_tasks": len(self.tasks),
            "task_status": task_counts,
            "local_node_id": self.local_node_id,
        }


if __name__ == "__main__":
    # Test node management
    print("🌐 Testing Multi-Node Distribution")
    print("=" * 50)

    manager = NodeManager()

    print("\n1. Local node registered:")
    local = manager.get_node(manager.local_node_id) if manager.local_node_id else None
    if local:
        print(f"   Name: {local.name}")
        print(f"   Host: {local.host}")
        print(f"   Status: {local.status}")

    print("\n2. Adding test nodes...")
    node1 = manager.register_node(
        "MacBook-Pro-Living-Room", "192.168.1.50", capabilities=["cpu", "gpu"]
    )
    print(f"   Added: {node1}")

    node2 = manager.register_node(
        "Ubuntu-Server-Office", "192.168.1.100", capabilities=["cpu", "ollama"]
    )
    print(f"   Added: {node2}")

    print("\n3. Creating distributed task...")
    task_id = manager.create_task(
        "ai_call", {"prompt": "Write a Python function", "model": "glm-4-plus"}, priority=4
    )
    print(f"   Task: {task_id}")

    print("\n4. Assigning task...")
    if manager.assign_task(task_id):
        task = manager.get_task(task_id)
        if task:
            print(f"   Assigned to: {task['assigned_node']}")

    print("\n5. Completing task...")
    manager.complete_task(task_id, result="def hello(): return 'world'")

    print("\n6. Stats:")
    stats = manager.get_stats()
    print(f"   Total nodes: {stats['total_nodes']}")
    print(f"   Online nodes: {stats['online_nodes']}")
    print(f"   Total tasks: {stats['total_tasks']}")

    print("\n✅ Multi-node distribution working!")
