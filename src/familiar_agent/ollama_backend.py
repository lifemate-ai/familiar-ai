"""Compatibility shim — the implementation lives in :mod:`familiar_runtime.models.ollama`."""

from familiar_runtime.models.ollama import (
    DEFAULT_BASE_URL,
    DEFAULT_NUM_CTX,
    OllamaBackend,
    normalize_base_url,
    think_flag,
)

__all__ = [
    "DEFAULT_BASE_URL",
    "DEFAULT_NUM_CTX",
    "OllamaBackend",
    "normalize_base_url",
    "think_flag",
]
