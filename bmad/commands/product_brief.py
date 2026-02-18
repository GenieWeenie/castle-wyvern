#!/usr/bin/env python3
"""
/product-brief Command
Product definition and MVP scope
Invokes: Goliath (vision) + Elisa (human context)
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from clan_wyvern import CastleWyvern


def product_brief(product_idea):
    """Create a product brief."""
    wyvern = CastleWyvern()

    print("=== PRODUCT BRIEF COMMAND ===")
    print(f"Product: {product_idea}")
    print()

    # Goliath defines the vision
    print("[GOLIATH]: 'Let me define what we're building...'")
    goliath_prompt = f"""
    Create a product vision for: {product_idea}
    
    Define:
    1. Problem statement (what pain are we solving?)
    2. Target users (who is this for?)
    3. Vision statement (what does success look like?)
    4. Core value proposition (why choose us?)
    5. MVP scope (minimum viable product)
    
    Think like a leader. Be inspiring but realistic.
    """

    vision = wyvern.gate._call_zai(goliath_prompt, wyvern.spells["goliath"][:1000])
    print(f"[GOLIATH]: {vision[:600]}...")
    print()

    # Elisa adds human context
    print("[ELISA]: 'Let me add the human perspective...'")
    elisa_prompt = f"""
    Based on Goliath's vision, provide human context for: {product_idea}
    
    Consider:
    1. User personas (specific types of people)
    2. Human workflows (how they currently solve this)
    3. Adoption challenges (why might they resist?)
    4. Ethical considerations (any concerns?)
    5. Legal/social constraints (what to watch for?)
    
    Ground this in human reality. What's the practical impact?
    """

    human_context = wyvern.gate._call_zai(elisa_prompt, wyvern.spells["elisa"][:1000])
    print(f"[ELISA]: {human_context[:600]}...")
    print()

    # Combined brief
    brief = f"""
# Product Brief

## Product
{product_idea}

## Vision (Goliath)
{vision}

## Human Context (Elisa)
{human_context}

## Next Steps
1. Review and refine vision
2. Run `/create-prd` for detailed requirements
3. Run `/create-architecture` for technical design

---
Castle Wyvern BMAD System
"""

    brief_file = f"products/brief_{product_idea.replace(' ', '_')[:20]}.md"
    os.makedirs("products", exist_ok=True)
    with open(brief_file, "w") as f:
        f.write(brief)

    print(f"✅ Product brief saved to: {brief_file}")
    print("\nNext: Run `/create-prd` for detailed requirements")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python product_brief.py 'product description'")
        print("Example: python product_brief.py 'AI chatbot for customer service'")
        sys.exit(1)

    product_idea = " ".join(sys.argv[1:])
    product_brief(product_idea)
