"""
Truth Enforcement Wrapper for Boss Interactions
FORCES verification before any response to Boss.

Usage:
    from truth_enforcement_wrapper import verify_before_responding
    
    @verify_before_responding
    def respond_to_boss(message):
        # This will be BLOCKED if unverified claims detected
        return generate_response(message)
"""

import sys
import json
sys.path.insert(0, '/Users/snack/castle-wyvern')

from eyrie.truth_enforcement_mcp import TruthEnforcementServer


class TruthEnforcer:
    """
    Hard enforcement wrapper.
    
    When enabled (which it always is for Boss), this:
    1. Intercepts all responses
    2. Analyzes for claims
    3. REQUIRES verification commands be run
    4. Blocks response if unverified claims found
    5. Only allows response through with verification table
    """
    
    def __init__(self):
        self.server = TruthEnforcementServer()
        self.enabled = True  # ALWAYS ON for Boss
        self.boss_mode = True  # Extra strict
        
    def enforce(self, response: str, context: str = "") -> dict:
        """
        Enforce truth on a response.
        
        Returns dict with:
        - allowed: bool (can this response be sent?)
        - response: str (modified response with verification)
        - blocked_reason: str (why it was blocked)
        - verification_required: list (commands to run)
        """
        if not self.enabled:
            return {
                "allowed": True,
                "response": response,
                "warning": "TRUTH ENFORCEMENT IS OFF"
            }
        
        # Analyze the response
        result = self.server.enforce_verification(response)
        
        if not result["can_proceed"]:
            # BLOCKED - cannot send this response
            return {
                "allowed": False,
                "response": None,
                "blocked_reason": result["reason"],
                "verification_required": result.get("required_verifications", []),
                "message": "\n".join([
                    "=" * 60,
                    "🚫 RESPONSE BLOCKED BY TRUTH ENFORCEMENT",
                    "=" * 60,
                    f"Reason: {result['reason']}",
                    "",
                    "You must verify before responding to Boss:",
                    ""
                ] + [
                    f"  {i+1}. Claim: {v['claim'][:40]}...\n     Command: {v['command']}\n     Run this and include output in response"
                    for i, v in enumerate(result.get("required_verifications", []))
                ] + [
                    "",
                    "=" * 60,
                    "Your streak has been reset to 0.",
                    "Target: 21 consecutive verified responses.",
                    "=" * 60
                ]),
                "streak": 0
            }
        
        # ALLOWED - can proceed
        # Prepend verification table to response
        if result.get("verification_table"):
            verified_response = result["verification_table"] + "\n" + response
        else:
            verified_response = response
        
        return {
            "allowed": True,
            "response": verified_response,
            "streak": result.get("streak", 0),
            "target": result.get("target", 21)
        }


# Global enforcer instance
enforcer = TruthEnforcer()


def verify_before_responding(response: str) -> str:
    """
    Main entry point: Use this before EVERY response to Boss.
    
    Example:
        raw_response = "The repo has 78 commits."
        final_response = verify_before_responding(raw_response)
        # If unverified: raises exception with instructions
        # If verified: returns response with verification table
    """
    result = enforcer.enforce(response)
    
    if not result["allowed"]:
        # Print the block message
        print(result["message"], file=sys.stderr)
        # Return the block message as the response
        # (so it's clear what went wrong)
        raise ValueError(result["message"])
    
    return result["response"]


def check_response(response: str) -> dict:
    """
    Check if a response would be allowed.
    
    Use this to preview if verification is needed.
    
    Returns:
        {
            "allowed": bool,
            "claims_found": list,
            "commands_needed": list
        }
    """
    result = enforcer.enforce(response)
    return {
        "allowed": result["allowed"],
        "claims_found": result.get("verification_required", []),
        "streak": result.get("streak", 0)
    }


def get_streak() -> dict:
    """Get current verification streak."""
    return enforcer.server.get_streak()


def force_verify_claim(claim: str) -> dict:
    """
    Force verification of a specific claim.
    
    Returns verification result.
    """
    record = enforcer.server.verify_claim(claim)
    return {
        "claim": record.claim,
        "command": record.command,
        "output": record.output,
        "verified": record.verified
    }


if __name__ == "__main__":
    # Test mode
    if len(sys.argv) > 1:
        test_response = sys.argv[1]
        
        print("Testing truth enforcement...")
        print(f"Response: {test_response}")
        print("-" * 60)
        
        try:
            result = verify_before_responding(test_response)
            print("✅ RESPONSE ALLOWED")
            print("-" * 60)
            print(result)
        except ValueError as e:
            print("❌ RESPONSE BLOCKED")
            print("-" * 60)
            print(str(e))
