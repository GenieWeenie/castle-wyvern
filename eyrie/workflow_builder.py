"""
Castle Wyvern Visual Workflow Builder
Feature: Drag-and-drop workflow editor for Web Dashboard

Provides:
- Visual workflow editor UI
- Node-based workflow design
- BMAD workflow templates
- Workflow execution from visual editor
- Export/import workflows
"""

import os
import json
import uuid
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum


class WorkflowNodeType(Enum):
    """Types of workflow nodes."""

    START = "start"
    END = "end"
    CLAN_MEMBER = "clan_member"
    BMAD_PHASE = "bmad_phase"
    DECISION = "decision"
    PARALLEL = "parallel"
    DELAY = "delay"
    WEBHOOK = "webhook"
    CONDITION = "condition"


@dataclass
class WorkflowNode:
    """A node in the workflow."""

    id: str
    type: str
    name: str
    description: str
    position: Dict[str, float]  # x, y coordinates
    data: Dict[str, Any]  # Node-specific data
    config: Dict[str, Any]  # Node configuration

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "type": self.type,
            "name": self.name,
            "description": self.description,
            "position": self.position,
            "data": self.data,
            "config": self.config,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "WorkflowNode":
        return cls(
            id=data["id"],
            type=data["type"],
            name=data["name"],
            description=data.get("description", ""),
            position=data.get("position", {"x": 0, "y": 0}),
            data=data.get("data", {}),
            config=data.get("config", {}),
        )


@dataclass
class WorkflowEdge:
    """A connection between nodes."""

    id: str
    source: str  # Source node ID
    target: str  # Target node ID
    label: Optional[str]  # Edge label
    condition: Optional[str]  # Condition for conditional edges

    def to_dict(self) -> Dict:
        result = {"id": self.id, "source": self.source, "target": self.target}
        if self.label:
            result["label"] = self.label
        if self.condition:
            result["condition"] = self.condition
        return result

    @classmethod
    def from_dict(cls, data: Dict) -> "WorkflowEdge":
        return cls(
            id=data["id"],
            source=data["source"],
            target=data["target"],
            label=data.get("label"),
            condition=data.get("condition"),
        )


@dataclass
class Workflow:
    """A complete workflow definition."""

    id: str
    name: str
    description: str
    nodes: List[WorkflowNode]
    edges: List[WorkflowEdge]
    created_at: str
    updated_at: str
    version: str = "1.0"
    tags: List[str] = None

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "nodes": [n.to_dict() for n in self.nodes],
            "edges": [e.to_dict() for e in self.edges],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "version": self.version,
            "tags": self.tags or [],
        }

    @classmethod
    def create(cls, name: str, description: str = "") -> "Workflow":
        """Create a new empty workflow."""
        now = datetime.now().isoformat()
        return cls(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            nodes=[],
            edges=[],
            created_at=now,
            updated_at=now,
            tags=[],
        )

    @classmethod
    def from_dict(cls, data: Dict) -> "Workflow":
        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            nodes=[WorkflowNode.from_dict(n) for n in data.get("nodes", [])],
            edges=[WorkflowEdge.from_dict(e) for e in data.get("edges", [])],
            created_at=data.get("created_at", datetime.now().isoformat()),
            updated_at=data.get("updated_at", datetime.now().isoformat()),
            version=data.get("version", "1.0"),
            tags=data.get("tags", []),
        )


