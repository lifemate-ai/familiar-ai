"""Observation and emotional memory - SQLite + multilingual-e5-small embeddings.

Architecture inspired by memory-mcp (Phase 11: SQLite+numpy).
- Fast startup: no heavy DB server
- Semantic search: multilingual-e5-small (~117MB, lazy loaded)
- Hybrid: vector similarity + LIKE keyword fallback
- Two memory types: observations (what I saw) + feelings (what I felt)
"""

from __future__ import annotations

import asyncio
import logging
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)

DB_PATH = str(Path.home() / ".familiar_ai" / "observations.db")
EMBEDDING_MODEL = "intfloat/multilingual-e5-small"

_DDL = """
CREATE TABLE IF NOT EXISTS observations (
    id TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    direction TEXT NOT NULL DEFAULT 'unknown',
    kind TEXT NOT NULL DEFAULT 'observation',
    emotion TEXT NOT NULL DEFAULT 'neutral',
    image_path TEXT,
    image_data TEXT
);
CREATE INDEX IF NOT EXISTS idx_obs_timestamp ON observations(timestamp);
CREATE INDEX IF NOT EXISTS idx_obs_date ON observations(date);
CREATE INDEX IF NOT EXISTS idx_obs_kind ON observations(kind);

CREATE TABLE IF NOT EXISTS obs_embeddings (
    obs_id TEXT PRIMARY KEY REFERENCES observations(id) ON DELETE CASCADE,
    vector BLOB NOT NULL
);
"""

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
    """Lazy-loaded multilingual-e5-small."""

    def __init__(self, model_name: str = EMBEDDING_MODEL):
        self._model_name = model_name
        self._model: Any = None

    def _load(self) -> None:
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            logger.info("Loading embedding model %s...", self._model_name)
            self._model = SentenceTransformer(self._model_name)
            logger.info("Embedding model loaded.")

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
        self._embedder = _EmbeddingModel(model_name)

    def _ensure_connected(self) -> sqlite3.Connection:
        if self._db is None:
            Path(self._db_path).parent.mkdir(parents=True, exist_ok=True)
            self._db = sqlite3.connect(self._db_path, check_same_thread=False)
            self._db.row_factory = sqlite3.Row
            self._db.execute("PRAGMA journal_mode = WAL")
            self._db.execute("PRAGMA synchronous = NORMAL")
            self._db.execute("PRAGMA foreign_keys = ON")
            for stmt in _DDL.strip().split(";"):
                stmt = stmt.strip()
                if stmt:
                    self._db.execute(stmt)
            # Add columns if upgrading from old schema
            for col, definition in [
                ("kind", "TEXT NOT NULL DEFAULT 'observation'"),
                ("emotion", "TEXT NOT NULL DEFAULT 'neutral'"),
                ("image_path", "TEXT"),
                ("image_data", "TEXT"),
            ]:
                try:
                    self._db.execute(f"ALTER TABLE observations ADD COLUMN {col} {definition}")
                    self._db.commit()
                except Exception:
                    pass
            self._db.commit()
        return self._db

    def save(
        self,
        content: str,
        direction: str = "unknown",
        kind: str = "observation",
        emotion: str = "neutral",
        image_path: str | None = None,
        override_date: str | None = None,
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
        """
        try:
            db = self._ensure_connected()
            now = datetime.now()
            obs_id = str(uuid.uuid4())

            if override_date:
                save_date = override_date
                save_time = "23:59"
                save_timestamp = f"{override_date}T23:59:59"
            else:
                save_date = now.strftime("%Y-%m-%d")
                save_time = now.strftime("%H:%M")
                save_timestamp = now.isoformat()

            image_data = _encode_image(image_path) if image_path else None

            vec = self._embedder.encode_document([content])[0]
            blob = _encode_vector(vec)

            db.execute(
                "INSERT INTO observations "
                "(id, content, timestamp, date, time, direction, kind, emotion, image_path, image_data) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    obs_id,
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
                (obs_id, blob),
            )
            db.commit()
            logger.info("Saved %s (%s): %s...", kind, emotion, content[:60])
            return True
        except Exception as e:
            logger.warning("Failed to save memory: %s", e)
            return False

    def recall(self, query: str, n: int = 3, kind: str | None = None) -> list[dict]:
        """Recall by vector similarity. Fallback to LIKE + recency."""
        try:
            db = self._ensure_connected()

            kind_filter = "AND kind = ?" if kind else ""
            kind_params: list[Any] = [kind] if kind else []

            count = db.execute("SELECT COUNT(*) FROM obs_embeddings").fetchone()[0]

            if count > 0:
                query_vec = np.array(self._embedder.encode_query([query])[0], dtype=np.float32)

                rows = db.execute(
                    f"SELECT o.id, o.content, o.date, o.time, o.direction, o.kind, o.emotion, e.vector "
                    f"FROM observations o JOIN obs_embeddings e ON o.id = e.obs_id "
                    f"WHERE 1=1 {kind_filter}",
                    kind_params,
                ).fetchall()

                if not rows:
                    return []

                vecs = np.stack([_decode_vector(bytes(r["vector"])) for r in rows])
                scores = _cosine_similarity(query_vec, vecs)

                top_indices = np.argsort(scores)[::-1][:n]
                return [
                    {
                        "summary": rows[i]["content"],
                        "date": rows[i]["date"],
                        "time": rows[i]["time"],
                        "direction": rows[i]["direction"],
                        "kind": rows[i]["kind"],
                        "emotion": rows[i]["emotion"],
                        "score": float(scores[i]),
                    }
                    for i in top_indices
                ]

            # Fallback: LIKE keyword search + recency
            keywords = [w for w in query.split() if len(w) > 1][:4]
            if keywords:
                conditions = " OR ".join("content LIKE ?" for _ in keywords)
                params_like: list[Any] = [f"%{kw}%" for kw in keywords]
                if kind:
                    rows = db.execute(
                        f"SELECT content, date, time, direction, kind, emotion FROM observations "
                        f"WHERE ({conditions}) AND kind = ? ORDER BY timestamp DESC LIMIT ?",
                        params_like + [kind, n],
                    ).fetchall()
                else:
                    rows = db.execute(
                        f"SELECT content, date, time, direction, kind, emotion FROM observations "
                        f"WHERE {conditions} ORDER BY timestamp DESC LIMIT ?",
                        params_like + [n],
                    ).fetchall()
                if rows:
                    return [
                        {
                            "summary": r["content"],
                            "date": r["date"],
                            "time": r["time"],
                            "direction": r["direction"],
                            "kind": r["kind"],
                            "emotion": r["emotion"],
                        }
                        for r in rows
                    ]

            # Last resort: most recent
            rows = db.execute(
                "SELECT content, date, time, direction, kind, emotion FROM observations "
                "ORDER BY timestamp DESC LIMIT ?",
                (n,),
            ).fetchall()
            return [
                {
                    "summary": r["content"],
                    "date": r["date"],
                    "time": r["time"],
                    "direction": r["direction"],
                    "kind": r["kind"],
                    "emotion": r["emotion"],
                }
                for r in rows
            ]

        except Exception as e:
            logger.warning("Failed to recall memories: %s", e)
            return []

    def recent_feelings(self, n: int = 5) -> list[dict]:
        """Return the most recent emotional memories."""
        try:
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
        lines = ["[過去の記憶]:"]
        for m in memories:
            score_str = f" (類似度:{m['score']:.2f})" if "score" in m else ""
            emotion_str = (
                f" [{m['emotion']}]" if m.get("emotion") and m["emotion"] != "neutral" else ""
            )
            lines.append(
                f"- {m['date']} {m['time']} ({m.get('direction', '?')}){score_str}{emotion_str}: {m['summary'][:120]}"
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
    ) -> bool:
        return await asyncio.to_thread(
            self.save, content, direction, kind, emotion, image_path, override_date
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
        lines = [
            "[私が覚えていること — 過去の日々に私が見たもの、感じたこと]:"
        ]
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
                emotion = f" [{m['emotion']}]" if m.get("emotion", "neutral") != "neutral" else ""
                img = " 📷" if m.get("image_path") else ""
                lines.append(
                    f"- {m['date']} {m['time']}{score}{emotion}{img}: {m['summary'][:120]}"
                )
            return "\n".join(lines), None

        return f"Unknown memory tool: {tool_name}", None
