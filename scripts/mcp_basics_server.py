from mcp.server import MCPServer


mcp = MCPServer("MCP Basics Demo")


@mcp.tool()
def add(
    a: int,
    b: int,
) -> int:
    """Add two integers."""
    return a + b


@mcp.resource("health://welcome")
def health_welcome() -> str:
    """Return a simple health-agent resource."""
    return "This is the AI Health Agent MCP demo resource."


@mcp.prompt()
def explain_health_metric(
    metric: str,
) -> str:
    """Create a prompt for explaining a health metric."""
    return f"Explain the following health metric in plain language: {metric}"


if __name__ == "__main__":
    mcp.run()
