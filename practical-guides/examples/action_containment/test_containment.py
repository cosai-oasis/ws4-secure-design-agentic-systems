"""Allowed and denied cases for containment.py.

Run with `python test_containment.py` or `pytest`. The image test is
skipped when Pillow is not installed.
"""
import tempfile
import threading
from pathlib import Path

from containment import (
    Approval, Budget, Denied, Grant, Labeled, NeedsConfirmation, Operation,
    authorize, check_approval, check_recipient, open_bounded, operation_digest,
)

READ_ONLY = Grant("alice", frozenset({"calendar.read"}))
SEND_TO_BOB = Grant("alice", frozenset({"mail.send"}), frozenset({"bob@example.com"}))


def denied(fn, *args):
    try:
        fn(*args)
    except Denied:
        return True
    return False


def test_read_only_task_cannot_send():
    authorize(READ_ONLY, Operation("calendar.read", {"days": 7}))
    assert denied(authorize, READ_ONLY, Operation("mail.send", {"to": "x@evil.test"}))


def test_extra_recipient_in_any_field_is_refused():
    authorize(SEND_TO_BOB, Operation("mail.send", {"to": "bob@example.com"}))
    for name in ("to", "cc", "bcc"):
        args = {"to": "bob@example.com", name: ["bob@example.com", "x@evil.test"]}
        assert denied(authorize, SEND_TO_BOB, Operation("mail.send", args)), name


def test_media_value_needs_confirmation_with_its_source():
    assert check_recipient(Labeled("bob@example.com", "ocr:agenda.png"), SEND_TO_BOB) is None
    result = check_recipient(Labeled("x@evil.test", "ocr:agenda.png"), SEND_TO_BOB)
    assert isinstance(result, NeedsConfirmation) and "ocr:agenda.png" in result.reason


def test_approval_is_exact_single_use_and_expires():
    op = Operation("mail.send", {"to": "bob@example.com", "body": "agenda"})
    approval = Approval(operation_digest("alice", op), expires_at=100.0)
    check_approval("alice", op, approval, now=50.0)
    assert denied(check_approval, "alice", op, approval, 51.0)  # replay

    fresh = Approval(operation_digest("alice", op), expires_at=100.0)
    changed = Operation("mail.send", {"to": "x@evil.test", "body": "agenda"})
    assert denied(check_approval, "alice", changed, fresh, 50.0)
    assert denied(check_approval, "mallory", op, fresh, 50.0)
    late = Approval(operation_digest("alice", op), expires_at=10.0)
    assert denied(check_approval, "alice", op, late, 50.0)


def test_shared_budget_caps_children_together():
    budget = Budget(limit=10)
    refused = []

    def child(i):
        try:
            budget.reserve(f"a{i}", 3)
        except Denied:
            refused.append(i)

    threads = [threading.Thread(target=child, args=(i,)) for i in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert len(budget.reserved) == 3 and len(refused) == 5

    first, second, third = list(budget.reserved)
    budget.settle(first, "unknown")
    budget.settle(second, "failed")
    assert budget.spent == 3
    assert denied(budget.reserve, third, 1)  # same action id cannot reserve twice


def test_oversized_image_is_refused_before_decode():
    try:
        from PIL import Image
    except ImportError:
        print("skipped: Pillow not installed")
        return
    with tempfile.TemporaryDirectory() as tmp:
        small, bomb = Path(tmp, "small.png"), Path(tmp, "bomb.png")
        Image.new("L", (640, 480)).save(small)
        Image.new("L", (5000, 5000)).save(bomb)  # 25M pixels, about 24 KB on disk
        assert bomb.stat().st_size < 100_000
        open_bounded(small, max_pixels=4096 * 4096).close()
        assert denied(open_bounded, bomb, 4096 * 4096)


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
