"""Tests for the generic Commitment store (secretary core)."""

from __future__ import annotations

import pytest

from familiar_runtime.commitments import (
    Commitment,
    CommitmentKind,
    CommitmentStatus,
    SQLiteCommitmentStore,
)


@pytest.fixture
def store(tmp_path):
    s = SQLiteCommitmentStore(tmp_path / "commitments.db")
    yield s
    s.close()


def test_create_and_get(store):
    c = store.create(summary="call dentist", kind=CommitmentKind.REMINDER)
    assert c.id.startswith("commit_")
    assert c.status is CommitmentStatus.OPEN
    assert c.kind is CommitmentKind.REMINDER
    got = store.get(c.id)
    assert got is not None
    assert got.summary == "call dentist"


def test_reload_persists(tmp_path):
    path = tmp_path / "commitments.db"
    s1 = SQLiteCommitmentStore(path)
    c = s1.create(summary="buy milk", due_at=1234.0, priority=2, person="kota")
    s1.close()

    s2 = SQLiteCommitmentStore(path)
    got = s2.get(c.id)
    assert got is not None
    assert got.summary == "buy milk"
    assert got.due_at == 1234.0
    assert got.priority == 2
    assert got.person == "kota"
    s2.close()


def test_list_open_excludes_done_and_cancelled(store):
    a = store.create(summary="a")
    b = store.create(summary="b")
    store.complete(a.id)
    store.cancel(b.id)
    store.create(summary="c")
    assert [x.summary for x in store.list_open()] == ["c"]


def test_due_and_upcoming(store):
    now = 1000.0
    store.create(summary="overdue", due_at=now - 10)
    store.create(summary="soon", due_at=now + 100)
    store.create(summary="far", due_at=now + 10_000)
    store.create(summary="no_due")

    assert [x.summary for x in store.list_due(now=now)] == ["overdue"]
    assert [x.summary for x in store.list_upcoming(now=now, horizon=3600)] == ["soon"]


def test_open_ordering_due_first_then_priority(store):
    now = 1000.0
    store.create(summary="low_due", due_at=now + 50, priority=0)
    store.create(summary="high_due", due_at=now + 10, priority=3)
    store.create(summary="no_due_hi", priority=2)
    store.create(summary="no_due_lo", priority=0)

    ordered = [x.summary for x in store.list_open()]
    # dated commitments first (earliest due), then undated by priority desc
    assert ordered == ["high_due", "low_due", "no_due_hi", "no_due_lo"]


def test_snooze_hides_until_window_then_reappears(store):
    now = 1000.0
    c = store.create(summary="ping", due_at=now - 5)
    assert [x.summary for x in store.list_due(now=now)] == ["ping"]

    store.snooze(c.id, until=now + 100)
    assert store.list_due(now=now) == []
    assert store.get(c.id).status is CommitmentStatus.SNOOZED

    # once the snooze window passes it is due again
    assert [x.summary for x in store.list_due(now=now + 200)] == ["ping"]


def test_complete_sets_timestamp(store):
    c = store.create(summary="done soon")
    done = store.complete(c.id)
    assert done.status is CommitmentStatus.DONE
    assert done.completed_at is not None


def test_update_unknown_id_raises(store):
    with pytest.raises(KeyError):
        store.complete("commit_does_not_exist")


def test_is_due_helper():
    c = Commitment(
        id="x",
        summary="s",
        kind=CommitmentKind.REMINDER,
        status=CommitmentStatus.OPEN,
        due_at=100.0,
    )
    assert c.is_due(now=200.0)
    assert not c.is_due(now=50.0)
    assert c.is_upcoming(now=50.0, horizon=100.0)
    assert not c.is_upcoming(now=50.0, horizon=10.0)
