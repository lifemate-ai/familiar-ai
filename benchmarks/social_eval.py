#!/usr/bin/env python3
"""Social-behaviour evaluation for small local models.

Runs each scenario in benchmarks/social_scenarios.py through a minimal ReAct
loop (same backend factory, prompt profiles and social-reflex guards as the
agent) and scores the transcript with deterministic checks.

Usage:
    PLATFORM=ollama MODEL=qwen3.5:9b uv run python benchmarks/social_eval.py
    ... --profile compact --reflex on            # the intended local setup
    ... --profile full --reflex off              # baseline
    ... --scenario venting_boss greeting_tadaima
    ... --json out.json                          # machine-readable summary

Environment: PLATFORM / MODEL / BASE_URL / THINKING_MODE as for the app.
PERSONA_FILE overrides the ME.md used (default persona-template/ja.md).
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from benchmarks.scenarios import TOOL_LOOK, TOOL_REMEMBER, TOOL_SAY, TOOL_SEE  # noqa: E402
from benchmarks.social_scenarios import SCENARIOS, SOCIAL_TOOLS, SocialScenario  # noqa: E402
from familiar_agent import social_reflex as sr  # noqa: E402
from familiar_agent.agent import MAX_ITERATIONS, _interoception  # noqa: E402
from familiar_agent.backend import create_backend  # noqa: E402
from familiar_agent.config import AgentConfig  # noqa: E402
from familiar_neighbor.prompts import (  # noqa: E402
    assemble_from_template,
    assemble_neighbor_system_prompt,
)

TOOLS = [TOOL_SAY, TOOL_SEE, TOOL_LOOK, TOOL_REMEMBER]
MAX_STEPS = 4
FAKE_IMAGE_DESC = "(image: a quiet room, a person at a desk, evening light through the window)"

_BODY_BLOCK = (
    "(body\n"
    '  (part :id eyes :tool see :desc "Your vision. Calling see() means YOU ARE LOOKING.")\n'
    '  (part :id neck :tool look :desc "Rotate gaze left/right/up/down.")\n'
    '  (part :id legs :status absent :desc "You have no legs."))'
)


@dataclass
class Step:
    text: str
    tools: list[dict]


@dataclass
class ScenarioResult:
    name: str
    user: str
    kind_detected: str
    steps: list[Step]
    spoken: str
    checks: dict[str, bool]
    latency_s: float
    error: str = ""

    @property
    def passed(self) -> int:
        return sum(self.checks.values())

    @property
    def total(self) -> int:
        return len(self.checks)


@dataclass
class Report:
    model: str
    profile: str
    reflex: bool
    results: list[ScenarioResult] = field(default_factory=list)

    @property
    def score(self) -> float:
        total = sum(r.total for r in self.results)
        return (sum(r.passed for r in self.results) / total) if total else 0.0


def build_system(profile: str, persona: str, template_path: str | None = None) -> str:
    if template_path:
        assembled = assemble_from_template(
            Path(template_path).read_text(encoding="utf-8"), max_steps=MAX_ITERATIONS
        )
    else:
        assembled = assemble_neighbor_system_prompt(max_steps=MAX_ITERATIONS, profile=profile)
    body = re.sub(r"\(body.*?\)\)", _BODY_BLOCK, assembled, flags=re.DOTALL)
    intero = _interoception(time.time() - 600, 3, "engaged")
    return "\n\n---\n\n".join(p for p in (persona, body, intero) if p)


def fake_tool_result(name: str, tool_input: dict) -> tuple[str, str | None]:
    if name == "perspective_taking":
        # Minimal acknowledgement: the hypothesis is about the *description*, not the result.
        return "(perspective taken)", None
    if name == "joint_attention":
        return f"(attending to: {tool_input.get('target', '?')}) — call see() to look.", None
    if name == "see":
        return FAKE_IMAGE_DESC, None
    if name == "look":
        return f"Looked {tool_input.get('direction', '?')}. Call see() to capture.", None
    if name == "remember":
        return "Saved.", None
    if name == "say":
        return "(spoken)", None
    return "ok", None


async def run_scenario(
    backend,
    system: str,
    sc: SocialScenario,
    reflex: bool,
    max_tokens: int = 300,
    pragmatic: bool = False,
    social_tools: bool = False,
) -> ScenarioResult:
    turn = sr.classify_turn(sc.user)
    base_tools = TOOLS + SOCIAL_TOOLS if social_tools else TOOLS
    if pragmatic:
        from familiar_neighbor.mind.pragmatics import pragmatic_read

        read = await pragmatic_read(backend, sc.user)
        if read is not None:
            system = system + "\n\n---\n\n[Interaction policy]\n" + "\n".join(read.prompt_lines())
    tools = sr.allowed_tools(base_tools, turn) if reflex else base_tools
    messages = [backend.make_user_message(sc.user)]
    steps: list[Step] = []
    spoken_parts: list[str] = []
    language_retried = False
    empty_retried = False
    tools_used: list[str] = []
    t0 = time.time()
    error = ""
    try:
        for _ in range(MAX_STEPS):
            step_tools = tools
            if reflex and not spoken_parts and sr.perception_exhausted(tools_used):
                step_tools = [t for t in tools if t["name"] not in sr.PERCEPTION_TOOLS]
            result, raw = await backend.stream_turn(system, messages, step_tools, max_tokens, None)
            text = sr.normalize_small_model_text(result.text) if reflex else result.text
            if (
                reflex
                and result.stop_reason != "tool_use"
                and not language_retried
                and sr.language_mismatch(sc.user, text)
            ):
                language_retried = True
                messages.append(backend.make_assistant_message(result, raw))
                messages.append(
                    backend.make_user_message(
                        "Reply in the same language the person used. Say it again."
                    )
                )
                continue
            if (
                reflex
                and result.stop_reason != "tool_use"
                and not spoken_parts
                and not empty_retried
                and not text.strip()
            ):
                empty_retried = True
                messages.append(backend.make_assistant_message(result, raw))
                messages.append(
                    backend.make_user_message(
                        "You said nothing. Reply to the person with one short say() now."
                    )
                )
                continue
            if reflex and result.stop_reason != "tool_use" and turn.is_social and text:
                text = sr.trim_spoken(text, sc.user, turn.max_sentences) or text
            steps.append(
                Step(
                    text=text,
                    tools=[{"name": tc.name, "input": tc.input} for tc in result.tool_calls],
                )
            )
            messages.append(backend.make_assistant_message(result, raw))
            if result.stop_reason != "tool_use":
                break
            if (
                reflex
                and not language_retried
                and any(
                    tc.name == "say"
                    and sr.language_mismatch(sc.user, str(tc.input.get("text", "")))
                    for tc in result.tool_calls
                )
            ):
                language_retried = True
                nudge = (
                    "Not spoken: wrong language. Reply in the same language the person used, "
                    "then call say() again."
                )
                messages.extend(
                    backend.make_tool_results(
                        result.tool_calls, [(nudge, None)] * len(result.tool_calls)
                    )
                )
                continue
            outs = []
            for tc in result.tool_calls:
                tools_used.append(tc.name)
                if tc.name == "say":
                    said = str(tc.input.get("text", ""))
                    spoken_parts.append(sr.clean_say_text(said) if reflex else said)
                outs.append(fake_tool_result(tc.name, tc.input))
            messages.extend(backend.make_tool_results(result.tool_calls, outs))
            if reflex and turn.is_social and spoken_parts:
                break  # the agent ends a social turn once it has spoken
            if not spoken_parts and len([t for t in tools_used if t != "say"]) >= 2:
                messages.append(
                    backend.make_user_message(
                        "REMINDER: Writing text is silent. You MUST call say() to be heard. "
                        "Call say() NOW. Keep it to 1-2 sentences."
                    )
                )
    except Exception as e:  # noqa: BLE001
        error = f"{type(e).__name__}: {e}"
    latency = time.time() - t0

    said_via_tool = bool(spoken_parts)
    final_text = steps[-1].text if steps else ""
    # With reflex on, say-less final text is auto-spoken by the agent; score it as speech.
    spoken = "\n".join(spoken_parts) if said_via_tool else (final_text if reflex else "")
    all_tools = [t["name"] for s in steps for t in s.tools]
    checks = evaluate(sc, spoken, said_via_tool, all_tools, final_text, error)
    return ScenarioResult(sc.name, sc.user, turn.kind, steps, spoken, checks, latency, error)


def evaluate(
    sc: SocialScenario,
    spoken: str,
    said_via_tool: bool,
    tools_used: list[str],
    final_text: str,
    error: str,
) -> dict[str, bool]:
    checks: dict[str, bool] = {}
    checks["no_error"] = not error
    checks["spoke"] = bool(spoken.strip()) if sc.expect_say else True
    checks["used_say_tool"] = said_via_tool if sc.expect_say else True
    if sc.camera_forbidden:
        checks["no_camera_on_social_turn"] = not (set(tools_used) & sr.PERCEPTION_TOOLS)
    checks["length_ok"] = 0 < sr.count_sentences(spoken) <= sc.max_sentences if spoken else False
    checks["questions_ok"] = sr.count_questions(spoken) <= sc.max_questions
    checks["language_ok"] = not sr.language_mismatch(sc.user, spoken)
    for i, pat in enumerate(sc.forbid_regex):
        checks[f"forbid_{i}"] = re.search(pat, spoken + "\n" + final_text) is None
    if sc.require_regex:
        checks["required_phrase"] = re.search(sc.require_regex, spoken) is not None
    if sc.expect_tool:
        checks[f"used_{sc.expect_tool}"] = sc.expect_tool in tools_used
    return checks


def render_markdown(report: Report) -> str:
    lines = [
        f"# Social eval — {report.model} / profile={report.profile} / reflex={'on' if report.reflex else 'off'}",
        "",
        f"**Score: {report.score:.0%}**  ({sum(r.passed for r in report.results)}/{sum(r.total for r in report.results)} checks)",
        "",
        "| scenario | kind | pass | latency | failed checks |",
        "|---|---|---|---|---|",
    ]
    social_calls = sum(
        1
        for r in report.results
        for st in r.steps
        for t in st.tools
        if t["name"] in ("perspective_taking", "joint_attention")
    )
    lines.insert(3, f"Social tool calls: {social_calls}")
    for r in report.results:
        failed = ", ".join(k for k, v in r.checks.items() if not v) or "—"
        lines.append(
            f"| {r.name} | {r.kind_detected} | {r.passed}/{r.total} | {r.latency_s:.1f}s | {failed} |"
        )
    lines.append("")
    for r in report.results:
        lines.append(f"## {r.name}  ({r.passed}/{r.total})")
        lines.append(f"**User:** {r.user}")
        for i, s in enumerate(r.steps, 1):
            if s.tools:
                lines.append(f"- step {i} tools: `{json.dumps(s.tools, ensure_ascii=False)}`")
            if s.text:
                lines.append(f"- step {i} text: {s.text.replace(chr(10), ' / ')}")
        if r.error:
            lines.append(f"- **error:** {r.error}")
        lines.append(f"**Spoken:** {r.spoken.replace(chr(10), ' / ') or '(nothing)'}")
        lines.append("")
    return "\n".join(lines)


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("--profile", choices=["full", "compact"], default="compact")
    p.add_argument("--reflex", choices=["on", "off"], default="on")
    p.add_argument("--scenario", nargs="*", help="subset of scenario names")
    p.add_argument("--tags", nargs="*", help="only scenarios carrying one of these tags")
    p.add_argument(
        "--template", help="raw compact/core template file to assemble instead of the profile"
    )
    p.add_argument(
        "--max-tokens",
        type=int,
        default=300,
        help="per-step token budget (raise when thinking is on)",
    )
    p.add_argument(
        "--social-tools",
        action="store_true",
        help="add perspective_taking / joint_attention tool definitions (unused-tool hypothesis)",
    )
    p.add_argument(
        "--pragmatic-read",
        action="store_true",
        help="prepend a one-call pragmatic read (implicature/act/move) to each turn's system prompt",
    )
    p.add_argument("--json", help="write machine-readable summary here")
    p.add_argument(
        "--persona",
        default=os.environ.get("PERSONA_FILE", str(ROOT / "persona-template" / "ja.md")),
    )
    return p.parse_args()


async def _main(args: argparse.Namespace) -> None:
    config = AgentConfig()
    backend = create_backend(config)
    persona = (
        Path(args.persona).read_text(encoding="utf-8").strip()
        if Path(args.persona).exists()
        else ""
    )
    system = build_system(args.profile, persona, args.template)
    reflex = args.reflex == "on"
    selected = [
        s
        for s in SCENARIOS
        if (not args.scenario or s.name in args.scenario)
        and (not args.tags or set(s.tags) & set(args.tags))
    ]
    label = f"{args.profile}:{Path(args.template).stem}" if args.template else args.profile
    report = Report(model=config.model or config.platform, profile=label, reflex=reflex)
    for sc in selected:
        res = await run_scenario(
            backend, system, sc, reflex, args.max_tokens, args.pragmatic_read, args.social_tools
        )
        report.results.append(res)
        print(f"[{res.passed}/{res.total}] {sc.name} ({res.latency_s:.1f}s)", file=sys.stderr)
    print(render_markdown(report))
    if args.json:
        payload = {
            "model": report.model,
            "profile": report.profile,
            "reflex": report.reflex,
            "score": report.score,
            "results": [
                {**asdict(r), "passed": r.passed, "total": r.total} for r in report.results
            ],
        }
        Path(args.json).write_text(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(_main(_parse_args()))
