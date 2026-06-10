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


# ── proactive-reminder cadence (Phase 3) ──

BASE = 600.0


def test_reminder_columns_persist(tmp_path):
    path = tmp_path / "commitments.db"
    s1 = SQLiteCommitmentStore(path)
    c = s1.create(summary="ping", due_at=10.0)
    s1.mark_reminded([c.id], at=100.0)
    s1.close()

    s2 = SQLiteCommitmentStore(path)
    got = s2.get(c.id)
    assert got.last_reminded_at == 100.0
    assert got.reminder_count == 1
    s2.close()


def test_mark_reminded_increments(store):
    c = store.create(summary="ping", due_at=10.0)
    store.mark_reminded([c.id], at=100.0)
    store.mark_reminded([c.id], at=200.0)
    got = store.get(c.id)
    assert got.reminder_count == 2
    assert got.last_reminded_at == 200.0


def test_due_for_reminder_first_time_fires(store):
    now = 10_000.0
    store.create(summary="fresh", due_at=now - 5)
    ready = store.list_due_for_reminder(now=now, base_cooldown=BASE)
    assert [c.summary for c in ready] == ["fresh"]


def test_due_for_reminder_respects_backoff(store):
    now = 10_000.0
    c = store.create(summary="ping", due_at=now - 5)
    store.mark_reminded([c.id], at=now)
    # within base cooldown → not yet
    assert store.list_due_for_reminder(now=now + BASE / 2, base_cooldown=BASE) == []
    # after base cooldown → fires again (2nd)
    assert len(store.list_due_for_reminder(now=now + BASE + 1, base_cooldown=BASE)) == 1


def test_due_for_reminder_escalates_and_caps(store):
    now = 10_000.0
    c = store.create(summary="ping", due_at=now - 5)
    # 1st fire
    store.mark_reminded([c.id], at=now)
    # 2nd fire after 1x base
    t2 = now + BASE + 1
    assert store.list_due_for_reminder(now=t2, base_cooldown=BASE)
    store.mark_reminded([c.id], at=t2)
    # 3rd needs 3x base; 1x is not enough
    assert store.list_due_for_reminder(now=t2 + BASE + 1, base_cooldown=BASE) == []
    t3 = t2 + 3 * BASE + 1
    assert store.list_due_for_reminder(now=t3, base_cooldown=BASE)
    store.mark_reminded([c.id], at=t3)
    # capped at 3 reminders → goes quiet forever
    assert store.list_due_for_reminder(now=t3 + 100 * BASE, base_cooldown=BASE) == []
    # but it is still surfaced for passive context
    assert store.list_due(now=t3 + 100 * BASE)


def test_due_for_reminder_clamps_inconsistent_zero_count():
    """count=0 with last_reminded_at set (unreachable via the public API) must use
    the base factor (1.0), not silently pick the longest backoff via idx=-1."""
    now = 10_000.0
    c = Commitment(
        id="x",
        summary="s",
        kind=CommitmentKind.REMINDER,
        status=CommitmentStatus.OPEN,
        due_at=now - 5,
        last_reminded_at=now - 1.5 * BASE,  # past 1.0*BASE, well short of 3.0*BASE
        reminder_count=0,
    )
    assert c.due_for_reminder(now=now, base_cooldown=BASE)


def test_snooze_resets_reminder_cadence(store):
    now = 10_000.0
    c = store.create(summary="ping", due_at=now - 5)
    store.mark_reminded([c.id], at=now)
    store.mark_reminded([c.id], at=now + BASE + 1)
    store.snooze(c.id, until=now + 10)
    got = store.get(c.id)
    assert got.reminder_count == 0
    assert got.last_reminded_at is None


def test_legacy_db_without_reminder_columns_migrates(tmp_path):
    import sqlite3

    path = tmp_path / "old.db"
    conn = sqlite3.connect(str(path))
    conn.executescript(
        """
        CREATE TABLE runtime_commitments (
            id TEXT PRIMARY KEY,
            summary TEXT NOT NULL,
            kind TEXT NOT NULL,
            status TEXT NOT NULL,
            due_at REAL,
            priority INTEGER NOT NULL,
            created_by TEXT NOT NULL,
            person TEXT,
            created_at REAL NOT NULL,
            updated_at REAL NOT NULL,
            completed_at REAL,
            snooze_until REAL,
            metadata_json TEXT NOT NULL
        );
        """
    )
    conn.execute(
        "INSERT INTO runtime_commitments VALUES "
        "('commit_old', 'legacy', 'reminder', 'open', 5.0, 0, 'user', NULL, "
        "1.0, 1.0, NULL, NULL, '{}')"
    )
    conn.commit()
    conn.close()

    store = SQLiteCommitmentStore(path)
    got = store.get("commit_old")
    assert got is not None
    assert got.reminder_count == 0
    assert got.last_reminded_at is None
    # the migrated DB supports the new reminder query
    assert [c.summary for c in store.list_due_for_reminder(now=100.0, base_cooldown=BASE)] == [
        "legacy"
    ]
    store.close()
