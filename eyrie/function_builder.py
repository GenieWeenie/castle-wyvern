"""
Self-Building Function System (BabyAGI-inspired)
Castle Wyvern can create its own tools dynamically
"""

import os
import json
import hashlib
import time
import re
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class FunctionMetadata:
    """Metadata for a self-built function."""

    name: str
    description: str
    dependencies: List[str]
    imports: List[str]
    created_at: float
    usage_count: int = 0
    last_used: Optional[float] = None
    tags: List[str] = field(default_factory=list)


@dataclass
class BuiltFunction:
    """A self-built function with metadata and executable code."""

    metadata: FunctionMetadata
    code: str
    func: Optional[Callable] = None

    def execute(self, *args, **kwargs) -> Any:
        """Execute the function."""
        if self.func is None:
            # Compile the function
            namespace: Dict[str, Any] = {}
            exec(self.code, namespace)
            # Find the function in namespace
            for name, obj in namespace.items():
                if callable(obj) and not name.startswith("_"):
                    self.func = obj
                    break

        if self.func:
            self.metadata.usage_count += 1
            self.metadata.last_used = time.time()
            return self.func(*args, **kwargs)
        else:
            raise ValueError(f"No callable function found in {self.metadata.name}")


class FunctionBuilder:
    """
    Self-building function system inspired by BabyAGI.

    Features:
    - Create functions from natural language descriptions
    - Track function dependencies
    - Organize functions into packs
    - Auto-generate function code using AI
    - Persistent storage of functions
    """

    def __init__(self, storage_dir: str = "~/.castle_wyvern/functions"):
        self.storage_dir = Path(storage_dir).expanduser()
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        self.functions: Dict[str, BuiltFunction] = {}
        self.packs: Dict[str, List[str]] = {}  # pack_name -> function_names

        self._load_functions()

    def _load_functions(self):
        """Load all saved functions from disk."""
        metadata_file = self.storage_dir / "functions.json"
        if metadata_file.exists():
            with open(metadata_file, "r") as f:
                data = json.load(f)
                for func_name, func_data in data.get("functions", {}).items():
                    self._load_function(func_name, func_data)
                self.packs = data.get("packs", {})

    def _load_function(self, name: str, data: dict):
        """Load a single function from disk."""
        code_file = self.storage_dir / f"{name}.py"
        if code_file.exists():
            with open(code_file, "r") as f:
                code = f.read()

            metadata = FunctionMetadata(
                name=name,
                description=data.get("description", ""),
                dependencies=data.get("dependencies", []),
                imports=data.get("imports", []),
                created_at=data.get("created_at", time.time()),
                usage_count=data.get("usage_count", 0),
                last_used=data.get("last_used"),
                tags=data.get("tags", []),
            )

            self.functions[name] = BuiltFunction(metadata=metadata, code=code)

    def _save_functions(self):
        """Save all functions metadata to disk."""
        metadata_file = self.storage_dir / "functions.json"
        data = {"functions": {}, "packs": self.packs}

        for name, func in self.functions.items():
            data["functions"][name] = {
                "description": func.metadata.description,
                "dependencies": func.metadata.dependencies,
                "imports": func.metadata.imports,
                "created_at": func.metadata.created_at,
                "usage_count": func.metadata.usage_count,
                "last_used": func.metadata.last_used,
                "tags": func.metadata.tags,
            }

        with open(metadata_file, "w") as f:
            json.dump(data, f, indent=2)

    def _generate_function_code(self, description: str, imports: List[str] = None) -> str:
        """
        Generate function code from description.

        In production, this would use an LLM. For now, we'll use templates
        for common patterns and a generic fallback.
        """
        description_lower = description.lower()

        # Extract function name from description
        name_match = re.search(
            r"(?:create|make|build|write).*?(?:function|tool|utility).*?(?:to|that|for)?\s+(\w+)",
            description_lower,
        )
        if name_match:
            func_name = name_match.group(1).lower()
        else:
            # Generate from hash
            func_name = (
                f"func_{hashlib.md5(description.encode(), usedforsecurity=False).hexdigest()[:8]}"
            )

        # Check for common patterns
        if (
            "fetch" in description_lower
            or "get" in description_lower
            or "download" in description_lower
        ):
            if (
                "url" in description_lower
                or "web" in description_lower
                or "http" in description_lower
            ):
                return self._generate_fetcher_code(func_name, description, imports)

        if "parse" in description_lower or "extract" in description_lower:
            return self._generate_parser_code(func_name, description, imports)

        if (
            "calculate" in description_lower
            or "compute" in description_lower
            or "math" in description_lower
        ):
            return self._generate_calculator_code(func_name, description, imports)

        if "format" in description_lower or "convert" in description_lower:
            return self._generate_converter_code(func_name, description, imports)

        # Generic fallback
        return self._generate_generic_code(func_name, description, imports)

    def _generate_fetcher_code(self, name: str, description: str, imports: List[str]) -> str:
        """Generate a web fetcher function."""
        return f'''"""
{description}
"""
import requests
from typing import Optional, Dict, Any

def {name}(url: str, params: Optional[Dict] = None, headers: Optional[Dict] = None) -> Any:
    """
    {description}
    
    Args:
        url: URL to fetch
        params: Optional query parameters
        headers: Optional HTTP headers
        
    Returns:
        Response data
    """
    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Try to return JSON if possible
        try:
            return response.json()
        except Exception:
            return response.text
            
    except Exception as e:
        return {{'error': str(e)}}
'''

    def _generate_parser_code(self, name: str, description: str, imports: List[str]) -> str:
        """Generate a parser function."""
        return f'''"""
{description}
"""
import re
from typing import List, Dict, Any

def {name}(text: str) -> List[Dict[str, Any]]:
    """
    {description}
    
    Args:
        text: Text to parse
        
    Returns:
        List of extracted items
    """
    results = []
    
    # TODO: Implement parsing logic based on description
    # This is a template - customize based on needs
    
    # Example: Extract URLs
    if 'url' in """{description}""".lower():
        pattern = r"https?://[^\\s<>\\\"']+|www\\.[^\\s<>\\\"']+"
        matches = re.findall(pattern, text)
        for match in matches:
            results.append({{'type': 'url', 'value': match}})
    
    return results
'''

    def _generate_calculator_code(self, name: str, description: str, imports: List[str]) -> str:
        """Generate a calculator function."""
        return f'''"""
{description}
"""
import math
from typing import List, Union

def {name}(values: List[Union[int, float]]) -> Dict[str, float]:
    """
    {description}
    
    Args:
        values: List of numbers to calculate
        
    Returns:
        Dictionary with calculated statistics
    """
    if not values:
        return {{'error': 'Empty input list'}}
    
    results = {{
        'count': len(values),
        'sum': sum(values),
        'mean': sum(values) / len(values),
        'min': min(values),
        'max': max(values),
    }}
    
    # Standard deviation
    if len(values) > 1:
        mean = results['mean']
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        results['std_dev'] = math.sqrt(variance)
    
    return results
'''

    def _generate_converter_code(self, name: str, description: str, imports: List[str]) -> str:
        """Generate a converter function."""
        return f'''"""
{description}
"""
from typing import Any

def {name}(input_data: Any, output_format: str = 'json') -> Any:
    """
    {description}
    
    Args:
        input_data: Data to convert
        output_format: Target format (json, csv, xml, etc.)
        
    Returns:
        Converted data
    """
    import json
    
    if output_format.lower() == 'json':
        if isinstance(input_data, str):
            # Try to parse from string
            try:
                return json.loads(input_data)
            except Exception:
                return {{'error': 'Invalid JSON input'}}
        else:
            # Convert to JSON string
            return json.dumps(input_data, indent=2)
    
    # Add more format conversions as needed
    return input_data
'''

    def _generate_generic_code(self, name: str, description: str, imports: List[str]) -> str:
        """Generate a generic function template."""
        return f'''"""
{description}
Auto-generated function based on natural language description.
Customize this implementation as needed.
"""
from typing import Any, Dict, List, Optional

def {name}(input_data: Any, **kwargs) -> Any:
    """
    {description}
    
    Args:
        input_data: Input data to process
        **kwargs: Additional keyword arguments
        
    Returns:
        Processed result
    """
    # TODO: Implement the function logic
    # This is a generated template - customize based on your needs
    
    result = {{
        'description': """{description}""",
        'input': input_data,
        'status': 'not_implemented'
    }}
    
    return result
'''

    def create_function(
        self,
        description: str,
        pack: Optional[str] = None,
        imports: List[str] = None,
        tags: List[str] = None,
    ) -> BuiltFunction:
        """
        Create a new function from natural language description.

        Args:
            description: Natural language description of what the function should do
            pack: Optional pack name to organize the function
            imports: Optional list of imports needed
            tags: Optional tags for categorization

        Returns:
            The created BuiltFunction
        """
        # Generate function code
        code = self._generate_function_code(description, imports)

        # Extract function name from code
        name_match = re.search(r"def (\w+)\(", code)
        func_name = name_match.group(1) if name_match else f"func_{int(time.time())}"

        # Detect dependencies from code
        dependencies = []
        if "import requests" in code:
            dependencies.append("requests")
        if "import re" in code:
            dependencies.append("re")
        if "import json" in code:
            dependencies.append("json")

        # Create metadata
        metadata = FunctionMetadata(
            name=func_name,
            description=description,
            dependencies=dependencies,
            imports=imports or [],
            created_at=time.time(),
            tags=tags or [],
        )

        # Create the function
        func = BuiltFunction(metadata=metadata, code=code)

        # Save to storage
        self.functions[func_name] = func
        code_file = self.storage_dir / f"{func_name}.py"
        with open(code_file, "w") as f:
            f.write(code)

        # Add to pack if specified
        if pack:
            if pack not in self.packs:
                self.packs[pack] = []
            self.packs[pack].append(func_name)

        # Save metadata
        self._save_functions()

        return func

    def get_function(self, name: str) -> Optional[BuiltFunction]:
        """Get a function by name."""
        return self.functions.get(name)

    def list_functions(self, pack: Optional[str] = None) -> List[FunctionMetadata]:
        """List all functions, optionally filtered by pack."""
        if pack:
            func_names = self.packs.get(pack, [])
            return [self.functions[name].metadata for name in func_names if name in self.functions]
        else:
            return [func.metadata for func in self.functions.values()]

    def list_packs(self) -> List[str]:
        """List all available packs."""
        return list(self.packs.keys())

    def get_pack_functions(self, pack: str) -> List[BuiltFunction]:
        """Get all functions in a pack."""
        func_names = self.packs.get(pack, [])
        return [self.functions[name] for name in func_names if name in self.functions]

    def search_functions(self, query: str) -> List[FunctionMetadata]:
        """Search functions by description or tags."""
        query_lower = query.lower()
        results = []

        for func in self.functions.values():
            if query_lower in func.metadata.description.lower() or any(
                query_lower in tag.lower() for tag in func.metadata.tags
            ):
                results.append(func.metadata)

        return results

    def get_dependency_graph(self) -> Dict[str, List[str]]:
        """Get the dependency graph of all functions."""
        graph = {}
        for name, func in self.functions.items():
            graph[name] = func.metadata.dependencies
        return graph

    def delete_function(self, name: str) -> bool:
        """Delete a function."""
        if name in self.functions:
            del self.functions[name]

            # Remove code file
            code_file = self.storage_dir / f"{name}.py"
            if code_file.exists():
                code_file.unlink()

            # Remove from packs
            for pack, funcs in self.packs.items():
                if name in funcs:
                    funcs.remove(name)

            self._save_functions()
            return True
        return False


# Standalone usage
if __name__ == "__main__":
    builder = FunctionBuilder()

    # Create a function
    print("Creating function...")
    func = builder.create_function(
        description="Create a function that fetches stock prices from Yahoo Finance",
        pack="finance",
        tags=["finance", "api", "stocks"],
    )

    print(f"\nCreated function: {func.metadata.name}")
    print(f"Description: {func.metadata.description}")
    print(f"\nCode:\n{func.code[:500]}...")

    # List all functions
    print(f"\n\nAll functions:")
    for meta in builder.list_functions():
        print(f"  - {meta.name}: {meta.description[:60]}...")

    # List packs
    print(f"\nPacks: {builder.list_packs()}")

    # Search
    print(f"\nSearch for 'fetch':")
    for meta in builder.search_functions("fetch"):
        print(f"  - {meta.name}")
