"""
Goal-Based Agent Mode
Give high-level goals, agent plans and executes autonomously
"""

from typing import List, Dict, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import time
import json


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass
class SubTask:
    """A subtask within a goal."""

    id: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    assigned_to: Optional[str] = None  # Clan member name
    result: Optional[str] = None
    error: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None


@dataclass
class Goal:
    """A high-level goal with subtasks."""

    id: str
    description: str
    subtasks: List[SubTask] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    created_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None
    current_subtask_index: int = 0


class GoalBasedAgent:
    """
    Autonomous goal-based agent.

    Instead of: /code "write a function"
    You say: /goal "Build a REST API for a todo app"

    The agent:
    1. Breaks down the goal into subtasks
    2. Assigns each subtask to appropriate clan member
    3. Executes sequentially or in parallel
    4. Reports progress and final result
    """

    def __init__(self, clan_members: Dict[str, Callable]):
        """
        Initialize goal-based agent.

        Args:
            clan_members: Dict of clan member names to their execution functions
        """
        self.clan_members = clan_members
        self.active_goals: Dict[str, Goal] = {}
        self.completed_goals: List[Goal] = []

    def create_goal(self, description: str) -> Goal:
        """
        Create a new goal from description.

        This uses simple rule-based planning. In production,
        this would use an LLM to generate the plan.
        """
        goal_id = f"goal_{int(time.time())}_{hash(description) % 10000}"

        # Analyze description and create subtasks
        subtasks = self._plan_subtasks(description)

        goal = Goal(id=goal_id, description=description, subtasks=subtasks)

        self.active_goals[goal_id] = goal
        return goal

    def _plan_subtasks(self, description: str) -> List[SubTask]:
        """
        Break down goal into subtasks.

        Rule-based planning. Production version would use LLM.
        """
        description_lower = description.lower()
        subtasks = []

        # Detect goal type and create appropriate plan
        if "api" in description_lower or "rest" in description_lower:
            subtasks = self._plan_api_project(description)
        elif (
            "web" in description_lower
            or "website" in description_lower
            or "app" in description_lower
        ):
            subtasks = self._plan_web_project(description)
        elif "script" in description_lower or "automation" in description_lower:
            subtasks = self._plan_script_project(description)
        elif "analyze" in description_lower or "research" in description_lower:
            subtasks = self._plan_research_project(description)
        else:
            # Generic software project
            subtasks = self._plan_generic_project(description)

        return subtasks

    def _plan_api_project(self, description: str) -> List[SubTask]:
        """Plan for API/backend projects."""
        return [
            SubTask(
                id="1",
                description="Analyze requirements and design API structure",
                assigned_to="brooklyn",
                dependencies=[],
            ),
            SubTask(
                id="2",
                description="Design database schema",
                assigned_to="brooklyn",
                dependencies=["1"],
            ),
            SubTask(
                id="3",
                description="Implement core API endpoints",
                assigned_to="lexington",
                dependencies=["2"],
            ),
            SubTask(
                id="4",
                description="Add authentication and security",
                assigned_to="xanatos",
                dependencies=["3"],
            ),
            SubTask(
                id="5",
                description="Write tests and documentation",
                assigned_to="broadway",
                dependencies=["3"],
            ),
            SubTask(
                id="6",
                description="Review and optimize",
                assigned_to="goliath",
                dependencies=["4", "5"],
            ),
        ]

    def _plan_web_project(self, description: str) -> List[SubTask]:
        """Plan for web/frontend projects."""
        return [
            SubTask(
                id="1",
                description="Analyze requirements and design UI/UX",
                assigned_to="brooklyn",
                dependencies=[],
            ),
            SubTask(
                id="2",
                description="Create HTML structure and components",
                assigned_to="lexington",
                dependencies=["1"],
            ),
            SubTask(
                id="3",
                description="Add styling and responsive design",
                assigned_to="lexington",
                dependencies=["2"],
            ),
            SubTask(
                id="4",
                description="Implement interactivity with JavaScript",
                assigned_to="lexington",
                dependencies=["3"],
            ),
            SubTask(
                id="5",
                description="Accessibility and performance review",
                assigned_to="xanatos",
                dependencies=["4"],
            ),
            SubTask(
                id="6",
                description="Final review and documentation",
                assigned_to="goliath",
                dependencies=["5"],
            ),
        ]

    def _plan_script_project(self, description: str) -> List[SubTask]:
        """Plan for scripts and automation."""
        return [
            SubTask(
                id="1",
                description="Analyze requirements and plan approach",
                assigned_to="brooklyn",
                dependencies=[],
            ),
            SubTask(
                id="2",
                description="Implement core functionality",
                assigned_to="lexington",
                dependencies=["1"],
            ),
            SubTask(
                id="3",
                description="Add error handling and edge cases",
                assigned_to="lexington",
                dependencies=["2"],
            ),
            SubTask(
                id="4", description="Security review", assigned_to="xanatos", dependencies=["2"]
            ),
            SubTask(
                id="5",
                description="Documentation and usage examples",
                assigned_to="broadway",
                dependencies=["3", "4"],
            ),
        ]

    def _plan_research_project(self, description: str) -> List[SubTask]:
        """Plan for research and analysis."""
        return [
            SubTask(
                id="1",
                description="Define research scope and questions",
                assigned_to="brooklyn",
                dependencies=[],
            ),
            SubTask(
                id="2",
                description="Gather information and sources",
                assigned_to="jade",  # Browser agent
                dependencies=["1"],
            ),
            SubTask(
                id="3",
                description="Analyze and synthesize findings",
                assigned_to="hudson",
                dependencies=["2"],
            ),
            SubTask(
                id="4",
                description="Create summary and recommendations",
                assigned_to="broadway",
                dependencies=["3"],
            ),
            SubTask(id="5", description="Final review", assigned_to="goliath", dependencies=["4"]),
        ]

    def _plan_generic_project(self, description: str) -> List[SubTask]:
        """Generic plan for unknown project types."""
        return [
            SubTask(
                id="1",
                description="Analyze requirements and plan approach",
                assigned_to="brooklyn",
                dependencies=[],
            ),
            SubTask(
                id="2",
                description="Design solution architecture",
                assigned_to="brooklyn",
                dependencies=["1"],
            ),
            SubTask(
                id="3",
                description="Implement solution",
                assigned_to="lexington",
                dependencies=["2"],
            ),
            SubTask(
                id="4",
                description="Review and security check",
                assigned_to="xanatos",
                dependencies=["3"],
            ),
            SubTask(
                id="5", description="Documentation", assigned_to="broadway", dependencies=["4"]
            ),
        ]

    def execute_goal(self, goal_id: str, progress_callback: Optional[Callable] = None) -> Goal:
        """
        Execute a goal autonomously.

        Args:
            goal_id: Goal ID to execute
            progress_callback: Optional callback(current_subtask, total_subtasks, status)

        Returns:
            Completed Goal object
        """
        goal = self.active_goals.get(goal_id)
        if not goal:
            raise ValueError(f"Goal {goal_id} not found")

        goal.status = TaskStatus.IN_PROGRESS
        total = len(goal.subtasks)

        for i, subtask in enumerate(goal.subtasks):
            # Check if dependencies are met
            if not self._dependencies_met(subtask, goal):
                subtask.status = TaskStatus.BLOCKED
                continue

            # Update progress
            if progress_callback:
                progress_callback(i + 1, total, f"Executing: {subtask.description}")

            # Execute subtask
            subtask.status = TaskStatus.IN_PROGRESS
            subtask.started_at = time.time()

            try:
                # Get the clan member function
                member_func = self.clan_members.get(subtask.assigned_to)
                if member_func:
                    # Execute (simplified - in production would use actual AI)
                    result = member_func(subtask.description)
                    subtask.result = result
                    subtask.status = TaskStatus.COMPLETED
                else:
                    subtask.error = f"Clan member {subtask.assigned_to} not available"
                    subtask.status = TaskStatus.FAILED

            except Exception as e:
                subtask.error = str(e)
                subtask.status = TaskStatus.FAILED

            subtask.completed_at = time.time()

            # Update goal status
            goal.current_subtask_index = i + 1

        # Mark goal complete
        goal.status = TaskStatus.COMPLETED
        goal.completed_at = time.time()

        # Move to completed
        self.completed_goals.append(goal)
        del self.active_goals[goal_id]

        return goal

    def _dependencies_met(self, subtask: SubTask, goal: Goal) -> bool:
        """Check if all dependencies are completed."""
        for dep_id in subtask.dependencies:
            dep_task = next((st for st in goal.subtasks if st.id == dep_id), None)
            if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                return False
        return True

    def get_goal_summary(self, goal_id: str) -> str:
        """Get human-readable summary of goal progress."""
        goal = self.active_goals.get(goal_id) or next(
            (g for g in self.completed_goals if g.id == goal_id), None
        )

        if not goal:
            return "Goal not found"

        lines = [
            f"🎯 Goal: {goal.description}",
            f"Status: {goal.status.value.upper()}",
            f"Progress: {sum(1 for st in goal.subtasks if st.status == TaskStatus.COMPLETED)}/{len(goal.subtasks)} tasks complete",
            "",
            "Subtasks:",
        ]

        for st in goal.subtasks:
            status_icon = {
                TaskStatus.COMPLETED: "✅",
                TaskStatus.IN_PROGRESS: "🔄",
                TaskStatus.FAILED: "❌",
                TaskStatus.BLOCKED: "⛔",
                TaskStatus.PENDING: "⏳",
            }.get(st.status, "⏳")

            lines.append(f"  {status_icon} [{st.assigned_to}] {st.description}")

            if st.result:
                lines.append(f"      Result: {st.result[:100]}...")
            if st.error:
                lines.append(f"      Error: {st.error}")

        return "\n".join(lines)

    def list_active_goals(self) -> List[Goal]:
        """List all active goals."""
        return list(self.active_goals.values())

    def list_completed_goals(self) -> List[Goal]:
        """List all completed goals."""
        return self.completed_goals


# Example usage
if __name__ == "__main__":
    # Mock clan members
    def mock_member(task):
        return f"Completed: {task}"

    clan = {
        "brooklyn": mock_member,
        "lexington": mock_member,
        "xanatos": mock_member,
        "broadway": mock_member,
        "goliath": mock_member,
        "jade": mock_member,
        "hudson": mock_member,
    }

    agent = GoalBasedAgent(clan)

    # Create a goal
    goal = agent.create_goal("Build a REST API for a todo app")

    print("Created goal with subtasks:")
    for st in goal.subtasks:
        print(f"  {st.id}. [{st.assigned_to}] {st.description}")

    print(f"\n{agent.get_goal_summary(goal.id)}")
