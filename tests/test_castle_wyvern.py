"""
Test suite for Castle Wyvern
Phase 1 & 2 feature testing with mocked AI responses.
"""

import pytest
import json
import os
import sys
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from eyrie.phoenix_gate import PhoenixGate
from eyrie.intent_router import IntentRouter, IntentType, IntentMatch
from eyrie.error_handler import (
    CastleWyvernError, PhoenixGateError, ErrorSeverity,
    retry_on_error, CircuitBreaker
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def mock_env():
    """Mock environment variables for testing."""
    with patch.dict(os.environ, {
        'AI_API_KEY': 'test-api-key',
        'OPENAI_API_KEY': 'test-openai-key'
    }):
        yield


@pytest.fixture
def phoenix_gate(mock_env):
    """Create PhoenixGate instance with mocked config."""
    return PhoenixGate()


@pytest.fixture
def intent_router(mock_env):
    """Create IntentRouter instance with AI disabled for speed."""
    return IntentRouter(use_ai_classification=False)


@pytest.fixture
def mock_zai_response():
    """Sample Z.ai API response."""
    return {
        "choices": [{
            "message": {
                "content": "Test response from AI"
            }
        }],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 5,
            "total_tokens": 15
        }
    }


# ============================================================================
# Phoenix Gate Tests
# ============================================================================

class TestPhoenixGate:
    """Test suite for Phoenix Gate API gateway."""
    
    def test_initialization(self, phoenix_gate):
        """Test PhoenixGate initializes correctly."""
        assert phoenix_gate.api_key == "test-api-key"
        assert phoenix_gate.model == "glm-4-plus"
        assert phoenix_gate.zai_base_url == "https://open.bigmodel.cn/api/paas/v4"
    
    def test_empty_prompt_raises_error(self, phoenix_gate):
        """Test that empty prompts raise PhoenixGateError."""
        with pytest.raises(PhoenixGateError) as exc_info:
            phoenix_gate.call_ai("", "System message")
        
        assert "empty" in str(exc_info.value).lower()
        assert exc_info.value.severity == ErrorSeverity.LOW
    
    def test_whitespace_prompt_raises_error(self, phoenix_gate):
        """Test that whitespace-only prompts raise error."""
        with pytest.raises(PhoenixGateError):
            phoenix_gate.call_ai("   ", "System message")
    
    @patch('eyrie.phoenix_gate.requests.post')
    def test_successful_zai_call(self, mock_post, phoenix_gate, mock_zai_response):
        """Test successful Z.ai API call."""
        mock_post.return_value = Mock(
            status_code=200,
            json=lambda: mock_zai_response,
            raise_for_status=lambda: None
        )
        
        result = phoenix_gate._call_zai("Hello", "You are a test system.")
        
        assert result == "Test response from AI"
        mock_post.assert_called_once()
    
    @patch('eyrie.phoenix_gate.requests.post')
    def test_zai_401_error(self, mock_post, phoenix_gate):
        """Test handling of Z.ai authentication error."""
        mock_post.return_value = Mock(
            status_code=401,
            raise_for_status=lambda: (_ for _ in ()).throw(
                Exception("401 Client Error")
            )
        )
        
        with pytest.raises(PhoenixGateError) as exc_info:
            phoenix_gate._call_zai("Hello", "System")
        
        assert "authentication" in str(exc_info.value).lower()
    
    @patch('eyrie.phoenix_gate.requests.post')
    def test_invalid_response_structure(self, mock_post, phoenix_gate):
        """Test handling of invalid API response."""
        mock_post.return_value = Mock(
            status_code=200,
            json=lambda: {"invalid": "response"},
            raise_for_status=lambda: None
        )
        
        with pytest.raises(PhoenixGateError) as exc_info:
            phoenix_gate._call_zai("Hello", "System")
        
        assert "response" in str(exc_info.value).lower()
    
    @patch('eyrie.phoenix_gate.requests.post')
    def test_health_check_online(self, mock_post, phoenix_gate, mock_zai_response):
        """Test health check when service is online."""
        mock_post.return_value = Mock(
            status_code=200,
            json=lambda: mock_zai_response,
            raise_for_status=lambda: None
        )
        
        health = phoenix_gate.health_check()
        
        assert health["status"] in ["ONLINE", "DEGRADED"]
        assert "Z.ai" in [p["name"] for p in health["providers"]]
    
    def test_health_check_no_api_key(self):
        """Test health check without API key."""
        with patch.dict(os.environ, {}, clear=True):
            gate = PhoenixGate()
            gate.api_key = None
            
            health = gate.health_check()
            
            assert health["status"] == "ERROR"
            assert "api key" in health["message"].lower()