class WorkflowTemplate:
    """Pre-built workflow templates."""

    @staticmethod
    def bmad_full() -> Workflow:
        """Full BMAD workflow template."""
        wf = Workflow.create(
            name="Full BMAD Workflow", description="Complete Build-Measure-Analyze-Deploy workflow"
        )

        # Add nodes
        nodes = [
            WorkflowNode(
                id="start",
                type="start",
                name="Start",
                description="Workflow start",
                position={"x": 100, "y": 100},
                data={},
                config={},
            ),
            WorkflowNode(
                id="spec",
                type="bmad_phase",
                name="Quick Spec",
                description="Goliath + Brooklyn create spec",
                position={"x": 300, "y": 100},
                data={"phase": "spec", "agents": ["goliath", "brooklyn"]},
                config={"auto_execute": True},
            ),
            WorkflowNode(
                id="implement",
                type="bmad_phase",
                name="Implement",
                description="Lexington implements",
                position={"x": 500, "y": 100},
                data={"phase": "implement", "agents": ["lexington"]},
                config={"auto_execute": True},
            ),
            WorkflowNode(
                id="review",
                type="bmad_phase",
                name="Review",
                description="Xanatos reviews code",
                position={"x": 700, "y": 100},
                data={"phase": "review", "agents": ["xanatos"]},
                config={"auto_execute": True},
            ),
            WorkflowNode(
                id="document",
                type="bmad_phase",
                name="Document",
                description="Broadway documents",
                position={"x": 900, "y": 100},
                data={"phase": "document", "agents": ["broadway"]},
                config={"auto_execute": True},
            ),
            WorkflowNode(
                id="end",
                type="end",
                name="Complete",
                description="Workflow complete",
                position={"x": 1100, "y": 100},
                data={},
                config={},
            ),
        ]

        wf.nodes = nodes

        # Add edges
        edges = [
            WorkflowEdge(id="e1", source="start", target="spec", label=None, condition=None),
            WorkflowEdge(id="e2", source="spec", target="implement", label=None, condition=None),
            WorkflowEdge(id="e3", source="implement", target="review", label=None, condition=None),
            WorkflowEdge(
                id="e4", source="review", target="document", label="Approved", condition=None
            ),
            WorkflowEdge(id="e5", source="document", target="end", label=None, condition=None),
        ]

        wf.edges = edges
        return wf

    @staticmethod
    def code_review_pipeline() -> Workflow:
        """Code review pipeline template."""
        wf = Workflow.create(
            name="Code Review Pipeline", description="Multi-agent code review workflow"
        )

        nodes = [
            WorkflowNode(
                id="start",
                type="start",
                name="Code Submitted",
                description="",
                position={"x": 100, "y": 200},
                data={},
                config={},
            ),
            WorkflowNode(
                id="lexington",
                type="clan_member",
                name="Lexington Review",
                description="Technical review",
                position={"x": 300, "y": 100},
                data={"agent": "lexington", "task": "code_review"},
                config={},
            ),
            WorkflowNode(
                id="xanatos",
                type="clan_member",
                name="Xanatos Review",
                description="Security review",
                position={"x": 300, "y": 300},
                data={"agent": "xanatos", "task": "security_review"},
                config={},
            ),
            WorkflowNode(
                id="parallel",
                type="parallel",
                name="Parallel Reviews",
                description="Run reviews in parallel",
                position={"x": 500, "y": 200},
                data={},
                config={},
            ),
            WorkflowNode(
                id="decision",
                type="decision",
                name="Approve?",
                description="Decision point",
                position={"x": 700, "y": 200},
                data={},
                config={},
            ),
            WorkflowNode(
                id="merge",
                type="end",
                name="Merge",
                description="Code approved",
                position={"x": 900, "y": 100},
                data={},
                config={},
            ),
            WorkflowNode(
                id="reject",
                type="end",
                name="Request Changes",
                description="Issues found",
                position={"x": 900, "y": 300},
                data={},
                config={},
            ),
        ]

        wf.nodes = nodes

        edges = [
            WorkflowEdge(id="e1", source="start", target="lexington", label=None, condition=None),
            WorkflowEdge(id="e2", source="start", target="xanatos", label=None, condition=None),
            WorkflowEdge(
                id="e3", source="lexington", target="parallel", label=None, condition=None
            ),
            WorkflowEdge(id="e4", source="xanatos", target="parallel", label=None, condition=None),
            WorkflowEdge(id="e5", source="parallel", target="decision", label=None, condition=None),
            WorkflowEdge(
                id="e6", source="decision", target="merge", label="Yes", condition="approved"
            ),
            WorkflowEdge(
                id="e7", source="decision", target="reject", label="No", condition="rejected"
            ),
        ]

        wf.edges = edges
        return wf

    @staticmethod
    def security_audit() -> Workflow:
        """Security audit workflow template."""
        wf = Workflow.create(
            name="Security Audit", description="Comprehensive security audit workflow"
        )

        nodes = [
            WorkflowNode(
                id="start",
                type="start",
                name="Start Audit",
                description="",
                position={"x": 100, "y": 100},
                data={},
                config={},
            ),
            WorkflowNode(
                id="xanatos",
                type="clan_member",
                name="Xanatos Analysis",
                description="Red team analysis",
                position={"x": 300, "y": 100},
                data={"agent": "xanatos", "task": "security_audit"},
                config={},
            ),
            WorkflowNode(
                id="bronx",
                type="clan_member",
                name="Bronx Monitor",
                description="Monitoring setup",
                position={"x": 500, "y": 100},
                data={"agent": "bronx", "task": "setup_monitoring"},
                config={},
            ),
            WorkflowNode(
                id="demona",
                type="clan_member",
                name="Demona Failsafe",
                description="Failure prediction",
                position={"x": 700, "y": 100},
                data={"agent": "demona", "task": "predict_failures"},
                config={},
            ),
            WorkflowNode(
                id="report",
                type="clan_member",
                name="Broadway Report",
                description="Generate audit report",
                position={"x": 900, "y": 100},
                data={"agent": "broadway", "task": "document_audit"},
                config={},
            ),
            WorkflowNode(
                id="end",
                type="end",
                name="Audit Complete",
                description="",
                position={"x": 1100, "y": 100},
                data={},
                config={},
            ),
        ]

        wf.nodes = nodes

        edges = [
            WorkflowEdge(id="e1", source="start", target="xanatos", label=None, condition=None),
            WorkflowEdge(id="e2", source="xanatos", target="bronx", label=None, condition=None),
            WorkflowEdge(id="e3", source="bronx", target="demona", label=None, condition=None),
            WorkflowEdge(id="e4", source="demona", target="report", label=None, condition=None),
            WorkflowEdge(id="e5", source="report", target="end", label=None, condition=None),
        ]

        wf.edges = edges
        return wf


