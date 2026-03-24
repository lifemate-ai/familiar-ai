"""Global pytest configuration for familiar-ai."""

from __future__ import annotations

import os


# ObservationMemory prewarms heavy embedding threads on init. In the full test
# suite that causes many concurrent daemon loads, noisy progress bars, and
# unstable shutdown behavior. Disable it globally unless a test explicitly opts in.
os.environ.setdefault("FAMILIAR_EMBEDDING_PREWARM", "0")
