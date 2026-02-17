"""Tests for the KnowledgeGraph class."""

import os
import pytest
from pathlib import Path

from eyrie.knowledge_graph import KnowledgeGraph, Entity, Relationship


@pytest.fixture
def kg(tmp_path):
    """Create a KnowledgeGraph with a temporary storage directory."""
    return KnowledgeGraph(storage_dir=str(tmp_path / "kg"))


@pytest.fixture
def populated_kg(kg):
    """KnowledgeGraph pre-populated with a few entities and relationships."""
    kg.add_entity("Lexington", "ClanMember", {"role": "tech expert"})
    kg.add_entity("Brooklyn", "ClanMember", {"role": "second-in-command"})
    kg.add_entity("React", "Technology", {"category": "frontend"})
    kg.add_entity("Castle Upgrade", "Project", {"status": "active", "owner": "Lexington"})
    kg.add_relationship("Lexington", "suggested", "React")
    kg.add_relationship("Brooklyn", "leads", "Castle Upgrade")
    return kg


# --- add_entity ---


class TestAddEntity:
    def test_returns_entity(self, kg):
        entity = kg.add_entity("Goliath", "ClanMember", {"role": "leader"})
        assert isinstance(entity, Entity)
        assert entity.name == "Goliath"
        assert entity.type == "ClanMember"
        assert entity.properties == {"role": "leader"}

    def test_entity_stored_in_graph(self, kg):
        entity = kg.add_entity("Goliath", "ClanMember")
        assert entity.id in kg.entities
        assert kg.entities[entity.id] is entity

    def test_entity_id_is_deterministic(self, kg):
        e1 = kg.add_entity("Goliath", "ClanMember")
        assert e1.id.startswith("ClanMember_")

    def test_all_valid_entity_types(self, kg):
        valid_types = [
            ("Lexington", "ClanMember"),
            ("Python", "Technology"),
            ("Rebuild", "Project"),
            ("Use JWT", "Decision"),
            ("XSS Bug", "SecurityIssue"),
            ("Fix login", "Task"),
        ]
        for name, etype in valid_types:
            entity = kg.add_entity(name, etype)
            assert entity.type == etype

    def test_invalid_entity_type_raises(self, kg):
        with pytest.raises(ValueError, match="Unknown entity type"):
            kg.add_entity("Foo", "InvalidType")

    def test_default_properties_empty(self, kg):
        entity = kg.add_entity("Hudson", "ClanMember")
        assert entity.properties == {}

    def test_source_stored(self, kg):
        entity = kg.add_entity("Hudson", "ClanMember", source="chat_log")
        assert entity.source == "chat_log"

    def test_indexes_updated(self, kg):
        entity = kg.add_entity("Broadway", "ClanMember")
        assert entity.id in kg.entity_by_type["ClanMember"]
        assert entity.id in kg.entity_by_name["broadway"]


# --- add_relationship ---


class TestAddRelationship:
    def test_returns_relationship(self, populated_kg):
        rel = populated_kg.add_relationship("Lexington", "implemented", "React")
        assert isinstance(rel, Relationship)
        assert rel.relation == "implemented"

    def test_relationship_stored(self, populated_kg):
        rel = populated_kg.add_relationship("Lexington", "implemented", "React")
        assert rel.id in populated_kg.relationships

    def test_source_entity_not_found(self, populated_kg):
        with pytest.raises(ValueError, match="Source entity not found"):
            populated_kg.add_relationship("Nonexistent", "suggested", "React")

    def test_target_entity_not_found(self, populated_kg):
        with pytest.raises(ValueError, match="Target entity not found"):
            populated_kg.add_relationship("Lexington", "suggested", "Nonexistent")

    def test_invalid_relation_type(self, populated_kg):
        with pytest.raises(ValueError, match="Unknown relation type"):
            populated_kg.add_relationship("Lexington", "destroyed", "React")

    def test_invalid_source_type_for_relation(self, kg):
        kg.add_entity("React", "Technology")
        kg.add_entity("Castle Upgrade", "Project")
        with pytest.raises(ValueError, match="Invalid source type"):
            # "leads" requires source type ClanMember, not Technology
            kg.add_relationship("React", "leads", "Castle Upgrade")

    def test_invalid_target_type_for_relation(self, kg):
        kg.add_entity("Lexington", "ClanMember")
        kg.add_entity("Brooklyn", "ClanMember")
        with pytest.raises(ValueError, match="Invalid target type"):
            # "leads" requires target type Project, not ClanMember
            kg.add_relationship("Lexington", "leads", "Brooklyn")

    def test_indexes_updated(self, populated_kg):
        rel = populated_kg.add_relationship("Lexington", "implemented", "React")
        assert rel.id in populated_kg.rel_by_source[rel.source]
        assert rel.id in populated_kg.rel_by_target[rel.target]
        assert rel.id in populated_kg.rel_by_type["implemented"]

    def test_all_valid_relation_types(self, kg):
        kg.add_entity("Lex", "ClanMember")
        kg.add_entity("React", "Technology")
        kg.add_entity("Upgrade", "Project")
        kg.add_entity("Use JWT", "Decision")
        kg.add_entity("XSS Bug", "SecurityIssue")
        kg.add_entity("Fix login", "Task")

        cases = [
            ("Lex", "suggested", "React"),
            ("Lex", "reviewed", "Upgrade"),
            ("Lex", "implemented", "React"),
            ("Upgrade", "involves", "React"),
            ("Fix login", "depends_on", "Upgrade"),
            ("Lex", "discovered", "XSS Bug"),
            ("Lex", "leads", "Upgrade"),
        ]
        for src, rel, tgt in cases:
            r = kg.add_relationship(src, rel, tgt)
            assert r.relation == rel


