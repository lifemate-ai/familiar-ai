"""Observation and emotional memory - SQLite + multilingual-e5-small embeddings.

Architecture inspired by memory-mcp (Phase 11: SQLite+numpy).
- Fast startup: no heavy DB server
- Semantic search: multilingual-e5-small (~117MB, lazy loaded)
- Hybrid: vector similarity + LIKE keyword fallback
- Two memory types: observations (what I saw) + feelings (what I felt)
"""

from __future__ import annotations

import asyncio
import json
import logging
import sqlite3
import threading
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import numpy as np
from ..sqlite_migrations import apply_migrations, default_migration_dir

logger = logging.getLogger(__name__)

DB_PATH = str(Path.home() / ".familiar_ai" / "observations.db")
EMBEDDING_MODEL = "intfloat/multilingual-e5-small"

_THUMB_SIZE = (320, 240)


def _encode_image(image_path: str) -> str | None:
    """Encode image to base64 thumbnail for storage."""
    try:
        import base64
        import io

        from PIL import Image

        with Image.open(image_path) as img:
            img.thumbnail(_THUMB_SIZE, Image.Resampling.LANCZOS)
            buf = io.BytesIO()
            img.convert("RGB").save(buf, format="JPEG", quality=60)
            return base64.b64encode(buf.getvalue()).decode()
    except Exception as e:
        logger.warning("Failed to encode image %s: %s", image_path, e)
        return None


# ── vector helpers ────────────────────────────────────────────


def _cosine_similarity(query: np.ndarray, corpus: np.ndarray) -> np.ndarray:
    q_norm = query / (np.linalg.norm(query) + 1e-10)
    c_norm = corpus / (np.linalg.norm(corpus, axis=1, keepdims=True) + 1e-10)
    return c_norm @ q_norm


def _encode_vector(vec: list[float]) -> bytes:
    return np.array(vec, dtype=np.float32).tobytes()


def _decode_vector(blob: bytes) -> np.ndarray:
    return np.frombuffer(blob, dtype=np.float32)


# ── lazy embedding model ──────────────────────────────────────


class _EmbeddingModel:
    """Lazy-loaded multilingual-e5-small.

    Thread-safe: multiple threads may call _load() concurrently (e.g. when
    pre_warm() races with the first encode call).  Double-checked locking
    ensures SentenceTransformer is instantiated exactly once.
    """

    def __init__(self, model_name: str = EMBEDDING_MODEL):
        self._model_name = model_name
        self._model: Any = None
        self._lock = threading.Lock()
        self._load_event = threading.Event()

    def _load(self) -> None:
        if self._model is not None:
            return  # fast path — already loaded, no lock needed
        with self._lock:
            if self._model is None:  # double-checked locking
                import logging as _logging

                _logging.getLogger("sentence_transformers").setLevel(_logging.ERROR)
                _logging.getLogger("huggingface_hub").setLevel(_logging.ERROR)
                # transformers uses propagate=False so we must use its own API
                import transformers as _transformers

                _transformers.logging.set_verbosity_error()
                from sentence_transformers import SentenceTransformer

                logger.info("Loading embedding model %s...", self._model_name)
                self._model = SentenceTransformer(self._model_name)
                logger.info("Embedding model loaded.")
                self._load_event.set()

    def pre_warm(self) -> None:
        """Start loading the embedding model in a background daemon thread.

        Returns immediately.  The model will be ready by the time the first
        encode call arrives (assuming enough startup lead time).
        """
        t = threading.Thread(target=self._load, daemon=True, name="embedding-prewarm")
        t.start()

    def is_ready(self) -> bool:
        """Return True once the embedding model has finished loading."""
        return self._load_event.is_set()

    def encode_document(self, texts: list[str]) -> list[list[float]]:
        self._load()
        prefixed = [f"passage: {t}" for t in texts]
        return self._model.encode(
            prefixed, normalize_embeddings=True, show_progress_bar=False
        ).tolist()

    def encode_query(self, texts: list[str]) -> list[list[float]]:
        self._load()
        prefixed = [f"query: {t}" for t in texts]
        return self._model.encode(
            prefixed, normalize_embeddings=True, show_progress_bar=False
        ).tolist()


