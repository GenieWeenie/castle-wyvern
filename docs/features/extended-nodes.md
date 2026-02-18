# Extended Workflow Nodes

Additional node types for the **Visual Workflow Builder**.

## New Node Types

| Node | Purpose |
|------|---------|
| **HTTP** | Make API requests to external services |
| **Condition** | Branch workflow based on logic |
| **Loop** | Iterate over collections |
| **Delay** | Pause execution for N seconds |
| **Transform** | Data mapping and transformation |
| **Variable** | Store and retrieve workflow variables |

## HTTP Node Example

```json
{
  "type": "http",
  "config": {
    "method": "GET",
    "url": "https://api.github.com/users/{username}",
    "headers": {"Authorization": "Bearer {token}"}
  }
}
```

## Condition Node Example

```json
{
  "type": "condition",
  "config": {
    "condition": "input.status_code == 200",
    "true_output": "success_branch",
    "false_output": "error_branch"
  }
}
```
