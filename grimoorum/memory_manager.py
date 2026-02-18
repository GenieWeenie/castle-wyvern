"""
Grimoorum Memory System v2.0
Enhanced conversation memory with context, search, and agent-specific storage.
"""

import json
import os
import hashlib
from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict
import re


@dataclass
class MemoryEntry:
    """A single memory entry with metadata."""

    id: str
    timestamp: str
    user_input: str
    agent_name: str
    agent_response: str
    intent: str
    importance: int  # 1-5, higher = more important
    tags: List[str]
    session_id: str

    @classmethod
    def create(
        cls,
        user_input: str,
        agent_name: str,
        agent_response: str,
        intent: str = "unknown",
        importance: int = 3,
        tags: List[str] = None,
        session_id: str = "default",
    ):
        """Factory method to create a new memory entry."""
        entry_id = hashlib.md5(f"{datetime.now().isoformat()}{user_input}".encode()).hexdigest()[
            :12
        ]

        return cls(
            id=entry_id,
            timestamp=datetime.now().isoformat(),
            user_input=user_input,
            agent_name=agent_name,
            agent_response=agent_response,
            intent=intent,
            importance=importance,
            tags=tags or [],
            session_id=session_id,
        )


@dataclass
class ConversationThread:
    """A threaded conversation with related messages."""

    id: str
    started_at: str
    topic: str
    entries: List[str]  # MemoryEntry IDs
    summary: str = ""
    last_activity: str = ""