# --- get_stats ---


class TestGetStats:
    def test_empty_graph(self, kg):
        stats = kg.get_stats()
        assert stats["total_entities"] == 0
        assert stats["total_relationships"] == 0

    def test_counts_match(self, populated_kg):
        stats = populated_kg.get_stats()
        assert stats["total_entities"] == 4
        assert stats["total_relationships"] == 2

    def test_entity_type_breakdown(self, populated_kg):
        stats = populated_kg.get_stats()
        assert stats["entity_types"]["ClanMember"] == 2
        assert stats["entity_types"]["Technology"] == 1
        assert stats["entity_types"]["Project"] == 1

    def test_relation_type_breakdown(self, populated_kg):
        stats = populated_kg.get_stats()
        assert stats["relation_types"]["suggested"] == 1
        assert stats["relation_types"]["leads"] == 1

    def test_schema_types_listed(self, kg):
        stats = kg.get_stats()
        assert "ClanMember" in stats["schema_entity_types"]
        assert "suggested" in stats["schema_relation_types"]


# --- get_entities_by_type ---


class TestGetEntitiesByType:
    def test_returns_matching_entities(self, populated_kg):
        members = populated_kg.get_entities_by_type("ClanMember")
        names = {e.name for e in members}
        assert names == {"Lexington", "Brooklyn"}

    def test_returns_empty_set_for_no_matches(self, populated_kg):
        tasks = populated_kg.get_entities_by_type("Task")
        assert tasks == set()

    def test_single_match(self, populated_kg):
        techs = populated_kg.get_entities_by_type("Technology")
        assert len(techs) == 1
        assert list(techs)[0].name == "React"

    def test_returns_entity_objects(self, populated_kg):
        members = populated_kg.get_entities_by_type("ClanMember")
        for entity in members:
            assert isinstance(entity, Entity)
            assert entity.type == "ClanMember"


# --- save_graph ---


class TestSaveGraph:
    def test_creates_files(self, populated_kg, tmp_path):
        populated_kg.save_graph()
        storage = populated_kg.storage_dir
        assert (storage / "entities.pkl").exists()
        assert (storage / "relationships.pkl").exists()
        assert (storage / "schema.json").exists()

    def test_roundtrip_preserves_entities(self, populated_kg):
        populated_kg.save_graph()
        reloaded = KnowledgeGraph(storage_dir=str(populated_kg.storage_dir))
        assert len(reloaded.entities) == len(populated_kg.entities)
        for eid, entity in populated_kg.entities.items():
            assert eid in reloaded.entities
            assert reloaded.entities[eid].name == entity.name
            assert reloaded.entities[eid].type == entity.type

    def test_roundtrip_preserves_relationships(self, populated_kg):
        populated_kg.save_graph()
        reloaded = KnowledgeGraph(storage_dir=str(populated_kg.storage_dir))
        assert len(reloaded.relationships) == len(populated_kg.relationships)
        for rid, rel in populated_kg.relationships.items():
            assert rid in reloaded.relationships
            assert reloaded.relationships[rid].relation == rel.relation

    def test_roundtrip_rebuilds_indexes(self, populated_kg):
        populated_kg.save_graph()
        reloaded = KnowledgeGraph(storage_dir=str(populated_kg.storage_dir))
        members = reloaded.get_entities_by_type("ClanMember")
        assert len(members) == 2
