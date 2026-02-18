"""
Enhanced Agent Coordination
Polish features for production use
"""

import json
import time
from typing import Dict, List, Optional, Tuple, cast
from dataclasses import dataclass, field
from pathlib import Path
from collections import defaultdict


@dataclass
class CoordinationMetrics:
    """Metrics for coordination system analysis."""

    total_tasks: int = 0
    successful_tasks: int = 0
    failed_tasks: int = 0
    avg_team_size: float = 0.0
    avg_execution_time: float = 0.0
    best_performing_agents: List[Tuple[str, float]] = field(default_factory=list)
    most_collaborative_pairs: List[Tuple[Tuple[str, str], float]] = field(default_factory=list)
    task_type_performance: Dict[str, Dict] = field(default_factory=dict)


class CoordinationAnalytics:
    """Analytics and insights for coordination system."""

    def __init__(self, coordination_system):
        self.coordination = coordination_system

    def calculate_metrics(self) -> CoordinationMetrics:
        """Calculate comprehensive metrics."""
        metrics = CoordinationMetrics()

        # Basic counts
        all_tasks = self.coordination.completed_tasks
        metrics.total_tasks = len(all_tasks)
        metrics.successful_tasks = len([t for t in all_tasks if t.status.value == "completed"])
        metrics.failed_tasks = len([t for t in all_tasks if t.status.value == "failed"])

        if all_tasks:
            metrics.avg_team_size = sum(len(t.assigned_agents) for t in all_tasks) / len(all_tasks)
            metrics.avg_execution_time = sum(t.execution_time for t in all_tasks) / len(all_tasks)

        # Best performing agents
        agent_scores = []
        for agent_id, agent in self.coordination.agents.items():
            score = agent.performance_score * agent.reliability
            agent_scores.append((agent.name, score))

        metrics.best_performing_agents = sorted(agent_scores, key=lambda x: x[1], reverse=True)[:5]

        # Most collaborative pairs
        pair_collaboration: Dict[Tuple[str, str], float] = defaultdict(float)
        for task in all_tasks:
            agents = task.assigned_agents
            for i, a1 in enumerate(agents):
                for a2 in agents[i + 1 :]:
                    pair = tuple(sorted([a1, a2]))
                    pair_collaboration[pair] += task.team_score

        metrics.most_collaborative_pairs = sorted(
            pair_collaboration.items(), key=lambda x: x[1], reverse=True
        )[:5]

        # Task type performance
        for task in all_tasks:
            req_key = ",".join(sorted(task.requirements))
            if req_key not in metrics.task_type_performance:
                metrics.task_type_performance[req_key] = {
                    "count": 0,
                    "success_count": 0,
                    "avg_score": 0.0,
                }

            perf = metrics.task_type_performance[req_key]
            perf["count"] += 1
            if task.status.value == "completed":
                perf["success_count"] += 1
            perf["avg_score"] = (perf["avg_score"] * (perf["count"] - 1) + task.team_score) / perf[
                "count"
            ]

        return metrics

    def get_agent_recommendations(self, task_requirements: List[str]) -> List[Dict]:
        """
        Get agent recommendations for a task based on historical performance.

        Returns:
            List of recommended agents with confidence scores
        """
        recommendations = []

        for agent_id, agent in self.coordination.agents.items():
            # Calculate match score
            matches = sum(1 for req in task_requirements if req in agent.capabilities)
            capability_match = matches / len(task_requirements) if task_requirements else 0.5

            # Calculate historical performance on similar tasks
            similar_tasks = [
                t
                for t in self.coordination.completed_tasks
                if agent_id in t.assigned_agents and t.status.value == "completed"
            ]

            if similar_tasks:
                avg_performance = sum(t.team_score for t in similar_tasks) / len(similar_tasks)
            else:
                avg_performance = agent.performance_score

            # Combined score
            confidence = capability_match * 0.5 + avg_performance * 0.3 + agent.reliability * 0.2

            recommendations.append(
                {
                    "agent_id": agent_id,
                    "name": agent.name,
                    "specialization": agent.specialization,
                    "confidence": confidence,
                    "reason": f"{matches}/{len(task_requirements)} capabilities match, performance: {avg_performance:.2f}",
                }
            )

        # Sort by confidence
        recommendations.sort(key=lambda x: x["confidence"], reverse=True)
        return recommendations

    def predict_success_rate(self, task_requirements: List[str], team: List[str]) -> float:
        """Predict success rate for a given team on a task."""
        # Get historical data for this team composition
        similar_tasks = [
            t
            for t in self.coordination.completed_tasks
            if set(t.assigned_agents) == set(team) and t.status.value == "completed"
        ]

        if similar_tasks:
            historical_success = len(similar_tasks) / len(
                [
                    t
                    for t in self.coordination.completed_tasks
                    if set(t.assigned_agents) == set(team)
                ]
            )
            return historical_success

        # Otherwise use agent performance scores
        team_scores = [
            self.coordination.agents[aid].performance_score
            for aid in team
            if aid in self.coordination.agents
        ]
        if team_scores:
            return cast(float, sum(team_scores) / len(team_scores))

        return 0.5  # Default prediction