class GrimoorumV2:
    """
    Enhanced memory system for Castle Wyvern.

    Features:
    - Conversation threading (group related messages)
    - Importance scoring (prioritize key memories)
    - Tag-based search (find by topic)
    - Agent-specific context (each agent has memory)
    - Context window management (smart pruning)
    - Session isolation (conversations don't bleed)
    """

    def __init__(self, storage_dir: str = None):
        # Default to grimoorum/ directory relative to this file
        if storage_dir is None:
            storage_dir = os.path.dirname(os.path.abspath(__file__))

        self.storage_dir = storage_dir
        self.memory_file = os.path.join(storage_dir, "clan_memory_v2.json")
        self.threads_file = os.path.join(storage_dir, "threads.json")
        self.index_file = os.path.join(storage_dir, "memory_index.json")

        self.memories: Dict[str, MemoryEntry] = {}
        self.threads: Dict[str, ConversationThread] = {}
        self.agent_contexts: Dict[str, List[str]] = defaultdict(list)

        self._initialize_storage()
        self._load_data()

    def _initialize_storage(self):
        """Create storage files if they don't exist."""
        os.makedirs(self.storage_dir, exist_ok=True)

        for file_path in [self.memory_file, self.threads_file, self.index_file]:
            if not os.path.exists(file_path):
                with open(file_path, "w") as f:
                    json.dump({} if "index" in file_path else [], f)

    def _load_data(self):
        """Load existing memories from storage."""
        try:
            with open(self.memory_file, "r") as f:
                data = json.load(f)
                self.memories = {m["id"]: MemoryEntry(**m) for m in data}

            with open(self.threads_file, "r") as f:
                data = json.load(f)
                self.threads = {t["id"]: ConversationThread(**t) for t in data}

            self._rebuild_agent_index()

        except (FileNotFoundError, json.JSONDecodeError):
            self.memories = {}
            self.threads = {}

    def _save_data(self):
        """Persist memories to storage."""
        with open(self.memory_file, "w") as f:
            json.dump([asdict(m) for m in self.memories.values()], f, indent=2)

        with open(self.threads_file, "w") as f:
            json.dump([asdict(t) for t in self.threads.values()], f, indent=2)

    def _rebuild_agent_index(self):
        """Rebuild agent-specific context index."""
        self.agent_contexts = defaultdict(list)
        for entry in self.memories.values():
            self.agent_contexts[entry.agent_name].append(entry.id)

    def record(
        self,
        user_input: str,
        agent_name: str,
        agent_response: str,
        intent: str = "unknown",
        importance: int = 3,
        tags: List[str] = None,
        thread_id: str = None,
        session_id: str = "default",
    ) -> str:
        """
        Record a new memory entry.

        Args:
            user_input: What the user said
            agent_name: Which agent responded
            agent_response: What the agent said
            intent: Classified intent (code, question, etc.)
            importance: 1-5, higher = more important
            tags: List of topic tags
            thread_id: Optional conversation thread ID
            session_id: Session identifier for isolation

        Returns:
            Memory entry ID
        """
        # Auto-generate tags if not provided
        if tags is None:
            tags = self._extract_tags(user_input)

        entry = MemoryEntry.create(
            user_input=user_input,
            agent_name=agent_name,
            agent_response=agent_response,
            intent=intent,
            importance=importance,
            tags=tags,
            session_id=session_id,
        )

        self.memories[entry.id] = entry
        self.agent_contexts[agent_name].append(entry.id)

        # Add to thread if specified
        if thread_id and thread_id in self.threads:
            self.threads[thread_id].entries.append(entry.id)
            self.threads[thread_id].last_activity = entry.timestamp

        self._save_data()
        return str(entry.id)

    def _extract_tags(self, text: str) -> List[str]:
        """Auto-extract tags from text."""
        tags = []

        # Technology tags
        tech_patterns = {
            "python": r"\bpython\b",
            "javascript": r"\b(javascript|js|node)\b",
            "database": r"\b(database|sql|postgres|mysql)\b",
            "api": r"\b(api|rest|graphql)\b",
            "security": r"\b(security|auth|encrypt|vulnerability)\b",
            "architecture": r"\b(architecture|microservice|design|pattern)\b",
        }

        text_lower = text.lower()
        for tag, pattern in tech_patterns.items():
            if re.search(pattern, text_lower):
                tags.append(tag)

        return tags

    def create_thread(self, topic: str, session_id: str = "default") -> str:
        """Create a new conversation thread."""
        thread_id = hashlib.md5(f"{datetime.now().isoformat()}{topic}".encode()).hexdigest()[:12]

        thread = ConversationThread(
            id=thread_id,
            started_at=datetime.now().isoformat(),
            topic=topic,
            entries=[],
            summary="",
            last_activity=datetime.now().isoformat(),
        )

        self.threads[thread_id] = thread
        self._save_data()
        return thread_id

    def get_context_for_agent(
        self, agent_name: str, limit: int = 5, session_id: str = None
    ) -> List[Dict]:
        """
        Get relevant context for a specific agent.

        Returns recent interactions with this agent, filtered by session
        if specified.
        """
        entry_ids = self.agent_contexts.get(agent_name, [])

        # Get entries
        entries = [self.memories[eid] for eid in entry_ids if eid in self.memories]

        # Filter by session if specified
        if session_id:
            entries = [e for e in entries if e.session_id == session_id]

        # Sort by timestamp (newest first)
        entries.sort(key=lambda x: x.timestamp, reverse=True)

        # Return last N
        return [asdict(e) for e in entries[:limit]]

    def get_recent_memories(self, limit: int = 10, session_id: str = None) -> List[Dict]:
        """Get most recent memories, optionally filtered by session."""
        entries = list(self.memories.values())

        if session_id:
            entries = [e for e in entries if e.session_id == session_id]

        entries.sort(key=lambda x: x.timestamp, reverse=True)
        return [asdict(e) for e in entries[:limit]]

    def search_by_tag(self, tag: str, limit: int = 10) -> List[Dict]:
        """Search memories by tag."""
        results = [
            asdict(e) for e in self.memories.values() if tag.lower() in [t.lower() for t in e.tags]
        ]
        return results[:limit]

    def search_by_keyword(self, keyword: str, limit: int = 10) -> List[Dict]:
        """Simple keyword search in user inputs and responses."""
        keyword_lower = keyword.lower()
        results = []

        for entry in self.memories.values():
            if (
                keyword_lower in entry.user_input.lower()
                or keyword_lower in entry.agent_response.lower()
            ):
                results.append(asdict(entry))

        return results[:limit]

    def get_thread(self, thread_id: str) -> Optional[Dict]:
        """Get a conversation thread with full entries."""
        if thread_id not in self.threads:
            return None

        thread = self.threads[thread_id]
        entries = [asdict(self.memories[eid]) for eid in thread.entries if eid in self.memories]

        return {
            "id": thread.id,
            "topic": thread.topic,
            "started_at": thread.started_at,
            "last_activity": thread.last_activity,
            "summary": thread.summary,
            "entries": entries,
        }

    def get_important_memories(self, min_importance: int = 4, limit: int = 20) -> List[Dict]:
        """Get high-importance memories."""
        results = [asdict(e) for e in self.memories.values() if e.importance >= min_importance]
        results.sort(key=lambda x: x["importance"], reverse=True)
        return results[:limit]

    def get_stats(self) -> Dict[str, Any]:
        """Get memory system statistics."""
        return {
            "total_memories": len(self.memories),
            "total_threads": len(self.threads),
            "agents_with_memories": len(self.agent_contexts),
            "agent_breakdown": {
                agent: len(entries) for agent, entries in self.agent_contexts.items()
            },
            "high_importance": len([e for e in self.memories.values() if e.importance >= 4]),
            "storage_size_kb": round(
                (os.path.getsize(self.memory_file) if os.path.exists(self.memory_file) else 0)
                / 1024,
                2,
            ),
        }

    def prune_old_memories(self, keep_days: int = 30, min_importance: int = 3):
        """
        Remove old, low-importance memories.
        Keeps high-importance memories regardless of age.
        """
        cutoff = datetime.now().timestamp() - (keep_days * 24 * 60 * 60)
        to_remove = []

        for entry_id, entry in self.memories.items():
            entry_time = datetime.fromisoformat(entry.timestamp).timestamp()
            if entry_time < cutoff and entry.importance < min_importance:
                to_remove.append(entry_id)

        for entry_id in to_remove:
            del self.memories[entry_id]

        # Clean up agent contexts
        self._rebuild_agent_index()
        self._save_data()

        return len(to_remove)

    def export_session(self, session_id: str, filepath: str):
        """Export all memories from a session to a file."""
        session_memories = [asdict(e) for e in self.memories.values() if e.session_id == session_id]

        with open(filepath, "w") as f:
            json.dump(session_memories, f, indent=2)

    def consult_archives(self, limit: int = 10) -> List[Dict]:
        """Backward-compatible: return recent memories (e.g. for summon_council)."""
        return self.get_recent_memories(limit=limit)

    def get_formatted_context(self, agent_name: str = None, limit: int = 5) -> str:
        """
        Get formatted context string for AI prompts.
        Returns recent conversation history in a readable format.
        """
        if agent_name:
            memories = self.get_context_for_agent(agent_name, limit)
        else:
            memories = self.get_recent_memories(limit)

        if not memories:
            return "No previous context."

        lines = ["## Previous Conversation Context", ""]

        for mem in reversed(memories):  # Oldest first
            lines.append(f"**User:** {mem['user_input']}")
            lines.append(f"**{mem['agent_name'].title()}:** {mem['agent_response'][:200]}...")
            lines.append("")

        return "\n".join(lines)


