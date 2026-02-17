"""
Extended Workflow Nodes
Additional node types for the Visual Workflow Builder
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import time
import json


@dataclass
class NodeResult:
    """Result of node execution."""

    success: bool
    output: Any
    error: Optional[str] = None
    execution_time: float = 0.0


class HTTPNode:
    """
    HTTP Request Node
    Makes HTTP requests to external APIs
    """

    def __init__(self, config: Dict[str, Any]):
        self.method = config.get("method", "GET")
        self.url = config.get("url", "")
        self.headers = config.get("headers", {})
        self.body = config.get("body", "")
        self.timeout = config.get("timeout", 30)

    def execute(self, input_data: Any) -> NodeResult:
        """Execute HTTP request."""
        import requests

        start = time.time()
        try:
            # Replace template variables in URL
            url = self._apply_template(self.url, input_data)

            # Replace template variables in body
            body = self._apply_template(self.body, input_data) if self.body else None

            # Parse body as JSON if content-type is application/json
            json_data = None
            if body and self.headers.get("Content-Type") == "application/json":
                try:
                    json_data = json.loads(body)
                    body = None
                except Exception:
                    pass

            response = requests.request(
                method=self.method,
                url=url,
                headers=self.headers,
                data=body,
                json=json_data,
                timeout=self.timeout,
            )

            return NodeResult(
                success=response.status_code < 400,
                output={
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "body": response.text,
                    "json": (
                        response.json()
                        if response.headers.get("content-type", "").startswith("application/json")
                        else None
                    ),
                },
                execution_time=time.time() - start,
            )

        except Exception as e:
            return NodeResult(
                success=False, output=None, error=str(e), execution_time=time.time() - start
            )

    def _apply_template(self, template: str, data: Any) -> str:
        """Apply template variables."""
        if isinstance(data, dict):
            for key, value in data.items():
                template = template.replace(f"{{{key}}}", str(value))
        return template


class ConditionNode:
    """
    Conditional Logic Node
    Routes based on conditions
    """

    def __init__(self, config: Dict[str, Any]):
        self.condition = config.get("condition", "")
        self.true_output = config.get("true_output", "true")
        self.false_output = config.get("false_output", "false")

    def execute(self, input_data: Any) -> NodeResult:
        """Evaluate condition and route accordingly."""
        start = time.time()

        try:
            # Build evaluation context
            context = {"input": input_data}
            if isinstance(input_data, dict):
                context.update(input_data)

            # Evaluate condition (safe eval with limited context)
            result = self._safe_eval(self.condition, context)

            return NodeResult(
                success=True,
                output={
                    "result": result,
                    "route": self.true_output if result else self.false_output,
                    "value": input_data,
                },
                execution_time=time.time() - start,
            )

        except Exception as e:
            return NodeResult(
                success=False,
                output={"route": self.false_output},
                error=str(e),
                execution_time=time.time() - start,
            )

    def _safe_eval(self, condition: str, context: Dict) -> bool:
        """Safely evaluate condition."""
        # Simple condition evaluation
        # Supports: x > y, x == y, x in y, etc.

        condition = condition.strip()

        # Replace common operators
        condition = condition.replace(" AND ", " and ")
        condition = condition.replace(" OR ", " or ")
        condition = condition.replace(" NOT ", " not ")

        try:
            result = eval(condition, {"__builtins__": {}}, context)
            return bool(result)
        except Exception:
            # If eval fails, do string comparison
            return bool(condition)


class LoopNode:
    """
    Loop/Iterator Node
    Iterates over collections
    """

    def __init__(self, config: Dict[str, Any]):
        self.collection_path = config.get("collection_path", "")
        self.max_iterations = config.get("max_iterations", 100)

    def execute(self, input_data: Any) -> NodeResult:
        """Iterate over collection."""
        start = time.time()

        try:
            # Get collection from input
            if self.collection_path:
                collection = self._get_nested_value(input_data, self.collection_path)
            else:
                collection = input_data

            if not isinstance(collection, (list, dict)):
                return NodeResult(
                    success=False,
                    output=None,
                    error=f"Collection must be list or dict, got {type(collection)}",
                    execution_time=time.time() - start,
                )

            # Convert dict to items list if needed
            if isinstance(collection, dict):
                items = list(collection.items())
            else:
                items = list(collection)

            # Limit iterations
            items = items[: self.max_iterations]

            return NodeResult(
                success=True,
                output={
                    "items": items,
                    "count": len(items),
                    "index": 0,
                    "current": items[0] if items else None,
                },
                execution_time=time.time() - start,
            )

        except Exception as e:
            return NodeResult(
                success=False, output=None, error=str(e), execution_time=time.time() - start
            )

    def _get_nested_value(self, data: Any, path: str) -> Any:
        """Get nested dictionary value by path."""
        keys = path.split(".")
        value = data
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None
        return value


class DelayNode:
    """
    Delay/Wait Node
    Pauses workflow execution
    """

    def __init__(self, config: Dict[str, Any]):
        self.delay_seconds = config.get("delay_seconds", 1)

    def execute(self, input_data: Any) -> NodeResult:
        """Wait for specified time."""
        time.sleep(self.delay_seconds)

        return NodeResult(
            success=True,
            output={"delayed_seconds": self.delay_seconds, "input": input_data},
            execution_time=self.delay_seconds,
        )


class TransformNode:
    """
    Data Transformation Node
    Transforms data using templates or functions
    """

    def __init__(self, config: Dict[str, Any]):
        self.transform_type = config.get("transform_type", "template")
        self.template = config.get("template", "")
        self.mapping = config.get("mapping", {})

    def execute(self, input_data: Any) -> NodeResult:
        """Transform input data."""
        start = time.time()

        try:
            if self.transform_type == "template":
                output = self._apply_template(self.template, input_data)
            elif self.transform_type == "mapping":
                output = self._apply_mapping(input_data)
            elif self.transform_type == "json":
                output = json.dumps(input_data, indent=2)
            else:
                output = input_data

            return NodeResult(success=True, output=output, execution_time=time.time() - start)

        except Exception as e:
            return NodeResult(
                success=False, output=None, error=str(e), execution_time=time.time() - start
            )

    def _apply_template(self, template: str, data: Any) -> str:
        """Apply template to data."""
        if isinstance(data, dict):
            for key, value in data.items():
                placeholder = f"{{{key}}}"
                template = template.replace(placeholder, str(value))
        return template

    def _apply_mapping(self, input_data: Any) -> Dict:
        """Apply field mapping."""
        result = {}
        for output_field, input_path in self.mapping.items():
            value = self._get_nested_value(input_data, input_path)
            result[output_field] = value
        return result

    def _get_nested_value(self, data: Any, path: str) -> Any:
        """Get nested value by path."""
        keys = path.split(".")
        value = data
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None
        return value


class VariableNode:
    """
    Variable/Storage Node
    Sets and gets workflow variables
    """

    def __init__(self, config: Dict[str, Any]):
        self.action = config.get("action", "set")  # set or get
        self.variable_name = config.get("variable_name", "")
        self.value = config.get("value", None)

    def execute(self, input_data: Any, variables: Dict[str, Any]) -> NodeResult:
        """Execute variable operation."""
        start = time.time()

        try:
            if self.action == "set":
                # Evaluate value if it's an expression
                if (
                    isinstance(self.value, str)
                    and self.value.startswith("{{")
                    and self.value.endswith("}}")
                ):
                    var_name = self.value[2:-2].strip()
                    value = variables.get(var_name, input_data)
                else:
                    value = self.value if self.value is not None else input_data

                variables[self.variable_name] = value

                return NodeResult(
                    success=True,
                    output={"set": self.variable_name, "value": value},
                    execution_time=time.time() - start,
                )

            elif self.action == "get":
                value = variables.get(self.variable_name)

                return NodeResult(
                    success=True,
                    output={"get": self.variable_name, "value": value},
                    execution_time=time.time() - start,
                )

            else:
                return NodeResult(
                    success=False,
                    output=None,
                    error=f"Unknown action: {self.action}",
                    execution_time=time.time() - start,
                )

        except Exception as e:
            return NodeResult(
                success=False, output=None, error=str(e), execution_time=time.time() - start
            )


# Node factory
NODE_TYPES = {
    "http": HTTPNode,
    "condition": ConditionNode,
    "loop": LoopNode,
    "delay": DelayNode,
    "transform": TransformNode,
    "variable": VariableNode,
}


def create_node(node_type: str, config: Dict[str, Any]):
    """Factory function to create nodes."""
    node_class = NODE_TYPES.get(node_type)
    if node_class:
        return node_class(config)
    return None


# Example usage
if __name__ == "__main__":
    # Test HTTP node
    http = HTTPNode(
        {
            "method": "GET",
            "url": "https://api.github.com/users/github",
            "headers": {"User-Agent": "Castle-Wyvern"},
        }
    )

    result = http.execute({})
    print(f"HTTP Result: {result.success}")
    if result.success:
        print(f"Status: {result.output['status_code']}")

    # Test condition node
    condition = ConditionNode(
        {"condition": "input > 10", "true_output": "big", "false_output": "small"}
    )

    result = condition.execute({"input": 15})
    print(f"\nCondition Result: {result.output}")

    # Test loop node
    loop = LoopNode({"collection_path": "items"})
    result = loop.execute({"items": [1, 2, 3, 4, 5]})
    print(f"\nLoop Result: {result.output}")
