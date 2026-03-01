"""Tests for _EmbeddingModel.pre_warm() background loading.

TDD: tests written before implementation.
Verifies that the embedding model starts loading immediately in a background
daemon thread when ObservationMemory is created, so the first agent.run()
call doesn't block waiting for SentenceTransformer to load.
"""

from __future__ import annotations

import threading
import time
from unittest.mock import MagicMock, patch

from familiar_agent.tools.memory import _EmbeddingModel


# ---------------------------------------------------------------------------
# _EmbeddingModel thread-safety and pre_warm tests
# ---------------------------------------------------------------------------


class TestEmbeddingModelPreWarm:
    def test_pre_warm_method_exists(self):
        model = _EmbeddingModel("some-model")
        assert hasattr(model, "pre_warm"), "_EmbeddingModel must have a pre_warm() method"
        assert callable(model.pre_warm)

    def test_pre_warm_starts_background_thread(self):
        """pre_warm() must start a daemon thread named 'embedding-prewarm'."""
        model = _EmbeddingModel("some-model")

        started_threads: list[threading.Thread] = []
        original_start = threading.Thread.start

        def track_start(self_thread):
            started_threads.append(self_thread)
            original_start(self_thread)

        with patch.object(threading.Thread, "start", track_start):
            # Prevent actual model load
            with patch.object(model, "_load"):
                model.pre_warm()

        assert len(started_threads) == 1
        t = started_threads[0]
        assert t.name == "embedding-prewarm"
        assert t.daemon is True

    def test_pre_warm_calls_load(self):
        """pre_warm() must eventually call _load() on the background thread."""
        model = _EmbeddingModel("some-model")
        load_event = threading.Event()

        def fake_load():
            load_event.set()

        with patch.object(model, "_load", fake_load):
            model.pre_warm()
            assert load_event.wait(timeout=2.0), "_load() was not called within 2 seconds"

    def test_lock_attribute_exists(self):
        """_EmbeddingModel must have a _lock attribute (threading.Lock)."""
        model = _EmbeddingModel("some-model")
        assert hasattr(model, "_lock"), "_EmbeddingModel must have a _lock attribute"
        assert isinstance(model._lock, type(threading.Lock()))

    def test_load_is_idempotent_with_lock(self):
        """_load() called concurrently must only instantiate SentenceTransformer once."""
        model = _EmbeddingModel("some-model")
        call_count = 0
        barrier = threading.Barrier(3)  # sync 3 threads to maximize race

        def fake_st(name):
            nonlocal call_count
            call_count += 1
            time.sleep(0.05)  # simulate slow load
            return MagicMock()

        # Patch via sentence_transformers so the local import inside _load picks it up
        with patch("sentence_transformers.SentenceTransformer", fake_st):

            def load_via_barrier():
                barrier.wait()  # all 3 threads arrive simultaneously
                model._load()

            threads = [threading.Thread(target=load_via_barrier) for _ in range(3)]
            for t in threads:
                t.start()
            for t in threads:
                t.join(timeout=3.0)

        # With double-checked locking, SentenceTransformer should be instantiated exactly once
        assert call_count == 1, f"SentenceTransformer instantiated {call_count} times, expected 1"


class TestEmbeddingModelIsReady:
    def test_is_ready_false_before_load(self):
        model = _EmbeddingModel("some-model")
        assert model.is_ready() is False

    def test_is_ready_true_after_load(self):
        model = _EmbeddingModel("some-model")
        with patch("sentence_transformers.SentenceTransformer", return_value=MagicMock()):
            model._load()
        assert model.is_ready() is True

    def test_is_ready_true_after_prewarm_completes(self):
        model = _EmbeddingModel("some-model")
        done = threading.Event()

        original_load = model._load

        def load_and_signal():
            with patch("sentence_transformers.SentenceTransformer", return_value=MagicMock()):
                original_load()
            done.set()

        with patch.object(model, "_load", load_and_signal):
            model.pre_warm()
        done.wait(timeout=2.0)
        assert model.is_ready() is True

    def test_observation_memory_exposes_is_embedding_ready(self, tmp_path):
        from familiar_agent.tools.memory import ObservationMemory

        db_path = str(tmp_path / "test.db")
        with patch.object(_EmbeddingModel, "pre_warm"):
            mem = ObservationMemory(db_path=db_path)
        assert hasattr(mem, "is_embedding_ready")
        assert callable(mem.is_embedding_ready)
        # Before load: should be False
        assert mem.is_embedding_ready() is False


class TestObservationMemoryPreWarm:
    def test_observation_memory_calls_pre_warm_on_init(self, tmp_path):
        """ObservationMemory.__init__ must call _embedder.pre_warm()."""
        from familiar_agent.tools.memory import ObservationMemory

        db_path = str(tmp_path / "test.db")

        with patch.object(_EmbeddingModel, "pre_warm") as mock_pre_warm:
            ObservationMemory(db_path=db_path)

        mock_pre_warm.assert_called_once()

    def test_observation_memory_pre_warm_is_non_blocking(self, tmp_path):
        """ObservationMemory.__init__ must complete quickly (pre_warm is non-blocking)."""
        from familiar_agent.tools.memory import ObservationMemory

        db_path = str(tmp_path / "test.db")
        load_started = threading.Event()
        load_can_proceed = threading.Event()

        def slow_load(self_model):
            load_started.set()
            load_can_proceed.wait(timeout=2.0)

        with patch.object(_EmbeddingModel, "_load", slow_load):
            start = time.monotonic()
            ObservationMemory(db_path=db_path)
            elapsed = time.monotonic() - start

        # __init__ should complete before the slow _load finishes
        assert elapsed < 1.0, f"ObservationMemory.__init__ blocked for {elapsed:.2f}s"
        load_can_proceed.set()  # let the background thread finish
