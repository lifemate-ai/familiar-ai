"""Neighbour-profile cognition hook.

Extracted from ``familiar_agent.agent.EmbodiedAgent.run`` in PR3 of the
runtime reorg.  ``EmbodiedAgentHook`` owns the pre-loop preparation
(appraisal, social policy, desire regulation, memory recall, mental-state
snapshot building) and the post-end-turn commit (mental-state bus append,
post-response pipeline kick) so the ReAct loop body in ``agent.py`` reads
as a thin model/tool dispatcher around the prepared state.

``EmbodiedAgentHook`` subclasses :class:`RuntimeHookBase`, so it satisfies
the ``RuntimeHook`` interface (inheriting safe no-op lifecycle methods) while
still holding a back-reference to the ``EmbodiedAgent`` instance for its
``prepare_turn`` / ``commit_after_end_turn`` flow.  The substrate now honours
``mid_turn_inject`` / ``RetryDecision`` / ``InterruptSource`` (wired in
``ReActLoop``); routing ``EmbodiedAgent.run`` through ``AgentRuntime.run_turn``
end-to-end remains a later migration.
"""

from __future__ import annotations

import asyncio
import logging
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
from familiar_neighbor.mind.desires import DesireSystem
from familiar_neighbor.mind.mental_state import MentalStateBus, MentalStateSnapshot
from familiar_neighbor.mind.social_policy import SocialPolicyDecision, SocialPolicyEngine
from familiar_runtime.runtime import RuntimeHookBase

if TYPE_CHECKING:
    from familiar_agent.agent import EmbodiedAgent


logger = logging.getLogger(__name__)


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

    Subclassing :class:`RuntimeHookBase` makes it a structural ``RuntimeHook``
    (inheriting no-op ``before_turn`` / ``build_context`` / ``mid_turn_inject`` /
    ``after_model_result`` / ``after_tool_result`` / ``after_turn`` defaults);
    the embodied flow currently drives the loop via ``prepare_turn`` /
    ``commit_after_end_turn`` rather than those lifecycle hooks.
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

        # ── Background tasks (MCP connections, memory worker) ──
        if agent._mcp and not agent._mcp.is_started:
            agent._mcp_start_task = asyncio.ensure_future(agent._mcp.start())
        if memory_worker and not memory_worker.is_running:
            await memory_worker.start()

        is_desire_turn = bool(inner_voice and not user_input)
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

        # ── Context compaction ──
        if agent._should_compact():
            await agent._compact_messages()

        # ── Memory recall + emotional context ──
        recall_n = 5 if agent._post_compact else 3
        agent._post_compact = False
        interoception_signal, interoception_pressure = agent._collect_interoception()
        prediction_signal = agent._prediction.last_signal()
        unfinished_business: list[dict] = []
        if not candidate_brief_turn:
            list_unfinished_business = getattr(
                agent._memory, "list_unfinished_business_async", None
            )
            unfinished_business = await _call_optional_async(
                list_unfinished_business,
                limit=3,
                fallback=[],
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
            )
        )

        # ── Social policy + provisional relationship update ──
        previous_response_hurt = any(
            token in user_input.lower() for token in ("hurt", "傷つ", "前の返事", "嫌だった")
        )
        social_policy = agent._social_policy.decide(
            user_text=user_input,
            affect=affect,
            trust=agent._relationship.trust,
            intimacy=agent._relationship.intimacy,
            interoception=interoception_pressure,
            previous_response_hurt=previous_response_hurt,
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
            heartbeat_ctx = agent._heartbeat.continuity_context_for_prompt()
            if heartbeat_ctx:
                continuity_ctx = (
                    continuity_ctx
                    + ("\n\n" if continuity_ctx else "")
                    + "[Continuation]\n"
                    + heartbeat_ctx
                )
            if unfinished_business:
                continuity_ctx = (
                    continuity_ctx
                    + ("\n\n" if continuity_ctx else "")
                    + "[Open unfinished business]\n"
                    + "\n".join(f"- {item['summary'][:160]}" for item in unfinished_business[:3])
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
