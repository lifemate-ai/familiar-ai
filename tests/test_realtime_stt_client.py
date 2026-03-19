"""Tests for realtime STT client URL and transcript parsing."""

from __future__ import annotations

from familiar_agent.tools.realtime_stt import _build_stt_ws_url, _extract_transcript_text


def test_build_stt_ws_url_includes_language_code_when_provided() -> None:
    url = _build_stt_ws_url("ja")

    assert "model_id=scribe_v2_realtime" in url
    assert "audio_format=pcm_16000" in url
    assert "tag_audio_events=false" in url
    assert "language_code=ja" in url


def test_build_stt_ws_url_omits_language_code_when_empty() -> None:
    url = _build_stt_ws_url("")

    assert "tag_audio_events=false" in url
    assert "language_code=" not in url


def test_extract_transcript_text_prefers_text_field() -> None:
    assert _extract_transcript_text({"text": " こんにちは "}) == "こんにちは"


def test_extract_transcript_text_falls_back_to_transcript_field() -> None:
    assert _extract_transcript_text({"transcript": " テスト "}) == "テスト"