class TeamOptimizer:
    """Optimize team composition for tasks."""

    def __init__(self, coordination_system):
        self.coordination = coordination_system

    def optimize_team(self, task_requirements: List[str], constraints: Dict = None) -> List[str]:
        """
        Find optimal team using optimization algorithm.

        Args:
            task_requirements: Required capabilities
            constraints: Optional constraints like:
                - max_team_size: int
                - min_reliability: float
                - exclude_agents: List[str]
                - require_agents: List[str]

        Returns:
            Optimal team composition
        """
        constraints = constraints or {}
        max_size = constraints.get("max_team_size", 4)
        min_reliability = constraints.get("min_reliability", 0.5)
        exclude = set(constraints.get("exclude_agents", []))
        require = set(constraints.get("require_agents", []))

        # Filter eligible agents
        eligible = [
            aid
            for aid, agent in self.coordination.agents.items()
            if aid not in exclude and agent.reliability >= min_reliability
        ]

        # Must include required agents
        team = list(require)

        # Add remaining agents based on fitness
        remaining_slots = max_size - len(team)

        if remaining_slots > 0:
            # Score each eligible agent
            agent_scores = []
            for aid in eligible:
                if aid in team:
                    continue

                agent = self.coordination.agents[aid]
                fitness = agent.calculate_fitness(task_requirements)
                agent_scores.append((aid, fitness))

            # Sort by fitness and take top N
            agent_scores.sort(key=lambda x: x[1], reverse=True)
            team.extend([aid for aid, _ in agent_scores[:remaining_slots]])

        return team

    def compare_teams(
        self, team1: List[str], team2: List[str], task_requirements: List[str]
    ) -> Dict:
        """Compare two potential teams for a task."""

        def score_team(team):
            scores = []
            for aid in team:
                if aid in self.coordination.agents:
                    agent = self.coordination.agents[aid]
                    scores.append(agent.calculate_fitness(task_requirements))
            return sum(scores) / len(scores) if scores else 0

        score1 = score_team(team1)
        score2 = score_team(team2)

        return {
            "team1": {
                "agents": [
                    self.coordination.agents[aid].name
                    for aid in team1
                    if aid in self.coordination.agents
                ],
                "score": score1,
            },
            "team2": {
                "agents": [
                    self.coordination.agents[aid].name
                    for aid in team2
                    if aid in self.coordination.agents
                ],
                "score": score2,
            },
            "winner": "team1" if score1 > score2 else "team2" if score2 > score1 else "tie",
            "difference": abs(score1 - score2),
        }


class CoordinationReport:
    """Generate detailed coordination reports."""

    def __init__(self, coordination_system):
        self.coordination = coordination_system
        self.analytics = CoordinationAnalytics(coordination_system)

    def generate_report(self) -> str:
        """Generate comprehensive markdown report."""
        metrics = self.analytics.calculate_metrics()

        success_rate = (
            metrics.successful_tasks / metrics.total_tasks * 100 if metrics.total_tasks > 0 else 0
        )
        report = f"""# Agent Coordination Report
Generated: {time.strftime('%Y-%m-%d %H:%M')}

## Overview

- **Total Tasks**: {metrics.total_tasks}
- **Success Rate**: {success_rate:.1f}%
- **Average Team Size**: {metrics.avg_team_size:.2f}
- **Average Execution Time**: {metrics.avg_execution_time:.2f}s

## Top Performing Agents

"""

        for i, (name, score) in enumerate(metrics.best_performing_agents, 1):
            report += f"{i}. **{name}** - Score: {score:.2f}\n"

        report += "\n## Most Collaborative Pairs\n\n"

        for (a1, a2), score in metrics.most_collaborative_pairs:
            name1 = self.coordination.agents[a1].name if a1 in self.coordination.agents else a1
            name2 = self.coordination.agents[a2].name if a2 in self.coordination.agents else a2
            report += f"- **{name1} + {name2}** - Collaboration Score: {score:.2f}\n"

        report += "\n## Performance by Task Type\n\n"

        for req_type, perf in metrics.task_type_performance.items():
            success_rate = perf["success_count"] / perf["count"] * 100 if perf["count"] > 0 else 0
            report += f"- **{req_type}**: {perf['count']} tasks, {success_rate:.1f}% success, avg score: {perf['avg_score']:.2f}\n"

        report += "\n## Agent Details\n\n"

        for agent_id, agent in self.coordination.agents.items():
            report += f"""### {agent.name}
- **Specialization**: {agent.specialization}
- **Capabilities**: {', '.join(agent.capabilities)}
- **Performance Score**: {agent.performance_score:.2f}
- **Reliability**: {agent.reliability:.2f}
- **Tasks Completed**: {agent.tasks_completed}
- **Collaboration Score**: {agent.collaboration_score:.2f}

"""

        return report

    def export_to_json(self, output_path: str):
        """Export coordination data to JSON."""
        metrics = self.analytics.calculate_metrics()

        data = {
            "generated_at": time.time(),
            "metrics": {
                "total_tasks": metrics.total_tasks,
                "successful_tasks": metrics.successful_tasks,
                "failed_tasks": metrics.failed_tasks,
                "avg_team_size": metrics.avg_team_size,
                "avg_execution_time": metrics.avg_execution_time,
            },
            "agents": [
                {
                    "id": aid,
                    "name": agent.name,
                    "specialization": agent.specialization,
                    "capabilities": agent.capabilities,
                    "performance_score": agent.performance_score,
                    "reliability": agent.reliability,
                    "tasks_completed": agent.tasks_completed,
                }
                for aid, agent in self.coordination.agents.items()
            ],
            "recent_tasks": [
                {
                    "id": task.id,
                    "description": task.description,
                    "requirements": task.requirements,
                    "assigned_agents": task.assigned_agents,
                    "status": task.status.value,
                    "team_score": task.team_score,
                }
                for task in self.coordination.completed_tasks[-10:]  # Last 10
            ],
        }

        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)

        return output_path


__all__ = ["CoordinationMetrics", "CoordinationAnalytics", "TeamOptimizer", "CoordinationReport"]
