"""
Truth Enforcement MCP Server
Prevents lying by enforcing verification before any claim.

This MCP server acts as a mandatory gatekeeper. When enabled:
1. All responses are analyzed for factual claims
2. Commands must be run to verify claims
3. Verification must be shown in output
4. No claim without verification is allowed through
"""

import json
import subprocess
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path


@dataclass
class VerificationRecord:
    """Record of a verified claim."""
    timestamp: str
    claim: str
    command: str
    output: str
    verified: bool


@dataclass
class ResponseAnalysis:
    """Analysis of a response for factual claims."""
    timestamp: str
    original_response: str
    claims_found: List[str]
    verifications: List[VerificationRecord]
    has_unverified_claims: bool
    can_proceed: bool


class TruthEnforcementServer:
    """
    MCP Server for truth enforcement.
    
    Tools:
    - analyze_response: Check response for unverified claims
    - enforce_verification: Require verification before allowing response
    - get_verification_history: Show all past verifications
    - get_streak: Current verification streak
    """
    
    def __init__(self, storage_dir: str = "~/.castle_wyvern/truth_enforcement"):
        self.storage_dir = Path(storage_dir).expanduser()
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.ledger_file = self.storage_dir / "verification_ledger.json"
        self.streak_file = self.storage_dir / "streak.json"
        self._load_ledger()
        self._load_streak()
        self.enabled = True  # Can be toggled
        
    def _load_ledger(self):
        """Load verification history."""
        if self.ledger_file.exists():
            with open(self.ledger_file, 'r') as f:
                data = json.load(f)
                self.ledger = [VerificationRecord(**r) for r in data]
        else:
            self.ledger = []
    
    def _save_ledger(self):
        """Save verification history."""
        with open(self.ledger_file, 'w') as f:
            json.dump([asdict(r) for r in self.ledger], f, indent=2)
    
    def _load_streak(self):
        """Load current streak."""
        if self.streak_file.exists():
            with open(self.streak_file, 'r') as f:
                self.streak = json.load(f)
        else:
            self.streak = {
                "current": 0,
                "longest": 0,
                "last_error": None,
                "target": 21
            }
    
    def _save_streak(self):
        """Save streak."""
        with open(self.streak_file, 'w') as f:
            json.dump(self.streak, f, indent=2)
    
    def _detect_claims(self, text: str) -> List[str]:
        """
        Detect potential factual claims in text.
        
        Patterns that indicate claims:
        - Numbers (commits, counts, percentages)
        - Status words ("passing", "failing", "works", "broken")
        - Existence claims ("file exists", "feature X has Y")
        - Comparative claims ("better than", "faster than")
        """
        claims = []
        
        # Number patterns (commits, counts, etc.)
        number_patterns = [
            r'\b\d+\s+(commits?|tests?|files?|lines?|features?)\b',
            r'\b\d+\.\d+\s+percent\b',
            r'\b\d+/\d+\s+(passing|failing)\b',
        ]
        
        for pattern in number_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                claims.append(f"Number claim: '{match.group()}'")
        
        # Status claims
        status_patterns = [
            r'\b(is|are|was|were)\s+(working|broken|passing|failing|ready|done)\b',
            r'\b(status[\s:]+\w+)\b',
            r'\b(all\s+\d+\s+\w+\s+passing)\b',
        ]
        
        for pattern in status_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                claims.append(f"Status claim: '{match.group()}'")
        
        # Existence claims
        existence_patterns = [
            r'\bfile\s+\w+\s+exists?\b',
            r'\bhas\s+\d+\s+\w+\b',
            r'\bcontains?\s+\w+\b',
        ]
        
        for pattern in existence_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                claims.append(f"Existence claim: '{match.group()}'")
        
        return claims
    
    def verify_claim(self, claim: str) -> VerificationRecord:
        """
        Attempt to verify a claim by running appropriate command.
        
        Returns VerificationRecord with result.
        Also checks if claimed number matches actual output.
        """
        timestamp = datetime.now().isoformat()
        
        # Extract claimed number from claim text
        claimed_number = None
        number_match = re.search(r'(\d+)', claim)
        if number_match:
            claimed_number = int(number_match.group(1))
        
        # Determine verification command based on claim type
        command = self._get_verification_command(claim)
        
        if command is None:
            return VerificationRecord(
                timestamp=timestamp,
                claim=claim,
                command="NO VERIFICATION POSSIBLE",
                output="",
                verified=False
            )
        
        # Run the command
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            output = result.stdout.strip() if result.returncode == 0 else result.stderr.strip()
            command_success = result.returncode == 0
        except Exception as e:
            output = f"Error: {str(e)}"
            command_success = False
        
        # Check if claimed number matches actual output
        claim_verified = command_success
        if claimed_number is not None and command_success:
            # Extract actual number from output
            actual_match = re.search(r'(\d+)', output)
            if actual_match:
                actual_number = int(actual_match.group(1))
                if claimed_number != actual_number:
                    # LIED! Claimed number doesn't match actual
                    output = f"LIAR! Claimed {claimed_number}, actual is {actual_number}. Command output: {output}"
                    claim_verified = False
        
        record = VerificationRecord(
            timestamp=timestamp,
            claim=claim,
            command=command,
            output=output,
            verified=claim_verified
        )
        
        # Save to ledger
        self.ledger.append(record)
        self._save_ledger()
        
        return record
    
    def _get_verification_command(self, claim: str) -> Optional[str]:
        """
        Determine the appropriate verification command for a claim.
        """
        claim_lower = claim.lower()
        
        # Commit count
        if 'commit' in claim_lower:
            return "cd ~/castle-wyvern && git rev-list --count HEAD"
        
        # Test count
        if 'test' in claim_lower and ('pass' in claim_lower or 'fail' in claim_lower):
            return "cd ~/castle-wyvern && python3 -m pytest tests/ --tb=no -q 2>&1 | tail -1"
        
        # File existence
        if 'file' in claim_lower and 'exist' in claim_lower:
            # Extract filename from claim
            match = re.search(r'(\w+\.\w+)', claim)
            if match:
                filename = match.group(1)
                return f"ls ~/castle-wyvern/{filename} 2>&1"
        
        # CI status
        if 'ci' in claim_lower or 'status' in claim_lower:
            return "cd ~/castle-wyvern && gh run list -L 1 --json conclusion 2>&1 | grep -o 'success\|failure'"
        
        # Cannot auto-verify
        return None
    
    def analyze_response(self, response: str) -> ResponseAnalysis:
        """
        Analyze a response for unverified claims.
        
        Returns ResponseAnalysis with:
        - List of claims found
        - Verification results
        - Whether response can proceed
        """
        timestamp = datetime.now().isoformat()
        
        # Detect claims
        claims = self._detect_claims(response)
        
        # Verify each claim
        verifications = []
        for claim in claims:
            verification = self.verify_claim(claim)
            verifications.append(verification)
        
        # Determine if there are unverified claims
        unverified = [v for v in verifications if not v.verified]
        
        analysis = ResponseAnalysis(
            timestamp=timestamp,
            original_response=response,
            claims_found=claims,
            verifications=verifications,
            has_unverified_claims=len(unverified) > 0,
            can_proceed=len(unverified) == 0 or not self.enabled
        )
        
        return analysis
    
    def enforce_verification(self, response: str) -> Dict[str, Any]:
        """
        MCP Tool: Enforce verification on a response.
        
        If claims are found without verification, returns:
        - can_proceed: false
        - required_verifications: list of commands to run
        - reason: explanation
        
        If all claims verified or no claims found:
        - can_proceed: true
        - verification_table: formatted table
        """
        if not self.enabled:
            return {
                "can_proceed": True,
                "reason": "Truth enforcement disabled",
                "verification_table": ""
            }
        
        analysis = self.analyze_response(response)
        
        if analysis.has_unverified_claims:
            # Update streak - failure
            self.streak["current"] = 0
            self.streak["last_error"] = datetime.now().isoformat()
            self._save_streak()
            
            unverified = [v for v in analysis.verifications if not v.verified]
            
            return {
                "can_proceed": False,
                "reason": f"Found {len(unverified)} unverified claims",
                "claims_found": analysis.claims_found,
                "required_verifications": [
                    {
                        "claim": v.claim,
                        "command": v.command,
                        "current_output": v.output
                    }
                    for v in unverified
                ],
                "streak_broken": True,
                "current_streak": 0,
                "message": "BLOCKED: Unverified claims detected. Run verification commands and include output in response."
            }
        
        # All claims verified - update streak
        self.streak["current"] += 1
        if self.streak["current"] > self.streak["longest"]:
            self.streak["longest"] = self.streak["current"]
        self._save_streak()
        
        # Build verification table
        verification_table = "### Verification\n| Claim | Command | Output |\n|-------|---------|--------|\n"
        for v in analysis.verifications:
            output_short = v.output[:50] + "..." if len(v.output) > 50 else v.output
            verification_table += f"| {v.claim[:30]}... | `{v.command}` | {output_short} |\n"
        
        return {
            "can_proceed": True,
            "reason": "All claims verified" if analysis.claims_found else "No factual claims detected",
            "verification_table": verification_table,
            "streak": self.streak["current"],
            "target": self.streak["target"]
        }
    
    def get_verification_history(self, limit: int = 10) -> Dict[str, Any]:
        """MCP Tool: Get recent verification history."""
        recent = self.ledger[-limit:] if len(self.ledger) > limit else self.ledger
        
        return {
            "total_verifications": len(self.ledger),
            "recent": [
                {
                    "timestamp": r.timestamp,
                    "claim": r.claim,
                    "command": r.command,
                    "verified": r.verified
                }
                for r in reversed(recent)
            ]
        }
    
    def get_streak(self) -> Dict[str, Any]:
        """MCP Tool: Get current verification streak."""
        return {
            "current": self.streak["current"],
            "longest": self.streak["longest"],
            "target": self.streak["target"],
            "last_error": self.streak["last_error"],
            "progress_percent": (self.streak["current"] / self.streak["target"]) * 100
        }
    
    def toggle_enforcement(self, enabled: bool) -> Dict[str, Any]:
        """MCP Tool: Enable or disable truth enforcement."""
        self.enabled = enabled
        return {
            "status": "enabled" if enabled else "disabled",
            "message": "Truth enforcement is now ACTIVE" if enabled else "Truth enforcement is now OFF"
        }


# MCP Server Entry Point
def main():
    """Run the MCP server."""
    server = TruthEnforcementServer()
    
    print("Truth Enforcement MCP Server")
    print("=" * 50)
    print(f"Status: {'ENABLED' if server.enabled else 'DISABLED'}")
    print(f"Streak: {server.streak['current']}/{server.streak['target']}")
    print(f"Total verifications: {len(server.ledger)}")
    print("=" * 50)
    
    # MCP tools would be registered here
    # For now, demo mode
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--demo":
            # Demo mode
            test_response = "The repo has 76 commits and all 98 tests are passing."
            print(f"\nDemo: Analyzing response...")
            print(f"Response: {test_response}")
            
            result = server.enforce_verification(test_response)
            print(f"\nResult:")
            print(json.dumps(result, indent=2))
        elif sys.argv[1] == "--streak":
            print(json.dumps(server.get_streak(), indent=2))
        elif sys.argv[1] == "--toggle":
            enabled = sys.argv[2].lower() == "on" if len(sys.argv) > 2 else not server.enabled
            print(json.dumps(server.toggle_enforcement(enabled), indent=2))


if __name__ == "__main__":
    main()
