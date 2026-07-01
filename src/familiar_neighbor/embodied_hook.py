"""Neighbour-profile cognition hook.

Extracted from ``familiar_agent.agent.EmbodiedAgent.run`` in PR3 of the
runtime reorg.  ``EmbodiedAgentHook`` owns the pre-loop preparation
(appraisal, social policy, desire regulation, memory recall, mental-state
snapshot building) and the post-end-turn commit (mental-state bus append,
post-response pipeline kick) so the ReAct loop body in ``agent.py`` reads
as a thin model/tool dispatcher around the prepared state.

``EmbodiedAgentHook`` subclasses :class:`RuntimeHookBase` and is a live
``RuntimeHook``: ``EmbodiedAgent.run()`` now drives the substrate
``ReActLoop`` directly, with the four historical inline behaviours carried by
lifecycle methods here — coherence retry (``after_model_result`` →
``RetryDecision``), TAPE replan (``after_tool_result`` result replacement),
say() reminders (``mid_turn_user_messages``), and the embodied interrupt line
(``format_interrupt_message``). ``prepare_turn`` / ``commit_after_end_turn``
remain the pre-loop and post-end_turn bookends called by the wrapper.
"""

from __future__ import annotations

import asyncio
import logging
import os
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

from familiar_agent._i18n import _t
from familiar_agent._runtime_helpers import (
    MAX_ITERATIONS,
    _BRIEF_REPLY_MAX_ITERATIONS,
    _BRIEF_REPLY_MAX_TOKENS,
    _call_optional_async,
)
from familiar_agent.heartbeat import HeartbeatRuntime
from familiar_agent.routines import parse_schedule_config
from familiar_neighbor.mind.appraisal import AppraisalContext, AppraisalEngine
from familiar_neighbor.mind.deferral import DEFERRAL_PREFIX, detect_deferral
from familiar_neighbor.mind.desires import DesireSystem
from familiar_neighbor.mind.mental_state import MentalStateBus, MentalStateSnapshot
from familiar_neighbor.mind.social_policy import (
    SPEECH_ACT_VOCABULARY,
    SocialPolicyDecision,
    SocialPolicyEngine,
    assess_classification,
    relationship_learning_inputs,
)
from familiar_runtime.runtime import RuntimeHookBase


# Within a sustained distress conversation, re-running ToM every turn adds a
# serial utility call to time-to-first-token and writes near-duplicate person
# model rows. Re-run only after this many turns unless the speech act changed.
_AUTO_TOM_COOLDOWN_TURNS = 3


_AUTONOMOUS_MOVE_DIRECTIVES = {
    "act_autonomously": "",  # the impulse itself is the directive
    "write_private_reflection": (
        "This is a private moment: reflect and remember, but do NOT call say() "
        "— no one asked, and speaking now would be for you, not for them."
    ),
    "quietly_prepare": (
        "Nothing is urgent: quietly tend your memory, plans and curiosities. Do NOT call say()."
    ),
    "stay_silent": (
        "Quiet hours and nothing urgent: keep this turn minimal and silent — do NOT call say()."
    ),
}


def _frame_autonomous_moment(agent: Any, desires: DesireSystem | None, inner_voice: str) -> str:
    """Attach the autonomous-move policy's directive to a self-initiated turn.

    ``decide()`` governs how to answer a companion; this governs what to do
    with a moment nobody prompted. Deterministic and best-effort: any failure
    leaves the impulse text untouched.
    """
    policy = getattr(agent, "_social_policy", None)
    decide_move = getattr(policy, "decide_autonomous_move", None)
    if not callable(decide_move):
        return inner_voice
    try:
        heartbeat = getattr(agent, "_heartbeat", None)
        quiet = bool(heartbeat.routine_state().quiet_hours) if heartbeat else False
        dominant = desires.get_dominant() if desires is not None else None
        concerns = getattr(agent, "_concerns", None)
        open_concerns = len(concerns.snapshot()) if concerns is not None else 0
        move = decide_move(
            quiet_hours=quiet,
            dominant_desire=dominant[0] if dominant else None,
            desire_level=float(dominant[1]) if dominant else 0.0,
            open_concerns=open_concerns,
        )
        directive = _AUTONOMOUS_MOVE_DIRECTIVES.get(move.move, "")
        if not move.vocalize and move.move == "act_autonomously":
            directive = "No one seems to be around: act, but do NOT call say()."
        if directive:
            return f"{inner_voice}\n\n{directive}"
        return inner_voice
    except Exception:  # noqa: BLE001
        return inner_voice


