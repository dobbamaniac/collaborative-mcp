from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from uuid import UUID


class Permission(StrEnum):
    ALLOW = "allow"
    ASK = "ask"
    DENY = "deny"


@dataclass(frozen=True, slots=True)
class ShellCommand:
    command: str
    cwd: Path


@dataclass(frozen=True, slots=True)
class FileWrite:
    path: Path
    content: str
    expected_sha256: str | None = None


Action = ShellCommand | FileWrite


@dataclass(frozen=True, slots=True)
class Operation:
    id: UUID
    workspace: Path
    action: Action
