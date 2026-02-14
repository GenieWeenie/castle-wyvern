"""
Castle Wyvern Documentation Generator
Feature 21: Auto-generate documentation

Provides:
- Auto-generate docs from code
- API documentation
- Architecture diagrams
- Usage examples
- Markdown export
"""

import os
import sys
import json
import ast
import inspect
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import re


@dataclass
class FunctionDoc:
    """Documentation for a function."""
    name: str
    signature: str
    docstring: str
    params: List[Dict]
    returns: str
    examples: List[str]


@dataclass
class ClassDoc:
    """Documentation for a class."""
    name: str
    docstring: str
    methods: List[FunctionDoc]
    attributes: List[Dict]


@dataclass
class ModuleDoc:
    """Documentation for a module."""
    name: str
    description: str
    classes: List[ClassDoc]
    functions: List[FunctionDoc]
    imports: List[str]


class CodeAnalyzer:
    """
    Analyzes Python code to extract documentation.
    """
    
    def analyze_file(self, filepath: str) -> Optional[ModuleDoc]:
        """Analyze a Python file and extract documentation."""
        try:
            with open(filepath, "r") as f:
                source = f.read()
            
            tree = ast.parse(source)
            
            module_name = os.path.basename(filepath).replace(".py", "")
            module_description = ast.get_docstring(tree) or ""
            
            classes = []
            functions = []
            imports = []
            
            for node in ast.iter_child_nodes(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    imports.append(f"{node.module}")
                elif isinstance(node, ast.ClassDef):
                    classes.append(self._analyze_class(node))
                elif isinstance(node, ast.FunctionDef):
                    functions.append(self._analyze_function(node))
            
            return ModuleDoc(
                name=module_name,
                description=module_description,
                classes=classes,
                functions=functions,
                imports=imports
            )
            
        except Exception as e:
            print(f"[DocGen] Error analyzing {filepath}: {e}")
            return None
    
    def _analyze_class(self, node: ast.ClassDef) -> ClassDoc:
        """Analyze a class definition."""
        docstring = ast.get_docstring(node) or ""
        
        methods = []
        attributes = []
        
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                if not item.name.startswith("_"):  # Public methods only
                    methods.append(self._analyze_function(item))
            elif isinstance(item, ast.Assign):
                # Class attributes
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        attributes.append({
                            "name": target.id,
                            "value": ast.unparse(item.value) if item.value else None
                        })
        
        return ClassDoc(
            name=node.name,
            docstring=docstring,
            methods=methods,
            attributes=attributes
        )
    
    def _analyze_function(self, node: ast.FunctionDef) -> FunctionDoc:
        """Analyze a function definition."""
        docstring = ast.get_docstring(node) or ""
        
        # Extract params
        params = []
        for arg in node.args.args:
            param_info = {"name": arg.arg}
            if arg.annotation:
                param_info["type"] = ast.unparse(arg.annotation)
            params.append(param_info)
        
        # Extract return type
        returns = ""
        if node.returns:
            returns = ast.unparse(node.returns)
        
        # Extract examples from docstring
        examples = []
        if "Example:" in docstring or "Examples:" in docstring:
            lines = docstring.split("\n")
            in_example = False
            example_lines = []
            
            for line in lines:
                if "Example:" in line or "Examples:" in line:
                    in_example = True
                elif in_example:
                    if line.strip() and not line.startswith(" "):
                        break
                    example_lines.append(line)
            
            if example_lines:
                examples.append("\n".join(example_lines))
        
        # Build signature
        args_str = ", ".join([p["name"] for p in params])
        signature = f"{node.name}({args_str})"
        
        return FunctionDoc(
            name=node.name,
            signature=signature,
            docstring=docstring,
            params=params,
            returns=returns,
            examples=examples
        )


class APIDocumenter:
    """
    Generates API documentation.
    """
    
    def __init__(self):
        self.endpoints: List[Dict] = []
    
    def add_endpoint(self, path: str, method: str, description: str,
                    params: List[Dict] = None, returns: Dict = None):
        """Add an API endpoint."""
        self.endpoints.append({
            "path": path,
            "method": method,
            "description": description,
            "params": params or [],
            "returns": returns or {}
        })
    
    def generate_markdown(self) -> str:
        """Generate API documentation in Markdown."""
        lines = [
            "# Castle Wyvern API Documentation",
            "",
            f"Generated: {datetime.now().isoformat()}",
            "",
            "## Endpoints",
            ""
        ]
        
        for endpoint in self.endpoints:
            lines.append(f"### {endpoint['method']} {endpoint['path']}")
            lines.append("")
            lines.append(endpoint['description'])
            lines.append("")
            
            if endpoint['params']:
                lines.append("**Parameters:**")
                lines.append("")
                for param in endpoint['params']:
                    req = " (required)" if param.get('required') else ""
                    lines.append(f"- `{param['name']}`{req}: {param.get('type', 'any')}")
                lines.append("")
            
            if endpoint['returns']:
                lines.append(f"**Returns:** `{endpoint['returns'].get('type', 'any')}`")
                lines.append("")
            
            lines.append("---")
            lines.append("")
        
        return "\n".join(lines)


class ArchitectureVisualizer:
    """
    Generates architecture diagrams and descriptions.
    """
    
    def __init__(self):
        self.components: List[Dict] = []
        self.connections: List[Dict] = []
    
    def add_component(self, name: str, component_type: str, 
                     description: str = ""):
        """Add a system component."""
        self.components.append({
            "name": name,
            "type": component_type,
            "description": description
        })
    
    def add_connection(self, from_component: str, to_component: str,
                      connection_type: str = "uses"):
        """Add a connection between components."""
        self.connections.append({
            "from": from_component,
            "to": to_component,
            "type": connection_type
        })
    
    def generate_text_diagram(self) -> str:
        """Generate a text-based architecture diagram."""
        lines = [
            "# Castle Wyvern Architecture",
            "",
            "## Components",
            ""
        ]
        
        # Group by type
        by_type: Dict[str, List[Dict]] = {}
        for comp in self.components:
            t = comp["type"]
            if t not in by_type:
                by_type[t] = []
            by_type[t].append(comp)
        
        for type_name, comps in sorted(by_type.items()):
            lines.append(f"### {type_name.title()}")
            lines.append("")
            for comp in comps:
                lines.append(f"- **{comp['name']}**: {comp['description']}")
            lines.append("")
        
        # Connections
        if self.connections:
            lines.append("## Connections")
            lines.append("")
            for conn in self.connections:
                lines.append(f"- `{conn['from']}` → `{conn['to']}` ({conn['type']})")
            lines.append("")
        
        return "\n".join(lines)
    
    def generate_mermaid(self) -> str:
        """Generate Mermaid diagram code."""
        lines = [
            "```mermaid",
            "graph TD",
        ]
        
        # Add nodes
        for comp in self.components:
            safe_name = comp["name"].replace(" ", "_").replace("-", "_")
            lines.append(f'    {safe_name}["{comp["name"]}"]')
        
        lines.append("")
        
        # Add connections
        for conn in self.connections:
            from_safe = conn["from"].replace(" ", "_").replace("-", "_")
            to_safe = conn["to"].replace(" ", "_").replace("-", "_")
            lines.append(f"    {from_safe} --> {to_safe}")
        
        lines.append("```")
        
        return "\n".join(lines)


class ExampleGenerator:
    """
    Generates usage examples.
    """
    
    def __init__(self):
        self.examples: List[Dict] = []
    
    def add_example(self, title: str, description: str, 
                   code: str, output: str = ""):
        """Add an example."""
        self.examples.append({
            "title": title,
            "description": description,
            "code": code,
            "output": output
        })
    
    def generate_markdown(self) -> str:
        """Generate examples in Markdown."""
        lines = [
            "# Castle Wyvern Usage Examples",
            "",
            f"Generated: {datetime.now().isoformat()}",
            ""
        ]
        
        for i, example in enumerate(self.examples, 1):
            lines.append(f"## Example {i}: {example['title']}")
            lines.append("")
            lines.append(example['description'])
            lines.append("")
            lines.append("```python")
            lines.append(example['code'])
            lines.append("```")
            lines.append("")
            
            if example['output']:
                lines.append("**Output:**")
                lines.append("```")
                lines.append(example['output'])
                lines.append("```")
                lines.append("")
        
        return "\n".join(lines)


class DocumentationGenerator:
    """
    Central documentation generator.
    """
    
    def __init__(self, output_dir: str = "docs"):
        self.output_dir = output_dir
        self.analyzer = CodeAnalyzer()
        self.api_doc = APIDocumenter()
        self.architecture = ArchitectureVisualizer()
        self.examples = ExampleGenerator()
        
        # Add default Castle Wyvern architecture
        self._setup_default_architecture()
        self._setup_default_examples()
    
    def _setup_default_architecture(self):
        """Setup default Castle Wyvern architecture."""
        # Components
        components = [
            ("Phoenix Gate", "gateway", "AI API gateway with retry logic"),
            ("Intent Router", "router", "Routes requests to appropriate agent"),
            ("Manhattan Clan", "agents", "9 specialized AI agents"),
            ("Grimoorum", "memory", "Memory and archive system"),
            ("BMAD Workflow", "workflow", "Build-Measure-Analyze-Deploy"),
            ("Plugin System", "extension", "Extensible plugin architecture"),
            ("Monitoring", "observability", "Metrics and health checks"),
            ("Security", "security", "Audit logging and encryption"),
        ]
        
        for name, ctype, desc in components:
            self.architecture.add_component(name, ctype, desc)
        
        # Connections
        self.architecture.add_connection("Phoenix Gate", "Intent Router")
        self.architecture.add_connection("Intent Router", "Manhattan Clan")
        self.architecture.add_connection("Manhattan Clan", "Grimoorum")
        self.architecture.add_connection("Plugin System", "Manhattan Clan")
        self.architecture.add_connection("Monitoring", "Phoenix Gate")
    
    def _setup_default_examples(self):
        """Setup default usage examples."""
        self.examples.add_example(
            "Basic Usage",
            "Ask the clan a simple question:",
            """from castle_wyvern import CastleWyvern

cw = CastleWyvern()
response = cw.ask("What is Python?")
print(response)
""",
            "Python is a high-level programming language..."
        )
        
        self.examples.add_example(
            "Code Generation",
            "Request code from Lexington:",
            """from castle_wyvern import CastleWyvern

cw = CastleWyvern()
code = cw.code("Write a fibonacci function")
print(code)
""",
            "```python\ndef fibonacci(n):\n    ...\n```"
        )
    
    def generate_module_docs(self, source_dir: str) -> Dict[str, ModuleDoc]:
        """Generate documentation for all modules in a directory."""
        docs = {}
        
        for root, dirs, files in os.walk(source_dir):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            
            for file in files:
                if file.endswith(".py") and not file.startswith("_"):
                    filepath = os.path.join(root, file)
                    doc = self.analyzer.analyze_file(filepath)
                    if doc:
                        docs[doc.name] = doc
        
        return docs
    
    def export_markdown(self, output_file: str = None):
        """Export all documentation to Markdown files."""
        if output_file is None:
            output_file = os.path.join(self.output_dir, "README.md")
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        lines = [
            "# Castle Wyvern Documentation",
            "",
            f"Generated: {datetime.now().isoformat()}",
            "",
            "## Table of Contents",
            "",
            "1. [Architecture](#architecture)",
            "2. [API Reference](#api-reference)",
            "3. [Usage Examples](#usage-examples)",
            "",
            "---",
            "",
            "## Architecture",
            "",
            self.architecture.generate_text_diagram(),
            "",
            "### Diagram",
            "",
            self.architecture.generate_mermaid(),
            "",
            "---",
            "",
            "## API Reference",
            "",
            self.api_doc.generate_markdown(),
            "",
            "---",
            "",
            "## Usage Examples",
            "",
            self.examples.generate_markdown(),
        ]
        
        with open(output_file, "w") as f:
            f.write("\n".join(lines))
        
        return output_file
    
    def generate_api_docs_from_server(self, api_server):
        """Generate API docs from an API server instance."""
        # This would introspect the Flask routes
        # For now, add manually
        endpoints = [
            ("/health", "GET", "Health check", [], {"type": "object"}),
            ("/clan", "GET", "List clan members", [], {"type": "array"}),
            ("/clan/ask", "POST", "Ask the clan", 
             [{"name": "message", "type": "string", "required": True}],
             {"type": "object"}),
        ]
        
        for path, method, desc, params, returns in endpoints:
            self.api_doc.add_endpoint(path, method, desc, params, returns)


# Standalone test
if __name__ == "__main__":
    print("🏰 Castle Wyvern Documentation Generator Test")
    print("=" * 50)
    
    docgen = DocumentationGenerator(output_dir="/tmp/cw_docs")
    
    # Test code analysis
    print("\n1. Testing code analysis...")
    test_code = '''
def hello(name: str) -> str:
    """
    Say hello to someone.
    
    Example:
        >>> hello("World")
        "Hello, World!"
    """
    return f"Hello, {name}!"
'''
    
    # Write temp file
    with open("/tmp/test_module.py", "w") as f:
        f.write(test_code)
    
    module_doc = docgen.analyzer.analyze_file("/tmp/test_module.py")
    if module_doc:
        print(f"   Module: {module_doc.name}")
        print(f"   Functions: {len(module_doc.functions)}")
        if module_doc.functions:
            print(f"   First function: {module_doc.functions[0].name}")
    
    # Test architecture diagram
    print("\n2. Testing architecture visualization...")
    diagram = docgen.architecture.generate_text_diagram()
    print(f"   Generated {len(diagram)} characters")
    
    # Test documentation export
    print("\n3. Testing documentation export...")
    output_file = docgen.export_markdown()
    print(f"   Exported to: {output_file}")
    print(f"   File size: {os.path.getsize(output_file)} bytes")
    
    print("\n✅ Documentation generator ready!")