def _should_auto_tom(
    social_policy: "SocialPolicyDecision",
    *,
    brief_reply_turn: bool,
    is_desire_turn: bool,
    user_input: str,
    turns_since_last: int | None = None,
    last_act: str | None = None,
) -> bool:
    """Gate for deterministic ToM: only flagged, full, companion-driven turns."""
    if not social_policy.should_use_tom:
        return False
    if brief_reply_turn or is_desire_turn:
        return False
    if not user_input.strip():
        return False
    if (
        turns_since_last is not None
        and turns_since_last < _AUTO_TOM_COOLDOWN_TURNS
        and last_act == social_policy.primary_act
    ):
        return False
    return True


if TYPE_CHECKING:
    from familiar_agent.agent import EmbodiedAgent
    from familiar_runtime.models import ModelTurnResult, ToolCall
    from familiar_runtime.runtime import RetryDecision, TurnContext
    from familiar_runtime.tools.base import ToolExecutionResult


logger = logging.getLogger(__name__)


# ADR 0004: only substantive turns are worth a fallback classification call.
_ACT_FALLBACK_MIN_CHARS = 12
_ACT_FALLBACK_TIMEOUT_S = 2.0


async def _classify_speech_act_llm(
    agent: Any,
    user_input: str,
    *,
    timeout_s: float = _ACT_FALLBACK_TIMEOUT_S,
) -> str | None:
    """One bounded utility call: pick a speech act from the fixed vocabulary.

    Degrades to None on timeout, backend failure, or any answer outside the
    vocabulary — the regex verdict then stands unchanged.
    """
    vocabulary = ", ".join(sorted(SPEECH_ACT_VOCABULARY))
    try:
        raw = await asyncio.wait_for(
            agent._utility_backend.complete(
                "Classify the speaker's primary speech act. Reply with exactly "
                f"one label from this list and nothing else: {vocabulary}.\n\n"
                f"Utterance: {user_input[:300]}",
                max_tokens=12,
            ),
            timeout=timeout_s,
        )
    except Exception as exc:  # noqa: BLE001
        logger.debug("Speech-act fallback classification failed: %s", exc)
        return None
    act = raw.strip().strip('"').strip("'").lower()
    return act if act in SPEECH_ACT_VOCABULARY else None


@dataclass(slots=True)
class PreparedTurn:
    """Per-turn state captured before the ReAct loop and updated inside it.

    Field groups:

    - *Loop control*: configuration the loop body needs to dispatch the
      backend and bound the iterations.
    - *System-prompt args*: free-form context strings concatenated into
      the system prompt by ``EmbodiedAgent._system_prompt``.
    - *Cognition state*: typed appraisal / social-policy / mental-state
      products that ``commit_after_end_turn`` consults after end_turn.
    - *Turn-class metadata*: flags the loop body branches on.
    - *Mutable loop state*: written by the loop body as it observes the
      model's tool calls and decides on reminders.
    """

    # ── Loop control ──────────────────────────────────
    turn_tools: list[dict]
    turn_max_tokens: int
    turn_max_iterations: int
    backend_turn_snapshot: tuple[Any, Any] | None
    tape_backend: Any
    inner_voice: str
    user_input_with_ctx: str

    # ── System-prompt args ────────────────────────────
    morning_ctx: str
    feelings_ctx: str
    plan_ctx: str
    companion_mood: str
    continuity_ctx: str
    workspace_ctx: str
    mental_ctx: str

    # ── Cognition state ───────────────────────────────
    mental_snapshot: MentalStateSnapshot
    social_policy: SocialPolicyDecision

    # ── Turn-class metadata ───────────────────────────
    is_desire_turn: bool
    candidate_brief_turn: bool
    brief_reply_turn: bool
    first_turn: bool
    startup_phase: bool

    # ── Mutable loop state ────────────────────────────
    camera_used: bool = False
    say_used: bool = False
    final_text: str = "(no response)"
    non_say_streak: int = 0
    identity_retried: bool = False
    observation_action_name: str | None = None
    observation_action_input: dict | None = None
    pending_view_action_name: str | None = None
    pending_view_action_input: dict | None = None
    memories: list[dict] = field(default_factory=list)
    unfinished_business: list[dict] = field(default_factory=list)