# Backward compatibility
Grimoorum = GrimoorumV2


if __name__ == "__main__":
    # Test the enhanced memory system
    print("🧠 Testing Grimoorum v2.0...")
    print("=" * 50)

    grimoorum = GrimoorumV2()

    # Record some test memories
    print("\n1. Recording test memories...")

    mem1 = grimoorum.record(
        user_input="Write a Python function to calculate fibonacci",
        agent_name="lexington",
        agent_response="Here's a recursive fibonacci function...",
        intent="code",
        importance=4,
        tags=["python", "algorithm"],
    )
    print(f"   Recorded: {mem1}")

    mem2 = grimoorum.record(
        user_input="How should I structure my microservices?",
        agent_name="brooklyn",
        agent_response="Consider using an API gateway...",
        intent="architecture",
        importance=5,
        tags=["architecture", "microservices"],
    )
    print(f"   Recorded: {mem2}")

    mem3 = grimoorum.record(
        user_input="Summarize the key points of machine learning",
        agent_name="broadway",
        agent_response="Machine learning involves...",
        intent="document",
        importance=3,
        tags=["ml", "summary"],
    )
    print(f"   Recorded: {mem3}")

    # Test search
    print("\n2. Searching by tag 'python'...")
    results = grimoorum.search_by_tag("python")
    print(f"   Found {len(results)} memories")

    print("\n3. Getting context for Lexington...")
    context = grimoorum.get_context_for_agent("lexington")
    print(f"   Found {len(context)} memories")

    print("\n4. Getting stats...")
    stats = grimoorum.get_stats()
    print(f"   Total memories: {stats['total_memories']}")
    print(f"   Total threads: {stats['total_threads']}")
    print(f"   Storage size: {stats['storage_size_kb']} KB")

    print("\n✅ Grimoorum v2.0 working!")