# ── ObservationMemory ─────────────────────────────────────────


class ObservationMemory:
    """SQLite + vector embedding memory for observations and feelings."""

    def __init__(self, db_path: str = DB_PATH, model_name: str = EMBEDDING_MODEL):
        self._db_path = db_path
        self._db: sqlite3.Connection | None = None
        self._db_lock = threading.Lock()  # serialize concurrent thread-pool access
        self._embedder = _EmbeddingModel(model_name)
        self._embedder.pre_warm()  # start loading in background immediately

    def is_embedding_ready(self) -> bool:
        """Return True once the embedding model has finished loading."""
        return self._embedder.is_ready()

    def close(self) -> None:
        """Commit pending writes and close the SQLite connection."""
        with self._db_lock:
            if self._db is not None:
                try:
                    self._db.commit()
                    self._db.close()
                except Exception:
                    pass
                finally:
                    self._db = None

    def _ensure_connected(self) -> sqlite3.Connection:
        if self._db is None:
            Path(self._db_path).parent.mkdir(parents=True, exist_ok=True)
            self._db = sqlite3.connect(self._db_path, check_same_thread=False)
            self._db.row_factory = sqlite3.Row
            self._db.execute("PRAGMA journal_mode = WAL")
            self._db.execute("PRAGMA synchronous = NORMAL")
            self._db.execute("PRAGMA foreign_keys = ON")
            apply_migrations(self._db, default_migration_dir())
            self._db.commit()
        return self._db

    @staticmethod
    def _now_iso() -> str:
        return datetime.now().isoformat()

    @staticmethod
    def _serialize_event_payload(payload: dict[str, Any]) -> str:
        return json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True)

    def _enqueue_memory_job_locked(
        self,
        db: sqlite3.Connection,
        event_id: str,
        job_type: str,
        now_iso: str,
    ) -> bool:
        """Insert a pending job for an event. Returns False when duplicate."""
        try:
            db.execute(
                "INSERT INTO memory_jobs "
                "(job_id, event_id, job_type, status, attempts, available_at, last_error, created_at, updated_at) "
                "VALUES (?, ?, ?, 'pending', 0, ?, NULL, ?, ?)",
                (str(uuid.uuid4()), event_id, job_type, now_iso, now_iso, now_iso),
            )
            return True
        except sqlite3.IntegrityError:
            return False

    def append_memory_event(
        self,
        event_type: str,
        payload: dict[str, Any],
        dedupe_key: str | None = None,
        queue_job: bool = True,
        job_type: str = "materialize_observation",
    ) -> tuple[str | None, bool]:
        """Append a durable memory event and optional pending job.

        Returns:
            (event_id, created_new). If dedupe_key matches an existing event,
            created_new is False and the existing event_id is returned.
        """
        now_iso = self._now_iso()
        payload_json = self._serialize_event_payload(payload)
        try:
            with self._db_lock:
                db = self._ensure_connected()
                if dedupe_key:
                    row = db.execute(
                        "SELECT event_id FROM memory_events WHERE dedupe_key = ?",
                        (dedupe_key,),
                    ).fetchone()
                    if row:
                        event_id = str(row["event_id"])
                        if queue_job:
                            self._enqueue_memory_job_locked(db, event_id, job_type, now_iso)
                        db.commit()
                        return event_id, False

                event_id = str(uuid.uuid4())
                db.execute(
                    "INSERT INTO memory_events (event_id, created_at, event_type, dedupe_key, payload_json) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (event_id, now_iso, event_type, dedupe_key, payload_json),
                )
                if queue_job:
                    self._enqueue_memory_job_locked(db, event_id, job_type, now_iso)
                db.commit()
                return event_id, True
        except Exception as e:
            logger.warning("Failed to append memory event (%s): %s", event_type, e)
            return None, False

    async def append_memory_event_async(
        self,
        event_type: str,
        payload: dict[str, Any],
        dedupe_key: str | None = None,
        queue_job: bool = True,
        job_type: str = "materialize_observation",
    ) -> tuple[str | None, bool]:
        return await asyncio.to_thread(
            self.append_memory_event,
            event_type,
            payload,
            dedupe_key,
            queue_job,
            job_type,
        )

    def claim_pending_jobs(self, limit: int = 10) -> list[dict[str, Any]]:
        """Claim pending memory jobs and mark them as running."""
        now_iso = self._now_iso()
        claimed: list[dict[str, Any]] = []
        with self._db_lock:
            db = self._ensure_connected()
            rows = db.execute(
                "SELECT j.job_id, j.event_id, j.job_type, j.attempts, "
                "e.event_type, e.payload_json "
                "FROM memory_jobs j JOIN memory_events e ON e.event_id = j.event_id "
                "WHERE j.status = 'pending' AND j.available_at <= ? "
                "ORDER BY j.created_at ASC LIMIT ?",
                (now_iso, limit),
            ).fetchall()
            for row in rows:
                updated = db.execute(
                    "UPDATE memory_jobs SET status = 'running', attempts = attempts + 1, updated_at = ? "
                    "WHERE job_id = ? AND status = 'pending'",
                    (now_iso, row["job_id"]),
                )
                if updated.rowcount != 1:
                    continue
                payload: dict[str, Any]
                try:
                    payload = json.loads(row["payload_json"])
                except Exception:
                    payload = {"raw_payload": row["payload_json"]}
                claimed.append(
                    {
                        "job_id": row["job_id"],
                        "event_id": row["event_id"],
                        "job_type": row["job_type"],
                        "attempts": int(row["attempts"]) + 1,
                        "event_type": row["event_type"],
                        "payload": payload,
                    }
                )
            db.commit()
        return claimed

    def mark_job_done(self, job_id: str) -> bool:
        """Mark a running job as done."""
        now_iso = self._now_iso()
        with self._db_lock:
            db = self._ensure_connected()
            updated = db.execute(
                "UPDATE memory_jobs SET status = 'done', updated_at = ?, last_error = NULL "
                "WHERE job_id = ?",
                (now_iso, job_id),
            )
            db.commit()
            return updated.rowcount == 1

    def mark_job_failed(
        self,
        job_id: str,
        error: str,
        retry_delay_sec: float = 10.0,
        max_attempts: int = 3,
    ) -> str:
        """Mark a running job as pending retry or dead_letter.

        Returns the resulting status: 'pending', 'dead_letter', or 'missing'.
        """
        now = datetime.now()
        now_iso = now.isoformat()
        with self._db_lock:
            db = self._ensure_connected()
            row = db.execute(
                "SELECT attempts FROM memory_jobs WHERE job_id = ?",
                (job_id,),
            ).fetchone()
            if row is None:
                return "missing"

            attempts = int(row["attempts"])
            if attempts >= max_attempts:
                status = "dead_letter"
                available_at = now_iso
            else:
                status = "pending"
                available_at = (now + timedelta(seconds=max(retry_delay_sec, 0.0))).isoformat()

            db.execute(
                "UPDATE memory_jobs SET status = ?, available_at = ?, last_error = ?, updated_at = ? "
                "WHERE job_id = ?",
                (status, available_at, error[:500], now_iso, job_id),
            )
            db.commit()
            return status

    def _materialize_memory_save_event(self, event_id: str, payload: dict[str, Any]) -> bool:
        """Materialize a memory.save payload into observations + embeddings."""
        content = str(payload.get("content", "")).strip()
        if not content:
            logger.warning("memory.save event missing content (event_id=%s)", event_id)
            return False

        direction = str(payload.get("direction", "unknown"))
        kind = str(payload.get("kind", "observation"))
        emotion = str(payload.get("emotion", "neutral"))
        image_path = payload.get("image_path")
        override_date = payload.get("override_date")

        # Compute embedding and thumbnail outside lock (CPU/IO)
        image_data = _encode_image(image_path) if image_path else None
        vec = self._embedder.encode_document([content])[0]
        blob = _encode_vector(vec)
        now = datetime.now()
        if override_date:
            save_date = str(override_date)
            save_time = "23:59"
            save_timestamp = f"{save_date}T23:59:59"
        else:
            save_date = now.strftime("%Y-%m-%d")
            save_time = now.strftime("%H:%M")
            save_timestamp = now.isoformat()

        with self._db_lock:
            db = self._ensure_connected()
            exists = db.execute(
                "SELECT 1 FROM observations WHERE id = ?",
                (event_id,),
            ).fetchone()
            if exists:
                return True
            db.execute(
                "INSERT INTO observations "
                "(id, content, timestamp, date, time, direction, kind, emotion, image_path, image_data) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    event_id,
                    content,
                    save_timestamp,
                    save_date,
                    save_time,
                    direction,
                    kind,
                    emotion,
                    image_path,
                    image_data,
                ),
            )
            db.execute(
                "INSERT INTO obs_embeddings (obs_id, vector) VALUES (?, ?)",
                (event_id, blob),
            )
            db.commit()
        return True

    def materialize_event(self, event_id: str) -> bool:
        """Materialize an event into queryable memory rows."""
        try:
            with self._db_lock:
                db = self._ensure_connected()
                row = db.execute(
                    "SELECT event_type, payload_json FROM memory_events WHERE event_id = ?",
                    (event_id,),
                ).fetchone()
            if row is None:
                logger.warning("No memory event found for event_id=%s", event_id)
                return False

            payload = json.loads(row["payload_json"])
            event_type = row["event_type"]
            if event_type == "memory.save":
                return self._materialize_memory_save_event(event_id, payload)

            logger.warning("Unsupported memory event type: %s", event_type)
            return False
        except Exception as e:
            logger.warning("Failed to materialize event %s: %s", event_id, e)
            return False

    def save(
        self,
        content: str,
        direction: str = "unknown",
        kind: str = "observation",
        emotion: str = "neutral",
        image_path: str | None = None,
        override_date: str | None = None,
        dedupe_key: str | None = None,
        materialize_now: bool = True,
    ) -> bool:
        """Save memory with embedding synchronously.

        Args:
            content: Text to store.
            direction: Spatial context (e.g. 'left', 'outside').
            kind: 'observation' | 'feeling' | 'conversation'
            emotion: 'neutral' | 'happy' | 'sad' | 'curious' | 'excited' | 'moved'
            image_path: Optional path to image file (thumbnail stored as base64).
            override_date: If set, use this date (YYYY-MM-DD) instead of now.
                           Useful for backfilling day summaries for past dates.
            dedupe_key: Optional idempotency key. When an event with the same key
                        already exists, this write is treated as already processed.
            materialize_now: If False, enqueue a durable job and return immediately.
                             If event append fails, falls back to immediate save.
        """
        try:
            event_payload = {
                "content": content,
                "direction": direction,
                "kind": kind,
                "emotion": emotion,
                "image_path": image_path,
                "override_date": override_date,
            }
            try:
                event_id, created_new = self.append_memory_event(
                    "memory.save",
                    event_payload,
                    dedupe_key=dedupe_key,
                    queue_job=True,
                    job_type="materialize_observation",
                )
            except Exception as e:
                logger.warning("Failed to record memory event (continuing): %s", e)
                event_id, created_new = None, False
            if dedupe_key and event_id and not created_new:
                logger.info("Deduped memory.save event for key=%s", dedupe_key)
                return True

            if not materialize_now and event_id:
                logger.debug("Queued memory.save event %s for async materialization", event_id)
                return True

            obs_id = event_id or str(uuid.uuid4())
            if not self._materialize_memory_save_event(obs_id, event_payload):
                return False
            logger.info("Saved %s (%s): %s...", kind, emotion, content[:60])
            return True
        except Exception as e:
            logger.warning("Failed to save memory: %s", e)
            return False

    def recall(self, query: str, n: int = 3, kind: str | None = None) -> list[dict]:
        """Recall by vector similarity. Fallback to LIKE + recency."""
        try:
            kind_filter = "AND kind = ?" if kind else ""
            kind_params: list[Any] = [kind] if kind else []

            # Fetch rows under lock, then compute similarity outside lock
            with self._db_lock:
                db = self._ensure_connected()
                count = db.execute("SELECT COUNT(*) FROM obs_embeddings").fetchone()[0]

                if count > 0:
                    rows = db.execute(
                        f"SELECT o.id, o.content, o.timestamp, o.date, o.time, "
                        f"o.direction, o.kind, o.emotion, o.image_path, e.vector "
                        f"FROM observations o JOIN obs_embeddings e ON o.id = e.obs_id "
                        f"WHERE 1=1 {kind_filter}",
                        kind_params,
                    ).fetchall()
                else:
                    rows = []

                # Fallback rows if no embeddings
                fallback_rows: list[Any] = []
                if count == 0:
                    keywords = [w for w in query.split() if len(w) > 1][:4]
                    if keywords:
                        conditions = " OR ".join("content LIKE ?" for _ in keywords)
                        params_like: list[Any] = [f"%{kw}%" for kw in keywords]
                        if kind:
                            fallback_rows = db.execute(
                                f"SELECT id, content, timestamp, date, time, direction, kind, emotion, image_path "
                                f"FROM observations WHERE ({conditions}) AND kind = ? "
                                f"ORDER BY timestamp DESC LIMIT ?",
                                params_like + [kind, n],
                            ).fetchall()
                        else:
                            fallback_rows = db.execute(
                                f"SELECT id, content, timestamp, date, time, direction, kind, emotion, image_path "
                                f"FROM observations WHERE {conditions} ORDER BY timestamp DESC LIMIT ?",
                                params_like + [n],
                            ).fetchall()
                    if not fallback_rows:
                        fallback_rows = db.execute(
                            "SELECT id, content, timestamp, date, time, direction, kind, emotion, image_path "
                            "FROM observations ORDER BY timestamp DESC LIMIT ?",
                            (n,),
                        ).fetchall()

            # Compute embeddings and similarity outside the lock
            if count > 0 and rows:
                query_vec = np.array(self._embedder.encode_query([query])[0], dtype=np.float32)
                vecs = np.stack([_decode_vector(bytes(r["vector"])) for r in rows])
                scores = _cosine_similarity(query_vec, vecs)
                top_indices = np.argsort(scores)[::-1][:n]
                return [
                    {
                        "memory_id": rows[i]["id"],
                        "timestamp": rows[i]["timestamp"],
                        "summary": rows[i]["content"],
                        "date": rows[i]["date"],
                        "time": rows[i]["time"],
                        "direction": rows[i]["direction"],
                        "kind": rows[i]["kind"],
                        "source_kind": rows[i]["kind"],
                        "emotion": rows[i]["emotion"],
                        "image_path": rows[i]["image_path"],
                        "score": float(scores[i]),
                        "confidence": max(0.0, min(1.0, (float(scores[i]) + 1.0) / 2.0)),
                        "retrieval_method": "semantic",
                    }
                    for i in top_indices
                ]

            # Fallback results
            method = "keyword" if query and any(len(w) > 1 for w in query.split()) else "recency"
            fallback_conf = 0.45 if method == "keyword" else 0.25
            return [
                {
                    "memory_id": r["id"],
                    "timestamp": r["timestamp"],
                    "summary": r["content"],
                    "date": r["date"],
                    "time": r["time"],
                    "direction": r["direction"],
                    "kind": r["kind"],
                    "source_kind": r["kind"],
                    "emotion": r["emotion"],
                    "image_path": r["image_path"],
                    "confidence": fallback_conf,
                    "retrieval_method": method,
                }
                for r in fallback_rows
            ]

        except Exception as e:
            logger.warning("Failed to recall memories: %s", e)
            return []

    def recent_feelings(self, n: int = 5) -> list[dict]:
        """Return the most recent emotional memories."""
        try:
            with self._db_lock:
                db = self._ensure_connected()
                rows = db.execute(
                    "SELECT content, date, time, emotion FROM observations "
                    "WHERE kind IN ('feeling', 'conversation') "
                    "ORDER BY timestamp DESC LIMIT ?",
                    (n,),
                ).fetchall()
            return [
                {
                    "summary": r["content"],
                    "date": r["date"],
                    "time": r["time"],
                    "emotion": r["emotion"],
                }
                for r in rows
            ]
        except Exception as e:
            logger.warning("Failed to fetch recent feelings: %s", e)
            return []

    def format_for_context(self, memories: list[dict]) -> str:
        if not memories:
            return ""
        lines = ["[過去の記憶（証拠つき）: conf<0.55 は不確か。断定しないこと]:"]
        for m in memories:
            score_str = f" (類似度:{m['score']:.2f})" if "score" in m else ""
            conf = float(m.get("confidence", 0.0))
            conf_str = f" conf:{conf:.2f}"
            low_conf = " low-confidence" if conf < 0.55 else ""
            emotion_str = (
                f" [{m['emotion']}]" if m.get("emotion") and m["emotion"] != "neutral" else ""
            )
            source_kind = m.get("source_kind", m.get("kind", "?"))
            memory_id = str(m.get("memory_id", ""))[:8] or "?"
            lines.append(
                f"- {m['date']} {m['time']} id:{memory_id} src:{source_kind}{score_str}{conf_str}{low_conf}"
                f" ({m.get('direction', '?')}){emotion_str}: {m['summary'][:120]}"
            )
        return "\n".join(lines)

    def format_feelings_for_context(self, feelings: list[dict]) -> str:
        if not feelings:
            return ""
        lines = ["[最近の気持ち・出来事]:"]
        for f in feelings:
            emotion_str = (
                f"[{f['emotion']}] " if f.get("emotion") and f["emotion"] != "neutral" else ""
            )
            lines.append(f"- {f['date']} {f['time']} {emotion_str}{f['summary'][:120]}")
        return "\n".join(lines)

    def recall_self_model(self, n: int = 5) -> list[dict]:
        """Return the most recent self-model insights (who I am, accumulated from experience)."""
        try:
            with self._db_lock:
                db = self._ensure_connected()
                rows = db.execute(
                    "SELECT content, date, time, emotion FROM observations "
                    "WHERE kind = 'self_model' "
                    "ORDER BY timestamp DESC LIMIT ?",
                    (n,),
                ).fetchall()
            return [
                {
                    "summary": r["content"],
                    "date": r["date"],
                    "time": r["time"],
                    "emotion": r["emotion"],
                }
                for r in rows
            ]
        except Exception as e:
            logger.warning("Failed to fetch self model: %s", e)
            return []

    def recall_curiosities(self, n: int = 5) -> list[dict]:
        """Return unresolved curiosity threads carried over from previous sessions."""
        try:
            with self._db_lock:
                db = self._ensure_connected()
                rows = db.execute(
                    "SELECT content, date, time FROM observations "
                    "WHERE kind = 'curiosity' "
                    "ORDER BY timestamp DESC LIMIT ?",
                    (n,),
                ).fetchall()
            return [
                {
                    "summary": r["content"],
                    "date": r["date"],
                    "time": r["time"],
                }
                for r in rows
            ]
        except Exception as e:
            logger.warning("Failed to fetch curiosities: %s", e)
            return []

    def format_self_model_for_context(self, self_model: list[dict]) -> str:
        if not self_model:
            return ""
        lines = ["[うちという存在 — 経験から積み上げてきた自己像]:"]
        for m in self_model:
            lines.append(f"- {m['summary'][:120]}")
        return "\n".join(lines)

    def format_curiosities_for_context(self, curiosities: list[dict]) -> str:
        if not curiosities:
            return ""
        lines = ["[まだ謎のまま・続きが気になること]:"]
        for c in curiosities:
            lines.append(f"- {c['date']} {c['time']}: {c['summary'][:120]}")
        return "\n".join(lines)

    async def save_async(
        self,
        content: str,
        direction: str = "unknown",
        kind: str = "observation",
        emotion: str = "neutral",
        image_path: str | None = None,
        override_date: str | None = None,
        dedupe_key: str | None = None,
        materialize_now: bool = True,
    ) -> bool:
        return await asyncio.to_thread(
            self.save,
            content,
            direction,
            kind,
            emotion,
            image_path,
            override_date,
            dedupe_key,
            materialize_now,
        )

    async def recall_async(self, query: str, n: int = 3, kind: str | None = None) -> list[dict]:
        return await asyncio.to_thread(self.recall, query, n, kind)

    async def recent_feelings_async(self, n: int = 5) -> list[dict]:
        return await asyncio.to_thread(self.recent_feelings, n)

    async def recall_self_model_async(self, n: int = 5) -> list[dict]:
        return await asyncio.to_thread(self.recall_self_model, n)

    async def recall_curiosities_async(self, n: int = 5) -> list[dict]:
        return await asyncio.to_thread(self.recall_curiosities, n)

    # ── Day summary support ────────────────────────────────────────

    def recall_day_summaries(self, n: int = 5) -> list[dict]:
        """Return the most recent day summaries."""
        try:
            db = self._ensure_connected()
            rows = db.execute(
                "SELECT content, date, time, emotion FROM observations "
                "WHERE kind = 'day_summary' "
                "ORDER BY timestamp DESC LIMIT ?",
                (n,),
            ).fetchall()
            return [
                {
                    "summary": r["content"],
                    "date": r["date"],
                    "time": r["time"],
                    "emotion": r["emotion"],
                }
                for r in rows
            ]
        except Exception as e:
            logger.warning("Failed to fetch day summaries: %s", e)
            return []

    async def recall_day_summaries_async(self, n: int = 5) -> list[dict]:
        return await asyncio.to_thread(self.recall_day_summaries, n)

    def get_dates_with_observations(self, limit: int = 7) -> list[str]:
        """Return distinct dates that have observations, most recent first."""
        try:
            db = self._ensure_connected()
            rows = db.execute(
                "SELECT DISTINCT date FROM observations "
                "WHERE kind IN ('observation', 'conversation') "
                "ORDER BY date DESC LIMIT ?",
                (limit,),
            ).fetchall()
            return [r["date"] for r in rows]
        except Exception as e:
            logger.warning("Failed to fetch observation dates: %s", e)
            return []

    def delete_day_summaries_for_date(self, date: str) -> int:
        """Delete all day_summary records for the given date. Returns count deleted."""
        try:
            with self._db_lock:
                db = self._ensure_connected()
                cursor = db.execute(
                    "DELETE FROM observations WHERE kind = 'day_summary' AND date = ?",
                    (date,),
                )
                db.commit()
                count = cursor.rowcount
            if count:
                logger.info("Deleted %d day summary(s) for %s", count, date)
            return count
        except Exception as e:
            logger.warning("Failed to delete day summaries for %s: %s", date, e)
            return 0

    def get_dates_with_summaries(self) -> set[str]:
        """Return set of dates that already have a day_summary."""
        try:
            with self._db_lock:
                db = self._ensure_connected()
                rows = db.execute(
                    "SELECT DISTINCT date FROM observations WHERE kind = 'day_summary'"
                ).fetchall()
            return {r["date"] for r in rows}
        except Exception as e:
            logger.warning("Failed to fetch summary dates: %s", e)
            return set()

    def get_observations_for_date(self, date: str, limit: int = 50) -> list[dict]:
        """Return observations and conversations for a specific date."""
        try:
            with self._db_lock:
                db = self._ensure_connected()
                rows = db.execute(
                    "SELECT content, time, kind, emotion FROM observations "
                    "WHERE date = ? AND kind IN ('observation', 'conversation') "
                    "ORDER BY timestamp ASC LIMIT ?",
                    (date, limit),
                ).fetchall()
            return [
                {
                    "content": r["content"],
                    "time": r["time"],
                    "kind": r["kind"],
                    "emotion": r["emotion"],
                }
                for r in rows
            ]
        except Exception as e:
            logger.warning("Failed to fetch observations for %s: %s", date, e)
            return []

    def format_day_summaries_for_context(self, summaries: list[dict]) -> str:
        if not summaries:
            return ""
        lines = ["[私が覚えていること — 過去の日々に私が見たもの、感じたこと]:"]
        for s in summaries:
            lines.append(f"- {s['date']}: {s['summary'][:200]}")
        return "\n".join(lines)


