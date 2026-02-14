import os
import requests
from dotenv import load_dotenv

load_dotenv()

class PhoenixGate:
    def __init__(self):
        # Z.ai/GLM API Configuration
        self.api_key = os.getenv("AI_API_KEY") or "4aedc0c3084f49c0b46679e6f27866c5.SpBz23Mne0vFednl"
        self.zai_base_url = "https://open.bigmodel.cn/api/paas/v4"  # Correct GLM endpoint
        self.model = "glm-4-plus"  # GLM-4 Plus model
        
        # Fallback configurations
        self.local_url = "http://localhost:11434/api/generate"  # Ollama local
        self.openai_url = "https://api.openai.com/v1/chat/completions"

    def call_ai(self, prompt, system_message, mode="cloud"):
        """Sends a request through the Gate to the chosen AI provider."""
        
        # Z.ai is the primary provider
        return self._call_zai(prompt, system_message)

    def _call_zai(self, prompt, system_message):
        """Calls Z.ai API (GLM models)."""
        if not self.api_key:
            return "Error: No Z.ai API Key found. Set AI_API_KEY in .env"
        
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
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        try:
            response = requests.post(
                f"{self.zai_base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except requests.exceptions.RequestException as e:
            return f"Phoenix Gate error (Z.ai): {str(e)}"
        except KeyError as e:
            return f"Phoenix Gate response error: {str(e)}"
        except Exception as e:
            return f"Phoenix Gate unexpected error: {str(e)}"

    def _call_local(self, prompt, system_message):
        """Standard logic for local inference engines (Ollama)."""
        payload = {
            "model": "llama3",
            "prompt": f"{system_message}\n\nUser: {prompt}",
            "stream": False
        }
        try:
            response = requests.post(
                self.local_url,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json().get("response", "Local AI returned empty response")
        except Exception as e:
            return f"Phoenix Gate local error: {str(e)}"

    def _call_openai(self, prompt, system_message):
        """Fallback to OpenAI if Z.ai fails."""
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            return "Error: No OpenAI API Key found for fallback"
        
        headers = {
            "Authorization": f"Bearer {openai_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ]
        }
        
        try:
            response = requests.post(
                self.openai_url,
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Phoenix Gate OpenAI fallback error: {str(e)}"

    def health_check(self):
        """Check if the Phoenix Gate is operational."""
        if not self.api_key:
            return {"status": "ERROR", "message": "No API key configured"}
        
        try:
            # Quick test call
            test_response = self._call_zai("Test", "You are a test system.")
            if "error" in test_response.lower():
                return {"status": "ERROR", "message": test_response}
            return {"status": "ONLINE", "message": "Phoenix Gate operational", "model": self.model}
        except Exception as e:
            return {"status": "ERROR", "message": str(e)}

if __name__ == "__main__":
    # Test the gate
    gate = PhoenixGate()
    print("Testing Phoenix Gate connectivity...")
    health = gate.health_check()
    print(f"Status: {health['status']}")
    print(f"Message: {health['message']}")
    if health['status'] == "ONLINE":
        print("\nTest call:")
        print(gate.call_ai("Hello from Castle Wyvern!", "You are Goliath, leader of the Manhattan Clan.", mode="cloud"))