# ============================================================================
# Intent Router Tests
# ============================================================================

class TestIntentRouter:
    """Test suite for Intent Router."""
    
    def test_keyword_code_classification(self, intent_router):
        """Test keyword-based code intent detection."""
        match = intent_router.classify("Write a Python function to sort a list")
        
        assert match.intent == IntentType.CODE
        assert match.confidence > 0.2  # Keyword matching gives 0.3 base
        assert match.primary_agent == "lexington"
    
    def test_keyword_security_classification(self, intent_router):
        """Test keyword-based security intent detection."""
        match = intent_router.classify("Is this password hashing secure?")
        
        assert match.intent == IntentType.SECURITY
        assert match.primary_agent == "bronx"
    
    def test_keyword_document_classification(self, intent_router):
        """Test keyword-based document intent detection."""
        match = intent_router.classify("Summarize the key points of this article")
        
        assert match.intent == IntentType.DOCUMENT
        assert match.primary_agent == "broadway"
    
    def test_keyword_architecture_classification(self, intent_router):
        """Test keyword-based architecture intent detection."""
        match = intent_router.classify("How should I structure my microservices?")
        
        assert match.intent == IntentType.ARCHITECTURE
        assert match.primary_agent == "brooklyn"
    
    def test_question_mark_boost(self, intent_router):
        """Test that question marks boost QUESTION intent."""
        match = intent_router.classify("What is the capital of France?")
        
        # Should have higher confidence due to question mark
        assert match.confidence > 0.2
    
    def test_unknown_intent_fallback(self, intent_router):
        """Test that unknown inputs route to Goliath."""
        match = intent_router.classify("xyz abc 123")
        
        assert match.intent == IntentType.UNKNOWN
        assert match.primary_agent == "goliath"
    
    def test_fallback_agents_provided(self, intent_router):
        """Test that fallback agents are always provided."""
        match = intent_router.classify("Write some code")
        
        assert len(match.fallback_agents) >= 1
        assert isinstance(match.fallback_agents, list)
    
    def test_reasoning_provided(self, intent_router):
        """Test that reasoning is included in match."""
        match = intent_router.classify("Debug this error")
        
        assert match.reasoning is not None
        assert len(match.reasoning) > 0
    
    @patch.object(PhoenixGate, 'call_ai')
    def test_ai_classification(self, mock_call_ai, mock_env):
        """Test AI-based classification."""
        mock_call_ai.return_value = '{"intent": "CODE", "confidence": 0.95, "reasoning": "test"}'
        
        router = IntentRouter(use_ai_classification=True)
        match = router.classify("Complex coding task")
        
        # Should use AI result
        assert match.intent == IntentType.CODE


# ============================================================================
# Error Handler Tests
# ============================================================================

class TestErrorHandler:
    """Test suite for Error Handler."""
    
    def test_castle_wyvern_error_creation(self):
        """Test basic error creation."""
        error = CastleWyvernError("Test error", severity=ErrorSeverity.HIGH)
        
        assert str(error) == "Test error"
        assert error.severity == ErrorSeverity.HIGH
        assert error.timestamp is not None
    
    def test_error_details_storage(self):
        """Test that error details are stored."""
        details = {"key": "value", "count": 42}
        error = CastleWyvernError("Test", details=details)
        
        assert error.details == details
    
    def test_phoenix_gate_error_inheritance(self):
        """Test PhoenixGateError inherits from CastleWyvernError."""
        error = PhoenixGateError("API failed")
        
        assert isinstance(error, CastleWyvernError)
        assert error.severity == ErrorSeverity.MEDIUM  # Default


