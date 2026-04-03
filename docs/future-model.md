# Chronos-Neighbor: Next-Generation Temporal Relational Model

## Motivation

Current familiar-ai uses frontier LLMs (Claude, GPT) as the core reasoning engine. This works but has fundamental limitations:

1. **API cost** — every turn costs money; autonomous behavior multiplies this
2. **Transcript-centric** — LLMs reason over conversation logs, not world state
3. **No temporal persistence** — each API call starts fresh; continuity is bolted on
4. **Latency** — cloud round-trips add seconds to every response

The goal is to progressively replace cloud LLM dependency with local, temporal, relational models purpose-built for neighbor-like behavior.

## Core Insight

Neighbor-like behavior requires predicting **states**, not **tokens**.

The model should predict:
- User state (fatigue, focus, affect, needs)
- Environment state (time, noise, activity)
- Relationship state (trust, intimacy, recent tension)
- Self state (arousal, confidence, intervention budget)
- Optimal action (intervene / observe / silence / escalate)

Language generation is a downstream task, not the core capability.

## Architecture

```
Event Stream → [Event Encoder] → [State Updater] → [Policy Head] → Action
                                       ↕
                              [Memory Read/Write]
                                       ↕
                              [Verbalizer (small LM)]
```

### Event Encoder (0.1-0.3B)
- Small multimodal transformer
- Converts raw events to latent representations
- Always running locally

### State Updater (0.3-1B)
- State-space model or linear attention
- Maintains latent world state continuously
- Handles long-term temporal dependencies efficiently
- Cheaper than dense transformer for continuous input

### Policy Head (0.1-0.5B)
- Lightweight transformer
- Decides: intervene / observe / silence / escalate
- Outputs intervention type, timing, and confidence

### Verbalizer (1-3B)
- Small language decoder
- Generates short utterances from policy output + state
- Only called when intervention is needed
- Can be augmented by cloud LLM for complex responses

## Training Objectives

1. **State consistency loss** — world state predictions match observed next state
2. **Temporal persistence loss** — correctly predict how long states persist
3. **Intervention utility loss** — interventions that improve user state are rewarded
4. **Relational fidelity loss** — actions maintain relationship consistency

## Staged Transition Plan

### Phase 1: Current (LLM + rule-based subsystems)
- Frontier LLM handles all reasoning and generation
- Rule-based state tracking, desires, concerns
- Embedding model for memory retrieval

### Phase 2: Learned state estimators
- Train small classifiers from logged data:
  - Fatigue predictor
  - Intervention-worthiness classifier
  - Relation update model
- Replace rule-based heuristics in self_state.py, prediction.py

### Phase 3: Local compact policy model
- Train intervention policy from logged decisions + outcomes
- Replace workspace competition with learned policy
- Cloud LLM only for complex verbalization

### Phase 4: Temporal relational latent model (Chronos-Neighbor v1)
- Event-centric input (not transcript)
- Continuous state updates via state-space model
- Memory read/write as model operations
- Cloud LLM as rare escalation path

## Data Strategy

Training data comes from:
1. **Real usage logs** — familiar-ai event logs, intervention outcomes
2. **Simulated life logs** — synthetic daily patterns with intervention scenarios
3. **Multi-agent interaction** — generated care/companion scenarios
4. **Replay with counterfactuals** — "what if we had intervened earlier/later?"

## Edge Deployment Targets

- **Always-on tier** (0.3-1.5B): Raspberry Pi 5 / smartphone NPU
- **On-demand tier** (3-8B): Laptop GPU / Apple Silicon
- **Escalation tier**: Cloud API (Claude / GPT)

Target: cloud dependency ratio < 10% for daily operation.
