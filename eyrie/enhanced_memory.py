"""
Castle Wyvern Enhanced Memory
Feature: Semantic search with embeddings

Provides:
- Vector-based memory storage
- Semantic similarity search
- Memory consolidation
- Context-aware retrieval
"""

import os
import json
import hashlib
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict
import pickle


@dataclass
class MemoryEmbedding:
    """A memory with its embedding vector."""

    id: str
    content: str
    embedding: List[float]
    metadata: Dict[str, Any]
    timestamp: str
    importance: int  # 1-5 scale
    access_count: int = 0
    last_accessed: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "content": self.content,
            "embedding": self.embedding,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
            "importance": self.importance,
            "access_count": self.access_count,
            "last_accessed": self.last_accessed,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "MemoryEmbedding":
        return cls(
            id=data["id"],
            content=data["content"],
            embedding=data["embedding"],
            metadata=data.get("metadata", {}),
            timestamp=data["timestamp"],
            importance=data.get("importance", 3),
            access_count=data.get("access_count", 0),
            last_accessed=data.get("last_accessed"),
        )


class SimpleEmbeddingGenerator:
    """
    Simple embedding generator using local methods.

    For production, replace with:
    - OpenAI embeddings API
    - Local embedding model (sentence-transformers)
    - Ollama embeddings
    """

    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.vocab: Dict[str, int] = {}
        self.vocab_size = 0

    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization."""
        # Lowercase and split on non-alphanumeric
        import re

        return re.findall(r"\b\w+\b", text.lower())

    def _get_word_vector(self, word: str) -> np.ndarray:
        """Get vector for a word using hash-based approach."""
        # Use hash to generate consistent vectors
        hash_val = int(hashlib.md5(word.encode()).hexdigest(), 16)
        np.random.seed(hash_val)
        vec = np.random.randn(self.dimension)
        np.random.seed()  # Reset seed
        return vec / np.linalg.norm(vec)  # Normalize

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text.

        This is a simplified approach. Real implementations would use:
        - sentence-transformers
        - OpenAI text-embedding-3-small
        - Ollama embeddings
        """
        tokens = self._tokenize(text)

        if not tokens:
            return [0.0] * self.dimension

        # Average word vectors with TF-IDF weighting
        vectors = []
        token_counts = defaultdict(int)

        for token in tokens:
            token_counts[token] += 1

        for token in tokens:
            vec = self._get_word_vector(token)
            # Simple TF weighting
            tf = token_counts[token] / len(tokens)
            vectors.append(vec * tf)

        # Average and normalize
        embedding = np.mean(vectors, axis=0)
        embedding = embedding / (np.linalg.norm(embedding) + 1e-8)

        return embedding.tolist()


