"""
llama.cpp Integration
Local LLM inference using llama.cpp (replacing Ollama dependency)
"""

import subprocess
import json
import os
from typing import Optional, Dict, Any, Iterator
from dataclasses import dataclass


@dataclass
class LlamaResponse:
    """Response from llama.cpp."""

    text: str
    tokens_generated: int
    generation_time: float


class LlamaCppClient:
    """
    Client for llama.cpp server.

    Features:
    - Connects to llama.cpp server (default: http://localhost:8080)
    - OpenAI-compatible API
    - Supports streaming
    - Model management
    - Better performance than Ollama
    """

    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self._check_connection()

    def _check_connection(self):
        """Check if llama.cpp server is running."""
        import urllib.request

        try:
            urllib.request.urlopen(f"{self.base_url}/health", timeout=2)
        except Exception:
            pass  # Will fail on first use if not running

    def is_available(self) -> bool:
        """Check if llama.cpp server is available."""
        import urllib.request

        try:
            urllib.request.urlopen(f"{self.base_url}/health", timeout=2)
            return True
        except Exception:
            return False

    def chat_completion(
        self,
        messages: list,
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        stream: bool = False,
    ) -> LlamaResponse:
        """
        Get chat completion from llama.cpp.

        Args:
            messages: List of message dicts with role and content
            model: Model name (optional)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            stream: Whether to stream response

        Returns:
            LlamaResponse with generated text
        """
        import urllib.request
        import time

        data = {
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream,
        }

        if model:
            data["model"] = model

        req = urllib.request.Request(
            f"{self.base_url}/v1/chat/completions",
            data=json.dumps(data).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        start_time = time.time()

        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                result = json.loads(response.read().decode())

                content = result["choices"][0]["message"]["content"]
                tokens = result.get("usage", {}).get("completion_tokens", 0)

                return LlamaResponse(
                    text=content, tokens_generated=tokens, generation_time=time.time() - start_time
                )
        except Exception as e:
            return LlamaResponse(text=f"Error: {str(e)}", tokens_generated=0, generation_time=0)

    def get_models(self) -> list:
        """Get list of available models."""
        import urllib.request

        try:
            with urllib.request.urlopen(f"{self.base_url}/v1/models", timeout=5) as response:
                result = json.loads(response.read().decode())
                return [m["id"] for m in result.get("data", [])]
        except Exception:
            return []

    @staticmethod
    def start_server(
        model_path: str, port: int = 8080, ctx_size: int = 4096, n_gpu_layers: int = 0
    ) -> subprocess.Popen:
        """
        Start llama.cpp server.

        Args:
            model_path: Path to GGUF model file
            port: Server port
            ctx_size: Context size
            n_gpu_layers: Number of layers to offload to GPU

        Returns:
            subprocess.Popen object
        """
        cmd = [
            "llama-server",
            "-m",
            model_path,
            "--port",
            str(port),
            "-c",
            str(ctx_size),
            "-ngl",
            str(n_gpu_layers),
        ]

        return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


# Compatibility layer with existing Ollama usage
class LocalLLM:
    """
    Unified interface for local LLMs.
    Tries llama.cpp first, falls back to Ollama.
    """

    def __init__(self):
        self.llama = LlamaCppClient()
        self.preferred = "llama.cpp" if self.llama.is_available() else "ollama"

    def chat(self, messages: list, **kwargs) -> str:
        """Chat with local LLM."""
        if self.preferred == "llama.cpp":
            response = self.llama.chat_completion(messages, **kwargs)
            return str(response.text)
        else:
            # Fall back to Ollama
            import requests

            response = requests.post(
                "http://localhost:11434/api/chat",
                json={
                    "model": kwargs.get("model", "llama2"),
                    "messages": messages,
                    "stream": False,
                },
            )
            return str(response.json()["message"]["content"])

    def status(self) -> dict:
        """Get status of local LLM."""
        return {
            "preferred_backend": self.preferred,
            "llama_cpp_available": self.llama.is_available(),
            "models": self.llama.get_models() if self.llama.is_available() else [],
        }


__all__ = ["LlamaCppClient", "LocalLLM", "LlamaResponse"]
