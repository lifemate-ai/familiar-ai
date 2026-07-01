"""WakeListener + wait_input_or_wake — precedence and degradation contracts.

The invariants pinned here: input always beats wake; a wake is
indistinguishable from an early poll (kind only, no side effects); a missing
or disabled daemon leaves the historical wait_for(queue.get(), timeout)
behavior fully intact — including the None shutdown sentinel staying
distinguishable from a timeout.
"""

from __future__ import annotations

import asyncio
import sys
import tempfile
from pathlib import Path

import pytest

from familiar_agent.wake import WakeListener, wait_input_or_wake


@pytest.mark.asyncio
async def test_disabled_listener_behaves_like_plain_timeout():
    queue: asyncio.Queue = asyncio.Queue()
    listener = WakeListener(enabled=False)

    kind, item = await wait_input_or_wake(queue, listener, 0.05)
    assert (kind, item) == ("timeout", None)

    await queue.put("hello")
    kind, item = await wait_input_or_wake(queue, listener, 0.05)
    assert (kind, item) == ("input", "hello")


@pytest.mark.asyncio
async def test_none_sentinel_stays_distinguishable_from_timeout():
    """The queue's None shutdown sentinel must arrive as kind='input'."""
    queue: asyncio.Queue = asyncio.Queue()
    await queue.put(None)
    kind, item = await wait_input_or_wake(queue, None, 0.05)
    assert kind == "input"
    assert item is None


@pytest.mark.asyncio
async def test_no_listener_argument_is_plain_wait():
    queue: asyncio.Queue = asyncio.Queue()
    kind, item = await wait_input_or_wake(queue, None, 0.05)
    assert (kind, item) == ("timeout", None)


@pytest.mark.skipif(sys.platform == "win32", reason="Unix sockets unavailable on Windows")
@pytest.mark.asyncio
async def test_enabled_listener_missing_socket_degrades_to_timeout():
    """Daemon enabled but not running: wait() must degrade to a timeout."""
    missing = Path(tempfile.mkdtemp(prefix="fam-", dir="/tmp")) / "nope.sock"
    queue: asyncio.Queue = asyncio.Queue()
    listener = WakeListener(missing, enabled=True)

    kind, item = await wait_input_or_wake(queue, listener, 0.3)
    assert (kind, item) == ("timeout", None)

    # Input still wins while the connection keeps failing.
    await queue.put("typed")
    kind, item = await wait_input_or_wake(queue, listener, 0.3)
    assert (kind, item) == ("input", "typed")
    listener.close()


@pytest.mark.skipif(sys.platform == "win32", reason="Unix sockets unavailable on Windows")
@pytest.mark.asyncio
async def test_wake_event_reported_and_input_beats_wake():
    """A pushed wake surfaces as kind='wake'; racing input takes precedence."""
    short_dir = Path(tempfile.mkdtemp(prefix="fam-", dir="/tmp"))
    sock = short_dir / "wake.sock"

    writers: list[asyncio.StreamWriter] = []

    async def _on_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        writers.append(writer)
        while not reader.at_eof():
            data = await reader.read(64)
            if not data:
                break

    server = await asyncio.start_unix_server(_on_client, path=str(sock))
    try:
        queue: asyncio.Queue = asyncio.Queue()
        listener = WakeListener(sock, enabled=True)

        # Connect (first wait times out with no event).
        assert await listener.wait(0.2) is None
        assert writers

        writers[0].write(b'{"type": "wake", "reason": "reminder", "ts": 1.0}\n')
        kind, event = await wait_input_or_wake(queue, listener, 2.0)
        assert kind == "wake"
        assert event.reason == "reminder"

        # Input queued before the call wins over a simultaneous wake.
        await queue.put("user says hi")
        writers[0].write(b'{"type": "wake", "reason": "desire", "ts": 2.0}\n')
        kind, item = await wait_input_or_wake(queue, listener, 2.0)
        assert (kind, item) == ("input", "user says hi")

        # Garbage lines are skipped, valid events still arrive.
        writers[0].write(b"not json\n")
        writers[0].write(b'{"type": "wake", "reason": "band_tick", "ts": 3.0}\n')
        event2 = await listener.wait(2.0)
        assert event2 is not None and event2.reason == "band_tick"

        listener.close()
    finally:
        server.close()
        await server.wait_closed()
