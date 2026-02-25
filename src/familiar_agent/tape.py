"""TAPE-inspired planning for familiar-ai (arxiv:2602.19633).

Two mechanisms adapted for embodied real-world agents:

1. Plan Generation (Planning Graph, lightweight)
   Before the react loop, generate a short 2-4 step action plan using the backend.
   This anchors the agent's reasoning without the cost of full graph aggregation.

2. Adaptive Replanning
   After each tool call that has an upfront plan, ask the LLM whether the
   observation *blocks* the plan (e.g., cat not found, obstacle encountered).
   If blocked, ask for a revised next step and append it to the tool result so
   the agent can course-correct without resetting the conversation.

   Note: the trigger is an observation that contradicts the plan's assumptions,
   NOT a technical tool failure (schema errors / API errors are caught elsewhere).
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

# ── prompts ────────────────────────────────────────────────────────────────────

_PLAN_PROMPT = """\
You are helping an embodied AI agent plan its actions for ONE turn.
Given the request and available tools, write a numbered list of 2-4 concrete steps.
Each step must name which tool to call and why. One sentence per step.
Write in the same language as the request. No headers, no explanations — just the list.

Available tools: {tools}
Request: {request}

Action plan:"""

_PLAN_BLOCKED_PROMPT = """\
An embodied AI agent has an action plan and just executed one step.
Decide whether the observation BLOCKS further progress on the plan.

"Blocked" means: the observation contradicts a key assumption in the plan,
or makes the next planned step impossible/pointless.
"NOT blocked" means: the step succeeded or partially succeeded and the plan can continue.

Plan:
{plan}

Step executed: {tool}({args_summary})
Observation received: {result_summary}

Reply with exactly one word: "blocked" or "ok"."""

_REPLAN_PROMPT = """\
An embodied AI agent's plan was blocked by an unexpected observation.
Suggest a revised next step in ONE sentence.
Write in the same language as the goal. Be concrete (name the tool if relevant).

Original plan:
{plan}

Step that got blocked: {tool}({args_summary})
Observation: {result_summary}

Revised next step:"""


# ── TAPE mechanism 1: plan generation ─────────────────────────────────────────


async def generate_plan(backend, user_input: str, tool_names: list[str]) -> str:
    """Generate a short action plan before the react loop starts.

    Lightweight substitute for the planning graph aggregation in the paper:
    instead of generating N full candidate plans and solving a graph, we generate
    one concise plan to anchor the agent's step-by-step reasoning.

    Returns a numbered-list string, or "" on failure.
    """
    if not user_input.strip() or not tool_names:
        return ""
    tools_desc = ", ".join(tool_names)
    prompt = _PLAN_PROMPT.format(tools=tools_desc, request=user_input[:300])
    try:
        plan = await backend.complete(prompt, max_tokens=150)
        return plan.strip()
    except Exception as e:
        logger.debug("Plan generation failed (non-critical): %s", e)
        return ""


# ── TAPE mechanism 2: adaptive replanning ─────────────────────────────────────


async def check_plan_blocked(
    backend,
    plan: str,
    tool_name: str,
    tool_args: dict,
    result: str,
) -> bool:
    """Ask the LLM whether this observation blocks the current plan.

    This is the core of TAPE's adaptive replanning: the trigger is NOT a
    technical tool failure, but an observation that contradicts the plan's
    assumptions — e.g., looking for the cat and not finding it, or trying
    to move and finding an obstacle.

    Only called when a plan exists (plan != "").  Returns False on any error
    so that failures in the check never break the agent loop.
    """
    if not plan:
        return False
    args_summary = ", ".join(f"{k}={v}" for k, v in list(tool_args.items())[:3])
    result_summary = result[:300]
    prompt = _PLAN_BLOCKED_PROMPT.format(
        plan=plan[:400],
        tool=tool_name,
        args_summary=args_summary or "no args",
        result_summary=result_summary,
    )
    try:
        answer = (await backend.complete(prompt, max_tokens=5)).strip().lower()
        return answer == "blocked"
    except Exception as e:
        logger.debug("Plan-blocked check failed (non-critical): %s", e)
        return False


async def generate_replan(
    backend,
    plan: str,
    tool_name: str,
    tool_args: dict,
    result: str,
) -> str:
    """Suggest a revised next step when an observation blocks the current plan.

    Called only after check_plan_blocked() returns True.
    Returns a one-sentence suggestion, or "" on failure.
    """
    args_summary = ", ".join(f"{k}={v}" for k, v in list(tool_args.items())[:3])
    result_summary = result[:300]
    prompt = _REPLAN_PROMPT.format(
        plan=plan[:400],
        tool=tool_name,
        args_summary=args_summary or "no args",
        result_summary=result_summary,
    )
    try:
        suggestion = (await backend.complete(prompt, max_tokens=80)).strip()
        return suggestion if suggestion else ""
    except Exception as e:
        logger.debug("Replan generation failed (non-critical): %s", e)
        return ""
