"""
Clan Knowledge Graph (KAG Integration)
Knowledge Augmented Generation for Castle Wyvern

Features:
- Entity extraction from text
- Relationship mapping
- Logical reasoning over knowledge graph
- Multi-hop queries
- Schema-constrained knowledge construction
"""

import os
import json
import re
import hashlib
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from collections import defaultdict
import pickle


@dataclass
class Entity:
    """A node in the knowledge graph."""

    id: str
    name: str
    type: str  # e.g., "ClanMember", "Technology", "Project", "Decision"
    properties: Dict[str, Any] = field(default_factory=dict)
    source: str = ""  # Where this entity was extracted from
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, Entity):
            return self.id == other.id
        return False


@dataclass
class Relationship:
    """An edge in the knowledge graph."""

    id: str
    source: str  # Source entity ID
    target: str  # Target entity ID
    relation: str  # e.g., "suggested", "reviewed", "implemented"
    properties: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())
    confidence: float = 1.0  # Extraction confidence

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, Relationship):
            return self.id == other.id
        return False


@dataclass
class KnowledgeSchema:
    """Schema for knowledge graph constraints."""

    entity_types: Dict[str, Dict] = field(default_factory=dict)
    relation_types: Dict[str, Dict] = field(default_factory=dict)

    def __post_init__(self):
        # Default Castle Wyvern schema
        if not self.entity_types:
            self.entity_types = {
                "ClanMember": {
                    "properties": ["role", "specialty", "personality"],
                    "description": "A member of the Manhattan Clan",
                },
                "Technology": {
                    "properties": ["category", "version", "documentation_url"],
                    "description": "Technology, tool, or framework",
                },
                "Project": {
                    "properties": ["status", "start_date", "owner", "priority"],
                    "description": "A project or initiative",
                },
                "Decision": {
                    "properties": ["decision_date", "rationale", "stakeholders"],
                    "description": "A decision made by the clan",
                },
                "SecurityIssue": {
                    "properties": ["severity", "status", "discovered_by"],
                    "description": "Security vulnerability or concern",
                },
                "Task": {
                    "properties": ["status", "assignee", "due_date", "priority"],
                    "description": "A task or action item",
                },
            }

        if not self.relation_types:
            self.relation_types = {
                "suggested": {
                    "from": ["ClanMember"],
                    "to": ["Technology", "Decision", "Project"],
                    "description": "Suggested or proposed something",
                },
                "reviewed": {
                    "from": ["ClanMember"],
                    "to": ["Project", "Technology", "SecurityIssue"],
                    "description": "Reviewed or audited something",
                },
                "implemented": {
                    "from": ["ClanMember"],
                    "to": ["Technology", "Project", "Decision"],
                    "description": "Implemented or built something",
                },
                "involves": {
                    "from": ["Project", "Decision", "Task"],
                    "to": ["Technology", "ClanMember", "SecurityIssue"],
                    "description": "Involves or includes something",
                },
                "depends_on": {
                    "from": ["Project", "Task", "Technology"],
                    "to": ["Project", "Technology"],
                    "description": "Depends on something",
                },
                "discovered": {
                    "from": ["ClanMember"],
                    "to": ["SecurityIssue"],
                    "description": "Discovered or found something",
                },
                "leads": {
                    "from": ["ClanMember"],
                    "to": ["Project"],
                    "description": "Leads or manages a project",
                },
            }