class MemoryTool:
    """Agent-callable memory tools: remember + recall (with optional image)."""

    def __init__(self, store: ObservationMemory) -> None:
        self._store = store

    def get_tool_definitions(self) -> list[dict]:
        return [
            {
                "name": "remember",
                "description": (
                    "Save something to long-term memory. Use this to remember important things: "
                    "what you saw, what happened, how you felt, conversations. "
                    "If you just took a photo with see(), pass the image_path to attach it."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "content": {
                            "type": "string",
                            "description": "What to remember (1-3 sentences).",
                        },
                        "emotion": {
                            "type": "string",
                            "enum": ["neutral", "happy", "sad", "curious", "excited", "moved"],
                            "description": "Emotional tone of this memory.",
                        },
                        "image_path": {
                            "type": "string",
                            "description": "Optional path to an image file to attach (e.g. from see()).",
                        },
                    },
                    "required": ["content"],
                },
            },
            {
                "name": "recall",
                "description": (
                    "Search long-term memory for things related to a topic. "
                    "Use this to remember past observations, conversations, or feelings."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "What to search for.",
                        },
                        "n": {
                            "type": "integer",
                            "description": "Number of memories to return (default 3).",
                        },
                    },
                    "required": ["query"],
                },
            },
        ]

    async def call(self, tool_name: str, tool_input: dict) -> tuple[str, str | None]:
        if tool_name == "remember":
            content = tool_input["content"]
            emotion = tool_input.get("emotion", "neutral")
            image_path = tool_input.get("image_path")
            ok = await self._store.save_async(
                content, kind="observation", emotion=emotion, image_path=image_path
            )
            if ok:
                suffix = " (with image)" if image_path else ""
                return f"Remembered{suffix}: {content[:60]}", None
            return "Failed to save memory.", None

        if tool_name == "recall":
            query = tool_input["query"]
            n = int(tool_input.get("n", 3))
            memories = await self._store.recall_async(query, n=n)
            if not memories:
                return "No relevant memories found.", None
            lines = []
            for m in memories:
                score = f" ({m['score']:.2f})" if "score" in m else ""
                confidence = f" conf:{float(m.get('confidence', 0.0)):.2f}"
                emotion = f" [{m['emotion']}]" if m.get("emotion", "neutral") != "neutral" else ""
                img = " 📷" if m.get("image_path") else ""
                memory_id = str(m.get("memory_id", ""))[:8] or "?"
                source_kind = m.get("source_kind", m.get("kind", "?"))
                lines.append(
                    f"- {m['date']} {m['time']} id:{memory_id} src:{source_kind}{score}{confidence}{emotion}{img}: "
                    f"{m['summary'][:120]}"
                )
            return "\n".join(lines), None

        return f"Unknown memory tool: {tool_name}", None
