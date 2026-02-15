"""
Unit tests for Knowledge Graph functionality.
"""

import pytest
from eyrie.knowledge_graph import KnowledgeGraph, Entity, Relationship, KnowledgeSchema


class TestKnowledgeGraph:
    """Test suite for Knowledge Graph."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.kg = KnowledgeGraph()
    
    def test_entity_creation(self):
        """Test creating an entity."""
        entity = self.kg.add_entity(
            name="Test Entity",
            type="Technology",
            properties={"category": "test"}
        )
        
        assert entity.name == "Test Entity"
        assert entity.type == "Technology"
        assert entity.properties["category"] == "test"
        assert entity.id in self.kg.entities
    
    def test_relationship_creation(self):
        """Test creating a relationship between entities."""
        # Create two entities
        entity1 = self.kg.add_entity("Python", "Technology")
        entity2 = self.kg.add_entity("Django", "Technology")
        
        # Create relationship by name (API uses names, not IDs)
        rel = self.kg.add_relationship(
            source_name="Python",
            relation="depends_on",
            target_name="Django"
        )
        
        assert rel.source == entity1.id
        assert rel.target == entity2.id
        assert rel.relation == "depends_on"
        assert rel.id in self.kg.relationships
    
    def test_get_stats(self):
        """Test getting knowledge graph statistics."""
        # Empty graph
        stats = self.kg.get_stats()
        assert stats["total_entities"] == 0
        assert stats["total_relationships"] == 0
        
        # Add entities and relationships
        e1 = self.kg.add_entity("Python", "Technology")
        e2 = self.kg.add_entity("React", "Technology")
        self.kg.add_relationship("Python", "depends_on", "React")
        
        stats = self.kg.get_stats()
        assert stats["total_entities"] == 2
        assert stats["total_relationships"] == 1
    
    def test_get_entities_by_type(self):
        """Test filtering entities by type."""
        self.kg.add_entity("Python", "Technology")
        self.kg.add_entity("JavaScript", "Technology")
        self.kg.add_entity("Goliath", "ClanMember")
        
        tech_entities = list(self.kg.get_entities_by_type("Technology"))
        assert len(tech_entities) == 2
        
        clan_entities = list(self.kg.get_entities_by_type("ClanMember"))
        assert len(clan_entities) == 1
    
    def test_get_entities_by_name(self):
        """Test finding entities by name."""
        self.kg.add_entity("Lexington", "ClanMember")
        
        entities = list(self.kg.get_entities_by_name("Lexington"))
        assert len(entities) == 1
        assert entities[0].type == "ClanMember"
    
    def test_save_graph(self):
        """Test saving knowledge graph to disk."""
        import tempfile
        from pathlib import Path
        
        # Create KG with temp storage
        temp_dir = Path(tempfile.mkdtemp())
        kg = KnowledgeGraph()
        kg.storage_dir = temp_dir
        
        # Add data
        e1 = kg.add_entity("Python", "Technology")
        e2 = kg.add_entity("Django", "Technology")
        kg.add_relationship("Python", "depends_on", "Django")
        
        # Save (should not raise)
        kg.save_graph()
        
        # Check files were created
        assert (temp_dir / "entities.pkl").exists()
        assert (temp_dir / "relationships.pkl").exists()


class TestKnowledgeGraphVisualization:
    """Test visualization utilities."""
    
    def setup_method(self):
        """Set up test fixtures."""
        from eyrie.knowledge_graph_utils import KnowledgeGraphVisualizer
        self.kg = KnowledgeGraph()
        self.visualizer = KnowledgeGraphVisualizer(self.kg)
    
    def test_to_dot(self):
        """Test DOT format export."""
        e1 = self.kg.add_entity("Python", "Technology")
        e2 = self.kg.add_entity("Django", "Technology")
        self.kg.add_relationship("Python", "depends_on", "Django")
        
        dot = self.visualizer.to_dot()
        assert "digraph KnowledgeGraph" in dot
        assert "Python" in dot
        assert "Django" in dot
        assert "depends_on" in dot
    
    def test_to_mermaid(self):
        """Test Mermaid format export."""
        e1 = self.kg.add_entity("Python", "Technology")
        e2 = self.kg.add_entity("Django", "Technology")
        self.kg.add_relationship("Python", "depends_on", "Django")
        
        mermaid = self.visualizer.to_mermaid()
        assert "graph LR" in mermaid
        assert "Python" in mermaid
        assert "Django" in mermaid


class TestEntityExtraction:
    """Test entity extraction."""
    
    def setup_method(self):
        """Set up test fixtures."""
        from eyrie.knowledge_graph_utils import SmartEntityExtractor
        self.kg = KnowledgeGraph()
        self.extractor = SmartEntityExtractor(self.kg)
    
    def test_extraction_runs(self):
        """Test that extraction runs without error."""
        text = "Python and React are technologies"
        result = self.extractor.extract_rule_based(text)
        
        # Basic smoke test
        assert isinstance(result, dict)
        assert "entities" in result
        assert "relationships" in result
    
    def test_extract_technologies(self):
        """Test extracting technology names."""
        text = "We should use Python and React for this"
        result = self.extractor.extract_rule_based(text)
        
        entity_names = [e["name"] for e in result["entities"]]
        assert "Python" in entity_names
        assert "React" in entity_names


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
