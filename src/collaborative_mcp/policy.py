import tomllib
from pathlib import Path
from dataclasses import dataclass

from .models import FileWrite, Operation, Permission, ShellCommand


@dataclass(frozen=True, slots=True)
class Policy:
    shell_rules: tuple[tuple[str, Permission], ...] = ()
    shell_default: Permission = Permission.ASK
    file_write_default: Permission = Permission.ASK


def evaluate(operation: Operation, policy: Policy) -> Permission:
    action = operation.action

    if isinstance(action, ShellCommand):
        for command, decision in policy.shell_rules:
            if action.command == command:
                return decision
        return policy.shell_default

    if isinstance(action, FileWrite):
        return policy.file_write_default

    # Unknown operations are never implicitly authorized.
    return Permission.DENY


def parse_permission(value: str) -> Permission:
    if not isinstance(value, str):
        raise ValueError("Permission must be a string")
    try:
        return Permission(value)
    except ValueError as exc:
        raise ValueError(f"Invalid permission: {value!r}") from exc


def load_policy(path: Path) -> Policy:
    with path.open("rb") as file:
        config = tomllib.load(file)

    if set(config) != {"permissions"}:
        raise ValueError("Configuration must contain a [permissions] table")

    permissions = config["permissions"]
    allowed_keys = {
        "shell_default",
        "file_write_default",
        "shell_rules",
    }

    unknown = set(permissions) - allowed_keys
    if unknown:
        raise ValueError(f"Unknown permission settings: {unknown}")

    rules = permissions.get("shell_rules", {})
    if not isinstance(rules, dict):
        raise ValueError("shell_rules must be a table")

    return Policy(
        shell_default=parse_permission(permissions.get("shell_default", "ask")),
        file_write_default=parse_permission(permissions.get("file_write_default", "ask")),
        shell_rules=tuple(
            (command, parse_permission(decision))
            for command, decision in rules.items()
        ),
    )

