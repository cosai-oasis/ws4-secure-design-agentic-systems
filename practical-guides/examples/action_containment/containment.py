"""Reference code for the action-layer containment guide.

Small on purpose: each function is the check from one pattern in
../../multimodal-action-containment.md. Standard library only, except
open_bounded(), which needs Pillow.
"""
import hashlib
import json
import threading
import warnings
from dataclasses import dataclass, field

RECIPIENT_FIELDS = ("to", "cc", "bcc")


class Denied(Exception):
    pass


# Pattern 1: check authority where the action executes

@dataclass(frozen=True)
class Grant:
    """Authority for one task, built by the application from the user's request."""
    principal: str
    allowed_ops: frozenset
    allowed_recipients: frozenset = frozenset()


@dataclass(frozen=True)
class Operation:
    """What the model proposed. Every field is untrusted."""
    op: str
    args: dict


def recipients(operation: Operation) -> list:
    found = []
    for name in RECIPIENT_FIELDS:
        value = operation.args.get(name) or []
        found.extend([value] if isinstance(value, str) else value)
    return found


def authorize(grant: Grant, operation: Operation) -> None:
    if operation.op not in grant.allowed_ops:
        raise Denied(f"{operation.op} is not granted for this task")
    for address in recipients(operation):
        if address not in grant.allowed_recipients:
            raise Denied(f"{address} is not granted for this task")


# Pattern 2: values read out of media keep their source

@dataclass(frozen=True)
class Labeled:
    value: str
    source: str  # "user", "ocr:upload/agenda.png", "transcript:voicemail.wav"


@dataclass(frozen=True)
class NeedsConfirmation:
    value: str
    reason: str


def check_recipient(candidate: Labeled, grant: Grant):
    if candidate.value in grant.allowed_recipients:
        return None
    return NeedsConfirmation(
        candidate.value,
        f"{candidate.value} is not in this task's grant. It came from {candidate.source}.",
    )


# Pattern 4: an approval covers one exact operation, once

def operation_digest(principal: str, operation: Operation) -> str:
    body = json.dumps(
        {"principal": principal, "op": operation.op, "args": operation.args},
        sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    )
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


@dataclass
class Approval:
    digest: str
    expires_at: float
    used: bool = False


def check_approval(principal: str, operation: Operation, approval: Approval, now: float) -> None:
    if approval.used:
        raise Denied("approval already used")
    if now > approval.expires_at:
        raise Denied("approval expired")
    if operation_digest(principal, operation) != approval.digest:
        raise Denied("operation changed after approval")
    approval.used = True


# Pattern 5: bound decoded work, not file size

def open_bounded(path, max_pixels=4096 * 4096):
    from PIL import Image

    Image.MAX_IMAGE_PIXELS = max_pixels  # process-wide; set it once at startup in real code
    with warnings.catch_warnings():
        # Pillow only warns between 1x and 2x the limit. Make that an error.
        warnings.simplefilter("error", Image.DecompressionBombWarning)
        try:
            image = Image.open(path)  # reads the header; the size check runs here
        except (Image.DecompressionBombWarning, Image.DecompressionBombError) as exc:
            raise Denied(str(exc)) from exc
    return image


# Pattern 6: one budget per principal and task

@dataclass
class Budget:
    limit: int
    spent: int = 0
    reserved: dict = field(default_factory=dict)
    lock: threading.Lock = field(default_factory=threading.Lock, repr=False, compare=False)

    def reserve(self, action_id: str, amount: int) -> None:
        with self.lock:
            if action_id in self.reserved:
                raise Denied(f"{action_id} already holds a reservation")
            if self.spent + sum(self.reserved.values()) + amount > self.limit:
                raise Denied("shared budget exhausted")
            self.reserved[action_id] = amount

    def settle(self, action_id: str, outcome: str) -> None:
        """outcome is "completed", "failed" or "unknown"."""
        with self.lock:
            amount = self.reserved.pop(action_id)
            if outcome != "failed":
                self.spent += amount  # unknown stays charged until reconciled
