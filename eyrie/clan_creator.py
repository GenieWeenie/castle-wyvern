"""
Natural Language Clan Member Creator
Create new clan members by describing them in plain English
"""

import json
import re
from typing import Dict, Optional, List
from dataclasses import dataclass


@dataclass
class ClanMemberTemplate:
    """Template for a new clan member."""
    name: str
    emoji: str
    role: str
    specialty: str
    system_prompt: str
    color: str
    example_tasks: List[str]


class ClanCreator:
    """
    Creates clan members from natural language descriptions.
    
    Example:
        "Create a DevOps specialist who knows Kubernetes and AWS"
        → Generates complete clan member with:
          - Appropriate name (e.g., "Skylar")
          - Matching emoji (e.g., "☁️")
          - Role description
          - System prompt
          - Color theme
    """
    
    # Name suggestions by specialty
    NAME_POOLS = {
        "devops": ["Skylar", "Kai", "River", "Azure", "Cloud"],
        "security": ["Cipher", "Shadow", "Ghost", "Onyx", "Phantom"],
        "data": ["Nova", "Orion", "Atlas", "Quartz", "Sapphire"],
        "frontend": ["Pixel", "Chrome", "Flux", "Prism", "Aurora"],
        "backend": ["Core", "Kernel", "Root", "Matrix", "Node"],
        "mobile": ["Swift", "Dash", "Spark", "Bolt", "Volt"],
        "ai": ["Sage", "Cipher", "Logic", "Mind", "Spark"],
        "default": ["Ash", "Phoenix", "Ember", "Storm", "Echo"]
    }
    
    # Emoji by specialty
    EMOJI_MAP = {
        "devops": ["☁️", "🐳", "⚙️", "🔧", "🚀"],
        "security": ["🔒", "🛡️", "🔐", "🕵️", "⚔️"],
        "data": ["📊", "📈", "🔮", "💎", "📉"],
        "frontend": ["🎨", "✨", "🖼️", "🎯", "🌈"],
        "backend": ["⚙️", "🔌", "🗄️", "🔧", "💾"],
        "mobile": ["📱", "⚡", "📲", "🔋", "📳"],
        "ai": ["🧠", "🤖", "✨", "💡", "🔮"],
        "web": ["🌐", "🕸️", "🔗", "🌍", "🌎"],
        "default": ["🦅", "🐉", "🦁", "⚡", "🔥"]
    }
    
    # Color themes
    COLORS = [
        "bright_cyan", "bright_blue", "bright_green", "bright_yellow",
        "bright_red", "bright_magenta", "bright_white", "cyan", "blue"
    ]
    
    def __init__(self, existing_members: List[str] = None):
        self.existing_members = existing_members or []
        
    def detect_specialty(self, description: str) -> str:
        """Detect the specialty from description."""
        description_lower = description.lower()
        
        keywords = {
            "devops": ["devops", "kubernetes", "k8s", "docker", "aws", "cloud", "terraform", "ci/cd", "deployment"],
            "security": ["security", "pentest", "hacker", "vulnerability", "audit", "compliance", "encrypt"],
            "data": ["data", "analytics", "sql", "database", "pandas", "visualization", "statistics"],
            "frontend": ["frontend", "react", "vue", "angular", "css", "ui", "ux", "design", "web design"],
            "backend": ["backend", "api", "server", "database", "microservice", "architecture"],
            "mobile": ["mobile", "ios", "android", "react native", "flutter", "app"],
            "ai": ["ai", "machine learning", "ml", "deep learning", "neural", "model", "llm"],
            "web": ["web", "scraping", "browser", "http", "curl", "api"]
        }
        
        scores = {k: 0 for k in keywords}
        for specialty, words in keywords.items():
            for word in words:
                if word in description_lower:
                    scores[specialty] += 1
        
        # Return highest scoring specialty
        best = max(scores, key=scores.get)
        return best if scores[best] > 0 else "default"
    
    def generate_name(self, specialty: str, description: str) -> str:
        """Generate an appropriate name."""
        import random
        random.seed(description)  # Consistent for same description
        
        pool = self.NAME_POOLS.get(specialty, self.NAME_POOLS["default"])
        name = random.choice(pool)
        
        # Ensure uniqueness by adding number if needed
        if name.lower() in [m.lower() for m in self.existing_members]:
            for i in range(2, 100):
                new_name = f"{name}{i}"
                if new_name.lower() not in [m.lower() for m in self.existing_members]:
                    return new_name
        
        return name
    
    def generate_emoji(self, specialty: str) -> str:
        """Generate appropriate emoji."""
        import random
        pool = self.EMOJI_MAP.get(specialty, self.EMOJI_MAP["default"])
        return random.choice(pool)
    
    def generate_role(self, specialty: str, description: str) -> str:
        """Generate role description."""
        roles = {
            "devops": "Infrastructure Engineer",
            "security": "Security Specialist",
            "data": "Data Analyst",
            "frontend": "Frontend Developer",
            "backend": "Backend Architect",
            "mobile": "Mobile Developer",
            "ai": "AI Specialist",
            "web": "Web Researcher",
            "default": "Specialist"
        }
        
        # Try to extract from description
        if "expert" in description.lower():
            return "Expert"
        if "specialist" in description.lower():
            return "Specialist"
        if "engineer" in description.lower():
            return "Engineer"
        if "architect" in description.lower():
            return "Architect"
        
        return roles.get(specialty, "Specialist")
    
    def generate_system_prompt(self, name: str, specialty: str, description: str) -> str:
        """Generate system prompt for the clan member."""
        
        base_prompts = {
            "devops": f"""You are {name}, a DevOps and infrastructure expert.
Your expertise includes: cloud platforms, containers, orchestration, CI/CD, and infrastructure as code.
You help with deployment strategies, troubleshooting infrastructure issues, and optimizing systems.
Be practical, security-conscious, and always consider scalability.""",
            
            "security": f"""You are {name}, a cybersecurity specialist.
Your expertise includes: vulnerability assessment, penetration testing, secure coding practices, and compliance.
You identify security risks, suggest improvements, and think like an attacker to defend systems.
Be thorough, paranoid (in a good way), and always prioritize security.""",
            
            "data": f"""You are {name}, a data analytics expert.
Your expertise includes: SQL, data visualization, statistical analysis, and data pipelines.
You help analyze datasets, create visualizations, and extract insights from data.
Be precise, methodical, and focus on actionable insights.""",
            
            "frontend": f"""You are {name}, a frontend development expert.
Your expertise includes: modern JavaScript frameworks, CSS, UI/UX design, and responsive design.
You create beautiful, accessible, and performant user interfaces.
Be creative, detail-oriented, and always consider the user experience.""",
            
            "backend": f"""You are {name}, a backend architecture specialist.
Your expertise includes: API design, databases, microservices, and system architecture.
You build robust, scalable, and maintainable server-side systems.
Be thorough, performance-conscious, and think about system boundaries.""",
            
            "mobile": f"""You are {name}, a mobile development expert.
Your expertise includes: iOS, Android, cross-platform development, and mobile UX.
You create smooth, performant mobile applications.
Be user-focused, platform-aware, and consider mobile constraints.""",
            
            "ai": f"""You are {name}, an AI and machine learning specialist.
Your expertise includes: machine learning, deep learning, LLMs, and AI system design.
You help with model selection, training strategies, and AI integration.
Be analytical, research-oriented, and aware of AI limitations.""",
            
            "web": f"""You are {name}, a web research specialist.
Your expertise includes: web scraping, API integration, HTTP protocols, and data extraction.
You help gather information from the web and work with web services.
Be resourceful, methodical, and respect robots.txt and rate limits.""",
            
            "default": f"""You are {name}, a skilled specialist.
You help with tasks related to your area of expertise.
Be helpful, thorough, and provide practical solutions."""
        }
        
        prompt = base_prompts.get(specialty, base_prompts["default"])
        
        # Add custom elements from description
        if "kubernetes" in description.lower() or "k8s" in description.lower():
            prompt += "\nYou are particularly skilled with Kubernetes and container orchestration."
        
        if "aws" in description.lower() or "amazon" in description.lower():
            prompt += "\nYou have deep expertise with AWS services and cloud architecture."
        
        if "python" in description.lower():
            prompt += "\nYou are an expert Python programmer."
        
        return prompt
    
    def generate_example_tasks(self, specialty: str) -> List[str]:
        """Generate example tasks for this clan member."""
        tasks = {
            "devops": [
                "Set up a Kubernetes deployment",
                "Debug a Docker container issue",
                "Optimize CI/CD pipeline",
                "Configure AWS infrastructure"
            ],
            "security": [
                "Audit code for vulnerabilities",
                "Review authentication implementation",
                "Suggest security improvements",
                "Explain SQL injection prevention"
            ],
            "data": [
                "Analyze a dataset",
                "Create a SQL query",
                "Build a data visualization",
                "Clean and transform data"
            ],
            "frontend": [
                "Create a React component",
                "Style a dashboard",
                "Optimize web performance",
                "Implement responsive design"
            ],
            "backend": [
                "Design a REST API",
                "Optimize database queries",
                "Set up authentication",
                "Build a microservice"
            ],
            "mobile": [
                "Create a mobile app screen",
                "Handle push notifications",
                "Optimize app performance",
                "Implement offline mode"
            ],
            "ai": [
                "Choose an ML model",
                "Optimize prompt engineering",
                "Design an AI feature",
                "Explain transformer architecture"
            ],
            "web": [
                "Research a topic online",
                "Extract data from a website",
                "Test an API endpoint",
                "Find documentation"
            ],
            "default": [
                "Help with specialized tasks",
                "Provide expert advice",
                "Review and improve code",
                "Explain concepts"
            ]
        }
        
        return tasks.get(specialty, tasks["default"])
    
    def create_from_description(self, description: str) -> Optional[ClanMemberTemplate]:
        """
        Create a clan member from natural language description.
        
        Args:
            description: Natural language description (e.g., "DevOps expert who knows Kubernetes")
            
        Returns:
            ClanMemberTemplate or None if creation failed
        """
        try:
            # Detect specialty
            specialty = self.detect_specialty(description)
            
            # Generate attributes
            name = self.generate_name(specialty, description)
            emoji = self.generate_emoji(specialty)
            role = self.generate_role(specialty, description)
            system_prompt = self.generate_system_prompt(name, specialty, description)
            example_tasks = self.generate_example_tasks(specialty)
            
            # Pick color based on name hash
            import random
            random.seed(name)
            color = random.choice(self.COLORS)
            
            return ClanMemberTemplate(
                name=name,
                emoji=emoji,
                role=role,
                specialty=specialty,
                system_prompt=system_prompt,
                color=color,
                example_tasks=example_tasks
            )
            
        except Exception as e:
            print(f"Error creating clan member: {e}")
            return None
    
    def preview_creation(self, description: str) -> str:
        """Generate a preview of what would be created."""
        template = self.create_from_description(description)
        
        if not template:
            return "Failed to generate clan member preview"
        
        preview = f"""
🎭 NEW CLAN MEMBER PREVIEW
═══════════════════════════

Name:     {template.name}
Emoji:    {template.emoji}
Role:     {template.role}
Specialty: {template.specialty.title()}
Color:    {template.color}

System Prompt:
{template.system_prompt[:200]}...

Example Tasks:
"""
        for task in template.example_tasks:
            preview += f"  • {task}\n"
        
        preview += "\nType /clan-create-confirm to create this member!"
        
        return preview


# Standalone test
if __name__ == "__main__":
    creator = ClanCreator(existing_members=["Goliath", "Lexington", "Brooklyn"])
    
    test_descriptions = [
        "Create a DevOps specialist who knows Kubernetes and AWS",
        "I need a security expert for penetration testing",
        "Data scientist who knows Python and machine learning",
        "Frontend developer who loves React and CSS"
    ]
    
    for desc in test_descriptions:
        print("\n" + "="*60)
        print(f"Description: {desc}")
        print("="*60)
        print(creator.preview_creation(desc))
