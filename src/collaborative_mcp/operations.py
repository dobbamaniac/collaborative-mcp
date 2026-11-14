from dataclasses import dataclass, replace
from enum import StrEnum
from threading import Lock
from uuid import UUID

from .models import Action, Operation, Permission
from .policy import Policy, evaluate


class ReviewStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"


@dataclass(frozen=True, slots=True)
class OperationRecord:
    original: Operation
    permission: Permission
    status: ReviewStatus
    approved: Operation | None = None
    feedback: str = ""


class OperationStore:
    def __init__(self, policy: Policy):
        self._policy = policy
        self._records: dict[UUID, OperationRecord] = {}
        self._lock = Lock()

    def submit(self, operation: Operation) -> OperationRecord:
        permission = evaluate(operation, self._policy)

        status = {
            Permission.ALLOW: ReviewStatus.APPROVED,
            Permission.ASK: ReviewStatus.PENDING,
            Permission.DENY: ReviewStatus.DENIED,
        }[permission]

        record = OperationRecord(
            original=operation,
            permission=permission,
            status=status,
            approved=operation if permission == Permission.ALLOW else None,
        )

        with self._lock:
            if operation.id in self._records:
                raise ValueError("Operation ID already exists")

            self._records[operation.id] = record

        return record

    def get(self, operation_id: UUID) -> OperationRecord:
        with self._lock:
            return self._records[operation_id]

    def approve(
        self,
        operation_id: UUID,
        action: Action | None = None,
        feedback: str = "",
    ) -> OperationRecord:
        with self._lock:
            record = self._records[operation_id]

            if record.status != ReviewStatus.PENDING:
                raise ValueError("Operation is not pending review")

            final_action = action if action is not None else record.original.action

            if type(final_action) is not type(record.original.action):
                raise ValueError("Cannot change the operation type")

            approved = replace(record.original, action=final_action)

            updated = replace(
                record,
                status=ReviewStatus.APPROVED,
                approved=approved,
                feedback=feedback,
            )

            self._records[operation_id] = updated
            return updated

    def deny(
        self,
        operation_id: UUID,
        feedback: str = "",
    ) -> OperationRecord:
        with self._lock:
            record = self._records[operation_id]

            if record.status != ReviewStatus.PENDING:
                raise ValueError("Operation is not pending review")

            updated = replace(
                record,
                status=ReviewStatus.DENIED,
                feedback=feedback,
            )

            self._records[operation_id] = updated
            return updated