class VectorMemoryStore:
    """
    Vector-based memory storage with semantic search.
    """

    def __init__(self, storage_dir: str = None, dimension: int = 384):
        if storage_dir is None:
            storage_dir = os.path.expanduser("~/.castle_wyvern/vector_memory")

        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)

        self.dimension = dimension
        self.embedder = SimpleEmbeddingGenerator(dimension)

        # In-memory storage
        self.memories: Dict[str, MemoryEmbedding] = {}

        # Index for fast retrieval (id -> memory)
        self.index: Dict[str, np.ndarray] = {}

        # Load existing memories
        self._load_memories()

    def _get_storage_path(self) -> str:
        """Get storage file path."""
        return os.path.join(self.storage_dir, "vector_memory.pkl")

    def _load_memories(self):
        """Load memories from disk."""
        storage_path = self._get_storage_path()

        if os.path.exists(storage_path):
            try:
                with open(storage_path, "rb") as f:
                    data = pickle.load(f)

                for mem_data in data.get("memories", []):
                    mem = MemoryEmbedding.from_dict(mem_data)
                    self.memories[mem.id] = mem
                    self.index[mem.id] = np.array(mem.embedding)

                print(f"[VectorMemory] Loaded {len(self.memories)} memories")

            except Exception as e:
                print(f"[VectorMemory] Error loading: {e}")

    def _save_memories(self):
        """Save memories to disk."""
        try:
            data = {
                "memories": [mem.to_dict() for mem in self.memories.values()],
                "dimension": self.dimension,
                "saved_at": datetime.now().isoformat(),
            }

            storage_path = self._get_storage_path()
            with open(storage_path, "wb") as f:
                pickle.dump(data, f)

        except Exception as e:
            print(f"[VectorMemory] Error saving: {e}")

    def add_memory(self, content: str, metadata: Dict = None, importance: int = 3) -> str:
        """
        Add a memory with embedding.

        Args:
            content: The memory content
            metadata: Additional metadata
            importance: Importance level (1-5)

        Returns:
            Memory ID
        """
        # Generate embedding
        embedding = self.embedder.generate_embedding(content)

        # Create memory
        mem_id = hashlib.md5(f"{content}{datetime.now()}".encode()).hexdigest()[:16]

        memory = MemoryEmbedding(
            id=mem_id,
            content=content,
            embedding=embedding,
            metadata=metadata or {},
            timestamp=datetime.now().isoformat(),
            importance=importance,
        )

        # Store
        self.memories[mem_id] = memory
        self.index[mem_id] = np.array(embedding)

        # Auto-save every 10 memories
        if len(self.memories) % 10 == 0:
            self._save_memories()

        return mem_id

    def search_similar(
        self, query: str, top_k: int = 5, min_similarity: float = 0.5
    ) -> List[Tuple[MemoryEmbedding, float]]:
        """
        Search for semantically similar memories.

        Args:
            query: Search query
            top_k: Number of results to return
            min_similarity: Minimum similarity threshold (0-1)

        Returns:
            List of (memory, similarity_score) tuples
        """
        if not self.memories:
            return []

        # Generate query embedding
        query_embedding = np.array(self.embedder.generate_embedding(query))

        # Calculate similarities
        similarities = []
        for mem_id, mem_embedding in self.index.items():
            # Cosine similarity
            similarity = np.dot(query_embedding, mem_embedding)
            similarities.append((mem_id, similarity))

        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)

        # Filter and return top results
        results = []
        for mem_id, similarity in similarities[:top_k]:
            if similarity >= min_similarity:
                memory = self.memories[mem_id]

                # Update access stats
                memory.access_count += 1
                memory.last_accessed = datetime.now().isoformat()

                results.append((memory, float(similarity)))

        return results

    def get_memory(self, mem_id: str) -> Optional[MemoryEmbedding]:
        """Get a specific memory by ID."""
        return self.memories.get(mem_id)

    def delete_memory(self, mem_id: str) -> bool:
        """Delete a memory."""
        if mem_id in self.memories:
            del self.memories[mem_id]
            del self.index[mem_id]
            self._save_memories()
            return True
        return False

    def get_recent_memories(self, limit: int = 10) -> List[MemoryEmbedding]:
        """Get recent memories."""
        sorted_memories = sorted(self.memories.values(), key=lambda m: m.timestamp, reverse=True)
        return sorted_memories[:limit]

    def get_important_memories(
        self, min_importance: int = 4, limit: int = 10
    ) -> List[MemoryEmbedding]:
        """Get high-importance memories."""
        important = [m for m in self.memories.values() if m.importance >= min_importance]

        # Sort by importance, then by access count
        important.sort(key=lambda m: (m.importance, m.access_count), reverse=True)

        return important[:limit]

    def get_context_for_conversation(
        self, query: str, recent_limit: int = 3, similar_limit: int = 3
    ) -> List[str]:
        """
        Get relevant context for a conversation.

        Combines recent memories + semantically similar memories.
        """
        context = []

        # Add recent memories
        recent = self.get_recent_memories(recent_limit)
        for mem in recent:
            context.append(f"Recent: {mem.content}")

        # Add similar memories
        similar = self.search_similar(query, top_k=similar_limit)
        for mem, score in similar:
            if mem.id not in [r.id for r in recent]:  # Avoid duplicates
                context.append(f"Related: {mem.content}")

        return context

    def consolidate_memories(self, age_days: int = 30, min_access_count: int = 2) -> int:
        """
        Consolidate old, rarely-accessed memories.

        Returns number of memories consolidated.
        """
        cutoff = datetime.now() - timedelta(days=age_days)
        consolidated = 0

        to_consolidate = []
        for mem_id, memory in self.memories.items():
            mem_time = datetime.fromisoformat(memory.timestamp)

            # Old and rarely accessed
            if mem_time < cutoff and memory.access_count < min_access_count:
                to_consolidate.append(mem_id)

        # In a real implementation, this would:
        # 1. Summarize related memories
        # 2. Create consolidated "memory of memories"
        # 3. Archive old ones

        # For now, just mark them
        for mem_id in to_consolidate:
            self.memories[mem_id].metadata["consolidated"] = True
            consolidated += 1

        if consolidated > 0:
            self._save_memories()

        return consolidated

    def get_stats(self) -> Dict:
        """Get memory statistics."""
        if not self.memories:
            return {"total_memories": 0, "avg_importance": 0, "total_accesses": 0}

        importances = [m.importance for m in self.memories.values()]
        accesses = [m.access_count for m in self.memories.values()]

        return {
            "total_memories": len(self.memories),
            "dimension": self.dimension,
            "avg_importance": sum(importances) / len(importances),
            "total_accesses": sum(accesses),
            "high_importance": sum(1 for i in importances if i >= 4),
            "consolidated": sum(
                1 for m in self.memories.values() if m.metadata.get("consolidated", False)
            ),
        }