class TestCircuitBreaker:
    """Test suite for Circuit Breaker pattern."""
    
    def test_initial_state_closed(self):
        """Test circuit breaker starts closed."""
        cb = CircuitBreaker()
        
        assert cb.state == "CLOSED"
        assert cb.failure_count == 0
    
    def test_successful_call(self):
        """Test successful function call."""
        cb = CircuitBreaker()
        mock_func = Mock(return_value="success")
        
        result = cb.call(mock_func, "arg1", kwarg1="value")
        
        assert result == "success"
        assert cb.state == "CLOSED"
        mock_func.assert_called_once_with("arg1", kwarg1="value")
    
    def test_failure_tracking(self):
        """Test that failures are tracked."""
        cb = CircuitBreaker(failure_threshold=3)
        mock_func = Mock(side_effect=Exception("fail"))
        
        for _ in range(2):
            with pytest.raises(Exception):
                cb.call(mock_func)
        
        assert cb.failure_count == 2
        assert cb.state == "CLOSED"  # Not yet at threshold
    
    def test_circuit_opens_at_threshold(self):
        """Test circuit opens when failure threshold reached."""
        cb = CircuitBreaker(failure_threshold=2)
        mock_func = Mock(side_effect=Exception("fail"))
        
        # First two failures
        for _ in range(2):
            with pytest.raises(Exception):
                cb.call(mock_func)
        
        # Circuit should now be open
        assert cb.state == "OPEN"
        assert cb.failure_count == 2
    
    def test_open_circuit_blocks_calls(self):
        """Test that open circuit blocks new calls."""
        cb = CircuitBreaker(failure_threshold=1)
        mock_func = Mock(side_effect=Exception("fail"))
        
        # Trigger open
        with pytest.raises(Exception):
            cb.call(mock_func)
        
        # Next call should be blocked
        with pytest.raises(CastleWyvernError) as exc_info:
            cb.call(Mock())
        
        assert "circuit breaker is open" in str(exc_info.value).lower()
    
    def test_circuit_resets_on_success(self):
        """Test circuit resets after successful call."""
        cb = CircuitBreaker(failure_threshold=5)
        
        # Some failures
        for _ in range(3):
            with pytest.raises(Exception):
                cb.call(Mock(side_effect=Exception("fail")))
        
        # Success should reset
        cb.call(Mock(return_value="success"))
        
        assert cb.state == "CLOSED"
        assert cb.failure_count == 0


class TestRetryDecorator:
    """Test suite for retry decorator."""
    
    def test_successful_call_no_retry(self):
        """Test successful function is called once."""
        mock_func = Mock(return_value="success")
        
        @retry_on_error(max_retries=3)
        def test_func():
            return mock_func()
        
        result = test_func()
        
        assert result == "success"
        assert mock_func.call_count == 1
    
    def test_retry_on_failure(self):
        """Test function is retried on failure."""
        mock_func = Mock(side_effect=[Exception("fail"), "success"])
        
        @retry_on_error(max_retries=3, delay=0.01)
        def test_func():
            return mock_func()
        
        result = test_func()
        
        assert result == "success"
        assert mock_func.call_count == 2
    
    def test_max_retries_exhausted(self):
        """Test exception raised when max retries exhausted."""
        mock_func = Mock(side_effect=Exception("always fails"))
        
        @retry_on_error(max_retries=2, delay=0.01)
        def test_func():
            return mock_func()
        
        with pytest.raises(Exception):
            test_func()
        
        assert mock_func.call_count == 3  # Initial + 2 retries
    
    def test_specific_exception_filtering(self):
        """Test only specified exceptions trigger retry."""
        mock_func = Mock(side_effect=ValueError("fail"))
        
        @retry_on_error(max_retries=2, delay=0.01, exceptions=(ValueError,))
        def test_func():
            return mock_func()
        
        with pytest.raises(ValueError):
            test_func()


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Integration tests for component interaction."""
    
    @patch('eyrie.phoenix_gate.requests.post')
    def test_intent_router_to_phoenix_gate(self, mock_post, mock_env, mock_zai_response):
        """Test full flow: Intent Router → Phoenix Gate."""
        mock_post.return_value = Mock(
            status_code=200,
            json=lambda: mock_zai_response,
            raise_for_status=lambda: None
        )
        
        router = IntentRouter(use_ai_classification=False)
        match = router.classify("Write a Python function")
        
        # Should route to Lexington for code
        assert match.primary_agent == "lexington"
        
        # Simulate calling that agent (would use Phoenix Gate in real scenario)
        gate = PhoenixGate()
        # In real usage: response = gate.call_ai(user_input, agent_system_prompt)


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])