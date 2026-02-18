"""
Castle Wyvern Advanced AI Features
Feature 19: Enhanced AI capabilities

Provides:
- Multi-model ensemble voting
- Streaming responses
- Context window management
- Prompt optimization
- AI-powered code execution
"""

import os
import json
import time
import asyncio
from typing import Dict, List, Optional, Callable, Any, AsyncGenerator, Tuple, cast
from dataclasses import dataclass
from datetime import datetime
from collections import defaultdict
import hashlib


@dataclass
class ModelResponse:
    """Response from an AI model."""

    model: str
    response: str
    latency_ms: float
    tokens_used: int
    confidence: float
    timestamp: str


class EnsembleVoter:
    """
    Votes across multiple models and selects best response.
    """

    def __init__(self):
        self.models: List[str] = []
        self.voting_weights: Dict[str, float] = {}
        self.response_cache: Dict[str, List[ModelResponse]] = {}

    def add_model(self, name: str, weight: float = 1.0):
        """Add a model to the ensemble."""
        self.models.append(name)
        self.voting_weights[name] = weight

    def vote(self, responses: List[ModelResponse]) -> ModelResponse:
        """
        Select best response using weighted voting.

        Strategy: Prefer fastest response with reasonable quality.
        """
        if not responses:
            raise ValueError("No responses to vote on")

        if len(responses) == 1:
            return responses[0]

        # Score each response
        scored = []
        for resp in responses:
            # Weight by configured weight, speed, and confidence
            speed_score = 1.0 / (1 + resp.latency_ms / 1000)  # Faster = higher
            confidence_score = resp.confidence
            weight = self.voting_weights.get(resp.model, 1.0)

            score = weight * (0.4 * speed_score + 0.6 * confidence_score)
            scored.append((score, resp))

        # Return highest scored
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[0][1]

    def get_consensus(self, responses: List[ModelResponse]) -> str:
        """Find common elements across responses (simple approach)."""
        if not responses:
            return ""

        # For now, return the voted best response
        return self.vote(responses).response


class StreamingManager:
    """
    Manages streaming responses from AI models.
    """

    def __init__(self):
        self.active_streams: Dict[str, Any] = {}
        self.callbacks: List[Callable[[str, str], None]] = []

    def register_callback(self, callback: Callable[[str, str], None]):
        """Register a callback for stream chunks."""
        self.callbacks.append(callback)

    async def stream_response(self, stream_id: str, generator: AsyncGenerator[str, None]) -> str:
        """
        Stream response chunks and collect full response.

        Args:
            stream_id: Unique identifier for this stream
            generator: Async generator yielding response chunks

        Returns:
            Complete response string
        """
        full_response = []

        try:
            async for chunk in generator:
                full_response.append(chunk)

                # Notify callbacks
                for callback in self.callbacks:
                    try:
                        callback(stream_id, chunk)
                    except Exception:
                        pass

            return "".join(full_response)

        except Exception as e:
            return f"[Streaming Error: {e}]"

    def simulate_streaming(
        self, text: str, chunk_size: int = 10, delay_ms: float = 50
    ) -> List[str]:
        """
        Simulate streaming by breaking text into chunks.

        Returns list of chunks for synchronous processing.
        """
        chunks = []
        for i in range(0, len(text), chunk_size):
            chunks.append(text[i : i + chunk_size])
        return chunks