class KnowledgeGraph:
    """
    Knowledge Graph for Castle Wyvern.

    Implements KAG (Knowledge Augmented Generation) principles:
    - Entities with types and properties
    - Relationships with semantics
    - Schema constraints
    - Multi-hop reasoning
    """

    def __init__(self, storage_dir: str = "~/.castle_wyvern/knowledge_graph"):
        self.storage_dir = Path(storage_dir).expanduser()
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        self.entities: Dict[str, Entity] = {}
        self.relationships: Dict[str, Relationship] = {}
        self.schema = KnowledgeSchema()

        # Indexes for fast lookup
        self.entity_by_type: Dict[str, Set[str]] = defaultdict(set)
        self.entity_by_name: Dict[str, Set[str]] = defaultdict(set)
        self.rel_by_source: Dict[str, Set[str]] = defaultdict(set)
        self.rel_by_target: Dict[str, Set[str]] = defaultdict(set)
        self.rel_by_type: Dict[str, Set[str]] = defaultdict(set)

        self._load_graph()

    def _load_graph(self):
        """Load knowledge graph from disk."""
        entities_file = self.storage_dir / "entities.pkl"
        relations_file = self.storage_dir / "relationships.pkl"
        schema_file = self.storage_dir / "schema.json"

        if entities_file.exists():
            with open(entities_file, "rb") as f:
                self.entities = pickle.load(f)

        if relations_file.exists():
            with open(relations_file, "rb") as f:
                self.relationships = pickle.load(f)

        if schema_file.exists():
            with open(schema_file, "r") as f:
                schema_data = json.load(f)
                self.schema = KnowledgeSchema(
                    entity_types=schema_data.get("entity_types", {}),
                    relation_types=schema_data.get("relation_types", {}),
                )

        # Rebuild indexes
        self._rebuild_indexes()

    def _rebuild_indexes(self):
        """Rebuild lookup indexes."""
        self.entity_by_type = defaultdict(set)
        self.entity_by_name = defaultdict(set)
        self.rel_by_source = defaultdict(set)
        self.rel_by_target = defaultdict(set)
        self.rel_by_type = defaultdict(set)

        for entity_id, entity in self.entities.items():
            self.entity_by_type[entity.type].add(entity_id)
            self.entity_by_name[entity.name.lower()].add(entity_id)

        for rel_id, rel in self.relationships.items():
            self.rel_by_source[rel.source].add(rel_id)
            self.rel_by_target[rel.target].add(rel_id)
            self.rel_by_type[rel.relation].add(rel_id)

    def save_graph(self):
        """Save knowledge graph to disk."""
        entities_file = self.storage_dir / "entities.pkl"
        relations_file = self.storage_dir / "relationships.pkl"
        schema_file = self.storage_dir / "schema.json"

        with open(entities_file, "wb") as f:
            pickle.dump(self.entities, f)

        with open(relations_file, "wb") as f:
            pickle.dump(self.relationships, f)

        with open(schema_file, "w") as f:
            json.dump(
                {
                    "entity_types": self.schema.entity_types,
                    "relation_types": self.schema.relation_types,
                },
                f,
                indent=2,
            )

    def add_entity(self, name: str, type: str, properties: Dict = None, source: str = "") -> Entity:
        """Add an entity to the knowledge graph."""
        # Validate against schema
        if type not in self.schema.entity_types:
            raise ValueError(f"Unknown entity type: {type}")

        # Generate ID
        entity_id = f"{type}_{hashlib.md5(name.encode()).hexdigest()[:12]}"

        entity = Entity(
            id=entity_id, name=name, type=type, properties=properties or {}, source=source
        )

        self.entities[entity_id] = entity
        self.entity_by_type[type].add(entity_id)
        self.entity_by_name[name.lower()].add(entity_id)

        return entity

    def add_relationship(
        self, source_name: str, relation: str, target_name: str, properties: Dict = None
    ) -> Relationship:
        """Add a relationship between entities."""
        # Find entities by name
        source_entities = self.get_entities_by_name(source_name)
        target_entities = self.get_entities_by_name(target_name)

        if not source_entities:
            raise ValueError(f"Source entity not found: {source_name}")
        if not target_entities:
            raise ValueError(f"Target entity not found: {target_name}")

        # Use first match (could be improved with disambiguation)
        source_id = list(source_entities)[0].id
        target_id = list(target_entities)[0].id

        # Validate against schema
        if relation not in self.schema.relation_types:
            raise ValueError(f"Unknown relation type: {relation}")

        rel_schema = self.schema.relation_types[relation]
        source_type = self.entities[source_id].type
        target_type = self.entities[target_id].type

        if source_type not in rel_schema["from"]:
            raise ValueError(f"Invalid source type {source_type} for relation {relation}")
        if target_type not in rel_schema["to"]:
            raise ValueError(f"Invalid target type {target_type} for relation {relation}")

        # Generate ID
        rel_id = (
            f"rel_{hashlib.md5(f'{source_id}_{relation}_{target_id}'.encode()).hexdigest()[:16]}"
        )

        relationship = Relationship(
            id=rel_id,
            source=source_id,
            target=target_id,
            relation=relation,
            properties=properties or {},
        )

        self.relationships[rel_id] = relationship
        self.rel_by_source[source_id].add(rel_id)
        self.rel_by_target[target_id].add(rel_id)
        self.rel_by_type[relation].add(rel_id)

        return relationship

    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """Get entity by ID."""
        return self.entities.get(entity_id)

    def get_entities_by_name(self, name: str) -> Set[Entity]:
        """Get entities by name (case insensitive)."""
        entity_ids = self.entity_by_name.get(name.lower(), set())
        return {self.entities[eid] for eid in entity_ids}

    def get_entities_by_type(self, type: str) -> Set[Entity]:
        """Get entities by type."""
        entity_ids = self.entity_by_type.get(type, set())
        return {self.entities[eid] for eid in entity_ids}

    def get_relationships_from(self, entity_id: str) -> List[Relationship]:
        """Get all relationships starting from an entity."""
        rel_ids = self.rel_by_source.get(entity_id, set())
        return [self.relationships[rid] for rid in rel_ids]

    def get_relationships_to(self, entity_id: str) -> List[Relationship]:
        """Get all relationships ending at an entity."""
        rel_ids = self.rel_by_target.get(entity_id, set())
        return [self.relationships[rid] for rid in rel_ids]

    def get_related_entities(
        self, entity_id: str, relation: str = None
    ) -> List[Tuple[Entity, str, Entity]]:
        """
        Get entities related to the given entity.

        Returns list of (source, relation, target) tuples.
        """
        results = []

        # Outgoing relationships
        for rel in self.get_relationships_from(entity_id):
            if relation is None or rel.relation == relation:
                target = self.entities.get(rel.target)
                if target:
                    results.append((self.entities[entity_id], rel.relation, target))

        # Incoming relationships
        for rel in self.get_relationships_to(entity_id):
            if relation is None or rel.relation == relation:
                source = self.entities.get(rel.source)
                if source:
                    results.append((source, rel.relation, self.entities[entity_id]))

        return results

    def multi_hop_query(self, start_entity: str, path: List[str]) -> List[Dict]:
        """
        Execute a multi-hop query along a relationship path.

        Args:
            start_entity: Starting entity name
            path: List of relationship types to traverse

        Returns:
            List of paths found
        """
        start_entities = self.get_entities_by_name(start_entity)
        if not start_entities:
            return []

        start_id = list(start_entities)[0].id
        results = []

        def traverse(current_id: str, path_idx: int, current_path: List):
            if path_idx >= len(path):
                results.append(current_path.copy())
                return

            rel_type = path[path_idx]
            for rel in self.get_relationships_from(current_id):
                if rel.relation == rel_type:
                    target = self.entities.get(rel.target)
                    if target:
                        current_path.append((rel, target))
                        traverse(rel.target, path_idx + 1, current_path)
                        current_path.pop()

        traverse(start_id, 0, [(None, self.entities[start_id])])
        return results

    def logical_reasoning(self, query: str) -> Dict:
        """
        Perform logical reasoning over the knowledge graph.

        This is a simplified version - in production would use LLM for complex reasoning.
        """
        query_lower = query.lower()

        # Pattern: "What did X suggest for Y?"
        match = re.search(r"what did (\w+) suggest for ([\w\s]+)\??", query_lower)
        if match:
            person = match.group(1)
            topic = match.group(2).strip()
            return self._reason_suggestion(person, topic)

        # Pattern: "Who worked on X?"
        match = re.search(r"who (\w+) (\w+\??)", query_lower)
        if match:
            relation = match.group(1)
            topic = match.group(2).strip("?")
            return self._reason_who_relation(relation, topic)

        # Pattern: "What involves X and Y?"
        match = re.search(r"what involves ([\w\s]+) and ([\w\s]+)\??", query_lower)
        if match:
            topic1 = match.group(1).strip()
            topic2 = match.group(2).strip()
            return self._reason_intersection(topic1, topic2)

        return {
            "query": query,
            "reasoning_type": "unknown",
            "result": "Could not parse query pattern",
            "suggestions": [
                "Try: 'What did Lexington suggest for authentication?'",
                "Try: 'Who worked on Project X?'",
                "Try: 'What involves security and Brooklyn?'",
            ],
        }

    def _reason_suggestion(self, person: str, topic: str) -> Dict:
        """Reason about suggestions."""
        # Find person entity
        person_entities = self.get_entities_by_name(person)
        if not person_entities:
            return {"error": f"Person not found: {person}"}

        person_id = list(person_entities)[0].id

        # Find "suggested" relationships
        suggestions = []
        for rel in self.get_relationships_from(person_id):
            if rel.relation == "suggested":
                target = self.entities.get(rel.target)
                if target and (
                    topic.lower() in target.name.lower()
                    or topic.lower() in str(target.properties).lower()
                ):
                    suggestions.append(
                        {
                            "suggestion": target.name,
                            "type": target.type,
                            "properties": target.properties,
                            "timestamp": rel.timestamp,
                        }
                    )

        return {
            "query_type": "suggestion_reasoning",
            "person": person,
            "topic": topic,
            "suggestions": suggestions,
            "count": len(suggestions),
        }

    def _reason_who_relation(self, relation: str, topic: str) -> Dict:
        """Reason about who has a relation to something."""
        # Find topic entity
        topic_entities = self.get_entities_by_name(topic)
        if not topic_entities:
            return {"error": f"Topic not found: {topic}"}

        topic_id = list(topic_entities)[0].id

        # Find relationships
        people = []
        for rel in self.get_relationships_to(topic_id):
            if rel.relation == relation:
                source = self.entities.get(rel.source)
                if source:
                    people.append(
                        {
                            "name": source.name,
                            "role": source.properties.get("role", "Unknown"),
                            "timestamp": rel.timestamp,
                        }
                    )

        return {
            "query_type": "who_relation",
            "relation": relation,
            "topic": topic,
            "people": people,
            "count": len(people),
        }

    def _reason_intersection(self, topic1: str, topic2: str) -> Dict:
        """Reason about intersection of two topics."""
        # Find entities for both topics
        entities1 = self.get_entities_by_name(topic1)
        entities2 = self.get_entities_by_name(topic2)

        # Find projects/decisions involving both
        results = []

        # Get all projects
        projects = self.get_entities_by_type("Project")

        for project in projects:
            project_rels = self.get_related_entities(project.id)
            related_names = [e[2].name.lower() for e in project_rels]

            if (
                topic1.lower() in related_names or any(topic1.lower() in r for r in related_names)
            ) and (
                topic2.lower() in related_names or any(topic2.lower() in r for r in related_names)
            ):
                results.append(
                    {
                        "project": project.name,
                        "status": project.properties.get("status", "Unknown"),
                        "properties": project.properties,
                    }
                )

        return {
            "query_type": "intersection",
            "topic1": topic1,
            "topic2": topic2,
            "projects": results,
            "count": len(results),
        }

    def extract_from_text(self, text: str, source: str = "") -> Dict:
        """
        Extract entities and relationships from text.

        In production, this would use an LLM for extraction.
        For now, we use rule-based extraction.
        """
        extracted = {"entities": [], "relationships": []}

        # Extract clan members
        clan_members = [
            "goliath",
            "lexington",
            "brooklyn",
            "broadway",
            "hudson",
            "bronx",
            "elisa",
            "xanatos",
            "demona",
            "jade",
        ]

        for member in clan_members:
            if member.lower() in text.lower():
                try:
                    entity = self.add_entity(name=member.title(), type="ClanMember", source=source)
                    extracted["entities"].append(entity)
                except ValueError:
                    pass  # Already exists

        # Extract technologies (simple pattern matching)
        tech_patterns = [
            r"\b(Python|JavaScript|React|Node\.js|Docker|Kubernetes|AWS|Azure|Git)\b",
            r"\b(PostgreSQL|MongoDB|Redis|Elasticsearch)\b",
            r"\b(OAuth|JWT|SSL|HTTPS|API|REST|GraphQL)\b",
        ]

        for pattern in tech_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in set(matches):
                try:
                    entity = self.add_entity(
                        name=match,
                        type="Technology",
                        properties={"category": "software"},
                        source=source,
                    )
                    extracted["entities"].append(entity)
                except ValueError:
                    pass

        # Extract relationships (simplified)
        # Pattern: "X suggested Y" or "X implemented Y"
        for member in clan_members:
            if member.lower() in text.lower():
                # Check for "suggested" pattern
                if re.search(rf"{member}\w*\s+suggested", text, re.IGNORECASE):
                    # Find what was suggested (next noun phrase)
                    match = re.search(rf"{member}\w*\s+suggested\s+(\w+)", text, re.IGNORECASE)
                    if match:
                        try:
                            rel = self.add_relationship(
                                source_name=member.title(),
                                relation="suggested",
                                target_name=match.group(1),
                            )
                            extracted["relationships"].append(rel)
                        except (ValueError, KeyError):
                            pass

        return extracted

    def get_stats(self) -> Dict:
        """Get knowledge graph statistics."""
        return {
            "total_entities": len(self.entities),
            "total_relationships": len(self.relationships),
            "entity_types": {t: len(eids) for t, eids in self.entity_by_type.items()},
            "relation_types": {r: len(rids) for r, rids in self.rel_by_type.items()},
            "schema_entity_types": list(self.schema.entity_types.keys()),
            "schema_relation_types": list(self.schema.relation_types.keys()),
        }

    def to_dict(self) -> Dict:
        """Export graph to dictionary."""
        return {
            "entities": [asdict(e) for e in self.entities.values()],
            "relationships": [asdict(r) for r in self.relationships.values()],
            "schema": {
                "entity_types": self.schema.entity_types,
                "relation_types": self.schema.relation_types,
            },
        }


__all__ = ["KnowledgeGraph", "Entity", "Relationship", "KnowledgeSchema"]
