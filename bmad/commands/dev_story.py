#!/usr/bin/env python3
"""
/dev-story Command
Implementation of a user story
Invokes: Lexington (developer) + Broadway (documentation)
"""

import sys
import os
# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from clan_wyvern import CastleWyvern

def dev_story(story_description=None):
    """Implement a user story."""
    wyvern = CastleWyvern()
    
    print("=== DEV STORY COMMAND ===")
    
    # If no description provided, check for spec
    if not story_description:
        # Look for most recent spec
        spec_dir = 'specs'
        if os.path.exists(spec_dir):
            specs = [f for f in os.listdir(spec_dir) if f.endswith('.md')]
            if specs:
                latest = sorted(specs)[-1]
                with open(os.path.join(spec_dir, latest)) as f:
                    story_description = f.read()
                print(f"Using spec: {latest}")
            else:
                story_description = input("Enter story description: ")
        else:
            story_description = input("Enter story description: ")
    
    print(f"Story: {story_description[:100]}...")
    print()
    
    # Lexington implements
    print("[LEXINGTON]: 'I'll build this! Let me start coding...'")
    lexington_prompt = f"""
    Implement this user story:
    {story_description}
    
    Provide:
    1. Code implementation (pseudocode or actual code)
    2. Key changes made
    3. Files created/modified
    4. Testing approach
    5. Any technical notes or gotchas
    
    Be thorough. Show your work!
    """
    
    implementation = wyvern.gate._call_zai(
        lexington_prompt,
        wyvern.spells['lexington'][:1000]
    )
    print(f"[LEXINGTON]: {implementation[:800]}...")
    print()
    
    # Broadway documents
    print("[BROADWAY]: 'Let me document what was built...'")
    broadway_prompt = f"""
    Based on Lexington's implementation, create documentation:
    
    Implementation:
    {implementation[:500]}
    
    Provide:
    1. What was built (summary)
    2. How to use it
    3. Any configuration needed
    4. Known limitations
    
    User-friendly documentation.
    """
    
    docs = wyvern.gate._call_zai(
        broadway_prompt,
        wyvern.spells['broadway'][:1000]
    )
    print(f"[BROADWAY]: {docs[:500]}...")
    print()
    
    # Save implementation
    impl_file = "implementations/latest_implementation.md"
    os.makedirs('implementations', exist_ok=True)
    with open(impl_file, 'w') as f:
        f.write(f"# Implementation\n\n{implementation}\n\n# Documentation\n\n{docs}\n")
    
    print(f"✅ Implementation saved to: {impl_file}")
    print("\nNext: Run `/code-review` to validate")

if __name__ == "__main__":
    description = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else None
    dev_story(description)