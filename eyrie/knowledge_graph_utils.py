"""
Enhanced Knowledge Graph Utilities
Polish features for production use
"""

import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime


class KnowledgeGraphVisualizer:
    """Visualize knowledge graph using Graphviz."""

    def __init__(self, knowledge_graph):
        self.kg = knowledge_graph

    def to_dot(self) -> str:
        """Convert knowledge graph to Graphviz DOT format."""
        lines = ["digraph KnowledgeGraph {", "  rankdir=LR;"]
        lines.append("  node [shape=box, style=filled, fillcolor=lightblue];")
        lines.append("  edge [color=gray];")

        # Add entity nodes
        entity_colors = {
            "ClanMember": "lightgreen",
            "Technology": "lightyellow",
            "Project": "lightcoral",
            "Decision": "lightpink",
            "SecurityIssue": "salmon",
            "Task": "lightcyan",
        }

        for entity_id, entity in self.kg.entities.items():
            color = entity_colors.get(entity.type, "lightblue")
            label = f"{entity.name}\\n({entity.type})"
            lines.append(f'  "{entity_id}" [label="{label}", fillcolor={color}];')

        # Add relationship edges
        for rel_id, rel in self.kg.relationships.items():
            lines.append(f'  "{rel.source}" -> "{rel.target}" [label="{rel.relation}"];')

        lines.append("}")
        return "\n".join(lines)

    def to_mermaid(self) -> str:
        """Convert knowledge graph to Mermaid format (for Markdown)."""
        lines = ["```mermaid", "graph LR"]

        # Add relationships
        for rel_id, rel in self.kg.relationships.items():
            source = (
                self.kg.entities[rel.source].name if rel.source in self.kg.entities else rel.source
            )
            target = (
                self.kg.entities[rel.target].name if rel.target in self.kg.entities else rel.target
            )
            lines.append(f"    {source}[{source}] --|{rel.relation}|--> {target}[{target}]")

        lines.append("```")
        return "\n".join(lines)

    def export_to_file(self, output_path: str, format: str = "dot") -> str:
        """
        Export graph to file.

        Args:
            output_path: Path to output file
            format: 'dot', 'mermaid', 'png' (requires graphviz), 'svg' (requires graphviz)
        """
        path = Path(output_path)

        if format in ["dot", "txt"]:
            content = self.to_dot()
            path.write_text(content)
            return str(path)

        elif format == "mermaid":
            content = self.to_mermaid()
            path.write_text(content)
            return str(path)

        elif format in ["png", "svg", "pdf"]:
            # Requires graphviz installed
            dot_content = self.to_dot()
            dot_path = path.with_suffix(".dot")
            dot_path.write_text(dot_content)

            try:
                result = subprocess.run(
                    ["dot", f"-T{format}", str(dot_path), "-o", str(output_path)],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                if result.returncode == 0:
                    dot_path.unlink()  # Clean up dot file
                    return str(path)
                else:
                    return f"Error: {result.stderr}"
            except FileNotFoundError:
                return "Error: Graphviz not installed. Run: brew install graphviz"
            except Exception as e:
                return f"Error: {str(e)}"

        else:
            raise ValueError(f"Unsupported format: {format}")

    def get_graph_summary(self) -> Dict:
        """Get summary statistics for visualization."""
        # Calculate node degrees
        node_degrees = {}
        for entity_id in self.kg.entities:
            out_degree = len(self.kg.get_relationships_from(entity_id))
            in_degree = len(self.kg.get_relationships_to(entity_id))
            node_degrees[entity_id] = out_degree + in_degree

        # Find most connected nodes
        top_nodes = sorted(node_degrees.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            "total_nodes": len(self.kg.entities),
            "total_edges": len(self.kg.relationships),
            "avg_degree": sum(node_degrees.values()) / len(node_degrees) if node_degrees else 0,
            "top_connected": [
                {"name": self.kg.entities[eid].name, "connections": degree}
                for eid, degree in top_nodes
            ],
            "entity_type_distribution": {
                etype: len(eids) for etype, eids in self.kg.entity_by_type.items()
            },
        }


class SmartEntityExtractor:
    """Enhanced entity extraction using multiple methods."""

    def __init__(self, knowledge_graph):
        self.kg = knowledge_graph
        self.extraction_patterns = self._build_patterns()

    def _build_patterns(self) -> Dict:
        """Build regex patterns for entity extraction."""
        return {
            "technologies": [
                r"\b(Python|JavaScript|TypeScript|Java|Go|Rust|C\+\+|Ruby|PHP)\b",
                r"\b(React|Vue|Angular|Svelte|Next\.js|Nuxt\.js)\b",
                r"\b(Node\.js|Django|Flask|FastAPI|Express|Rails|Laravel)\b",
                r"\b(Docker|Kubernetes|AWS|Azure|GCP|Heroku|Vercel)\b",
                r"\b(PostgreSQL|MySQL|MongoDB|Redis|Elasticsearch|SQLite)\b",
                r"\b(GraphQL|REST|gRPC|WebSocket|OAuth|JWT)\b",
                r"\b(TensorFlow|PyTorch|Scikit-learn|OpenAI|HuggingFace)\b",
                r"\b(Git|GitHub|GitLab|Bitbucket|Jenkins|CircleCI|Travis)\b",
            ],
            "actions": [
                r"(?:\w+)\s+(suggested|recommended|proposed|advised)",
                r"(?:\w+)\s+(implemented|built|created|developed)",
                r"(?:\w+)\s+(reviewed|audited|checked|verified)",
                r"(?:\w+)\s+(discovered|found|identified|detected)",
                r"(?:\w+)\s+(leads|manages|directs|oversees)",
                r"(?:\w+)\s+(depends on|requires|needs|uses)",
            ],
            "project_indicators": [
                r"\b(project|initiative|system|application|platform|service)\s+(?:called|named)?\s+[\'\"]?([A-Z][a-zA-Z\s]+)",
                r"\b(building|developing|creating)\s+(?:a|an)?\s+([a-zA-Z\s]+?)(?:\s+for|\s+to|\s+that)",
            ],
        }

    def extract_with_llm(self, text: str, llm_client=None) -> Dict:
        """
        Extract entities using LLM (if available).

        Falls back to rule-based if no LLM.
        """
        if llm_client:
            try:
                prompt = f"""
                Extract entities and relationships from this text:
                "{text}"
                
                Return JSON with format:
                {{
                    "entities": [
                        {{"name": "Entity Name", "type": "EntityType", "properties": {{}}}}
                    ],
                    "relationships": [
                        {{"source": "Entity1", "relation": "relation_type", "target": "Entity2"}}
                    ]
                }}
                
                Valid entity types: ClanMember, Technology, Project, Decision, SecurityIssue, Task
                Valid relations: suggested, reviewed, implemented, involves, depends_on, discovered, leads
                """

                # In production, this would call actual LLM
                # For now, fall back to rule-based
                return self.extract_rule_based(text)

            except Exception:
                return self.extract_rule_based(text)
        else:
            return self.extract_rule_based(text)

    def extract_rule_based(self, text: str) -> Dict[str, Any]:
        """Extract entities using enhanced rule-based approach."""
        import re

        extracted: Dict[str, Any] = {"entities": [], "relationships": []}

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
            "you",
        ]

        text_lower = text.lower()

        for member in clan_members:
            if member in text_lower:
                extracted["entities"].append(
                    {"name": member.title(), "type": "ClanMember", "confidence": 0.9}
                )

        # Extract technologies
        for pattern in self.extraction_patterns["technologies"]:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                extracted["entities"].append(
                    {"name": match, "type": "Technology", "confidence": 0.8}
                )

        # Extract actions (relationships)
        for pattern in self.extraction_patterns["actions"]:
            action_matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in action_matches:
                person = match.group(1)
                action = match.group(2).lower()

                # Map action to relation type
                relation_map = {
                    "suggested": "suggested",
                    "recommended": "suggested",
                    "proposed": "suggested",
                    "implemented": "implemented",
                    "built": "implemented",
                    "created": "implemented",
                    "reviewed": "reviewed",
                    "audited": "reviewed",
                    "discovered": "discovered",
                    "leads": "leads",
                    "depends on": "depends_on",
                }

                if action in relation_map:
                    # Try to find what they acted on (next noun phrase)
                    after_text = text[match.end() :]
                    target_match = re.search(r"\b([A-Z][a-zA-Z]+)", after_text)
                    if target_match:
                        extracted["relationships"].append(
                            {
                                "source": (
                                    person.title() if person.lower() in clan_members else "Someone"
                                ),
                                "relation": relation_map[action],
                                "target": target_match.group(1),
                                "confidence": 0.7,
                            }
                        )

        # Extract projects
        for pattern in self.extraction_patterns["project_indicators"]:
            project_matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in project_matches:
                project_name = match.group(2).strip()
                if len(project_name) > 2:
                    extracted["entities"].append(
                        {"name": project_name, "type": "Project", "confidence": 0.6}
                    )

        return extracted

    def extract_batch(self, texts: List[str]) -> List[Dict]:
        """Extract entities from multiple texts."""
        return [self.extract_rule_based(text) for text in texts]