class EnhancedGrimoorum:
    """
    Enhanced version of Grimoorum with vector-based semantic memory.

    Wraps the original Grimoorum and adds vector search capabilities.
    """

    def __init__(self, original_grimoorum=None):
        self.original = original_grimoorum
        self.vector_store = VectorMemoryStore()

    def add(
        self, content: str, doc_type: str = "note", metadata: Dict = None, importance: int = 3
    ) -> str:
        """
        Add content to both original and vector memory.
        """
        # Add to original Grimoorum (if available)
        original_id = None
        if self.original:
            try:
                original_id = self.original.add(content, doc_type, metadata)
            except Exception:
                pass

        # Add to vector store
        vector_metadata = {**(metadata or {}), "original_id": original_id, "doc_type": doc_type}

        vector_id = self.vector_store.add_memory(
            content=content, metadata=vector_metadata, importance=importance
        )

        return vector_id

    def search(self, query: str, limit: int = 10, use_semantic: bool = True) -> List[Dict]:
        """
        Search memories.

        Args:
            query: Search query
            limit: Max results
            use_semantic: Use semantic search (vs keyword)
        """
        if use_semantic:
            results = self.vector_store.search_similar(query, top_k=limit)
            return [
                {
                    "id": mem.id,
                    "content": mem.content,
                    "similarity": score,
                    "metadata": mem.metadata,
                    "timestamp": mem.timestamp,
                }
                for mem, score in results
            ]
        else:
            # Fallback to original search
            if self.original:
                return self.original.search(query, limit)
            return []

    def get_context(self, query: str, max_items: int = 5) -> str:
        """
        Get relevant context as a formatted string.
        """
        context_items = self.vector_store.get_context_for_conversation(
            query, recent_limit=2, similar_limit=max_items - 2
        )

        if context_items:
            return "\n\n".join(context_items)
        return ""

    def get_stats(self) -> Dict:
        """Get combined statistics."""
        vector_stats = self.vector_store.get_stats()

        if self.original:
            try:
                original_stats = self.original.get_stats()
            except Exception:
                original_stats = {}
        else:
            original_stats = {}

        return {"vector_memory": vector_stats, "original_memory": original_stats, "enhanced": True}


# Standalone test
if __name__ == "__main__":
    print("🏰 Castle Wyvern Enhanced Memory Test")
    print("=" * 50)

    # Create enhanced memory
    memory = EnhancedGrimoorum()

    # Add some test memories
    print("\n1. Adding test memories...")
    memories = [
        ("Python is a high-level programming language", {"topic": "programming"}),
        ("Machine learning is a subset of AI", {"topic": "ai"}),
        ("Neural networks are inspired by the human brain", {"topic": "ai"}),
        ("Flask is a Python web framework", {"topic": "programming"}),
        ("REST APIs use HTTP methods", {"topic": "web"}),
    ]

    for content, meta in memories:
        mem_id = memory.add(content, metadata=meta, importance=4)
        print(f"   Added: {content[:40]}...")

    # Test semantic search
    print("\n2. Testing semantic search...")
    results = memory.search("What is AI?", use_semantic=True)
    print(f"   Found {len(results)} results:")
    for r in results:
        print(f"   - {r['content'][:40]}... (sim: {r['similarity']:.2f})")

    # Test context retrieval
    print("\n3. Testing context retrieval...")
    context = memory.get_context("Tell me about programming")
    print(f"   Context:\n{context}")

    # Test stats
    print("\n4. Memory stats:")
    print(f"   {memory.get_stats()}")

    print("\n✅ Enhanced Memory ready!")
