"""
Phoenix Gate - Enhanced AI API Gateway
With robust error handling, retry logic, and circuit breakers.
"""

import os
import requests
import logging
from typing import Optional, Dict, Any
from dotenv import load_dotenv

from eyrie.error_handler import (
    PhoenixGateError, ErrorSeverity,
    retry_on_error, validate_input,
    zai_circuit_breaker, openai_circuit_breaker
)

# Configure logger
logger = logging.getLogger(__name__)

load_dotenv()


class PhoenixGate:
    """
    The Phoenix Gate - AI API Gateway for Castle Wyvern.
    
    Routes requests to appropriate AI providers with:
    - Automatic retry with exponential backoff
    - Circuit breaker pattern for resilience
    - Comprehensive error handling
    - Fallback chain: Z.ai → OpenAI → Local
    """
    
    def __init__(self):
        # Z.ai/GLM API Configuration
        self.api_key = os.getenv("AI_API_KEY")
        self.zai_base_url = "https://open.bigmodel.cn/api/paas/v4"
        self.model = "glm-4-plus"
        
        # Fallback configurations
        self.local_url = "http://localhost:11434/api/generate"
        self.openai_url = "https://api.openai.com/v1/chat/completions"
        
        # Request defaults
        self.default_timeout = 60
        self.max_tokens = 2000
        self.temperature = 0.7
        
        logger.info("Phoenix Gate initialized")

    def call_ai(self, prompt: str, system_message: str, mode: str = "cloud") -> str:
        """
        Sends a request through the Gate to the chosen AI provider.
        
        Args:
            prompt: The user prompt
            system_message: System context/instructions
            mode: 'cloud' (default), 'local', or 'openai'
            
        Returns:
            AI response text
            
        Raises:
            PhoenixGateError: If all providers fail
        """
        if not prompt or not prompt.strip():
            raise PhoenixGateError(
                "Prompt cannot be empty",
                severity=ErrorSeverity.LOW
            )
        
        if mode == "cloud":
            return self._call_with_fallback(prompt, system_message)
        elif mode == "local":
            return self._call_local(prompt, system_message)
        elif mode == "openai":
            return self._call_openai(prompt, system_message)
        else:
            raise PhoenixGateError(
                f"Unknown mode: {mode}",
                severity=ErrorSeverity.MEDIUM,
                details={'valid_modes': ['cloud', 'local', 'openai']}
            )

    def _call_with_fallback(self, prompt: str, system_message: str) -> str:
        """Try Z.ai first, fall back to OpenAI, then local."""
        errors = []
        
        # Try Z.ai (primary)
        try:
            logger.info("Attempting Z.ai API call...")
            return self._call_zai(prompt, system_message)
        except Exception as e:
            logger.warning(f"Z.ai failed: {e}")
            errors.append(f"Z.ai: {e}")
        
        # Try OpenAI (fallback)
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            try:
                logger.info("Falling back to OpenAI...")
                return self._call_openai(prompt, system_message)
            except Exception as e:
                logger.warning(f"OpenAI fallback failed: {e}")
                errors.append(f"OpenAI: {e}")
        else:
            logger.info("OpenAI fallback skipped (no API key)")
        
        # Try local (last resort)
        try:
            logger.info("Falling back to local AI...")
            return self._call_local(prompt, system_message)
        except Exception as e:
            logger.warning(f"Local AI failed: {e}")
            errors.append(f"Local: {e}")
        
        # All failed
        raise PhoenixGateError(
            "All AI providers failed",
            severity=ErrorSeverity.CRITICAL,
            details={'errors': errors}
        )

    @retry_on_error(max_retries=3, delay=1.0, 
                    exceptions=(requests.exceptions.RequestException,))
    def _call_zai(self, prompt: str, system_message: str) -> str:
        """Calls Z.ai API (GLM models) with retry and circuit breaker."""
        if not self.api_key:
            raise PhoenixGateError(
                "No Z.ai API Key found. Set AI_API_KEY in .env",
                severity=ErrorSeverity.HIGH
            )
        
        return zai_circuit_breaker.call(
            self._execute_zai_call, prompt, system_message
        )

    def _execute_zai_call(self, prompt: str, system_message: str) -> str:
        """Execute the actual Z.ai API call."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
        
        logger.debug(f"Z.ai request: model={self.model}, tokens={self.max_tokens}")
        
        response = requests.post(
            f"{self.zai_base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=self.default_timeout
        )
        
        # Handle HTTP errors
        if response.status_code == 401:
            raise PhoenixGateError(
                "Z.ai authentication failed - check API key",
                severity=ErrorSeverity.CRITICAL
            )
        elif response.status_code == 429:
            raise PhoenixGateError(
                "Z.ai rate limit exceeded - please wait",
                severity=ErrorSeverity.HIGH
            )
        elif response.status_code >= 500:
            raise PhoenixGateError(
                f"Z.ai server error: {response.status_code}",
                severity=ErrorSeverity.HIGH
            )
        
        response.raise_for_status()
        data = response.json()
        
        # Validate response structure
        if "choices" not in data or not data["choices"]:
            raise PhoenixGateError(
                "Invalid response structure from Z.ai",
                severity=ErrorSeverity.HIGH,
                details={'response_keys': list(data.keys())}
            )
        
        content = data["choices"][0].get("message", {}).get("content")
        if not content:
            raise PhoenixGateError(
                "Empty response content from Z.ai",
                severity=ErrorSeverity.MEDIUM
            )
        
        # Log usage info if available
        if "usage" in data:
            usage = data["usage"]
            logger.info(f"Z.ai usage: {usage.get('prompt_tokens', 0)} in, "
                       f"{usage.get('completion_tokens', 0)} out, "
                       f"{usage.get('total_tokens', 0)} total")
        
        return content

    @retry_on_error(max_retries=2, delay=1.0,
                    exceptions=(requests.exceptions.RequestException,))
    def _call_openai(self, prompt: str, system_message: str) -> str:
        """Calls OpenAI API with retry and circuit breaker."""
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            raise PhoenixGateError(
                "No OpenAI API Key found for fallback",
                severity=ErrorSeverity.HIGH
            )
        
        return openai_circuit_breaker.call(
            self._execute_openai_call, prompt, system_message, openai_key
        )

    def _execute_openai_call(self, prompt: str, system_message: str, api_key: str) -> str:
        """Execute the actual OpenAI API call."""
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
        
        logger.debug("OpenAI fallback request")
        
        response = requests.post(
            self.openai_url,
            headers=headers,
            json=payload,
            timeout=self.default_timeout
        )
        response.raise_for_status()
        data = response.json()
        
        return data["choices"][0]["message"]["content"]

    def _call_local(self, prompt: str, system_message: str) -> str:
        """Standard logic for local inference engines (Ollama)."""
        payload = {
            "model": "llama3",
            "prompt": f"{system_message}\n\nUser: {prompt}",
            "stream": False
        }
        
        logger.debug("Local AI request")
        
        try:
            response = requests.post(
                self.local_url,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            
            content = result.get("response")
            if not content:
                raise PhoenixGateError(
                    "Local AI returned empty response",
                    severity=ErrorSeverity.MEDIUM
                )
            
            return content
        except requests.exceptions.ConnectionError:
            raise PhoenixGateError(
                "Local AI (Ollama) not running. Start with: ollama run llama3",
                severity=ErrorSeverity.HIGH
            )

    def health_check(self) -> Dict[str, Any]:
        """Check if the Phoenix Gate is operational."""
        if not self.api_key:
            return {
                "status": "ERROR", 
                "message": "No API key configured",
                "providers": []
            }
        
        providers = []
        
        # Test Z.ai
        try:
            test_response = self._call_zai("Test", "You are a test system.")
            if "error" not in test_response.lower():
                providers.append({"name": "Z.ai", "status": "ONLINE"})
            else:
                providers.append({"name": "Z.ai", "status": "ERROR", "message": test_response})
        except Exception as e:
            providers.append({"name": "Z.ai", "status": "ERROR", "message": str(e)})
        
        # Check OpenAI (without making call)
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            providers.append({"name": "OpenAI", "status": "AVAILABLE"})
        else:
            providers.append({"name": "OpenAI", "status": "NOT_CONFIGURED"})
        
        # Check local (without making call)
        try:
            requests.get(self.local_url.replace('/generate', '/tags'), timeout=2)
            providers.append({"name": "Local (Ollama)", "status": "ONLINE"})
        except Exception:
            providers.append({"name": "Local (Ollama)", "status": "OFFLINE"})
        
        # Overall status
        online_count = sum(1 for p in providers if p["status"] in ["ONLINE", "AVAILABLE"])
        
        if online_count == 0:
            status = "ERROR"
            message = "No AI providers available"
        elif online_count == 1:
            status = "DEGRADED"
            message = "Limited AI providers available"
        else:
            status = "ONLINE"
            message = "Phoenix Gate operational"
        
        return {
            "status": status,
            "message": message,
            "model": self.model,
            "providers": providers
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get current circuit breaker stats."""
        return {
            "zai_circuit_breaker": {
                "state": zai_circuit_breaker.state,
                "failure_count": zai_circuit_breaker.failure_count
            },
            "openai_circuit_breaker": {
                "state": openai_circuit_breaker.state,
                "failure_count": openai_circuit_breaker.failure_count
            }
        }


if __name__ == "__main__":
    # Test the gate
    print("🏰 Testing Phoenix Gate...")
    print("=" * 50)
    
    gate = PhoenixGate()
    
    # Health check
    health = gate.health_check()
    print(f"\nStatus: {health['status']}")
    print(f"Message: {health['message']}")
    print(f"Model: {health.get('model', 'N/A')}")
    print("\nProviders:")
    for provider in health['providers']:
        print(f"  • {provider['name']}: {provider['status']}")
    
    # Test call if online
    if health['status'] in ["ONLINE", "DEGRADED"]:
        print("\n" + "=" * 50)
        print("Test call to Goliath:")
        print("-" * 50)
        try:
            response = gate.call_ai(
                "Hello from Castle Wyvern! Report your status.",
                "You are Goliath, leader of the Manhattan Clan. Be brief and commanding.",
                mode="cloud"
            )
            print(response)
        except Exception as e:
            print(f"Error: {e}")
    
    # Show stats
    print("\n" + "=" * 50)
    print("Circuit Breaker Stats:")
    stats = gate.get_stats()
    for name, data in stats.items():
        print(f"  {name}: {data['state']} (failures: {data['failure_count']})")