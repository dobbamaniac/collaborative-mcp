import unittest
from pathlib import Path
from uuid import uuid4

from collaborative_mcp.models import (
    FileWrite,
    Operation,
    Permission,
    ShellCommand,
)
from collaborative_mcp.policy import Policy, evaluate


class TestPolicy(unittest.TestCase):
    def setUp(self):
        self.workspace = Path("/tmp/project")
        self.policy = Policy(
            shell_rules=(
                ("pwd", Permission.ALLOW),
                ("printf DENIED", Permission.DENY),
            ),
        )

    def operation(self, action):
        return Operation(
            id=uuid4(),
            workspace=self.workspace,
            action=action,
        )

    def test_allowed_command(self):
        operation = self.operation(
            ShellCommand("pwd", self.workspace)
        )
        self.assertEqual(
            evaluate(operation, self.policy),
            Permission.ALLOW,
        )

    def test_denied_command(self):
        operation = self.operation(
            ShellCommand("printf DENIED", self.workspace)
        )
        self.assertEqual(
            evaluate(operation, self.policy),
            Permission.DENY,
        )

    def test_unknown_command_requires_review(self):
        operation = self.operation(
            ShellCommand("printf TEST", self.workspace)
        )
        self.assertEqual(
            evaluate(operation, self.policy),
            Permission.ASK,
        )

    def test_compound_command_is_not_allowed(self):
        operation = self.operation(
            ShellCommand("pwd && echo TEST", self.workspace)
        )
        self.assertEqual(
            evaluate(operation, self.policy),
            Permission.ASK,
        )

    def test_file_write_requires_review(self):
        operation = self.operation(
            FileWrite(
                path=self.workspace / "example.py",
                content="print('hello')",
            )
        )
        self.assertEqual(
            evaluate(operation, self.policy),
            Permission.ASK,
        )


if __name__ == "__main__":
    unittest.main()
