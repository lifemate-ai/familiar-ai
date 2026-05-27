# ADR 0002: Keep Python First, Add a Sidecar Only After Measurement

## Status

Accepted

## Context

The runtime reorganization could tempt a rewrite of process, filesystem, search, or scheduling
pieces into another language. familiar-ai currently benefits from Python's LLM SDK support, async
orchestration, ML/embedding ecosystem, hardware libraries, GUI/TUI integration, and existing test
coverage.

Current likely bottlenecks are not known to be Python CPU execution. More likely sources are model
latency, utility-model round trips, embedding startup/encoding, SQLite/vector scans, repository
search, subprocess cancellation, audio/event streams, and cross-platform process behavior.

## Decision

Keep the runtime Python-first.

Introduce a Rust or Go sidecar only when benchmarks show a concrete bottleneck or safety problem
that Python wrappers cannot handle well enough. If a sidecar becomes justified, prefer a narrow
supervisor process for file search, process execution, cancellation, git inspection, and workspace
snapshots.

## Consequences

- Existing packaging and hardware support remain simple.
- Runtime extraction can focus on architecture rather than language migration.
- Future sidecar work must start from benchmarks and preserve Python fallbacks.
- Normal Python package installation must not require a Rust build.

## Decision Gate For A Sidecar

Start a sidecar spike only if one of these is demonstrated:

- `grep`, `glob`, `bash`, or test execution becomes a top latency contributor.
- Process cancellation or streaming output is unreliable in real task runs.
- Always-on event/audio processing drops events.
- Stronger sandbox guarantees are needed than Python subprocess wrappers can provide.
