from pathlib import Path
from uuid import uuid4

from mcp.server import MCPServer

from .models import Operation, ShellCommand
from .operations import OperationStore


def register_tools(
    mcp: MCPServer,
    store: OperationStore,
    workspace: Path,
) -> None:
    @mcp.tool()
    def shell_command(command: str) -> dict[str, str]:
        """Request a shell command. Currently stages it without executing."""
        if not command.strip():
            raise ValueError("Command cannot be empty")

        operation = Operation(
            id=uuid4(),
            workspace=workspace,
            action=ShellCommand(
                command=command,
                cwd=workspace,
            ),
        )

        record = store.submit(operation)

        return {
            "operation_id": str(operation.id),
            "command": command,
            "permission": record.permission.value,
            "status": record.status.value,
        }
