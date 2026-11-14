from pathlib import Path

from mcp.server import MCPServer

from collaborative_mcp.operations import OperationStore
from collaborative_mcp.policy import load_policy
from collaborative_mcp.tools import register_tools


mcp = MCPServer("Collaborative MCP")

workspace = Path.cwd().resolve()
policy = load_policy(workspace / "config.toml")
store = OperationStore(policy)

register_tools(mcp, store, workspace)


@mcp.tool()
def ping() -> str:
    """Check whether the MCP server is responding."""
    return "pong"


if __name__ == "__main__":
    mcp.run()
