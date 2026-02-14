"""
Castle Wyvern - Intent Router
Analyzes user input and routes to the appropriate clan member.
"""

import os
import json
import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import logging

# Add parent directory to path for imports
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eyrie.phoenix_gate import PhoenixGate

logger = logging.getLogger(__name__)


class IntentType(Enum):
    """Types of user intents for routing."""
    CODE = "code"                    # Write/fix/debug code
    ARCHITECTURE = "architecture"    # Design systems, plan structure
    DOCUMENT = "document"            # Summarize, explain, write docs
    ANALYZE = "analyze"              # Review code, find issues
    SECURITY = "security"            # Security audit, vulnerabilities
    PLAN = "plan"                    # Project planning, roadmaps
    CREATIVE = "creative"            # Stories, creative writing
    QUESTION = "question"            # General knowledge questions
    CHAT = "chat"                    # Casual conversation
    UNKNOWN = "unknown"              # Could not determine


@dataclass
class IntentMatch:
    """Result of intent analysis."""
    intent: IntentType
    confidence: float  # 0.0 to 1.0
    primary_agent: str
    fallback_agents: List[str]
    reasoning: str


class IntentRouter:
    """
    Routes user requests to the appropriate clan member based on intent.
    
    Uses hybrid approach:
    1. Keyword-based classification (fast, deterministic)
    2. AI-based classification (accurate for complex queries)
    """
    
    # Intent patterns for keyword matching
    INTENT_PATTERNS = {
        IntentType.CODE: [
            r'\b(code|function|class|script|program|implement|write\s+(python|js|java|rust|go|cpp?)|debug|fix\s+bug|refactor|optimize|algorithm|api|endpoint|database|sql)\b',
            r'\b(create|build|make)\s+(a|an)?\s*(function|script|app|bot|tool)\b',
        ],
        IntentType.ARCHITECTURE: [
            r'\b(architecture|design|structure|system|framework|pattern|microservice|api\s+design|database\s+schema|data\s+model)\b',
            r'\b(how\s+should\s+I\s+structure|best\s+way\s+to\s+organize)\b',
        ],
        IntentType.DOCUMENT: [
            r'\b(summarize|summary|explain|document|readme|guide|tutorial|docstring|comment|description|what\s+is|how\s+does)\b',
            r'\b(write|create)\s+(docs?|documentation|readme|guide)\b',
        ],
        IntentType.ANALYZE: [
            r'\b(review|analyze|check|evaluate|assess|critique|improve|better|optimize|performance)\b',
            r'\b(what\s+do\s+you\s+think|feedback|thoughts|opinion)\b',
        ],
        IntentType.SECURITY: [
            r'\b(security|vulnerability|exploit|hack|protect|encrypt|auth|password|token|injection|xss|csrf|sanitize|validate)\b',
            r'\b(is\s+this\s+secure|security\s+review|audit)\b',
        ],
        IntentType.PLAN: [
            r'\b(plan|roadmap|milestone|schedule|timeline|sprint|backlog|priority|organize)\b',
            r'\b(how\s+to\s+approach|what\s+steps|break\s+down)\b',
        ],
        IntentType.CREATIVE: [
            r'\b(story|poem|creative|write\s+(a|an)\s+(story|poem|script|dialogue)|character|plot|scene|imagine)\b',
        ],
    }
    
    # Agent routing map
    AGENT_ROUTING = {
        IntentType.CODE: {
            'primary': 'lexington',
            'fallback': ['brooklyn', 'goliath'],
            'reason': 'Lexington is the technician - code is his domain'
        },
        IntentType.ARCHITECTURE: {
            'primary': 'brooklyn',
            'fallback': ['goliath', 'lexington'],
            'reason': 'Brooklyn is the strategist - he designs systems'
        },
        IntentType.DOCUMENT: {
            'primary': 'broadway',
            'fallback': ['hudson', 'goliath'],
            'reason': 'Broadway is the chronicler - he writes and explains'
        },
        IntentType.ANALYZE: {
            'primary': 'xanatos',
            'fallback': ['demona', 'goliath'],
            'reason': 'Xanatos is the red team - he critiques and finds issues'
        },
        IntentType.SECURITY: {
            'primary': 'bronx',
            'fallback': ['xanatos', 'demona'],
            'reason': 'Bronx is the watchdog - security is his watch'
        },
        IntentType.PLAN: {
            'primary': 'brooklyn',
            'fallback': ['goliath', 'elisa'],
            'reason': 'Brooklyn excels at strategy and multi-path planning'
        },
        IntentType.CREATIVE: {
            'primary': 'broadway',
            'fallback': ['hudson', 'elisa'],
            'reason': 'Broadway has the soul of a storyteller'
        },
        IntentType.QUESTION: {
            'primary': 'hudson',
            'fallback': ['goliath', 'broadway'],
            'reason': 'Hudson is the archivist - he has the knowledge'
        },
        IntentType.CHAT: {
            'primary': 'goliath',
            'fallback': ['elisa', 'broadway'],
            'reason': 'Goliath leads - he handles general conversation'
        },
        IntentType.UNKNOWN: {
            'primary': 'goliath',
            'fallback': ['brooklyn', 'lexington'],
            'reason': 'When uncertain, defer to the leader'
        }
    }
    
    def __init__(self, use_ai_classification: bool = True):
        self.use_ai = use_ai_classification
        self.phoenix_gate = PhoenixGate()
        self._compile_patterns()
        
    def _compile_patterns(self):
        """Compile regex patterns for performance."""
        self.compiled_patterns = {}
        for intent, patterns in self.INTENT_PATTERNS.items():
            self.compiled_patterns[intent] = [
                re.compile(p, re.IGNORECASE | re.VERBOSE) 
                for p in patterns
            ]
    
    def classify(self, user_input: str, context: Optional[str] = None) -> IntentMatch:
        """
        Classify user intent and return routing decision.
        
        Args:
            user_input: The user's message
            context: Optional conversation context
            
        Returns:
            IntentMatch with routing information
        """
        # Try keyword matching first (fast)
        keyword_intent, keyword_confidence = self._keyword_classify(user_input)
        
        # If high confidence from keywords, use it
        if keyword_confidence >= 0.8:
            logger.info(f"Keyword classification: {keyword_intent.value} ({keyword_confidence:.2f})")
            return self._create_match(keyword_intent, keyword_confidence, "keyword")
        
        # If AI classification enabled, get second opinion
        if self.use_ai:
            try:
                ai_intent, ai_confidence = self._ai_classify(user_input, context)
                
                # Combine results (weighted toward AI for borderline cases)
                if ai_confidence > keyword_confidence:
                    final_intent = ai_intent
                    final_confidence = ai_confidence
                    method = "ai"
                else:
                    final_intent = keyword_intent
                    final_confidence = max(keyword_confidence, ai_confidence * 0.9)
                    method = "hybrid"
                    
                logger.info(f"{method.capitalize()} classification: {final_intent.value} ({final_confidence:.2f})")
                return self._create_match(final_intent, final_confidence, method)
                
            except Exception as e:
                logger.warning(f"AI classification failed: {e}. Falling back to keywords.")
                return self._create_match(keyword_intent, keyword_confidence, "keyword_fallback")
        
        # No AI, use keywords
        return self._create_match(keyword_intent, keyword_confidence, "keyword")
    
    def _keyword_classify(self, user_input: str) -> Tuple[IntentType, float]:
        """Classify based on keyword patterns."""
        scores = {intent: 0 for intent in IntentType}
        user_lower = user_input.lower()
        
        for intent, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                matches = len(pattern.findall(user_input))
                scores[intent] += matches * 0.3  # Each match adds 0.3
        
        # Boost for question marks (questions)
        if '?' in user_input:
            scores[IntentType.QUESTION] += 0.2
            scores[IntentType.CHAT] += 0.1
        
        # Find highest scoring intent
        best_intent = max(scores, key=scores.get)
        best_score = scores[best_intent]
        
        # Normalize confidence
        confidence = min(best_score, 1.0) if best_score > 0 else 0.3
        
        # If no clear match, return UNKNOWN
        if best_score == 0:
            return IntentType.UNKNOWN, 0.3
            
        return best_intent, confidence
    
    def _ai_classify(self, user_input: str, context: Optional[str]) -> Tuple[IntentType, float]:
        """Use AI to classify intent (more accurate for complex queries)."""
        
        system_prompt = """You are an intent classification system for Castle Wyvern, a multi-agent AI infrastructure.

Classify the user's input into ONE of these categories:
- CODE: Writing, fixing, or debugging code
- ARCHITECTURE: System design, structure, patterns
- DOCUMENT: Summarize, explain, write documentation
- ANALYZE: Review, critique, find issues
- SECURITY: Security audit, vulnerabilities, protection
- PLAN: Project planning, roadmaps, organization
- CREATIVE: Stories, creative writing
- QUESTION: General knowledge questions
- CHAT: Casual conversation

Respond with ONLY a JSON object in this format:
{"intent": "CATEGORY", "confidence": 0.95, "reasoning": "brief explanation"}

Confidence should be 0.0 to 1.0 based on how certain you are."""

        try:
            response = self.phoenix_gate.call_ai(
                f"Classify this user input: \"{user_input}\"",
                system_prompt,
                mode="cloud"
            )
            
            # Parse JSON response
            # Handle potential markdown code blocks
            json_str = response
            if '```json' in response:
                json_str = response.split('```json')[1].split('```')[0]
            elif '```' in response:
                json_str = response.split('```')[1].split('```')[0]
            
            result = json.loads(json_str.strip())
            
            intent_str = result.get('intent', 'UNKNOWN').upper()
            confidence = float(result.get('confidence', 0.5))
            
            # Map string to enum
            intent_map = {i.name: i for i in IntentType}
            intent = intent_map.get(intent_str, IntentType.UNKNOWN)
            
            return intent, confidence
            
        except json.JSONDecodeError:
            logger.warning(f"Could not parse AI classification response: {response}")
            return IntentType.UNKNOWN, 0.3
        except Exception as e:
            logger.error(f"AI classification error: {e}")
            return IntentType.UNKNOWN, 0.3
    
    def _create_match(self, intent: IntentType, confidence: float, method: str) -> IntentMatch:
        """Create IntentMatch from intent and confidence."""
        routing = self.AGENT_ROUTING.get(intent, self.AGENT_ROUTING[IntentType.UNKNOWN])
        
        return IntentMatch(
            intent=intent,
            confidence=confidence,
            primary_agent=routing['primary'],
            fallback_agents=routing['fallback'],
            reasoning=f"{routing['reason']} (detected via {method})"
        )
    
    def get_agent_for_task(self, user_input: str, context: Optional[str] = None) -> IntentMatch:
        """Convenience method to get the right agent for a task."""
        return self.classify(user_input, context)


# Simple command-line test
if __name__ == "__main__":
    print("🏰 Castle Wyvern - Intent Router Test")
    print("=" * 50)
    
    router = IntentRouter(use_ai_classification=True)
    
    test_inputs = [
        "Write a Python function to reverse a string",
        "Summarize the key points of machine learning",
        "Review this code and find bugs",
        "Is this authentication secure?",
        "How should I structure my React app?",
        "What's the weather like today?",
        "Write a story about a gargoyle",
        "Create a project roadmap for the next 3 months",
    ]
    
    for user_input in test_inputs:
        print(f"\n👤 User: \"{user_input}\"")
        match = router.classify(user_input)
        print(f"🎯 Intent: {match.intent.value} ({match.confidence:.0%} confidence)")
        print(f"🛡️  Primary Agent: {match.primary_agent}")
        print(f"📋 Reasoning: {match.reasoning}")
        print("-" * 50)