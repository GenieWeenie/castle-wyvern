"""
Agent Coordination Loops
Self-organizing agent swarms with dynamic team formation

Based on research from r/LocalLLaMA community:
- Match → Exchange → Score → Re-match loop
- Dynamic team formation based on task fit
- Performance scoring per task
- Optimal team composition automatically
"""

import random
import time
import json
from typing import Dict, List, Optional, Callable, Tuple, Any, cast
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import pickle


class TaskStatus(Enum):
    PENDING = "pending"
    MATCHING = "matching"
    EXCHANGING = "exchanging"
    EXECUTING = "executing"
    SCORING = "scoring"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class AgentProfile:
    """Profile of an agent in the coordination system."""

    id: str
    name: str
    capabilities: List[str]
    performance_score: float = 1.0
    tasks_completed: int = 0
    tasks_failed: int = 0
    specialization: str = "general"
    reliability: float = 1.0  # 0.0 to 1.0
    speed: float = 1.0  # Tasks per hour
    collaboration_score: float = 1.0  # How well they work with others
    last_active: float = field(default_factory=time.time)

    def calculate_fitness(self, task_requirements: List[str]) -> float:
        """Calculate how fit this agent is for a task."""
        # Match capabilities with requirements
        matches = sum(1 for req in task_requirements if req in self.capabilities)
        match_ratio = matches / len(task_requirements) if task_requirements else 0.5

        # Weighted fitness score
        fitness = (
            match_ratio * 0.4
            + self.performance_score * 0.2
            + self.reliability * 0.2
            + self.collaboration_score * 0.2
        )

        return fitness


@dataclass
class CoordinationTask:
    """A task in the coordination system."""

    id: str
    description: str
    requirements: List[str]
    status: TaskStatus = TaskStatus.PENDING
    assigned_agents: List[str] = field(default_factory=list)
    team_score: float = 0.0
    execution_time: float = 0.0
    result: Any = None
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    exchange_history: List[Dict] = field(default_factory=list)


@dataclass
class TeamComposition:
    """A team of agents for a task."""

    task_id: str
    agents: List[str]
    formation_score: float = 0.0
    estimated_success_rate: float = 0.0
    estimated_completion_time: float = 0.0