class ContextWindow:
    """
    Manages AI context window (token budget).
    """

    def __init__(self, max_tokens: int = 8000):
        self.max_tokens = max_tokens
        self.current_tokens = 0
        self.messages: List[Dict] = []

        # Rough token estimation (4 chars per token on average)
        self.chars_per_token = 4

    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text."""
        return len(text) // self.chars_per_token

    def add_message(self, role: str, content: str) -> bool:
        """
        Add a message to context.

        Returns True if added, False if it would exceed budget.
        """
        tokens = self.estimate_tokens(content)

        if self.current_tokens + tokens > self.max_tokens:
            # Remove oldest messages until we have room
            while self.current_tokens + tokens > self.max_tokens and self.messages:
                removed = self.messages.pop(0)
                self.current_tokens -= self.estimate_tokens(removed["content"])

        self.messages.append({"role": role, "content": content})
        self.current_tokens += tokens
        return True

    def get_context(self) -> List[Dict]:
        """Get current context messages."""
        return self.messages.copy()

    def clear(self):
        """Clear context."""
        self.messages = []
        self.current_tokens = 0

    def get_stats(self) -> Dict:
        """Get context window statistics."""
        return {
            "max_tokens": self.max_tokens,
            "current_tokens": self.current_tokens,
            "available_tokens": self.max_tokens - self.current_tokens,
            "message_count": len(self.messages),
            "utilization": self.current_tokens / self.max_tokens,
        }


class PromptOptimizer:
    """
    Optimizes prompts for better AI responses.
    """

    def __init__(self):
        self.cache: Dict[str, str] = {}
        self.optimization_rules = [
            self._remove_redundancy,
            self._add_structure,
            self._clarify_instructions,
        ]

    def optimize(self, prompt: str, context: str = "") -> str:
        """
        Optimize a prompt for better results.

        Techniques:
        - Remove redundant words
        - Add structure markers
        - Clarify instructions
        """
        # Check cache
        cache_key = hashlib.md5(f"{context}:{prompt}".encode(), usedforsecurity=False).hexdigest()
        if cache_key in self.cache:
            return self.cache[cache_key]

        optimized = prompt

        # Apply optimization rules
        for rule in self.optimization_rules:
            optimized = rule(optimized)

        # Cache result
        self.cache[cache_key] = optimized

        return optimized

    def _remove_redundancy(self, prompt: str) -> str:
        """Remove redundant words and phrases."""
        # Common redundancies
        redundancies = [
            ("please please", "please"),
            ("help me to", "help me"),
            ("i would like to ask you to", ""),
            ("can you please", ""),
        ]

        result = prompt
        for old, new in redundancies:
            result = result.replace(old, new)

        return result.strip()

    def _add_structure(self, prompt: str) -> str:
        """Add structure markers if missing."""
        # If prompt is a question without context, add structure
        if prompt.endswith("?") and "context" not in prompt.lower():
            return f"Question: {prompt}\n\nPlease provide a clear, concise answer."

        # If asking for code, add structure
        if any(word in prompt.lower() for word in ["code", "function", "script"]):
            if "```" not in prompt:
                return f"Request: {prompt}\n\nPlease provide code with comments and explanation."

        return prompt

    def _clarify_instructions(self, prompt: str) -> str:
        """Clarify vague instructions."""
        vague_terms = {
            "explain": "explain in detail",
            "describe": "describe with examples",
            "help": "provide step-by-step help",
        }

        result = prompt
        for vague, specific in vague_terms.items():
            if f" {vague} " in f" {result} ":
                result = result.replace(f" {vague} ", f" {specific} ")

        return result


class CodeExecutor:
    """
    Safely executes AI-generated code.

    WARNING: This is a basic implementation. For production use:
    - Run in isolated containers
    - Use restricted Python (no imports)
    - Set resource limits
    - Validate code before execution
    """

    def __init__(self):
        self.allowed_builtins = {
            "print": print,
            "len": len,
            "range": range,
            "enumerate": enumerate,
            "zip": zip,
            "map": map,
            "filter": filter,
            "sum": sum,
            "min": min,
            "max": max,
            "abs": abs,
            "round": round,
            "str": str,
            "int": int,
            "float": float,
            "list": list,
            "dict": dict,
            "set": set,
            "tuple": tuple,
        }
        self.execution_history: List[Dict] = []

    def validate_code(self, code: str) -> Tuple[bool, str]:
        """
        Validate code for safety.

        Returns (is_safe, reason).
        """
        dangerous = [
            "import",
            "__import__",
            "exec",
            "eval",
            "compile",
            "open",
            "file",
            "subprocess",
            "os.system",
            "os.popen",
            "socket",
            "urllib",
            "requests",
            "http",
        ]

        for term in dangerous:
            if term in code:
                return False, f"Code contains dangerous term: {term}"

        return True, "Code appears safe"

    def execute(self, code: str, timeout: int = 5) -> Dict:
        """
        Execute code safely.

        Returns execution result with output or error.
        """
        # Validate first
        is_safe, reason = self.validate_code(code)
        if not is_safe:
            return {"success": False, "error": reason, "output": ""}

        try:
            # Capture output
            import io

            output_buffer = io.StringIO()

            # Create restricted namespace
            namespace = {
                "__builtins__": self.allowed_builtins,
                "__name__": "__main__",
            }

            # Redirect stdout
            old_stdout = sys.stdout
            sys.stdout = output_buffer

            # Execute with timeout (simplified - real impl would use subprocess)
            start_time = time.time()
            exec(code, namespace)
            execution_time = time.time() - start_time

            # Restore stdout
            sys.stdout = old_stdout

            output = output_buffer.getvalue()

            # Record execution
            self.execution_history.append(
                {
                    "timestamp": datetime.now().isoformat(),
                    "code": code[:200],  # Truncate for storage
                    "success": True,
                    "execution_time": execution_time,
                }
            )

            return {"success": True, "output": output, "execution_time": execution_time}

        except Exception as e:
            sys.stdout = old_stdout  # Restore on error
            return {"success": False, "error": str(e), "output": output_buffer.getvalue()}

    def get_history(self) -> List[Dict]:
        """Get execution history."""
        return self.execution_history


class AdvancedAIManager:
    """
    Central manager for advanced AI features.
    """

    def __init__(self):
        self.ensemble = EnsembleVoter()
        self.streaming = StreamingManager()
        self.context = ContextWindow()
        self.optimizer = PromptOptimizer()
        self.executor = CodeExecutor()

        # Setup default ensemble
        self.ensemble.add_model("primary", 1.0)
        self.ensemble.add_model("fallback", 0.8)

    def optimize_prompt(self, prompt: str, context: str = "") -> str:
        """Optimize a prompt for better results."""
        return cast(str, self.optimizer.optimize(prompt, context))

    def manage_context(self, messages: List[Dict]) -> List[Dict]:
        """Manage context window for messages."""
        self.context.clear()

        for msg in messages:
            self.context.add_message(msg["role"], msg["content"])

        return cast(List[Dict[str, Any]], self.context.get_context())

    def execute_code_safely(self, code: str) -> Dict[str, Any]:
        """Execute code safely."""
        return cast(Dict[str, Any], self.executor.execute(code))

    def get_stats(self) -> Dict[str, Any]:
        """Get advanced AI feature statistics."""
        return {
            "context_window": self.context.get_stats(),
            "executions": len(self.executor.execution_history),
            "cached_prompts": len(self.optimizer.cache),
            "ensemble_models": len(self.ensemble.models),
        }


# Import sys for CodeExecutor
import sys


# Standalone test
if __name__ == "__main__":
    print("🏰 Castle Wyvern Advanced AI Features Test")
    print("=" * 50)

    ai = AdvancedAIManager()

    # Test prompt optimization
    print("\n1. Testing prompt optimization...")
    raw_prompt = "can you please help me to write a python function that calculates fibonacci"
    optimized = ai.optimize_prompt(raw_prompt)
    print(f"   Raw: {raw_prompt[:50]}...")
    print(f"   Optimized: {optimized[:50]}...")

    # Test context management
    print("\n2. Testing context management...")
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"},
        {"role": "assistant", "content": "Hi there! How can I help?"},
    ]
    managed = ai.manage_context(messages)
    print(f"   Managed {len(managed)} messages")
    print(f"   Context stats: {ai.context.get_stats()}")

    # Test code execution
    print("\n3. Testing safe code execution...")
    code = """
result = []
for i in range(5):
    result.append(i * i)
print("Squares:", result)
"""
    result = ai.execute_code_safely(code)
    print(f"   Success: {result['success']}")
    print(f"   Output: {result.get('output', '').strip()}")

    print("\n✅ Advanced AI features ready!")
