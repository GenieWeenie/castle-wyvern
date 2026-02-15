"""
Unit tests for Agent Coordination functionality.
"""

import pytest
from unittest.mock import Mock
from eyrie.agent_coordination import (
    ClanCoordinationManager, Agent, Task, CoordinationLoop,
    AgentStatus, TaskStatus
)


class TestAgent:
    """Test suite for Agent class."""
    
    def test_agent_creation(self):
        """Test creating an agent."""
        agent = Agent(
            id="test_agent",
            name="Test Agent",
            specialization="coding",
            capabilities=["python", "javascript"]
        )
        
        assert agent.id == "test_agent"
        assert agent.name == "Test Agent"
        assert agent.specialization == "coding"
        assert "python" in agent.capabilities
        assert agent.status == AgentStatus.AVAILABLE
    
    def test_agent_fitness_calculation(self):
        """Test agent fitness for task requirements."""
        agent = Agent(
            id="test",
            name="Test",
            capabilities=["python", "testing", "debugging"]
        )
        
        # Perfect match
        fitness = agent.calculate_fitness(["python", "testing"])
        assert fitness > 0.8
        
        # Partial match
        fitness = agent.calculate_fitness(["python", "rust"])
        assert 0.4 < fitness < 0.8
        
        # No match
        fitness = agent.calculate_fitness(["java", "kotlin"])
        assert fitness < 0.4


class TestTask:
    """Test suite for Task class."""
    
    def test_task_creation(self):
        """Test creating a task."""
        task = Task(
            id="task_1",
            description="Implement feature",
            requirements=["python", "api"]
        )
        
        assert task.id == "task_1"
        assert task.description == "Implement feature"
        assert task.requirements == ["python", "api"]
        assert task.status == TaskStatus.PENDING
        assert len(task.assigned_agents) == 0
    
    def test_task_assign_agent(self):
        """Test assigning agent to task."""
        task = Task(id="task_1", description="Test", requirements=[])
        
        task.assign_agent("agent_1")
        
        assert "agent_1" in task.assigned_agents
    
    def test_task_execution_time(self):
        """Test tracking task execution time."""
        import time
        task = Task(id="task_1", description="Test", requirements=[])
        
        task.start_execution()
        time.sleep(0.1)  # Small delay
        task.complete_execution()
        
        assert task.execution_time >= 0.1


class TestCoordinationLoop:
    """Test suite for CoordinationLoop."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.loop = CoordinationLoop()
    
    def test_register_agent(self):
        """Test registering an agent."""
        agent = Agent(id="test", name="Test", capabilities=[])
        
        self.loop.register_agent(agent)
        
        assert "test" in self.loop.agents
    
    def test_create_task(self):
        """Test creating a task."""
        task = self.loop.create_task("Test task", ["python"])
        
        assert task.id in self.loop.tasks
        assert task.description == "Test task"
    
    def test_find_best_team(self):
        """Test finding optimal team for task."""
        # Register agents
        agent1 = Agent(id="a1", name="Python Dev", capabilities=["python"])
        agent2 = Agent(id="a2", name="JS Dev", capabilities=["javascript"])
        self.loop.register_agent(agent1)
        self.loop.register_agent(agent2)
        
        # Find team for python task
        team = self.loop.find_best_team(["python"])
        
        assert "a1" in team  # Python dev should be selected


class TestClanCoordinationManager:
    """Test suite for ClanCoordinationManager."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.manager = ClanCoordinationManager()
    
    def test_initialization(self):
        """Test manager initializes with clan members."""
        stats = self.manager.coordination.get_coordination_stats()
        
        assert stats["registered_agents"] == 10  # 10 clan members
    
    def test_get_agent_performance(self):
        """Test getting agent performance stats."""
        stats = self.manager.get_agent_performance("lexington")
        
        assert stats is not None
        assert stats["name"] == "Lexington"
        assert "performance_score" in stats


class TestCoordinationAnalytics:
    """Test analytics functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        from eyrie.agent_coordination_utils import CoordinationAnalytics
        from eyrie.agent_coordination import ClanCoordinationManager
        
        self.manager = ClanCoordinationManager()
        self.analytics = CoordinationAnalytics(self.manager.coordination)
    
    def test_calculate_metrics(self):
        """Test calculating coordination metrics."""
        metrics = self.analytics.calculate_metrics()
        
        assert hasattr(metrics, 'total_tasks')
        assert hasattr(metrics, 'best_performing_agents')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
