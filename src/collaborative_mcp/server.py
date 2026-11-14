from mcp.server import MCPServer

mcp = MCPServer("Collaborative MCP")


@mcp.tool()
def ping() -> str:
    """Check whether the MCP server is responding."""
    return "pong"


if __name__ == "__main__":
    mcp.run()
