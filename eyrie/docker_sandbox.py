"""
Docker Sandbox for Safe Code Execution
Executes code in isolated Docker containers
"""

import subprocess
import tempfile
import os
import json
import time
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SandboxResult:
    """Result of sandboxed code execution."""

    success: bool
    stdout: str
    stderr: str
    exit_code: int
    execution_time: float
    container_id: Optional[str] = None
    error_message: Optional[str] = None


class DockerSandbox:
    """
    Docker-based sandbox for secure code execution.

    Features:
    - Isolated execution environment
    - Network isolation (optional)
    - Resource limits (CPU, memory)
    - Time limits
    - Auto-cleanup after execution
    - Multi-language support

    Safety Features:
    - Read-only root filesystem
    - No privileged mode
    - Drop all capabilities
    - Resource limits prevent DoS
    """

    # Docker images for different languages
    IMAGES = {
        "python": "python:3.11-slim",
        "javascript": "node:18-slim",
        "bash": "alpine:latest",
        "go": "golang:1.21-alpine",
        "rust": "rust:1.70-slim",
        "java": "openjdk:17-slim",
    }

    # File extensions
    EXTENSIONS = {
        "python": ".py",
        "javascript": ".js",
        "bash": ".sh",
        "go": ".go",
        "rust": ".rs",
        "java": ".java",
    }

    def __init__(self):
        self.enabled = self._check_docker()
        self.default_timeout = 30  # seconds
        self.default_memory = "256m"  # 256MB
        self.default_cpu = "1.0"  # 1 CPU core

    def _check_docker(self) -> bool:
        """Check if Docker is available."""
        try:
            result = subprocess.run(
                ["docker", "--version"], capture_output=True, text=True, timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def _pull_image(self, image: str) -> bool:
        """Pull Docker image if not present."""
        try:
            result = subprocess.run(
                ["docker", "pull", image], capture_output=True, text=True, timeout=60
            )
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            return False

    def _create_container(
        self,
        image: str,
        command: List[str],
        working_dir: str,
        memory: str,
        cpu: str,
        network: bool = False,
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Create a Docker container.

        Returns:
            Tuple of (container_id, error_message)
        """
        # Base docker run command
        docker_cmd = [
            "docker",
            "run",
            "--rm",  # Auto-remove after execution
            "--detach",  # Run in background initially
            f"--memory={memory}",
            f"--memory-swap={memory}",  # No swap
            f"--cpus={cpu}",
            "--read-only",  # Read-only root filesystem
            "--security-opt",
            "no-new-privileges:true",
            "--cap-drop",
            "ALL",  # Drop all capabilities
            "-v",
            f"{working_dir}:/workspace:rw",
            "-w",
            "/workspace",
        ]

        # Network isolation
        if not network:
            docker_cmd.append("--network=none")

        docker_cmd.extend([image] + command)

        try:
            result = subprocess.run(docker_cmd, capture_output=True, text=True, timeout=10)

            if result.returncode != 0:
                return None, f"Failed to create container: {result.stderr}"

            container_id = result.stdout.strip()
            return container_id, None

        except subprocess.TimeoutExpired:
            return None, "Timeout creating container"
        except Exception as e:
            return None, f"Error creating container: {str(e)}"

    def execute(
        self,
        code: str,
        language: str = "python",
        timeout: Optional[int] = None,
        memory: Optional[str] = None,
        cpu: Optional[str] = None,
        network: bool = False,
    ) -> SandboxResult:
        """
        Execute code in a Docker sandbox.

        Args:
            code: Code to execute
            language: Programming language (python, javascript, bash, go, rust, java)
            timeout: Execution timeout in seconds
            memory: Memory limit (e.g., "256m", "512m", "1g")
            cpu: CPU limit (e.g., "1.0", "0.5")
            network: Whether to allow network access

        Returns:
            SandboxResult with execution results
        """
        if not self.enabled:
            return SandboxResult(
                success=False,
                stdout="",
                stderr="",
                exit_code=-1,
                execution_time=0,
                error_message="Docker is not available. Install Docker to use sandbox execution.",
            )

        # Validate language
        if language not in self.IMAGES:
            return SandboxResult(
                success=False,
                stdout="",
                stderr="",
                exit_code=-1,
                execution_time=0,
                error_message=f"Unsupported language: {language}. Supported: {', '.join(self.IMAGES.keys())}",
            )

        # Use defaults if not specified
        timeout = timeout or self.default_timeout
        memory = memory or self.default_memory
        cpu = cpu or self.default_cpu

        image = self.IMAGES[language]
        extension = self.EXTENSIONS[language]

        # Pull image if needed
        if not self._pull_image(image):
            return SandboxResult(
                success=False,
                stdout="",
                stderr="",
                exit_code=-1,
                execution_time=0,
                error_message=f"Failed to pull Docker image: {image}",
            )

        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Write code to file
            code_file = os.path.join(temp_dir, f"main{extension}")
            with open(code_file, "w") as f:
                f.write(code)

            # Determine execution command
            command = self._get_execution_command(language, f"main{extension}")

            # Create and run container
            start_time = time.time()
            container_id, error = self._create_container(
                image=image,
                command=command,
                working_dir=temp_dir,
                memory=memory,
                cpu=cpu,
                network=network,
            )

            if error:
                return SandboxResult(
                    success=False,
                    stdout="",
                    stderr="",
                    exit_code=-1,
                    execution_time=0,
                    error_message=error,
                )

            # Wait for container with timeout
            try:
                result = subprocess.run(
                    ["docker", "wait", container_id],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                )

                exit_code = int(result.stdout.strip())

                # Get logs
                logs_result = subprocess.run(
                    ["docker", "logs", container_id], capture_output=True, text=True, timeout=10
                )

                stdout = logs_result.stdout
                stderr = logs_result.stderr

                # Remove container (should auto-remove, but just in case)
                subprocess.run(
                    ["docker", "rm", "-f", container_id], capture_output=True, timeout=10
                )

                execution_time = time.time() - start_time

                return SandboxResult(
                    success=exit_code == 0,
                    stdout=stdout,
                    stderr=stderr,
                    exit_code=exit_code,
                    execution_time=execution_time,
                    container_id=container_id,
                )

            except subprocess.TimeoutExpired:
                # Kill container on timeout
                subprocess.run(["docker", "kill", container_id], capture_output=True, timeout=5)

                return SandboxResult(
                    success=False,
                    stdout="",
                    stderr="",
                    exit_code=-1,
                    execution_time=timeout,
                    container_id=container_id,
                    error_message=f"Execution timed out after {timeout} seconds",
                )

    def _get_execution_command(self, language: str, filename: str) -> List[str]:
        """Get the command to execute code for a language."""
        commands = {
            "python": ["python", filename],
            "javascript": ["node", filename],
            "bash": ["sh", filename],
            "go": ["sh", "-c", f"go run {filename}"],
            "rust": ["sh", "-c", f"rustc {filename} -o main && ./main"],
            "java": ["sh", "-c", f"javac {filename} && java Main"],
        }
        return commands.get(language, ["sh", filename])

    def execute_python(self, code: str, **kwargs) -> SandboxResult:
        """Convenience method for Python execution."""
        return self.execute(code, language="python", **kwargs)

    def execute_javascript(self, code: str, **kwargs) -> SandboxResult:
        """Convenience method for JavaScript execution."""
        return self.execute(code, language="javascript", **kwargs)

    def get_status(self) -> Dict:
        """Get sandbox status."""
        return {
            "enabled": self.enabled,
            "docker_available": self.enabled,
            "supported_languages": list(self.IMAGES.keys()),
            "default_timeout": self.default_timeout,
            "default_memory": self.default_memory,
            "default_cpu": self.default_cpu,
        }

    def list_running_containers(self) -> List[Dict]:
        """List currently running sandbox containers."""
        if not self.enabled:
            return []

        try:
            result = subprocess.run(
                ["docker", "ps", "--format", "{{json .}}"],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode != 0:
                return []

            containers = []
            for line in result.stdout.strip().split("\n"):
                if line:
                    try:
                        container = json.loads(line)
                        # Only show our sandbox images
                        if any(img in container.get("Image", "") for img in self.IMAGES.values()):
                            containers.append(
                                {
                                    "id": container.get("ID", "")[:12],
                                    "image": container.get("Image", ""),
                                    "status": container.get("Status", ""),
                                    "created": container.get("CreatedAt", ""),
                                }
                            )
                    except json.JSONDecodeError:
                        continue

            return containers

        except Exception:
            return []

    def cleanup_all(self) -> int:
        """Clean up all sandbox containers. Returns count of removed containers."""
        if not self.enabled:
            return 0

        removed = 0
        for image in self.IMAGES.values():
            try:
                # Find containers using this image
                result = subprocess.run(
                    ["docker", "ps", "-aq", "--filter", f"ancestor={image}"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )

                if result.stdout.strip():
                    container_ids = result.stdout.strip().split("\n")
                    for cid in container_ids:
                        if cid:
                            subprocess.run(
                                ["docker", "rm", "-f", cid], capture_output=True, timeout=5
                            )
                            removed += 1

            except Exception:
                continue

        return removed


# Legacy wrapper for backward compatibility
class SafeCodeExecutor:
    """
    Wrapper that uses DockerSandbox when available, falls back to restricted local execution.
    """

    def __init__(self):
        self.sandbox = DockerSandbox()
        self.use_sandbox = self.sandbox.enabled

    def execute(self, code: str, language: str = "python", **kwargs) -> SandboxResult:
        """Execute code safely."""
        if self.use_sandbox:
            return self.sandbox.execute(code, language=language, **kwargs)
        else:
            # Fallback: Return error with instructions
            return SandboxResult(
                success=False,
                stdout="",
                stderr="",
                exit_code=-1,
                execution_time=0,
                error_message="""Docker sandbox not available.

To enable safe code execution:
1. Install Docker: https://docs.docker.com/get-docker/
2. Start Docker daemon
3. Restart Castle Wyvern

Without Docker, code execution is disabled for security.""",
            )

    def get_status(self) -> Dict:
        """Get execution status."""
        return {
            "mode": "docker_sandbox" if self.use_sandbox else "disabled",
            "docker_available": self.sandbox.enabled,
            "message": (
                "Safe execution enabled"
                if self.use_sandbox
                else "Install Docker to enable safe execution"
            ),
        }


# Standalone test
if __name__ == "__main__":
    sandbox = DockerSandbox()

    print("Docker Sandbox Status:")
    print(json.dumps(sandbox.get_status(), indent=2))

    if sandbox.enabled:
        print("\nTesting Python execution:")
        result = sandbox.execute_python("print('Hello from Docker!')")
        print(f"Success: {result.success}")
        print(f"Output: {result.stdout}")
        print(f"Time: {result.execution_time:.2f}s")

        print("\nTesting with error:")
        result = sandbox.execute_python("print(1/0)")
        print(f"Success: {result.success}")
        print(f"Error: {result.stderr[:100] if result.stderr else 'None'}")
