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
