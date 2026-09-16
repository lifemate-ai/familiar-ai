"""Tests for TTS/STT self-loop guard logic."""

from __future__ import annotations

from familiar_agent.voice_guard import VoiceLoopGuard


def test_voice_guard_blocks_self_echo_during_speaking(monkeypatch) -> None:
    ts = iter([10.0, 10.1])
    monkeypatch.setattr("familiar_agent.voice_guard._guard_now", lambda: next(ts))

    guard = VoiceLoopGuard()
    guard.on_tts_start("[cheerful] こんにちは")

    decision = guard.check_transcript("こんにちは")

    assert decision.blocked is True
    assert decision.reason == "tts_active"
    assert decision.should_restart is False


def test_voice_guard_blocks_recent_self_echo_after_tts(monkeypatch) -> None:
    ts = iter([20.0, 20.2, 20.4, 22.0])
    monkeypatch.setattr("familiar_agent.voice_guard._guard_now", lambda: next(ts))

    guard = VoiceLoopGuard(suppression_window_secs=1.0)
    guard.on_tts_start("今日はいい天気だね")
    guard.on_tts_end("今日はいい天気だね", played=True)

    blocked = guard.check_transcript("今日はいい天気だね。")
    allowed = guard.check_transcript("窓を開ける？")

    assert blocked.blocked is True
    assert blocked.reason == "tts_suppression"
    assert allowed.blocked is False


def test_voice_guard_requests_watchdog_restart_after_repeated_echo(monkeypatch) -> None:
    ts = iter([30.0, 30.1, 30.3, 30.6, 30.9])
    monkeypatch.setattr("familiar_agent.voice_guard._guard_now", lambda: next(ts))

    guard = VoiceLoopGuard(suppression_window_secs=2.0, loop_trigger_count=3)
    guard.on_tts_start("おはよう")
    guard.on_tts_end("おはよう", played=True)

    first = guard.check_transcript("おはよう")
    second = guard.check_transcript("おはよう")
    third = guard.check_transcript("おはよう")

    assert first.should_restart is False
    assert second.should_restart is False
    assert third.should_restart is True
    assert guard.loop_counter == 3