class QueryEngine:
    """Enhanced query engine for knowledge graph."""

    def __init__(self, knowledge_graph):
        self.kg = knowledge_graph

    def find_path(self, start_entity: str, end_entity: str, max_depth: int = 5) -> List[List[str]]:
        """
        Find paths between two entities.

        Returns list of paths (each path is list of entity IDs).
        """
        start_entities = self.kg.get_entities_by_name(start_entity)
        end_entities = self.kg.get_entities_by_name(end_entity)

        if not start_entities or not end_entities:
            return []

        start_id = list(start_entities)[0].id
        end_id = list(end_entities)[0].id

        paths = []
        visited = set()

        def dfs(current_id: str, target_id: str, path: List[str], depth: int):
            if depth > max_depth:
                return

            if current_id == target_id:
                paths.append(path.copy())
                return

            visited.add(current_id)

            # Get outgoing relationships
            for rel in self.kg.get_relationships_from(current_id):
                if rel.target not in visited:
                    path.append(rel.target)
                    dfs(rel.target, target_id, path, depth + 1)
                    path.pop()

            visited.remove(current_id)

        dfs(start_id, end_id, [start_id], 0)
        return paths

    def find_collaborators(self, entity_name: str) -> List[Dict]:
        """Find entities that frequently collaborate with given entity."""
        entities = self.kg.get_entities_by_name(entity_name)
        if not entities:
            return []

        entity_id = list(entities)[0].id

        # Find all paths of length 2 (collaborator patterns)
        collaborators = {}

        for rel1 in self.kg.get_relationships_from(entity_id):
            intermediate = rel1.target

            for rel2 in self.kg.get_relationships_from(intermediate):
                if rel2.target != entity_id:
                    collab_id = rel2.target
                    if collab_id not in collaborators:
                        collaborators[collab_id] = {
                            "entity": self.kg.entities[collab_id],
                            "paths": [],
                        }
                    collaborators[collab_id]["paths"].append(
                        {
                            "via": self.kg.entities[intermediate],
                            "relation1": rel1.relation,
                            "relation2": rel2.relation,
                        }
                    )

        return list(collaborators.values())

    def semantic_search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Simple semantic search over entities.

        In production, would use embeddings. This uses keyword matching.
        """
        query_terms = query.lower().split()
        scores = {}

        for entity_id, entity in self.kg.entities.items():
            score = 0
            entity_text = f"{entity.name} {entity.type} {str(entity.properties)}".lower()

            for term in query_terms:
                if term in entity_text:
                    score += 1

            if score > 0:
                scores[entity_id] = score

        # Sort by score
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        return [
            {"entity": self.kg.entities[eid], "score": score}
            for eid, score in sorted_scores[:top_k]
        ]


class KnowledgeGraphExporter:
    """Export knowledge graph to various formats."""

    def __init__(self, knowledge_graph):
        self.kg = knowledge_graph

    def to_json(self) -> str:
        """Export to JSON."""
        data = {
            "entities": [
                {
                    "id": e.id,
                    "name": e.name,
                    "type": e.type,
                    "properties": e.properties,
                    "created": e.timestamp,
                }
                for e in self.kg.entities.values()
            ],
            "relationships": [
                {
                    "id": r.id,
                    "source": r.source,
                    "target": r.target,
                    "relation": r.relation,
                    "properties": r.properties,
                }
                for r in self.kg.relationships.values()
            ],
        }
        return json.dumps(data, indent=2)

    def to_csv(self) -> Tuple[str, str]:
        """Export to CSV (entities and relationships)."""
        # Entities CSV
        entities_csv = "id,name,type,properties\n"
        for e in self.kg.entities.values():
            props = json.dumps(e.properties).replace('"', '""')
            entities_csv += f'"{e.id}","{e.name}","{e.type}","{props}"\n'

        # Relationships CSV
        rels_csv = "id,source,target,relation\n"
        for r in self.kg.relationships.values():
            rels_csv += f'"{r.id}","{r.source}","{r.target}","{r.relation}"\n'

        return entities_csv, rels_csv

    def export_report(self, output_path: str):
        """Export a comprehensive markdown report."""
        visualizer = KnowledgeGraphVisualizer(self.kg)
        stats = visualizer.get_graph_summary()

        report = f"""# Knowledge Graph Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Statistics

- **Total Entities**: {stats['total_nodes']}
- **Total Relationships**: {stats['total_edges']}
- **Average Connections**: {stats['avg_degree']:.2f}

## Entity Distribution

"""

        for etype, count in stats["entity_type_distribution"].items():
            report += f"- {etype}: {count}\n"

        report += "\n## Most Connected Entities\n\n"
        for node in stats["top_connected"]:
            report += f"- **{node['name']}**: {node['connections']} connections\n"

        report += "\n## Graph Visualization (Mermaid)\n\n"
        report += visualizer.to_mermaid()

        Path(output_path).write_text(report)
        return output_path


# Add to knowledge_graph.py
__all__ = [
    "KnowledgeGraphVisualizer",
    "SmartEntityExtractor",
    "QueryEngine",
    "KnowledgeGraphExporter",
]
