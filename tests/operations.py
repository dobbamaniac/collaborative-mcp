import unittest
from pathlib import Path
from uuid import uuid4

from collaborative_mcp.models import (
    FileWrite,
    Operation,
    Permission,
    ShellCommand,
)
from collaborative_mcp.operations import OperationStore, ReviewStatus
from collaborative_mcp.policy import Policy


class TestOperationStore(unittest.TestCase):
    def setUp(self):
        self.workspace = Path("/tmp/project")
        self.store = OperationStore(
            Policy(
                shell_rules=(
                    ("pwd", Permission.ALLOW),
                    ("printf DENIED", Permission.DENY),
                ),
            )
        )

    def operation(self, command: str) -> Operation:
        return Operation(
            id=uuid4(),
            workspace=self.workspace,
            action=ShellCommand(command, self.workspace),
        )

    def test_policy_decisions(self):
        allowed = self.store.submit(self.operation("pwd"))
        pending = self.store.submit(self.operation("printf BEFORE"))
        denied = self.store.submit(self.operation("printf DENIED"))

        self.assertEqual(allowed.status, ReviewStatus.APPROVED)
        self.assertEqual(pending.status, ReviewStatus.PENDING)
        self.assertEqual(denied.status, ReviewStatus.DENIED)

    def test_edited_approval(self):
        operation = self.operation("printf BEFORE")
        self.store.submit(operation)

        result = self.store.approve(
            operation.id,
            action=ShellCommand("printf AFTER", self.workspace),
            feedback="Use AFTER instead",
        )

        self.assertEqual(result.status, ReviewStatus.APPROVED)
        self.assertEqual(result.original.action.command, "printf BEFORE")
        self.assertEqual(result.approved.action.command, "printf AFTER")
        self.assertEqual(result.feedback, "Use AFTER instead")
        self.assertEqual(result.approved.id, operation.id)

    def test_denial(self):
        operation = self.operation("printf TEST")
        self.store.submit(operation)

        result = self.store.deny(operation.id, "Not needed")

        self.assertEqual(result.status, ReviewStatus.DENIED)
        self.assertIsNone(result.approved)
        self.assertEqual(result.feedback, "Not needed")

    def test_cannot_review_twice(self):
        operation = self.operation("printf TEST")
        self.store.submit(operation)
        self.store.approve(operation.id)

        with self.assertRaises(ValueError):
            self.store.approve(operation.id)

        with self.assertRaises(ValueError):
            self.store.deny(operation.id)

    def test_duplicate_id_rejected(self):
        operation = self.operation("printf TEST")
        self.store.submit(operation)

        with self.assertRaises(ValueError):
            self.store.submit(operation)

    def test_denied_operation_cannot_be_approved(self):
        operation = self.operation("printf DENIED")
        self.store.submit(operation)

        with self.assertRaises(ValueError):
            self.store.approve(operation.id)

    def test_cannot_change_action_type(self):
        operation = self.operation("printf TEST")
        self.store.submit(operation)

        with self.assertRaises(ValueError):
            self.store.approve(
                operation.id,
                action=FileWrite(
                    path=self.workspace / "test.py",
                    content="print('hello')",
                ),
            )


if __name__ == "__main__":
    unittest.main()