class AgentCoordinationLoop:
    """
    Self-organizing agent coordination system.

    Implements the coordination loop:
    1. MATCH - Find initial team based on task requirements
    2. EXCHANGE - Agents exchange information, refine approach
    3. EXECUTE - Team executes the task
    4. SCORE - Evaluate performance
    5. RE-MATCH - Learn and improve future team formation

    Inspired by research in multi-agent systems and swarm intelligence.
    """

    def __init__(self, storage_dir: str = "~/.castle_wyvern/coordination"):
        self.storage_dir = Path(storage_dir).expanduser()
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        self.agents: Dict[str, AgentProfile] = {}
        self.tasks: Dict[str, CoordinationTask] = {}
        self.completed_tasks: List[CoordinationTask] = []

        # Coordination parameters
        self.match_threshold = 0.6  # Minimum fitness score to match
        self.team_size_min = 2
        self.team_size_max = 4
        self.exchange_rounds = 2

        self._load_data()

    def _load_data(self):
        """Load coordination data from disk."""
        agents_file = self.storage_dir / "agents.pkl"
        tasks_file = self.storage_dir / "tasks.pkl"

        if agents_file.exists():
            with open(agents_file, "rb") as f:
                self.agents = pickle.load(f)

        if tasks_file.exists():
            with open(tasks_file, "rb") as f:
                data = pickle.load(f)
                self.tasks = data.get("tasks", {})
                self.completed_tasks = data.get("completed", [])

    def save_data(self):
        """Save coordination data to disk."""
        agents_file = self.storage_dir / "agents.pkl"
        tasks_file = self.storage_dir / "tasks.pkl"

        with open(agents_file, "wb") as f:
            pickle.dump(self.agents, f)

        with open(tasks_file, "wb") as f:
            pickle.dump({"tasks": self.tasks, "completed": self.completed_tasks}, f)

    def register_agent(
        self, agent_id: str, name: str, capabilities: List[str], specialization: str = "general"
    ) -> AgentProfile:
        """Register an agent in the coordination system."""
        agent = AgentProfile(
            id=agent_id, name=name, capabilities=capabilities, specialization=specialization
        )

        self.agents[agent_id] = agent
        self.save_data()

        return agent

    def create_task(self, description: str, requirements: List[str]) -> CoordinationTask:
        """Create a new coordination task."""
        task_id = f"task_{int(time.time())}_{hash(description) % 10000}"

        task = CoordinationTask(id=task_id, description=description, requirements=requirements)

        self.tasks[task_id] = task
        return task

    def match_phase(self, task_id: str) -> TeamComposition:
        """
        Phase 1: MATCH
        Find the best team for the task based on agent fitness scores.
        """
        task = self.tasks.get(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        task.status = TaskStatus.MATCHING

        # Calculate fitness for all agents
        agent_fitness = []
        for agent_id, agent in self.agents.items():
            fitness = agent.calculate_fitness(task.requirements)
            if fitness >= self.match_threshold:
                agent_fitness.append((agent_id, fitness))

        # Sort by fitness (highest first)
        agent_fitness.sort(key=lambda x: x[1], reverse=True)

        # Select top N agents
        team_size = min(self.team_size_max, max(self.team_size_min, len(agent_fitness)))

        selected_agents = [agent_id for agent_id, _ in agent_fitness[:team_size]]

        # Calculate team formation score
        formation_score = (
            sum(fitness for _, fitness in agent_fitness[:team_size]) / team_size
            if team_size > 0
            else 0
        )

        # Estimate success rate and completion time
        avg_reliability = (
            sum(self.agents[aid].reliability for aid in selected_agents) / len(selected_agents)
            if selected_agents
            else 0
        )
        avg_speed = (
            sum(self.agents[aid].speed for aid in selected_agents) / len(selected_agents)
            if selected_agents
            else 1
        )

        team = TeamComposition(
            task_id=task_id,
            agents=selected_agents,
            formation_score=formation_score,
            estimated_success_rate=avg_reliability * formation_score,
            estimated_completion_time=len(task.requirements) * 10 / avg_speed,  # minutes
        )

        # Update task
        task.assigned_agents = selected_agents
        task.team_score = formation_score
        task.exchange_history.append(
            {
                "phase": "MATCH",
                "agents": selected_agents,
                "score": formation_score,
                "timestamp": time.time(),
            }
        )

        return team

    def exchange_phase(self, task_id: str) -> Dict:
        """
        Phase 2: EXCHANGE
        Agents exchange information and refine the approach.
        """
        task = self.tasks.get(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        task.status = TaskStatus.EXCHANGING

        exchanges = []

        # Simulate agent exchange rounds
        for round_num in range(self.exchange_rounds):
            round_exchanges = []

            for agent_id in task.assigned_agents:
                agent = self.agents.get(agent_id)
                if agent:
                    # Agent shares their expertise
                    relevant_caps = [cap for cap in agent.capabilities if cap in task.requirements]

                    exchange = {
                        "round": round_num + 1,
                        "agent": agent_id,
                        "agent_name": agent.name,
                        "expertise": relevant_caps,
                        "contribution": f"{agent.name} contributes expertise in {', '.join(relevant_caps)}",
                    }

                    round_exchanges.append(exchange)

            exchanges.append({"round": round_num + 1, "exchanges": round_exchanges})

        # Update task
        task.exchange_history.append(
            {
                "phase": "EXCHANGE",
                "rounds": self.exchange_rounds,
                "exchanges": exchanges,
                "timestamp": time.time(),
            }
        )

        return {
            "task_id": task_id,
            "rounds": self.exchange_rounds,
            "exchanges": exchanges,
            "participating_agents": len(task.assigned_agents),
        }

    def execute_phase(self, task_id: str, execution_func: Optional[Callable] = None) -> Dict:
        """
        Phase 3: EXECUTE
        Execute the task with the coordinated team.
        """
        task = self.tasks.get(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        task.status = TaskStatus.EXECUTING
        task.started_at = time.time()

        # Simulate execution (in production, would call actual agent functions)
        start_time = time.time()

        if execution_func:
            try:
                result = execution_func(task)
                success = True
            except Exception as e:
                result = str(e)
                success = False
        else:
            # Simulate execution
            time.sleep(0.5)  # Simulate work

            # Calculate success probability based on team score
            success_probability = task.team_score * 0.8 + 0.2
            success = random.random() < success_probability

            if success:
                result = f"Task '{task.description}' completed successfully by team: {', '.join(task.assigned_agents)}"
            else:
                result = f"Task '{task.description}' encountered issues"

        execution_time = time.time() - start_time

        # Update task
        task.execution_time = execution_time
        task.result = result
        task.completed_at = time.time()
        task.status = TaskStatus.COMPLETED if success else TaskStatus.FAILED

        # Update agent stats
        for agent_id in task.assigned_agents:
            agent = self.agents.get(agent_id)
            if agent:
                agent.tasks_completed += 1 if success else 0
                agent.tasks_failed += 0 if success else 1
                agent.last_active = time.time()

        task.exchange_history.append(
            {
                "phase": "EXECUTE",
                "success": success,
                "execution_time": execution_time,
                "timestamp": time.time(),
            }
        )

        return {
            "task_id": task_id,
            "success": success,
            "execution_time": execution_time,
            "result": result,
            "team": task.assigned_agents,
        }

    def score_phase(self, task_id: str, manual_score: Optional[float] = None) -> Dict:
        """
        Phase 4: SCORE
        Evaluate team performance and update agent profiles.
        """
        task = self.tasks.get(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        task.status = TaskStatus.SCORING

        # Calculate score
        if manual_score is not None:
            performance_score = manual_score
        else:
            # Auto-calculate based on execution
            success_bonus = 1.0 if task.status == TaskStatus.COMPLETED else 0.0
            time_efficiency = min(1.0, 10 / (task.execution_time + 1))  # Normalize
            team_synergy = task.team_score

            performance_score = success_bonus * 0.5 + time_efficiency * 0.3 + team_synergy * 0.2

        # Update agent performance scores
        for agent_id in task.assigned_agents:
            agent = self.agents.get(agent_id)
            if agent:
                # Moving average of performance
                agent.performance_score = (
                    agent.performance_score * agent.tasks_completed + performance_score
                ) / (agent.tasks_completed + 1)

                # Update collaboration score based on team success
                if task.status == TaskStatus.COMPLETED:
                    agent.collaboration_score = min(1.0, agent.collaboration_score + 0.05)

        task.exchange_history.append(
            {"phase": "SCORE", "performance_score": performance_score, "timestamp": time.time()}
        )

        # Move to completed tasks
        self.completed_tasks.append(task)
        del self.tasks[task_id]

        self.save_data()

        return {
            "task_id": task_id,
            "performance_score": performance_score,
            "team": task.assigned_agents,
            "status": "completed" if task.status == TaskStatus.COMPLETED else "failed",
        }

    def run_coordination_loop(
        self, description: str, requirements: List[str], execution_func: Optional[Callable] = None
    ) -> Dict:
        """
        Run the full coordination loop: MATCH → EXCHANGE → EXECUTE → SCORE
        """
        # Create task
        task = self.create_task(description, requirements)

        results: Dict[str, Any] = {"task_id": task.id, "description": description, "phases": {}}

        # Phase 1: MATCH
        team = self.match_phase(task.id)
        results["phases"]["match"] = {
            "team": team.agents,
            "formation_score": team.formation_score,
            "estimated_success": team.estimated_success_rate,
        }

        # Phase 2: EXCHANGE
        exchange = self.exchange_phase(task.id)
        results["phases"]["exchange"] = exchange

        # Phase 3: EXECUTE
        execution = self.execute_phase(task.id, execution_func)
        results["phases"]["execute"] = execution

        # Phase 4: SCORE
        scoring = self.score_phase(task.id)
        results["phases"]["score"] = scoring

        results["final_status"] = scoring["status"]
        results["performance_score"] = scoring["performance_score"]

        return cast(Dict[str, Any], results)

    def get_agent_stats(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get statistics for an agent."""
        agent = self.agents.get(agent_id)
        if not agent:
            return None

        return {
            "id": agent.id,
            "name": agent.name,
            "specialization": agent.specialization,
            "capabilities": agent.capabilities,
            "performance_score": agent.performance_score,
            "tasks_completed": agent.tasks_completed,
            "tasks_failed": agent.tasks_failed,
            "reliability": agent.reliability,
            "speed": agent.speed,
            "collaboration_score": agent.collaboration_score,
        }

    def get_all_agents(self) -> List[Optional[Dict[str, Any]]]:
        """Get all registered agents."""
        return [self.get_agent_stats(aid) for aid in self.agents.keys()]

    def get_coordination_stats(self) -> Dict[str, Any]:
        """Get overall coordination system statistics."""
        total_tasks = len(self.completed_tasks) + len(self.tasks)
        completed = len([t for t in self.completed_tasks if t.status == TaskStatus.COMPLETED])
        failed = len([t for t in self.completed_tasks if t.status == TaskStatus.FAILED])

        return {
            "registered_agents": len(self.agents),
            "active_tasks": len(self.tasks),
            "completed_tasks": completed,
            "failed_tasks": failed,
            "success_rate": completed / (completed + failed) if (completed + failed) > 0 else 0,
            "avg_team_size": (
                sum(len(t.assigned_agents) for t in self.completed_tasks)
                / len(self.completed_tasks)
                if self.completed_tasks
                else 0
            ),
        }

    def reinitialize_agents(self):
        """
        Phase 5: RE-MATCH (implicit)
        Reinitialize agents based on learned performance.
        This happens continuously as agents complete tasks.
        """
        # Update reliability based on success rate
        for agent in self.agents.values():
            total = agent.tasks_completed + agent.tasks_failed
            if total > 0:
                agent.reliability = agent.tasks_completed / total

        self.save_data()


# Integration with Castle Wyvern Clan
class ClanCoordinationManager:
    """
    Bridge between Castle Wyvern clan members and coordination system.
    """

    def __init__(self):
        self.coordination = AgentCoordinationLoop()
        self._register_clan_members()

    def _register_clan_members(self):
        """Register all clan members as coordination agents."""
        clan_members = [
            ("goliath", "Goliath", ["strategy", "leadership", "decision_making"], "leader"),
            (
                "lexington",
                "Lexington",
                ["coding", "technical", "implementation", "debugging"],
                "technician",
            ),
            (
                "brooklyn",
                "Brooklyn",
                ["architecture", "planning", "strategy", "design"],
                "strategist",
            ),
            (
                "broadway",
                "Broadway",
                ["documentation", "writing", "summarization", "communication"],
                "chronicler",
            ),
            ("hudson", "Hudson", ["memory", "history", "context", "archiving"], "archivist"),
            ("xanatos", "Xanatos", ["security", "review", "testing", "auditing"], "red_team"),
            ("demona", "Demona", ["error_prediction", "edge_cases", "failsafe"], "failsafe"),
            ("elisa", "Elisa", ["ethics", "human_context", "legal", "bridging"], "bridge"),
            ("jade", "Jade", ["research", "browsing", "information_gathering"], "researcher"),
        ]

        for agent_id, name, capabilities, spec in clan_members:
            if agent_id not in self.coordination.agents:
                self.coordination.register_agent(agent_id, name, capabilities, spec)

    def coordinate_task(self, description: str, requirements: List[str]) -> Dict:
        """
        Coordinate a task using the clan members.

        Example:
            coordinate_task(
                "Build authentication system",
                ["security", "coding", "technical"]
            )
        """
        return cast(Dict[str, Any], self.coordination.run_coordination_loop(description, requirements))

    def get_optimal_team(self, task_description: str, requirements: List[str]) -> List[str]:
        """Get the optimal team for a task without executing."""
        task = self.coordination.create_task(task_description, requirements)
        team = self.coordination.match_phase(task.id)

        # Clean up the temporary task
        if task.id in self.coordination.tasks:
            del self.coordination.tasks[task.id]

        return list(team.agents)

    def get_agent_performance(self, clan_member: str) -> Optional[Dict[str, Any]]:
        """Get performance stats for a clan member."""
        return cast(Optional[Dict[str, Any]], self.coordination.get_agent_stats(clan_member))


__all__ = [
    "AgentCoordinationLoop",
    "ClanCoordinationManager",
    "AgentProfile",
    "CoordinationTask",
    "TeamComposition",
    "TaskStatus",
]
