#!/usr/bin/env python3
"""
/code-review Command
Code review and validation
Invokes: Xanatos (adversarial) + Demona (failsafe) + Bronx (security)
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from clan_wyvern import CastleWyvern


def code_review(code_source=None):
    """Review code for quality, security, and issues."""
    wyvern = CastleWyvern()

    print("=== CODE REVIEW COMMAND ===")

    # Get code to review
    if not code_source:
        # Check implementations
        impl_file = "implementations/latest_implementation.md"
        if os.path.exists(impl_file):
            with open(impl_file) as f:
                code_source = f.read()
            print(f"Reviewing: {impl_file}")
        else:
            print("No implementation found. Please specify code to review.")
            return

    print("Initiating comprehensive code review...")
    print()

    # Xanatos finds vulnerabilities
    print("[XANATOS]: 'Let me find the weaknesses...'")
    xanatos_prompt = f"""
    Review this code as an adversary would:
    {code_source[:2000]}
    
    Find:
    1. Security vulnerabilities
    2. Logic flaws
    3. Edge cases not handled
    4. Ways this could break
    5. Performance issues
    
    Be ruthless. Show me every weakness.
    """

    vulnerabilities = wyvern.gate._call_zai(xanatos_prompt, wyvern.spells["xanatos"][:1000])
    print(f"[XANATOS]: {vulnerabilities[:600]}...")
    print()

    # Demona predicts failures
    print("[DEMONA]: 'I know what will fail...'")
    demona_prompt = f"""
    Predict failures in this code:
    {code_source[:2000]}
    
    Tell me:
    1. What WILL fail (be specific)
    2. Under what conditions
    3. Cascading failure effects
    4. Missing error handling
    5. What backups are needed
    
    I know failure. Trust me.
    """

    failures = wyvern.gate._call_zai(demona_prompt, wyvern.spells["demona"][:1000])
    print(f"[DEMONA]: {failures[:600]}...")
    print()

    # Bronx security scan
    print("[BRONX]: '*scanning* Security check...'")
    bronx_prompt = f"""
    Security scan of this code:
    {code_source[:2000]}
    
    Report:
    1. Security issues found (CRITICAL/HIGH/MEDIUM/LOW)
    2. Best practice violations
    3. Input validation gaps
    4. Authentication/authorization issues
    5. Overall security grade
    
    Alert level: 🟢 Safe / 🟡 Watch / 🟠 Caution / 🔴 Alert
    """

    security = wyvern.gate._call_zai(bronx_prompt, wyvern.spells["bronx"][:1000])
    print(f"[BRONX]: {security[:600]}...")
    print()

    # Combined review report
    review = f"""
# Code Review Report

## Security Assessment (Xanatos)
{vulnerabilities}

## Failure Prediction (Demona)
{failures}

## Security Scan (Bronx)
{security}

## Summary
Review complete. Address critical issues before deployment.

---
Reviewed by Castle Wyvern BMAD System
"""

    # Save review
    review_file = "reviews/latest_review.md"
    os.makedirs("reviews", exist_ok=True)
    with open(review_file, "w") as f:
        f.write(review)

    print(f"✅ Review saved to: {review_file}")
    print("\nFix issues, then run `/deploy-check` when ready")


if __name__ == "__main__":
    code_source = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else None
    code_review(code_source)