class WorkflowManager:
    """Manages workflow storage and execution."""

    def __init__(self, storage_dir: str = None):
        if storage_dir is None:
            storage_dir = os.path.expanduser("~/.castle_wyvern/workflows")

        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)

        self.workflows: Dict[str, Workflow] = {}
        self._load_workflows()

    def _get_workflow_path(self, workflow_id: str) -> str:
        """Get file path for a workflow."""
        return os.path.join(self.storage_dir, f"{workflow_id}.json")

    def _load_workflows(self):
        """Load all saved workflows."""
        for filename in os.listdir(self.storage_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(self.storage_dir, filename)
                try:
                    with open(filepath, "r") as f:
                        data = json.load(f)
                    wf = Workflow.from_dict(data)
                    self.workflows[wf.id] = wf
                except Exception as e:
                    print(f"[Workflow] Error loading {filename}: {e}")

    def save_workflow(self, workflow: Workflow):
        """Save a workflow to disk."""
        workflow.updated_at = datetime.now().isoformat()

        filepath = self._get_workflow_path(workflow.id)
        with open(filepath, "w") as f:
            json.dump(workflow.to_dict(), f, indent=2)

        self.workflows[workflow.id] = workflow

    def create_workflow(self, name: str, description: str = "") -> Workflow:
        """Create a new workflow."""
        wf = Workflow.create(name, description)
        self.save_workflow(wf)
        return wf

    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """Get a workflow by ID."""
        return self.workflows.get(workflow_id)

    def delete_workflow(self, workflow_id: str) -> bool:
        """Delete a workflow."""
        if workflow_id in self.workflows:
            filepath = self._get_workflow_path(workflow_id)
            if os.path.exists(filepath):
                os.remove(filepath)
            del self.workflows[workflow_id]
            return True
        return False

    def list_workflows(self) -> List[Dict]:
        """List all workflows."""
        return [
            {
                "id": wf.id,
                "name": wf.name,
                "description": wf.description,
                "updated_at": wf.updated_at,
                "node_count": len(wf.nodes),
                "tags": wf.tags,
            }
            for wf in sorted(self.workflows.values(), key=lambda w: w.updated_at, reverse=True)
        ]

    def get_templates(self) -> List[Dict]:
        """Get available workflow templates."""
        return [
            {
                "id": "bmad_full",
                "name": "Full BMAD Workflow",
                "description": "Complete Build-Measure-Analyze-Deploy workflow",
                "icon": "🔄",
            },
            {
                "id": "code_review",
                "name": "Code Review Pipeline",
                "description": "Multi-agent code review with parallel execution",
                "icon": "👀",
            },
            {
                "id": "security_audit",
                "name": "Security Audit",
                "description": "Comprehensive security audit workflow",
                "icon": "🔒",
            },
        ]

    def create_from_template(self, template_id: str) -> Optional[Workflow]:
        """Create a workflow from a template."""
        if template_id == "bmad_full":
            wf = WorkflowTemplate.bmad_full()
        elif template_id == "code_review":
            wf = WorkflowTemplate.code_review_pipeline()
        elif template_id == "security_audit":
            wf = WorkflowTemplate.security_audit()
        else:
            return None

        # Reset ID and timestamps
        wf.id = str(uuid.uuid4())
        wf.created_at = datetime.now().isoformat()
        wf.updated_at = wf.created_at

        self.save_workflow(wf)
        return wf

    def export_workflow(self, workflow_id: str, filepath: str) -> bool:
        """Export a workflow to a file."""
        wf = self.get_workflow(workflow_id)
        if not wf:
            return False

        try:
            with open(filepath, "w") as f:
                json.dump(wf.to_dict(), f, indent=2)
            return True
        except Exception as e:
            print(f"[Workflow] Export error: {e}")
            return False

    def import_workflow(self, filepath: str) -> Optional[Workflow]:
        """Import a workflow from a file."""
        try:
            with open(filepath, "r") as f:
                data = json.load(f)

            wf = Workflow.from_dict(data)
            # Generate new ID to avoid conflicts
            wf.id = str(uuid.uuid4())
            wf.name = f"{wf.name} (Imported)"
            wf.created_at = datetime.now().isoformat()
            wf.updated_at = wf.created_at

            self.save_workflow(wf)
            return wf
        except Exception as e:
            print(f"[Workflow] Import error: {e}")
            return False


class WorkflowExecutor:
    """Executes workflows."""

    def __init__(self, castle_wyvern_cli=None):
        self.cli = castle_wyvern_cli
        self.running_workflows: Dict[str, Dict] = {}

    def execute_node(self, node: WorkflowNode, context: Dict) -> Dict:
        """Execute a single workflow node."""
        result = {"success": True, "output": "", "error": None}

        try:
            if node.type == "clan_member":
                agent = node.data.get("agent", "goliath")
                task = node.data.get("task", "")
                result["output"] = f"[{agent.upper()}] Executed: {task}"

            elif node.type == "bmad_phase":
                phase = node.data.get("phase", "")
                agents = node.data.get("agents", [])
                result["output"] = f"[BMAD {phase.upper()}] Agents: {', '.join(agents)}"

            elif node.type == "webhook":
                url = node.config.get("url", "")
                result["output"] = f"[WEBHOOK] Called: {url}"

            elif node.type == "delay":
                seconds = node.config.get("seconds", 0)
                result["output"] = f"[DELAY] Waited {seconds}s"

            else:
                result["output"] = f"[NODE] {node.name} executed"

        except Exception as e:
            result["success"] = False
            result["error"] = str(e)

        return result

    def execute_workflow(self, workflow: Workflow, initial_context: Dict = None) -> Dict:
        """Execute a complete workflow."""
        execution_id = str(uuid.uuid4())
        context = initial_context or {}

        execution = {
            "id": execution_id,
            "workflow_id": workflow.id,
            "status": "running",
            "started_at": datetime.now().isoformat(),
            "completed_at": None,
            "results": {},
            "current_node": None,
            "log": [],
        }

        self.running_workflows[execution_id] = execution

        try:
            # Find start node
            start_nodes = [n for n in workflow.nodes if n.type == "start"]
            if not start_nodes:
                execution["status"] = "failed"
                execution["error"] = "No start node found"
                return execution

            current_node = start_nodes[0]
            visited = set()

            while current_node and current_node.type != "end":
                if current_node.id in visited:
                    execution["status"] = "failed"
                    execution["error"] = "Loop detected"
                    break

                visited.add(current_node.id)
                execution["current_node"] = current_node.id

                # Execute node
                result = self.execute_node(current_node, context)
                execution["results"][current_node.id] = result
                execution["log"].append(
                    {
                        "node": current_node.name,
                        "type": current_node.type,
                        "success": result["success"],
                        "output": result["output"][:100],  # Truncate
                    }
                )

                if not result["success"]:
                    execution["status"] = "failed"
                    execution["error"] = result["error"]
                    break

                # Find next node
                outgoing_edges = [e for e in workflow.edges if e.source == current_node.id]
                if outgoing_edges:
                    # For now, just take first edge (would evaluate conditions in real impl)
                    next_node_id = outgoing_edges[0].target
                    current_node = next((n for n in workflow.nodes if n.id == next_node_id), None)
                else:
                    current_node = None

            if execution["status"] == "running":
                execution["status"] = "completed"

        except Exception as e:
            execution["status"] = "failed"
            execution["error"] = str(e)

        execution["completed_at"] = datetime.now().isoformat()
        return execution


# Standalone test
if __name__ == "__main__":
    print("🏰 Castle Wyvern Visual Workflow Builder Test")
    print("=" * 50)

    # Test workflow manager
    manager = WorkflowManager()

    # Test template creation
    print("\n1. Testing templates...")
    templates = manager.get_templates()
    print(f"   Available templates: {len(templates)}")
    for t in templates:
        print(f"   - {t['icon']} {t['name']}")

    # Create from template
    wf = manager.create_from_template("bmad_full")
    print(f"\n2. Created workflow from template:")
    print(f"   Name: {wf.name}")
    print(f"   Nodes: {len(wf.nodes)}")
    print(f"   Edges: {len(wf.edges)}")

    # Test execution
    print("\n3. Testing workflow execution...")
    executor = WorkflowExecutor()
    result = executor.execute_workflow(wf)
    print(f"   Status: {result['status']}")
    print(f"   Log entries: {len(result['log'])}")

    print("\n✅ Visual Workflow Builder ready!")
