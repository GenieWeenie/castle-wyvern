"""
BMAD Integration for Castle Wyvern CLI
Build, Measure, Analyze, Deploy workflow commands.
"""

import os
from typing import Dict, Optional
from rich.panel import Panel
from rich.markdown import Markdown
from rich import box

from eyrie.phoenix_gate import PhoenixGate
from grimoorum.memory_manager import GrimoorumV2


class BMADWorkflow:
    """
    BMAD (Build, Measure, Analyze, Deploy) workflow integration.
    
    Commands:
    - /quick-spec: Rapid spec for small features
    - /dev-story: Implementation with Lexington + Broadway
    - /code-review: Review with Xanatos + Demona
    - /product-brief: Full PRD for complex features
    """
    
    def __init__(self, console, phoenix_gate: PhoenixGate, grimoorum: GrimoorumV2):
        self.console = console
        self.gate = phoenix_gate
        self.grimoorum = grimoorum
        
        # Agent system prompts
        self.agent_prompts = {
            "goliath": "You are Goliath, leader of the Manhattan Clan. You scope work and provide clarity. Be commanding and wise.",
            "brooklyn": "You are Brooklyn, the strategist. You design technical approaches and architecture. Be tactical and forward-thinking.",
            "lexington": "You are Lexington, the technician. You write code and implement solutions. Be enthusiastic about technology.",
            "broadway": "You are Broadway, the chronicler. You write documentation and tests. Be thorough and narrative.",
            "xanatos": "You are Xanatos, the red team. You critique code and find issues. Be clever and challenging.",
            "demona": "You are Demona, the failsafe. You predict failures and edge cases. Be cautious and protective.",
        }
    
    def quick_spec(self, description: str) -> Dict:
        """
        /quick-spec: Rapid specification for bug fixes and small features.
        Agents: Goliath (scope) + Brooklyn (technical approach)
        """
        self.console.print(f"\n[bold cyan]⚡ QUICK SPEC[/bold cyan]: {description}\n")
        
        # Goliath scopes the work
        self.console.print("[yellow]🦁 Goliath is scoping the work...[/yellow]")
        goliath_prompt = f"""A user needs a quick technical spec for: {description}

Provide:
1. Problem statement (1-2 sentences)
2. Scope (what's in/out)
3. Success criteria (how do we know it's done?)
4. Any risks or concerns

Be concise. This is a quick spec, not a full PRD."""
        
        goliath_response = self.gate.call_ai(goliath_prompt, self.agent_prompts["goliath"])
        
        self.console.print(Panel(
            Markdown(goliath_response),
            title="🦁 Goliath's Scope",
            border_style="yellow",
            box=box.ROUNDED
        ))
        
        # Brooklyn provides technical approach
        self.console.print("[red]🎯 Brooklyn is designing the technical approach...[/red]")
        brooklyn_prompt = f"""Based on this task: {description}

Provide:
1. Suggested implementation approach
2. Key files/components to modify
3. Estimated complexity (Simple/Medium/Complex)
4. Any dependencies or blockers

Keep it actionable. Lexington will use this to build."""
        
        brooklyn_response = self.gate.call_ai(brooklyn_prompt, self.agent_prompts["brooklyn"])
        
        self.console.print(Panel(
            Markdown(brooklyn_response),
            title="🎯 Brooklyn's Technical Approach",
            border_style="red",
            box=box.ROUNDED
        ))
        
        # Save to memory
        self.grimoorum.record(
            user_input=f"/quick-spec {description}",
            agent_name="goliath",
            agent_response=f"Scope: {goliath_response}\n\nApproach: {brooklyn_response}",
            intent="plan",
            importance=4,
            tags=["bmad", "spec", "planning"]
        )
        
        return {
            "command": "quick-spec",
            "description": description,
            "scope": goliath_response,
            "approach": brooklyn_response
        }
    
    def dev_story(self, spec_description: str) -> Dict:
        """
        /dev-story: Implementation phase with Lexington (code) + Broadway (docs/tests).
        """
        self.console.print(f"\n[bold cyan]🔨 DEV STORY[/bold cyan]: {spec_description}\n")
        
        # Lexington implements
        self.console.print("[cyan]🔧 Lexington is coding...[/cyan]")
        lex_prompt = f"""Implement this feature: {spec_description}

Provide:
1. Complete code implementation
2. Key functions/classes with docstrings
3. Usage example
4. Any assumptions made

Write production-ready Python code."""
        
        lex_response = self.gate.call_ai(lex_prompt, self.agent_prompts["lexington"])
        
        self.console.print(Panel(
            Markdown(lex_response),
            title="🔧 Lexington's Implementation",
            border_style="cyan",
            box=box.ROUNDED
        ))
        
        # Broadway writes docs and tests
        self.console.print("[green]📜 Broadway is writing documentation...[/green]")
        broadway_prompt = f"""For this implementation, provide:

1. Brief documentation/README section
2. Test cases (pytest style)
3. Usage examples

Code context: {lex_response[:500]}..."""
        
        broadway_response = self.gate.call_ai(broadway_prompt, self.agent_prompts["broadway"])
        
        self.console.print(Panel(
            Markdown(broadway_response),
            title="📜 Broadway's Documentation & Tests",
            border_style="green",
            box=box.ROUNDED
        ))
        
        # Save to memory
        self.grimoorum.record(
            user_input=f"/dev-story {spec_description}",
            agent_name="lexington",
            agent_response=f"Code:\n{lex_response}\n\nDocs:\n{broadway_response}",
            intent="code",
            importance=5,
            tags=["bmad", "implementation", "code"]
        )
        
        return {
            "command": "dev-story",
            "code": lex_response,
            "docs": broadway_response
        }
    
    def code_review(self, code_description: str) -> Dict:
        """
        /code-review: Review phase with Xanatos (critique) + Demona (edge cases).
        """
        self.console.print(f"\n[bold cyan]🔍 CODE REVIEW[/bold cyan]: {code_description}\n")
        
        # Xanatos critiques
        self.console.print("[bright_black]🎭 Xanatos is reviewing for issues...[/bright_black]")
        xanatos_prompt = f"""Review this code/feature for issues:

{code_description}

Check for:
1. Bugs or logic errors
2. Security vulnerabilities
3. Performance issues
4. Code smells or anti-patterns
5. Missing error handling

Be thorough and critical. Find what others would miss."""
        
        xanatos_response = self.gate.call_ai(xanatos_prompt, self.agent_prompts["xanatos"])
        
        self.console.print(Panel(
            Markdown(xanatos_response),
            title="🎭 Xanatos's Critique",
            border_style="bright_black",
            box=box.ROUNDED
        ))
        
        # Demona finds edge cases
        self.console.print("[red]🔥 Demona is hunting edge cases...[/red]")
        demona_prompt = f"""For this code/feature, identify:

1. Edge cases that could break it
2. Failure modes and error conditions
3. Race conditions or timing issues
4. Input validation gaps
5. Worst-case scenarios

Think like a pessimist. What could go wrong?"""
        
        demona_response = self.gate.call_ai(demona_prompt, self.agent_prompts["demona"])
        
        self.console.print(Panel(
            Markdown(demona_response),
            title="🔥 Demona's Edge Cases",
            border_style="red",
            box=box.ROUNDED
        ))
        
        # Save to memory
        self.grimoorum.record(
            user_input=f"/code-review {code_description}",
            agent_name="xanatos",
            agent_response=f"Critique:\n{xanatos_response}\n\nEdge Cases:\n{demona_response}",
            intent="analyze",
            importance=4,
            tags=["bmad", "review", "quality"]
        )
        
        return {
            "command": "code-review",
            "critique": xanatos_response,
            "edge_cases": demona_response
        }
    
    def product_brief(self, product_description: str) -> Dict:
        """
        /product-brief: Full PRD for complex features.
        Agents: All clan members contribute to comprehensive spec.
        """
        self.console.print(f"\n[bold cyan]📋 PRODUCT BRIEF[/bold cyan]: {product_description}\n")
        
        # Goliath provides vision
        self.console.print("[yellow]🦁 Goliath is defining the vision...[/yellow]")
        goliath_prompt = f"""Create a product vision for: {product_description}

Include:
1. Problem statement (what pain does this solve?)
2. Target user(s)
3. Value proposition (why should they care?)
4. Success metrics (how do we measure success?)

Be inspiring but grounded."""
        
        vision = self.gate.call_ai(goliath_prompt, self.agent_prompts["goliath"])
        self.console.print(Panel(Markdown(vision), title="🦁 Vision", border_style="yellow"))
        
        # Brooklyn architects the solution
        self.console.print("[red]🎯 Brooklyn is architecting the solution...[/red]")
        brooklyn_prompt = f"""Based on this vision, design the architecture:

{vision[:300]}...

Provide:
1. High-level architecture diagram (describe in text)
2. Key components/modules
3. Data flow
4. Technology choices
5. Integration points

Think big picture but actionable."""
        
        architecture = self.gate.call_ai(brooklyn_prompt, self.agent_prompts["brooklyn"])
        self.console.print(Panel(Markdown(architecture), title="🎯 Architecture", border_style="red"))
        
        # Elisa provides human/ethical context
        self.console.print("[white]🌉 Elisa is considering human factors...[/white]")
        elisa_prompt = f"""For this product, consider:

1. User experience concerns
2. Accessibility considerations
3. Ethical implications
4. Legal/compliance aspects
5. Human-centered design principles

Ground the technical in human reality."""
        
        human_factors = self.gate.call_ai(elisa_prompt, self.agent_prompts.get("elisa", self.agent_prompts["goliath"]))
        self.console.print(Panel(Markdown(human_factors), title="🌉 Human Factors", border_style="white"))
        
        # Save comprehensive brief
        brief = f"""# Product Brief: {product_description}

## Vision
{vision}

## Architecture
{architecture}

## Human Factors
{human_factors}

## Next Steps
1. Review with stakeholders
2. Create technical specs with /quick-spec
3. Build MVP with /dev-story
4. Review with /code-review
"""
        
        self.grimoorum.record(
            user_input=f"/product-brief {product_description}",
            agent_name="goliath",
            agent_response=brief,
            intent="plan",
            importance=5,
            tags=["bmad", "prd", "product", "planning"]
        )
        
        return {
            "command": "product-brief",
            "vision": vision,
            "architecture": architecture,
            "human_factors": human_factors,
            "full_brief": brief
        }