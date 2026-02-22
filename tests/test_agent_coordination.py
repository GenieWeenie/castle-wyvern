"""Tests for eyrie.agent_coordination module."""

import pytest
import time
from eyrie.agent_coordination import (
    AgentProfile,
    CoordinationTask,
    AgentCoordinationLoop,
    ClanCoordinationManager,
    TaskStatus,
)

# --- AgentProfile tests ---


class TestAgentProfile:
    def test_creation_defaults(self):
        agent = AgentProfile(id="a1", name="Alpha", capabilities=["coding"])
        assert agent.id == "a1"
        assert agent.name == "Alpha"
        assert agent.capabilities == ["coding"]
        assert agent.performance_score == 1.0
        assert agent.tasks_completed == 0
        assert agent.tasks_failed == 0
        assert agent.specialization == "general"
        assert agent.reliability == 1.0
        assert agent.speed == 1.0
        assert agent.collaboration_score == 1.0

    def test_creation_custom_values(self):
        agent = AgentProfile(
            id="a2",
            name="Beta",
            capabilities=["testing", "debugging"],
            performance_score=0.8,
            specialization="tester",
            reliability=0.9,
        )
        assert agent.specialization == "tester"
        assert agent.performance_score == 0.8
        assert agent.reliability == 0.9

    def test_fitness_full_match(self):
        agent = AgentProfile(
            id="a1",
            name="Alpha",
            capabilities=["coding", "testing"],
            performance_score=1.0,
            reliability=1.0,
            collaboration_score=1.0,
        )
        fitness = agent.calculate_fitness(["coding", "testing"])
        # match_ratio=1.0*0.4 + perf=1.0*0.2 + rel=1.0*0.2 + collab=1.0*0.2 = 1.0
        assert fitness == pytest.approx(1.0)

    def test_fitness_partial_match(self):
        agent = AgentProfile(
            id="a1",
            name="Alpha",
            capabilities=["coding"],
            performance_score=1.0,
            reliability=1.0,
            collaboration_score=1.0,
        )
        fitness = agent.calculate_fitness(["coding", "testing"])
        # match_ratio=0.5*0.4 + 1.0*0.2 + 1.0*0.2 + 1.0*0.2 = 0.2+0.6 = 0.8
        assert fitness == pytest.approx(0.8)

    def test_fitness_no_match(self):
        agent = AgentProfile(
            id="a1",
            name="Alpha",
            capabilities=["writing"],
            performance_score=1.0,
            reliability=1.0,
            collaboration_score=1.0,
        )
        fitness = agent.calculate_fitness(["coding", "testing"])
        # match_ratio=0*0.4 + 1.0*0.2 + 1.0*0.2 + 1.0*0.2 = 0.6
        assert fitness == pytest.approx(0.6)

    def test_fitness_empty_requirements(self):
        agent = AgentProfile(id="a1", name="Alpha", capabilities=["coding"])
        fitness = agent.calculate_fitness([])
        assert isinstance(fitness, float)


# --- CoordinationTask tests ---


class TestCoordinationTask:
    def test_creation_defaults(self):
        task = CoordinationTask(
            id="t1",
            description="Build feature",
            requirements=["coding", "testing"],
        )
        assert task.id == "t1"
        assert task.description == "Build feature"
        assert task.requirements == ["coding", "testing"]
        assert task.status == TaskStatus.PENDING
        assert task.assigned_agents == []
        assert task.team_score == 0.0
        assert task.result is None

    def test_agent_assignment(self):
        task = CoordinationTask(
            id="t1",
            description="Test task",
            requirements=["coding"],
        )
        task.assigned_agents.append("a1")
        assert "a1" in task.assigned_agents


# --- AgentCoordinationLoop tests ---


class TestCoordinationLoop:
    @pytest.fixture(autouse=True)
    def setup_loop(self, tmp_path):
        """Use a temp dir for storage so tests pass on Windows (no /tmp)."""
        self.loop = AgentCoordinationLoop(storage_dir=str(tmp_path / "coordination"))
        yield

    def test_register_agent(self):
        agent = self.loop.register_agent(
            agent_id="a1",
            name="Alpha",
            capabilities=["coding", "testing"],
            specialization="developer",
        )
        assert isinstance(agent, AgentProfile)
        assert agent.id == "a1"
        assert agent.name == "Alpha"
        assert agent.capabilities == ["coding", "testing"]
        assert agent.specialization == "developer"
        assert "a1" in self.loop.agents

    def test_register_multiple_agents(self):
        # Register two agents
        self.loop.register_agent("a1", "Alpha", ["coding"])
        self.loop.register_agent("a2", "Beta", ["testing"])
        # Verify both are registered (may be more from persistence)
        assert "a1" in self.loop.agents
        assert "a2" in self.loop.agents
        assert self.loop.agents["a1"].name == "Alpha"
        assert self.loop.agents["a2"].name == "Beta"

    def test_create_task(self):
        task = self.loop.create_task(
            description="Implement feature X",
            requirements=["coding", "testing"],
        )
        assert isinstance(task, CoordinationTask)
        assert task.description == "Implement feature X"
        assert task.requirements == ["coding", "testing"]
        assert task.status == TaskStatus.PENDING
        assert task.id in self.loop.tasks

    def test_find_best_team(self):
        self.loop.register_agent("a1", "Coder", ["coding", "debugging"])
        self.loop.register_agent("a2", "Tester", ["testing", "debugging"])
        self.loop.register_agent("a3", "Writer", ["writing", "documentation"])
        self.loop.register_agent("a4", "Reviewer", ["testing", "review", "coding"])

        task = self.loop.create_task(
            description="Build and test module",
            requirements=["coding", "testing"],
        )

        team = self.loop.match_phase(task.id)
        assert len(team.agents) >= self.loop.team_size_min
        assert len(team.agents) <= self.loop.team_size_max
        # Agents with coding/testing capabilities should be preferred
        assert any(a in team.agents for a in ["a1", "a2", "a4"])

    def test_find_best_team_scores(self):
        self.loop.register_agent("a1", "Coder", ["coding", "testing"])
        self.loop.register_agent("a2", "Writer", ["writing"])
        self.loop.register_agent("a3", "Analyst", ["coding", "analysis"])

        task = self.loop.create_task(
            description="Code task",
            requirements=["coding"],
        )

        team = self.loop.match_phase(task.id)
        assert team.formation_score > 0


# --- ClanCoordinationManager tests ---


class TestClanCoordinationManager:
    def test_initialization(self):
        manager = ClanCoordinationManager()
        assert isinstance(manager.coordination, AgentCoordinationLoop)

    def test_clan_members_registered(self):
        manager = ClanCoordinationManager()
        expected_members = [
            "goliath",
            "lexington",
            "brooklyn",
            "broadway",
            "hudson",
            "xanatos",
            "demona",
            "elisa",
            "jade",
        ]
        for member_id in expected_members:
            assert member_id in manager.coordination.agents

    def test_clan_member_count(self):
        manager = ClanCoordinationManager()
        assert len(manager.coordination.agents) == 9

    def test_clan_member_specializations(self):
        manager = ClanCoordinationManager()
        agents = manager.coordination.agents
        assert agents["goliath"].specialization == "leader"
        assert agents["lexington"].specialization == "technician"
        assert agents["brooklyn"].specialization == "strategist"
        assert agents["hudson"].specialization == "archivist"
        assert agents["xanatos"].specialization == "red_team"

    def test_clan_member_capabilities(self):
        manager = ClanCoordinationManager()
        lex = manager.coordination.agents["lexington"]
        assert "coding" in lex.capabilities
        assert "technical" in lex.capabilities