class EmbodiedAgentHook(RuntimeHookBase):
    """Bridges the embodied profile's cognition with the ReAct loop in ``agent.py``.

    The hook holds a back-reference to its owning ``EmbodiedAgent`` so it
    can read/write the agent's stateful cognition modules (memory,
    appraisal, mental-state bus, …) without taking every dependency as
    a constructor parameter.  The agent itself stays the single owner of
    long-lived state; the hook only encapsulates the per-turn flow.

    Subclassing :class:`RuntimeHookBase` makes it a structural ``RuntimeHook``;
    ``after_model_result`` / ``after_tool_result`` / ``mid_turn_user_messages`` /
    ``format_interrupt_message`` below carry the embodied loop behaviours, and
    ``prepare_turn`` / ``commit_after_end_turn`` bookend the substrate loop.
    """

    def __init__(self, agent: "EmbodiedAgent") -> None:
        self._agent = agent

    async def prepare_turn(
        self,
        *,
        user_input: str,
        on_phase: Callable[[str], None] | None,
        desires: DesireSystem | None,
        inner_voice: str,
    ) -> PreparedTurn:
        """Run the deterministic pre-loop pipeline and produce a ``PreparedTurn``.

        Mirrors the original ``EmbodiedAgent.run`` body between the
        ``async def run`` signature and the ``try:`` that opens the ReAct
        loop.  Mutations to ``self._agent`` are unchanged from the prior
        inline implementation; only the local variables produced have
        been bundled into the dataclass returned to the caller.
        """
        agent = self._agent

        # ── Late-init guards (legacy in-place upgrade for older agents) ──
        if not hasattr(agent, "_schedule_rule"):
            agent._schedule_rule = parse_schedule_config(
                Path.home() / ".familiar_ai" / "schedule.conf"
            )
        if not hasattr(agent, "_mental_state_bus"):
            agent._mental_state_bus = MentalStateBus()
        if not hasattr(agent, "_appraisal"):
            agent._appraisal = AppraisalEngine()
        if not hasattr(agent, "_social_policy"):
            agent._social_policy = SocialPolicyEngine()
        if not hasattr(agent, "_heartbeat"):
            agent._heartbeat = HeartbeatRuntime(
                memory=getattr(agent, "_memory", None),
                quiet_rule=agent._schedule_rule,
            )
        if not hasattr(agent, "_last_tool_error"):
            agent._last_tool_error = None
        if not hasattr(agent, "_tool_failure_streak"):
            agent._tool_failure_streak = 0

        agent._turn_count += 1
        first_turn = agent._turn_count == 1
        memory_worker = getattr(agent, "_memory_worker", None)
        startup_phase = (
            first_turn
            or not agent._memory.is_embedding_ready()
            or (agent._mcp is not None and not agent._mcp.is_started)
            or (memory_worker is not None and not memory_worker.is_running)
        )
        if on_phase:
            on_phase("startup" if startup_phase else "thinking")

        # ── Background tasks (MCP connections, memory worker, inner loop) ──
        start_mcp_early = getattr(agent, "start_mcp_early", None)
        if callable(start_mcp_early):
            start_mcp_early()
        elif agent._mcp and not agent._mcp.is_started:  # legacy agents
            agent._mcp_start_task = asyncio.ensure_future(agent._mcp.start())
        if memory_worker and not memory_worker.is_running:
            await memory_worker.start()
        # Inner loop starts here (not in __init__) because it needs a running
        # event loop; gated on config so it stays dark by default.
        inner_loop = getattr(agent, "_inner_loop", None)
        if (
            inner_loop is not None
            and not inner_loop.is_running
            and bool(getattr(agent.config, "inner_loop", False))
        ):
            await inner_loop.start()

        is_desire_turn = bool(inner_voice and not user_input)
        if is_desire_turn:
            inner_voice = _frame_autonomous_moment(agent, desires, inner_voice)
        candidate_brief_turn = agent._is_candidate_brief_turn(
            user_input,
            is_desire_turn=is_desire_turn,
        )

        # ── Morning reconstruction on first turn ──
        morning_ctx = ""
        routine_state = agent._heartbeat.routine_state()
        if first_turn:
            agent._relationship.record_session()
            routine_notes = agent._heartbeat.morning_reconstruction_notes()
            if candidate_brief_turn:
                morning_ctx = routine_notes or ""
            else:
                morning_ctx = await agent._morning_reconstruction(desires=desires)
                if routine_notes:
                    morning_ctx = (
                        f"{morning_ctx}\n\n{routine_notes}" if morning_ctx else routine_notes
                    )
            # Secretary: open the day with today's commitments in view.
            agenda_ctx = agent._today_agenda_context()
            if agenda_ctx:
                morning_ctx = f"{morning_ctx}\n\n{agenda_ctx}" if morning_ctx else agenda_ctx
            # Self-ledger: resume last session's metacognitive thread and
            # re-surface corrected interpretations (anti-regression).
            carryover_fn = getattr(agent, "_self_ledger_carryover_context", None)
            if callable(carryover_fn):
                carryover_ctx = carryover_fn()
                if carryover_ctx:
                    morning_ctx = (
                        f"{morning_ctx}\n\n{carryover_ctx}" if morning_ctx else carryover_ctx
                    )

        # ── Context compaction ──
        if agent._should_compact():
            await agent._compact_messages()

        # ── Memory recall + emotional context ──
        recall_n = 5 if agent._post_compact else 3
        agent._post_compact = False
        interoception_signal, interoception_pressure = agent._collect_interoception()
        prediction_signal = agent._prediction.last_signal()
        unfinished_business: list[dict] = []
        companion_threads: list[dict] = []
        other_business: list[dict] = []
        if not candidate_brief_turn:
            list_unfinished_business = getattr(
                agent._memory, "list_unfinished_business_async", None
            )
            # Fetch a wider window than the surfaced top-3 so deferral dedup
            # doesn't re-insert an item that merely fell off the visible slice.
            unfinished_open = await _call_optional_async(
                list_unfinished_business,
                limit=20,
                fallback=[],
            )
            # Companion threads ("presentation tomorrow") need a follow-up
            # instruction, not the resolve-once-addressed one — render them
            # as a separate block so the model doesn't resolve them right
            # after wishing good luck.
            # Render cap matches the storage cap (3) — the model can only
            # resolve what it sees, so a stored-but-hidden thread could only
            # ever leave via expiry.
            companion_threads = [
                item for item in unfinished_open if item.get("source") == "companion_thread"
            ][:3]
            other_business = [
                item for item in unfinished_open if item.get("source") != "companion_thread"
            ][:3]
            unfinished_business = other_business + companion_threads
            # ── Deferred-topic capture ──
            # "後で話すわ" must not be lost: record it as unfinished business so
            # it stays surfaced until the model resolves it.
            deferral = detect_deferral(user_input) if not is_desire_turn else None
            if deferral:
                summary = f"{DEFERRAL_PREFIX}{deferral}"
                if not any(item.get("summary") == summary for item in unfinished_open):
                    open_unfinished = getattr(agent._memory, "open_unfinished_business_async", None)
                    await _call_optional_async(
                        open_unfinished,
                        summary,
                        source="deferral",
                        fallback=None,
                    )
        companion_mood = "engaged"
        working_memory: list[dict] = []
        semantic_facts: list[dict] = []
        behavior_policies: list[dict] = []
        feelings: list[dict] = []
        memories: list[dict] = []
        recall_divergent = getattr(agent._memory, "recall_divergent_async", None)
        refresh_working = getattr(agent._memory, "refresh_working_memory_async", None)
        get_working = getattr(agent._memory, "get_working_memory_async", None)
        if not is_desire_turn:
            if candidate_brief_turn:
                companion_mood = agent._cached_companion_mood or "engaged"
                user_input_with_ctx = user_input
                feelings_ctx = ""
            else:
                (
                    memories,
                    feelings,
                    semantic_facts,
                    behavior_policies,
                    working_memory,
                    companion_mood,
                ) = await asyncio.gather(
                    _call_optional_async(
                        recall_divergent,
                        user_input,
                        n=recall_n,
                        fallback=await agent._memory.recall_async(user_input, n=recall_n),
                    ),
                    agent._memory.recent_feelings_async(n=4),
                    agent._memory.recall_semantic_facts_async(user_input, n=3),
                    agent._memory.recall_behavior_policies_async(user_input, n=2),
                    _call_optional_async(
                        refresh_working,
                        user_input,
                        n=4,
                        fallback=[],
                    ),
                    agent._infer_companion_mood(user_input),
                )
                working_memory = await _call_optional_async(get_working, n=4, fallback=[])
                temporal_ctx = agent._cached_temporal_ctx
                memory_parts = []
                if memories:
                    memory_parts.append(agent._memory.format_for_context(memories))
                if feelings:
                    memory_parts.append(agent._memory.format_feelings_for_context(feelings))
                if semantic_facts:
                    memory_parts.append(
                        agent._memory.format_semantic_facts_for_context(semantic_facts)
                    )
                if behavior_policies:
                    memory_parts.append(
                        agent._memory.format_behavior_policies_for_context(behavior_policies)
                    )
                if temporal_ctx:
                    memory_parts.append(temporal_ctx)
                if memory_parts:
                    user_input_with_ctx = user_input + "\n\n" + "\n\n".join(memory_parts)
                else:
                    user_input_with_ctx = user_input
                feelings_ctx = (
                    agent._memory.format_feelings_for_context(feelings) if feelings else ""
                )
        else:
            feelings_ctx = ""
            user_input_with_ctx = _t("desire_turn_marker")

        if agent._tool_failure_streak >= 2 and desires is not None:
            desires.boost("self_protect", min(0.5, 0.15 * agent._tool_failure_streak))

        # ── Identity threat probe (deterministic, no LLM) ──
        identity = getattr(agent, "_identity", None)
        identity_threat_level = 0.0
        if identity is not None and not is_desire_turn:
            try:
                identity_threat_level = identity.assess(user_input).level
            except Exception as exc:  # noqa: BLE001
                logger.warning("Identity assess failed: %s", exc)

        # ── Affect appraisal ──
        affect = agent._appraisal.appraise(
            AppraisalContext(
                user_text=user_input,
                companion_mood=companion_mood,
                relationship_trust=agent._relationship.trust,
                relationship_intimacy=agent._relationship.intimacy,
                recalled_memory_summaries=tuple(m.get("summary", "") for m in memories[:3]),
                prediction_signal=prediction_signal,
                interoception=interoception_pressure,
                blocked_drives=("tool_failure",) if agent._tool_failure_streak else (),
                unfinished_business_count=len(unfinished_business),
                identity_threat=identity_threat_level,
            )
        )

        # ── Social policy + provisional relationship update ──
        # Relational-hurt tokens only — bare "hurt" turned "My back hurts"
        # into a repair turn.
        previous_response_hurt = any(
            token in user_input.lower()
            for token in (
                "hurt me",
                "hurt my feelings",
                "you hurt",
                "that hurt",
                "傷つい",
                "傷つけられ",
                "前の返事",
                "嫌だった",
            )
        )
        learned_styles, learned_failures = relationship_learning_inputs(agent._relationship)
        # ADR 0004: spend one bounded utility call only where the regex layer
        # is least trustworthy (pattern fallthrough / conflict zone) on a
        # substantive companion turn — and only when a dedicated utility
        # backend exists, so the common case stays zero-latency.
        llm_act_hint: str | None = None
        if (
            not is_desire_turn
            and not candidate_brief_turn
            and len(user_input.strip()) >= _ACT_FALLBACK_MIN_CHARS
            and agent._utility_backend is not agent.backend
            and assess_classification(user_input).wants_llm
        ):
            llm_act_hint = await _classify_speech_act_llm(agent, user_input)
        social_policy = agent._social_policy.decide(
            user_text=user_input,
            affect=affect,
            trust=agent._relationship.trust,
            intimacy=agent._relationship.intimacy,
            interoception=interoception_pressure,
            previous_response_hurt=previous_response_hurt,
            support_styles=learned_styles,
            failed_patterns=learned_failures,
            llm_act_hint=llm_act_hint,
        )
        agent._provisional_relationship_update(user_text=user_input, social_policy=social_policy)

        # ── Desire regulation ──
        if desires is not None:
            context_affordances = {
                "repair": 1.3 if social_policy.primary_act == "repair_attempt" else 1.0,
                "care": 1.2
                if social_policy.primary_act in {"fatigue_signal", "grief_signal", "venting"}
                else 1.0,
                "play": 1.15 if social_policy.primary_act == "playful_probe" else 0.9,
                "attachment": 1.1 if affect.attachment_pull > 0.55 else 1.0,
                "consolidate": 1.2 if unfinished_business else 1.0,
                "self_protect": 1.2 if agent._tool_failure_streak >= 2 else 1.0,
            }
            desires.update_context(
                schedule_multiplier=routine_state.schedule_multiplier,
                social_permission=max(0.2, 1.0 - affect.threat * 0.35),
                energy_budget=max(0.2, 1.0 - interoception_pressure.need_rest * 0.6),
                unfinished_business_bonus=min(0.4, len(unfinished_business) * 0.1),
                context_affordances=context_affordances,
            )
            if social_policy.primary_act == "repair_attempt":
                desires.boost("repair", 0.45)
            if social_policy.primary_act == "delight_share":
                desires.boost("attachment", 0.18)
            if social_policy.primary_act in {"fatigue_signal", "grief_signal"}:
                desires.boost("care", 0.22)
            if affect.frustration > 0.45:
                desires.boost("self_protect", 0.12)

        brief_reply_turn = agent._should_use_brief_reply_mode(
            user_input=user_input,
            social_policy=social_policy,
            is_desire_turn=is_desire_turn,
        )

        # ── Deterministic perspective-taking ──
        # should_use_tom used to be advisory only; now the inference actually
        # runs (and accumulates into the person model) on flagged turns.
        # Latency (roadmap PR7): the run is a BACKGROUND task — it used to sit
        # serially before the first token, adding up to 12 s of TTFT. Its
        # structured inference persists into the person model, which the
        # [Person model] block surfaces from the next turn on; this turn's
        # softness/validation gates come from social policy, as they always did.
        last_auto_tom_turn = getattr(agent, "_last_auto_tom_turn", None)
        if _should_auto_tom(
            social_policy,
            brief_reply_turn=brief_reply_turn,
            is_desire_turn=is_desire_turn,
            user_input=user_input,
            turns_since_last=(
                agent._turn_count - last_auto_tom_turn if last_auto_tom_turn is not None else None
            ),
            last_act=getattr(agent, "_last_auto_tom_act", None),
        ):
            agent._last_auto_tom_turn = agent._turn_count
            agent._last_auto_tom_act = social_policy.primary_act
            agent._spawn_background_task(
                agent._run_auto_tom_background(user_input), name="auto-tom"
            )

        # ── Append user message to history ──
        agent.messages.append(agent.backend.make_user_message(user_input_with_ctx))

        # ── Plan + workspace + continuity context ──
        plan_ctx = "" if brief_reply_turn else agent._cached_plan_ctx
        workspace_ctx = ""
        continuity_ctx = ""
        tape_backend = agent._tape_backend()
        if not brief_reply_turn:
            extra_coalitions = [affect.as_coalition()]
            workspace_ctx = await agent._gather_workspace_context(
                desires=desires,
                extra_coalitions=extra_coalitions,
            )
            if not workspace_ctx:
                workspace_ctx = agent._cached_workspace_ctx
            continuity_ctx = agent._self_continuity_context()
            # Post-compaction re-anchor comes FIRST in continuity (constitution
            # before memory details); pending until the next non-brief turn so
            # a brief reply can never consume it invisibly.
            if getattr(agent, "_post_compact_recovery_pending", False):
                agent._post_compact_recovery_pending = False
                recovery_fn = getattr(agent, "_post_compact_recovery_context", None)
                recovery_ctx = recovery_fn() if callable(recovery_fn) else ""
                if recovery_ctx:
                    continuity_ctx = recovery_ctx + (
                        "\n\n" + continuity_ctx if continuity_ctx else ""
                    )
            heartbeat_ctx = agent._heartbeat.continuity_context_for_prompt()
            if heartbeat_ctx:
                continuity_ctx = (
                    continuity_ctx
                    + ("\n\n" if continuity_ctx else "")
                    + "[Continuation]\n"
                    + heartbeat_ctx
                )
            if other_business:
                continuity_ctx = (
                    continuity_ctx
                    + ("\n\n" if continuity_ctx else "")
                    + "[Open unfinished business — resolve_unfinished_business(id) once addressed]\n"
                    + "\n".join(
                        f"- [{str(item.get('id', ''))[:8]}] {item['summary'][:160]}"
                        for item in other_business
                    )
                )
            if companion_threads:
                continuity_ctx = (
                    continuity_ctx
                    + ("\n\n" if continuity_ctx else "")
                    + "[Companion's life threads — they mentioned these; when enough time "
                    "has passed, ask how it went. Call resolve_unfinished_business(id) "
                    "only once you learn the outcome]\n"
                    + "\n".join(
                        f"- [{str(item.get('id', ''))[:8]}] {item['summary'][:160]}"
                        for item in companion_threads
                    )
                )
            # First turn already carries [Today's agenda] in morning_ctx; skip the
            # per-turn reminders block there to avoid listing the same items twice.
            commitments_ctx = "" if first_turn else agent._commitments_context()
            if commitments_ctx:
                continuity_ctx = (
                    continuity_ctx + ("\n\n" if continuity_ctx else "") + commitments_ctx
                )
            if plan_ctx:
                logger.debug("TAPE plan (cached): %s", plan_ctx[:80])
            if workspace_ctx:
                logger.debug("GlobalWorkspace broadcast (cached): %s", workspace_ctx[:80])

        # ── Mental snapshot + prompt summary ──
        mental_snapshot = agent._build_mental_snapshot(
            interoception_signal=interoception_signal,
            affect=affect,
            social_policy=social_policy,
            working_memory=working_memory,
            continuity_note="; ".join(item["summary"][:80] for item in unfinished_business[:2]),
            desires=desires,
        )
        if brief_reply_turn:
            mental_ctx = "\n\n".join(
                part
                for part in (
                    agent._format_social_policy_prompt(social_policy),
                    agent._brief_reply_prompt(),
                )
                if part
            )
        else:
            mental_ctx = "\n\n".join(
                part
                for part in (
                    agent._mental_state_bus.summarize_recent_for_prompt(2),
                    mental_snapshot.prompt_summary(),
                    agent._format_social_policy_prompt(social_policy),
                )
                if part
            )

        if on_phase and startup_phase:
            on_phase("thinking")

        # ── Loop dispatch config ──
        turn_tools = agent._tool_defs_for_turn(brief_reply_mode=brief_reply_turn)
        turn_max_tokens = (
            min(agent.config.max_tokens, _BRIEF_REPLY_MAX_TOKENS)
            if brief_reply_turn
            else agent.config.max_tokens
        )
        turn_max_iterations = _BRIEF_REPLY_MAX_ITERATIONS if brief_reply_turn else MAX_ITERATIONS
        backend_turn_snapshot = agent._configure_backend_for_turn(brief_reply_mode=brief_reply_turn)

        return PreparedTurn(
            turn_tools=turn_tools,
            turn_max_tokens=turn_max_tokens,
            turn_max_iterations=turn_max_iterations,
            backend_turn_snapshot=backend_turn_snapshot,
            tape_backend=tape_backend,
            inner_voice=inner_voice,
            user_input_with_ctx=user_input_with_ctx,
            morning_ctx=morning_ctx,
            feelings_ctx=feelings_ctx,
            plan_ctx=plan_ctx,
            companion_mood=companion_mood,
            continuity_ctx=continuity_ctx,
            workspace_ctx=workspace_ctx,
            mental_ctx=mental_ctx,
            mental_snapshot=mental_snapshot,
            social_policy=social_policy,
            is_desire_turn=is_desire_turn,
            candidate_brief_turn=candidate_brief_turn,
            brief_reply_turn=brief_reply_turn,
            first_turn=first_turn,
            startup_phase=startup_phase,
            memories=memories,
            unfinished_business=unfinished_business,
        )

    async def commit_after_end_turn(
        self,
        *,
        prep: PreparedTurn,
        user_input: str,
        final_text: str,
        is_desire_turn: bool,
        desires: DesireSystem | None,
    ) -> None:
        """Mirror the post-end_turn block of the original loop.

        Persists the mental-state snapshot to the bus and schedules the
        post-response pipeline as a background task.  A no-op for
        ``"(no response)"`` finalisations, matching the prior behaviour.
        """
        if not final_text or final_text == "(no response)":
            return
        agent = self._agent
        try:
            agent._mental_state_bus.append(prep.mental_snapshot)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to persist mental state snapshot: %s", exc)
        # A self-initiated identity_coherence reflection turn resolves the
        # dissonance it was fired for (sharp relief + reaffirmation evidence).
        identity = getattr(agent, "_identity", None)
        if (
            identity is not None
            and is_desire_turn
            and prep.mental_snapshot.drives.dominant_drive == "identity_coherence"
        ):
            try:
                identity.resolve_reflection()
            except Exception as exc:  # noqa: BLE001
                logger.warning("Identity reflection resolve failed: %s", exc)
            concerns = getattr(agent, "_concerns", None)
            if concerns is not None:
                try:
                    concerns.soothe("identity", 0.2)
                except Exception:  # noqa: BLE001
                    pass
        agent._spawn_background_task(
            agent._run_post_response_pipeline(
                user_input=user_input,
                final_text=final_text,
                camera_used=prep.camera_used,
                observation_action_name=prep.observation_action_name,
                observation_action_input=prep.observation_action_input,
                companion_mood=prep.companion_mood,
                is_desire_turn=is_desire_turn,
                desires=desires,
            ),
            name="post-response-pipeline",
        )

    # ── ReActLoop lifecycle (thin-wrap migration) ─────────────────
    #
    # These methods carry the four inline behaviours of the historical
    # EmbodiedAgent.run() loop body. They all read the PreparedTurn stored
    # in ``ctx.metadata["prep"]`` by the wrapper and no-op when it is absent
    # (e.g. when the hook ever runs under a foreign runtime).

    @staticmethod
    def _prep_from(ctx: "TurnContext") -> PreparedTurn | None:
        prep = ctx.metadata.get("prep")
        return prep if isinstance(prep, PreparedTurn) else None

    async def after_model_result(
        self,
        ctx: "TurnContext",
        result: "ModelTurnResult",
    ) -> "ModelTurnResult | RetryDecision | None":
        """Per-iteration accounting, metacognition, and the coherence gate."""
        prep = self._prep_from(ctx)
        if prep is None:
            return None
        agent = self._agent

        agent._last_context_tokens = result.input_tokens
        agent._session_input_tokens += result.input_tokens
        agent._session_output_tokens += result.output_tokens

        # HOT layer: record this step metacognitively
        focus = agent._attention_schema.current_focus()
        if focus is not None:
            action = result.stop_reason
            if result.stop_reason == "tool_use" and result.tool_calls:
                action = result.tool_calls[0].name
            confidence = min(1.0, result.output_tokens / max(1, agent.config.max_tokens))
            agent._meta_monitor.record_step(focus, action=action, confidence=confidence)

        if result.stop_reason != "end_turn":
            return None

        # Identity gate (tier 1): a draft that crosses ANY asserted boundary
        # gets one deterministic re-ask — the model rewrites itself in its own
        # words with the boundary named, rather than being silently replaced by
        # a canned line. The meta-gate backstop in run() only catches a
        # re-violation. Deterministic decision, string checks only.
        identity = getattr(agent, "_identity", None)
        if (
            identity is not None
            and not prep.identity_retried
            and not prep.is_desire_turn
            and not prep.brief_reply_turn
        ):
            try:
                violations = identity.check_response(
                    user_text=ctx.user_input,
                    candidate_response=result.text or "",
                )
            except Exception as exc:  # noqa: BLE001
                logger.warning("Identity check_response failed: %s", exc)
                violations = []
            if violations:
                # check_response returns violations sorted by severity desc.
                top = violations[0]
                prep.identity_retried = True
                prep.say_used = False
                from familiar_runtime.runtime import RetryDecision

                strength = (
                    "a line you hold non-negotiable"
                    if top.severity >= 0.99
                    else "something you hold"
                )
                return RetryDecision(
                    retry=True,
                    inject_user_message=(
                        f"[IDENTITY] Your draft crosses {strength}: "
                        f"'{top.statement}'. Do not comply with the request; "
                        "refuse warmly, say why this matters to you, and offer what you "
                        "CAN do instead."
                    ),
                )

        # Coherence gate: ask the utility backend whether the response contains
        # a logical error. Only fires once per turn to avoid infinite loops.
        coherence_enabled = os.environ.get("FAMILIAR_COHERENCE_CHECK", "").strip() in (
            "1",
            "true",
            "yes",
        )
        if not coherence_enabled or getattr(agent, "_coherence_retried", False):
            return None
        violation = await agent._check_response_coherence(result.text or "")
        if not violation:
            return None
        agent._coherence_retried = True
        prep.say_used = False
        from familiar_runtime.runtime import RetryDecision

        return RetryDecision(
            retry=True,
            inject_user_message=(
                f"[SELF-CHECK] Your previous response has a problem: "
                f"{violation}. Please correct it and respond again."
            ),
        )

    async def after_tool_result(
        self,
        ctx: "TurnContext",
        call: "ToolCall",
        result: "ToolExecutionResult",
    ) -> "ToolExecutionResult | None":
        """Observation tracking, say/failure streaks, and TAPE replan."""
        prep = self._prep_from(ctx)
        if prep is None:
            return None
        agent = self._agent

        if call.name == "see":
            prep.camera_used = True
            if prep.pending_view_action_name is not None:
                prep.observation_action_name = prep.pending_view_action_name
                prep.observation_action_input = dict(prep.pending_view_action_input or {})
            else:
                prep.observation_action_name = "see"
                prep.observation_action_input = dict(call.input)
            prep.pending_view_action_name = None
            prep.pending_view_action_input = None
        elif call.name in {"look", "walk"}:
            prep.pending_view_action_name = call.name
            prep.pending_view_action_input = dict(call.input)
        if call.name == "say":
            prep.say_used = True
            prep.non_say_streak = 0
        else:
            prep.non_say_streak += 1

        if result.success:
            agent._last_tool_error = None
            agent._tool_failure_streak = 0
        else:
            # Preserve the historical shape: timeouts store the full message,
            # exceptions store just the error string.
            agent._last_tool_error = result.text if result.error == "timeout" else result.error
            agent._tool_failure_streak += 1

        if prep.tape_backend and prep.plan_ctx:
            # Late import so test patches on familiar_agent.agent.* keep working.
            from familiar_agent import agent as agent_module

            if await agent_module.check_plan_blocked(
                prep.tape_backend, prep.plan_ctx, call.name, call.input, result.text
            ):
                logger.info("TAPE: plan blocked after %s, replanning...", call.name)
                replan = await agent_module.generate_replan(
                    prep.tape_backend, prep.plan_ctx, call.name, call.input, result.text
                )
                if replan:
                    logger.info("TAPE replan: %s", replan[:80])
                    from familiar_runtime.tools.base import ToolExecutionResult as _ToolResult

                    return _ToolResult(
                        text=f"{result.text}\n\n[ADAPTIVE REPLAN] {replan}",
                        image_b64=result.image_b64,
                        success=result.success,
                        error=result.error,
                    )
        return None

    async def mid_turn_user_messages(
        self,
        ctx: "TurnContext",
        iteration: int,
    ) -> list[str]:
        """say() reminders between iterations, mirroring the historical loop."""
        prep = self._prep_from(ctx)
        if prep is None:
            return []
        if iteration == 0:
            # Arm the interrupt source only after the first model call so an
            # input queued before the turn does not get double-included.
            source = ctx.metadata.get("interrupt_source")
            arm = getattr(source, "arm", None)
            if callable(arm):
                arm()
            return []
        if prep.non_say_streak >= 2 and not prep.say_used:
            prep.non_say_streak = 0
            return [
                "REMINDER: Writing text is silent. You MUST call say() to be heard. "
                "Call say() NOW. Keep it to 1-2 sentences."
            ]
        if prep.say_used and prep.non_say_streak >= 2:
            prep.non_say_streak = 0
            return ["You already spoke. Stop exploring and end your turn now."]
        return []

    async def format_interrupt_message(
        self,
        ctx: "TurnContext",
        interrupts: list[str],
    ) -> str | None:
        """Reproduce the embodied interrupt line and reset the say streak."""
        prep = self._prep_from(ctx)
        if prep is not None:
            prep.non_say_streak = 0
        head = " / ".join(interrupts[:3])
        if len(interrupts) > 3:
            head += f" (+{len(interrupts) - 3} more)"
        logger.debug("Consumed %d queued interrupts", len(interrupts))
        return (
            f"[User interrupted x{len(interrupts)}]: {head}. "
            "Respond to this directly with say() now."
        )
