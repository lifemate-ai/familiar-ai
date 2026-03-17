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
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..workspace import Coalition

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
        self._failed = False
        self._fallback_dim = 384
        self._lock = threading.Lock()
        self._load_event = threading.Event()

    def _load(self) -> None:
        if self._model is not None or self._failed:
            return  # fast path — already loaded (or failed), no lock needed
        with self._lock:
            if self._model is None and not self._failed:  # double-checked locking
                import logging as _logging

                _logging.getLogger("sentence_transformers").setLevel(_logging.ERROR)
                _logging.getLogger("huggingface_hub").setLevel(_logging.ERROR)
                _logging.getLogger("transformers").setLevel(_logging.ERROR)
                try:
                    from sentence_transformers import SentenceTransformer

                    logger.info("Loading embedding model %s...", self._model_name)
                    self._model = SentenceTransformer(self._model_name)
                    logger.info("Embedding model loaded.")
                except Exception as e:
                    # Keep app usable even if torch/transformers DLLs fail on packaged builds.
                    self._failed = True
                    logger.warning(
                        "Failed to load embedding model; disabling semantic search: %s", e
                    )
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

    def _zero_vectors(self, n: int) -> list[list[float]]:
        return [[0.0] * self._fallback_dim for _ in range(n)]

    def encode_document(self, texts: list[str]) -> list[list[float]]:
        self._load()
        if self._model is None:
            return self._zero_vectors(len(texts))
        prefixed = [f"passage: {t}" for t in texts]
        try:
            return self._model.encode(
                prefixed, normalize_embeddings=True, show_progress_bar=False
            ).tolist()
        except Exception as e:
            logger.warning("Embedding encode_document failed; using fallback vectors: %s", e)
            self._model = None
            self._failed = True
            return self._zero_vectors(len(texts))

    def encode_query(self, texts: list[str]) -> list[list[float]]:
        self._load()
        if self._model is None:
            return self._zero_vectors(len(texts))
        prefixed = [f"query: {t}" for t in texts]
        try:
            return self._model.encode(
                prefixed, normalize_embeddings=True, show_progress_bar=False
            ).tolist()
        except Exception as e:
            logger.warning("Embedding encode_query failed; using fallback vectors: %s", e)
            self._model = None
            self._failed = True
            return self._zero_vectors(len(texts))


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

    def _upsert_semantic_fact_locked(
        self,
        db: sqlite3.Connection,
        fact_key: str,
        fact_text: str,
        source_memory_id: str | None = None,
        confidence: float = 0.6,
        tags: str = "",
    ) -> None:
        now_iso = self._now_iso()
        confidence = max(0.0, min(1.0, float(confidence)))
        existing = db.execute(
            "SELECT id, fact_text, confidence FROM semantic_facts WHERE fact_key = ?",
            (fact_key,),
        ).fetchone()
        if existing:
            prev_text = str(existing["fact_text"])
            prev_conf = float(existing["confidence"])
            new_conf = max(prev_conf, confidence)
            db.execute(
                "UPDATE semantic_facts "
                "SET fact_text = ?, source_memory_id = COALESCE(?, source_memory_id), "
                "confidence = MAX(confidence, ?), tags = ?, last_seen_at = ?, updated_at = ? "
                "WHERE fact_key = ?",
                (
                    fact_text,
                    source_memory_id,
                    confidence,
                    tags,
                    now_iso,
                    now_iso,
                    fact_key,
                ),
            )
            if prev_text != fact_text or abs(new_conf - prev_conf) > 1e-6:
                self._insert_revision_locked(
                    db,
                    entity_type="semantic_fact",
                    entity_key=fact_key,
                    previous_text=prev_text,
                    new_text=fact_text,
                    previous_confidence=prev_conf,
                    new_confidence=new_conf,
                    source_memory_id=source_memory_id,
                )
            return
        db.execute(
            "INSERT INTO semantic_facts "
            "(id, fact_key, fact_text, source_memory_id, confidence, tags, last_seen_at, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                str(uuid.uuid4()),
                fact_key,
                fact_text,
                source_memory_id,
                confidence,
                tags,
                now_iso,
                now_iso,
                now_iso,
            ),
        )

    def _upsert_behavior_policy_locked(
        self,
        db: sqlite3.Connection,
        policy_key: str,
        policy_text: str,
        trigger_context: str = "",
        action_hint: str = "",
        source_memory_id: str | None = None,
        confidence: float = 0.6,
    ) -> None:
        now_iso = self._now_iso()
        confidence = max(0.0, min(1.0, float(confidence)))
        existing = db.execute(
            "SELECT id, policy_text, confidence FROM behavior_policies WHERE policy_key = ?",
            (policy_key,),
        ).fetchone()
        if existing:
            prev_text = str(existing["policy_text"])
            prev_conf = float(existing["confidence"])
            new_conf = max(prev_conf, confidence)
            db.execute(
                "UPDATE behavior_policies "
                "SET policy_text = ?, trigger_context = ?, action_hint = ?, "
                "source_memory_id = COALESCE(?, source_memory_id), "
                "confidence = MAX(confidence, ?), last_seen_at = ?, updated_at = ? "
                "WHERE policy_key = ?",
                (
                    policy_text,
                    trigger_context,
                    action_hint,
                    source_memory_id,
                    confidence,
                    now_iso,
                    now_iso,
                    policy_key,
                ),
            )
            if prev_text != policy_text or abs(new_conf - prev_conf) > 1e-6:
                self._insert_revision_locked(
                    db,
                    entity_type="behavior_policy",
                    entity_key=policy_key,
                    previous_text=prev_text,
                    new_text=policy_text,
                    previous_confidence=prev_conf,
                    new_confidence=new_conf,
                    source_memory_id=source_memory_id,
                )
            return
        db.execute(
            "INSERT INTO behavior_policies "
            "(id, policy_key, policy_text, trigger_context, action_hint, source_memory_id, confidence, "
            "last_seen_at, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                str(uuid.uuid4()),
                policy_key,
                policy_text,
                trigger_context,
                action_hint,
                source_memory_id,
                confidence,
                now_iso,
                now_iso,
                now_iso,
            ),
        )

    def _insert_revision_locked(
        self,
        db: sqlite3.Connection,
        entity_type: str,
        entity_key: str,
        previous_text: str,
        new_text: str,
        previous_confidence: float,
        new_confidence: float,
        source_memory_id: str | None,
        reason: str = "projection_update",
    ) -> None:
        db.execute(
            "INSERT INTO memory_revisions "
            "(id, entity_type, entity_key, previous_text, new_text, previous_confidence, "
            "new_confidence, source_memory_id, reason, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                str(uuid.uuid4()),
                entity_type,
                entity_key,
                previous_text[:800],
                new_text[:800],
                max(0.0, min(1.0, float(previous_confidence))),
                max(0.0, min(1.0, float(new_confidence))),
                source_memory_id,
                reason,
                self._now_iso(),
            ),
        )

    def _adjust_projection_confidence_locked(
        self,
        db: sqlite3.Connection,
        *,
        table: str,
        key_column: str,
        text_column: str,
        entity_type: str,
        entity_key: str,
        delta: float,
        reason: str,
    ) -> float | None:
        row = db.execute(
            f"SELECT {text_column}, confidence FROM {table} WHERE {key_column} = ?",
            (entity_key,),
        ).fetchone()
        if row is None:
            return None

        prev_text = str(row[text_column])
        prev_conf = float(row["confidence"])
        new_conf = max(0.0, min(1.0, prev_conf + float(delta)))
        if abs(new_conf - prev_conf) <= 1e-6:
            return new_conf

        now_iso = self._now_iso()
        db.execute(
            f"UPDATE {table} SET confidence = ?, last_seen_at = ?, updated_at = ? "
            f"WHERE {key_column} = ?",
            (new_conf, now_iso, now_iso, entity_key),
        )
        self._insert_revision_locked(
            db,
            entity_type=entity_type,
            entity_key=entity_key,
            previous_text=prev_text,
            new_text=prev_text,
            previous_confidence=prev_conf,
            new_confidence=new_conf,
            source_memory_id=None,
            reason=reason,
        )
        return new_conf

    def _project_memory_locked(
        self,
        db: sqlite3.Connection,
        source_memory_id: str,
        content: str,
        kind: str,
        emotion: str,
    ) -> None:
        text = content.strip()
        if not text:
            return

        # Episodic -> semantic (stable self/companion facts)
        if kind == "self_model":
            self._upsert_semantic_fact_locked(
                db,
                fact_key="self_model:core",
                fact_text=text[:220],
                source_memory_id=source_memory_id,
                confidence=0.82,
                tags="self_model",
            )
            return

        if kind == "companion_status":
            self._upsert_semantic_fact_locked(
                db,
                fact_key="companion_status:latest",
                fact_text=text[:220],
                source_memory_id=source_memory_id,
                confidence=0.78,
                tags="companion_status",
            )
            return

        # Episodic -> policy (action tendencies)
        if kind == "curiosity":
            policy_text = f"When idle, follow up this curiosity thread: {text[:180]}"
            self._upsert_behavior_policy_locked(
                db,
                policy_key="curiosity:active",
                policy_text=policy_text,
                trigger_context="idle",
                action_hint="look_around",
                source_memory_id=source_memory_id,
                confidence=0.74,
            )
            return

        if kind == "conversation" and emotion in {"moved", "excited"}:
            policy_text = f"Prefer this response style when supporting the companion: {text[:180]}"
            self._upsert_behavior_policy_locked(
                db,
                policy_key="conversation:supportive_style",
                policy_text=policy_text,
                trigger_context="conversation",
                action_hint="respond_supportively",
                source_memory_id=source_memory_id,
                confidence=0.62,
            )

    def adjust_semantic_fact_confidence(
        self,
        fact_key: str,
        delta: float,
        *,
        reason: str = "adaptive_update",
    ) -> float | None:
        with self._db_lock:
            db = self._ensure_connected()
            result = self._adjust_projection_confidence_locked(
                db,
                table="semantic_facts",
                key_column="fact_key",
                text_column="fact_text",
                entity_type="semantic_fact",
                entity_key=fact_key,
                delta=delta,
                reason=reason,
            )
            db.commit()
            return result

    def adjust_behavior_policy_confidence(
        self,
        policy_key: str,
        delta: float,
        *,
        reason: str = "adaptive_update",
        policy_text: str | None = None,
        trigger_context: str = "",
        action_hint: str = "",
    ) -> float | None:
        with self._db_lock:
            db = self._ensure_connected()
            result = self._adjust_projection_confidence_locked(
                db,
                table="behavior_policies",
                key_column="policy_key",
                text_column="policy_text",
                entity_type="behavior_policy",
                entity_key=policy_key,
                delta=delta,
                reason=reason,
            )
            if result is None and policy_text and delta > 0.0:
                result = max(0.0, min(1.0, 0.6 + float(delta)))
                self._upsert_behavior_policy_locked(
                    db,
                    policy_key=policy_key,
                    policy_text=policy_text,
                    trigger_context=trigger_context,
                    action_hint=action_hint,
                    confidence=result,
                )
            db.commit()
            return result

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
            self._project_memory_locked(
                db,
                source_memory_id=event_id,
                content=content,
                kind=kind,
                emotion=emotion,
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
                        f"o.direction, o.kind, o.emotion, o.image_path, "
                        f"COALESCE(o.importance, 1.0) AS importance, e.vector "
                        f"FROM observations o JOIN obs_embeddings e ON o.id = e.obs_id "
                        f"WHERE o.superseded_by IS NULL {kind_filter}",
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
                                f"AND superseded_by IS NULL "
                                f"ORDER BY timestamp DESC LIMIT ?",
                                params_like + [kind, n],
                            ).fetchall()
                        else:
                            fallback_rows = db.execute(
                                f"SELECT id, content, timestamp, date, time, direction, kind, emotion, image_path "
                                f"FROM observations WHERE ({conditions}) AND superseded_by IS NULL "
                                f"ORDER BY timestamp DESC LIMIT ?",
                                params_like + [n],
                            ).fetchall()
                    if not fallback_rows:
                        fallback_rows = db.execute(
                            "SELECT id, content, timestamp, date, time, direction, kind, emotion, image_path "
                            "FROM observations WHERE superseded_by IS NULL ORDER BY timestamp DESC LIMIT ?",
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

    def recall_semantic_facts(self, query: str, n: int = 5) -> list[dict]:
        """Recall stable semantic facts relevant to the current topic."""
        try:
            like = f"%{query.strip()}%" if query.strip() else "%"
            with self._db_lock:
                db = self._ensure_connected()
                rows = db.execute(
                    "SELECT fact_key, fact_text, source_memory_id, confidence, tags, last_seen_at "
                    "FROM semantic_facts "
                    "WHERE (? = '%' OR fact_text LIKE ? OR tags LIKE ?) "
                    "ORDER BY CASE WHEN fact_text LIKE ? THEN 0 ELSE 1 END, last_seen_at DESC "
                    "LIMIT ?",
                    (like, like, like, like, n),
                ).fetchall()
            return [
                {
                    "key": r["fact_key"],
                    "summary": r["fact_text"],
                    "source_memory_id": r["source_memory_id"],
                    "confidence": float(r["confidence"]),
                    "tags": r["tags"],
                    "last_seen_at": r["last_seen_at"],
                }
                for r in rows
            ]
        except Exception as e:
            logger.warning("Failed to recall semantic facts: %s", e)
            return []

    def recall_behavior_policies(self, query: str, n: int = 5) -> list[dict]:
        """Recall behavior policies relevant to the current topic."""
        try:
            like = f"%{query.strip()}%" if query.strip() else "%"
            with self._db_lock:
                db = self._ensure_connected()
                rows = db.execute(
                    "SELECT policy_key, policy_text, trigger_context, action_hint, "
                    "source_memory_id, confidence, last_seen_at "
                    "FROM behavior_policies "
                    "WHERE (? = '%' OR policy_text LIKE ? OR trigger_context LIKE ? OR action_hint LIKE ?) "
                    "ORDER BY CASE WHEN policy_text LIKE ? THEN 0 ELSE 1 END, last_seen_at DESC "
                    "LIMIT ?",
                    (like, like, like, like, like, n),
                ).fetchall()
            return [
                {
                    "key": r["policy_key"],
                    "summary": r["policy_text"],
                    "trigger_context": r["trigger_context"],
                    "action_hint": r["action_hint"],
                    "source_memory_id": r["source_memory_id"],
                    "confidence": float(r["confidence"]),
                    "last_seen_at": r["last_seen_at"],
                }
                for r in rows
            ]
        except Exception as e:
            logger.warning("Failed to recall behavior policies: %s", e)
            return []

    def format_semantic_facts_for_context(self, facts: list[dict]) -> str:
        if not facts:
            return ""
        lines = ["[安定した事実（semantic memory）]:"]
        for fact in facts:
            lines.append(
                f"- conf:{float(fact.get('confidence', 0.0)):.2f} "
                f"key:{str(fact.get('key', '?'))[:24]}: {str(fact.get('summary', ''))[:140]}"
            )
        return "\n".join(lines)

    def format_behavior_policies_for_context(self, policies: list[dict]) -> str:
        if not policies:
            return ""
        lines = ["[行動方針（policy memory）]:"]
        for policy in policies:
            trigger = str(policy.get("trigger_context", ""))[:24]
            action = str(policy.get("action_hint", ""))[:32]
            lines.append(
                f"- conf:{float(policy.get('confidence', 0.0)):.2f} "
                f"trigger:{trigger} action:{action}: {str(policy.get('summary', ''))[:140]}"
            )
        return "\n".join(lines)

    def recall_revisions(
        self, entity_type: str | None = None, entity_key: str | None = None, n: int = 20
    ) -> list[dict]:
        """Return recent revision records for semantic/policy memory."""
        try:
            clauses: list[str] = []
            params: list[Any] = []
            if entity_type:
                clauses.append("entity_type = ?")
                params.append(entity_type)
            if entity_key:
                clauses.append("entity_key = ?")
                params.append(entity_key)
            where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
            with self._db_lock:
                db = self._ensure_connected()
                rows = db.execute(
                    "SELECT entity_type, entity_key, previous_text, new_text, "
                    "previous_confidence, new_confidence, source_memory_id, reason, created_at "
                    f"FROM memory_revisions {where} "
                    "ORDER BY created_at DESC LIMIT ?",
                    params + [n],
                ).fetchall()
            return [
                {
                    "entity_type": r["entity_type"],
                    "entity_key": r["entity_key"],
                    "previous_text": r["previous_text"],
                    "new_text": r["new_text"],
                    "previous_confidence": float(r["previous_confidence"]),
                    "new_confidence": float(r["new_confidence"]),
                    "source_memory_id": r["source_memory_id"],
                    "reason": r["reason"],
                    "created_at": r["created_at"],
                }
                for r in rows
            ]
        except Exception as e:
            logger.warning("Failed to recall revisions: %s", e)
            return []

    def save_with_id(
        self,
        content: str,
        direction: str = "unknown",
        kind: str = "observation",
        emotion: str = "neutral",
        image_path: str | None = None,
        override_date: str | None = None,
        dedupe_key: str | None = None,
        materialize_now: bool = True,
    ) -> tuple[str | None, bool]:
        """Like save(), but returns (memory_id, success) instead of just bool."""
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
                return event_id, True

            if not materialize_now and event_id:
                return event_id, True

            obs_id = event_id or str(uuid.uuid4())
            ok = self._materialize_memory_save_event(obs_id, event_payload)
            if ok:
                logger.info("Saved %s (%s): %s...", kind, emotion, content[:60])
            return (obs_id if ok else None), ok
        except Exception as e:
            logger.warning("Failed to save memory: %s", e)
            return None, False

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

    async def save_async_with_id(
        self,
        content: str,
        direction: str = "unknown",
        kind: str = "observation",
        emotion: str = "neutral",
        image_path: str | None = None,
        override_date: str | None = None,
        dedupe_key: str | None = None,
        materialize_now: bool = True,
    ) -> tuple[str | None, bool]:
        return await asyncio.to_thread(
            self.save_with_id,
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

    async def recall_semantic_facts_async(self, query: str, n: int = 5) -> list[dict]:
        return await asyncio.to_thread(self.recall_semantic_facts, query, n)

    async def recall_behavior_policies_async(self, query: str, n: int = 5) -> list[dict]:
        return await asyncio.to_thread(self.recall_behavior_policies, query, n)

    async def adjust_semantic_fact_confidence_async(
        self,
        fact_key: str,
        delta: float,
        *,
        reason: str = "adaptive_update",
    ) -> float | None:
        return await asyncio.to_thread(
            self.adjust_semantic_fact_confidence,
            fact_key,
            delta,
            reason=reason,
        )

    async def adjust_behavior_policy_confidence_async(
        self,
        policy_key: str,
        delta: float,
        *,
        reason: str = "adaptive_update",
        policy_text: str | None = None,
        trigger_context: str = "",
        action_hint: str = "",
    ) -> float | None:
        return await asyncio.to_thread(
            self.adjust_behavior_policy_confidence,
            policy_key,
            delta,
            reason=reason,
            policy_text=policy_text,
            trigger_context=trigger_context,
            action_hint=action_hint,
        )

    # ------------------------------------------------------------------
    # Phase 2-2: importance decay
    # ------------------------------------------------------------------

    def decay_importance(self, before_date: str, factor: float = 0.95) -> int:
        """Multiply importance by factor for all observations older than before_date.

        Args:
            before_date: ISO date string (exclusive upper bound). Records with
                         date < before_date are decayed.
            factor: Decay multiplier (default 0.95 = 5% decay per cycle).

        Returns:
            Number of rows updated.
        """
        with self._db_lock:
            db = self._ensure_connected()
            try:
                cur = db.execute(
                    "UPDATE observations SET importance = importance * ? "
                    "WHERE date < ? AND superseded_by IS NULL",
                    (factor, before_date),
                )
                db.commit()
                return cur.rowcount
            except Exception:
                # Column may not exist on older DBs — safe to ignore
                logger.debug("decay_importance: column missing, skipping")
                return 0

    async def decay_importance_async(self, before_date: str, factor: float = 0.95) -> int:
        return await asyncio.to_thread(self.decay_importance, before_date, factor)

    # ------------------------------------------------------------------
    # Phase 2-3: near-duplicate detection and supersession
    # ------------------------------------------------------------------

    def mark_superseded(self, old_id: str, new_id: str) -> None:
        """Mark old_id as superseded by new_id.

        Superseded observations are excluded from recall() results.
        """
        with self._db_lock:
            db = self._ensure_connected()
            db.execute(
                "UPDATE observations SET superseded_by = ? WHERE id = ?",
                (new_id, old_id),
            )
            db.commit()

    def find_near_duplicates(
        self, threshold: float = 0.95, max_candidates: int = 500
    ) -> list[tuple[str, str, float]]:
        """Find pairs of non-superseded observations with cosine similarity >= threshold.

        Returns list of (id_older, id_newer, similarity) tuples, sorted by similarity desc.
        Older = earlier timestamp is marked as the one to supersede.
        """
        with self._db_lock:
            db = self._ensure_connected()
            rows = db.execute(
                """
                SELECT o.id, o.timestamp, e.vector
                FROM observations o
                JOIN obs_embeddings e ON o.id = e.obs_id
                WHERE o.superseded_by IS NULL
                ORDER BY o.timestamp DESC
                LIMIT ?
                """,
                (max_candidates,),
            ).fetchall()

        if len(rows) < 2:
            return []

        ids = [r[0] for r in rows]
        timestamps = [r[1] for r in rows]
        vecs = np.stack([_decode_vector(bytes(r[2])) for r in rows])

        # Normalise
        norms = np.linalg.norm(vecs, axis=1, keepdims=True)
        vecs_norm = vecs / (norms + 1e-10)

        # Pairwise cosine similarity (upper triangle only)
        sim_matrix = vecs_norm @ vecs_norm.T

        pairs: list[tuple[str, str, float]] = []
        n = len(ids)
        for i in range(n):
            for j in range(i + 1, n):
                sim = float(sim_matrix[i, j])
                if sim >= threshold:
                    # Older record (earlier timestamp) is superseded by newer
                    if timestamps[i] < timestamps[j]:
                        pairs.append((ids[i], ids[j], sim))
                    else:
                        pairs.append((ids[j], ids[i], sim))

        pairs.sort(key=lambda x: x[2], reverse=True)
        return pairs

    async def find_near_duplicates_async(
        self, threshold: float = 0.95
    ) -> list[tuple[str, str, float]]:
        return await asyncio.to_thread(self.find_near_duplicates, threshold)

    async def recall_revisions_async(
        self, entity_type: str | None = None, entity_key: str | None = None, n: int = 20
    ) -> list[dict]:
        return await asyncio.to_thread(self.recall_revisions, entity_type, entity_key, n)

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

    def recall_on_this_day(self, month: int, day: int, n: int = 3) -> list[dict]:
        """Return memories from the same month-day in past years.

        Excludes today so only true anniversaries are surfaced.
        """
        md = f"{month:02d}-{day:02d}"
        try:
            db = self._ensure_connected()
            rows = db.execute(
                "SELECT content, date, emotion, kind FROM observations "
                "WHERE strftime('%m-%d', date) = ? AND date < date('now') "
                "ORDER BY date DESC LIMIT ?",
                (md, n),
            ).fetchall()
            return [dict(r) for r in rows]
        except Exception as e:
            logger.warning("recall_on_this_day failed: %s", e)
            return []

    async def recall_on_this_day_async(self, month: int, day: int, n: int = 3) -> list[dict]:
        return await asyncio.to_thread(self.recall_on_this_day, month, day, n)

    def get_earliest_date(self) -> str | None:
        """Return the earliest date in the observations table, or None if empty."""
        try:
            db = self._ensure_connected()
            row = db.execute("SELECT MIN(date) AS earliest FROM observations").fetchone()
            return row["earliest"] if row and row["earliest"] else None
        except Exception as e:
            logger.warning("get_earliest_date failed: %s", e)
            return None

    async def get_earliest_date_async(self) -> str | None:
        return await asyncio.to_thread(self.get_earliest_date)

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

    # ------------------------------------------------------------------
    # Associative links
    # ------------------------------------------------------------------

    def link_memories(
        self,
        source_id: str,
        target_id: str,
        link_type: str = "related",
        note: str | None = None,
    ) -> bool:
        """Create a typed link between two memories. Returns True on success.

        link_type: "related" | "similar" | "caused_by" | "leads_to"
        """
        link_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        try:
            with self._db_lock:
                db = self._ensure_connected()
                db.execute(
                    "INSERT OR IGNORE INTO memory_links "
                    "(id, source_id, target_id, link_type, note, created_at) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (link_id, source_id, target_id, link_type, note, now),
                )
                db.commit()
            return True
        except Exception as e:
            logger.warning("link_memories failed: %s", e)
            return False

    async def link_memories_async(
        self,
        source_id: str,
        target_id: str,
        link_type: str = "related",
        note: str | None = None,
    ) -> bool:
        return await asyncio.to_thread(self.link_memories, source_id, target_id, link_type, note)

    def get_linked_memories(self, memory_id: str, direction: str = "both") -> list[dict]:
        """Return memories linked to/from the given memory_id.

        direction: "out" (source→target), "in" (target→source), "both"
        """
        try:
            db = self._ensure_connected()
            results: list[dict] = []

            if direction in ("out", "both"):
                rows = db.execute(
                    "SELECT o.id, o.content, o.date, o.time, o.emotion, o.kind, "
                    "       ml.link_type, ml.note "
                    "FROM memory_links ml "
                    "JOIN observations o ON o.id = ml.target_id "
                    "WHERE ml.source_id = ? AND o.superseded_by IS NULL",
                    (memory_id,),
                ).fetchall()
                results.extend({**dict(r), "link_direction": "→"} for r in rows)

            if direction in ("in", "both"):
                rows = db.execute(
                    "SELECT o.id, o.content, o.date, o.time, o.emotion, o.kind, "
                    "       ml.link_type, ml.note "
                    "FROM memory_links ml "
                    "JOIN observations o ON o.id = ml.source_id "
                    "WHERE ml.target_id = ? AND o.superseded_by IS NULL",
                    (memory_id,),
                ).fetchall()
                results.extend({**dict(r), "link_direction": "←"} for r in rows)
            return results
        except Exception as e:
            logger.warning("get_linked_memories failed: %s", e)
            return []

    async def get_linked_memories_async(
        self, memory_id: str, direction: str = "both"
    ) -> list[dict]:
        return await asyncio.to_thread(self.get_linked_memories, memory_id, direction)

    async def as_coalition_async(self) -> Coalition | None:
        """Return a workspace Coalition from recent recalled memories."""
        from ..workspace import Coalition

        memories = await self.recall_async("最近の出来事 印象的な記憶", n=3)
        if not memories:
            return None

        # Use highest-confidence recalled memory
        top = max(memories, key=lambda m: m.get("confidence", 0.0))
        summary = top.get("summary", "")[:80]
        confidence = top.get("confidence", 0.3)

        lines = ["[Memory recall]"]
        for m in memories:
            emotion = m.get("emotion", "neutral")
            lines.append(f"  [{emotion}] {m.get('summary', '')[:60]}")
        context_block = "\n".join(lines)

        return Coalition(
            source="memory",
            summary=summary,
            activation=confidence,
            urgency=0.1,
            novelty=0.0,
            context_block=context_block,
        )


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
                    "If you just took a photo with see(), pass the image_path to attach it. "
                    "Use link_to to associate this memory with a related one (pass its memory_id)."
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
                        "link_to": {
                            "type": "string",
                            "description": "Optional memory_id to link this memory to (associative link).",
                        },
                        "link_type": {
                            "type": "string",
                            "enum": ["related", "similar", "caused_by", "leads_to"],
                            "description": "Type of link (default: related).",
                        },
                    },
                    "required": ["content"],
                },
            },
            {
                "name": "recall",
                "description": (
                    "Search long-term memory for things related to a topic. "
                    "Returns memories with their IDs, emotions, and any linked memories."
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
            link_to = tool_input.get("link_to")
            link_type = tool_input.get("link_type", "related")

            memory_id, ok = await self._store.save_async_with_id(
                content, kind="observation", emotion=emotion, image_path=image_path
            )
            if not ok:
                return "Failed to save memory.", None

            # Create associative link if requested
            link_info = ""
            if link_to and memory_id:
                linked = await self._store.link_memories_async(
                    memory_id, link_to, link_type=link_type
                )
                if linked:
                    link_info = f" [linked:{link_type}→{link_to[:8]}]"

            suffix = " (with image)" if image_path else ""
            id_tag = f" [id:{memory_id[:8]}]" if memory_id else ""
            return (
                f"Remembered{suffix}{id_tag}{link_info}: {content[:80]}\n"
                f"emotion={emotion} | id={memory_id or '?'}"
            ), None

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
                emo = m.get("emotion", "neutral")
                img = " 📷" if m.get("image_path") else ""
                memory_id = str(m.get("memory_id", ""))
                short_id = memory_id[:8] if memory_id else "?"
                source_kind = m.get("source_kind", m.get("kind", "?"))
                lines.append(
                    f"- [{emo}] {m['date']} {m['time']} id:{short_id} src:{source_kind}"
                    f"{score}{confidence}{img}\n"
                    f"  {m['summary'][:150]}"
                )

                # Fetch links for this memory and show them
                if memory_id:
                    links = await self._store.get_linked_memories_async(memory_id)
                    for lm in links[:2]:
                        lt = lm.get("link_type", "related")
                        ld = lm.get("link_direction", "→")
                        lines.append(
                            f"  {ld} [{lt}] {lm.get('date', '')} [{lm.get('emotion', 'neutral')}]: "
                            f"{lm.get('content', '')[:80]}"
                        )

            return "\n".join(lines), None

        return f"Unknown memory tool: {tool_name}", None
