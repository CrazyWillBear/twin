"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Copyright (c) 2026 William Chastain. All rights reserved.
"""

from langchain_core.messages import AIMessage, AnyMessage, HumanMessage, SystemMessage

from agent.AgentState import AgentState
from agent.models.config import MODEL_CONFIG

TOKEN_THRESHOLD = 80_000
TAIL_KEEP = 10  # messages preserved verbatim after summarization

_SUMMARY_PROMPT = """\
You are compressing a long conversation between a human and an AI agent into a structured summary.
This summary will replace the full history in the agent's context window. Nothing important can be lost.
The agent must be able to continue the task seamlessly after reading only this summary.

Produce a summary using exactly these sections (omit any that have no content):

## Long Term Overall Task
The original goal the user gave — preserved as precisely as possible, verbatim if short.
This is the most important thing to carry forward. Do not paraphrase away intent or constraints.

## Current Sub-Goal
Any refinements, sub-tasks, or pivots made since the original task. What the agent was working on most recently.

## Completed Steps
What has been done so far. Be specific: exact filenames, function names, commands, and the rationale behind key decisions.

## Files In Play
Every file created, read, or modified. For each: full path, what it contains or does, and its current state (complete / partial / broken).

## Commands Run
Shell commands or scripts that were executed. Include outcomes: success, failure, key output, or side effects.

## Current State
Where things stand right now — what works, what is broken, what is in progress.

## Blockers & Open Questions
Unresolved errors (exact messages matter), pending decisions, anything the agent was stuck on.

## Constraints & Preferences
Anything the user stated about how they want things done: style, tools, libraries, structure, things to avoid.

Do not paraphrase away specifics. Exact paths, exact error text, and exact decisions are load-bearing.\
"""


def effective_history(state: AgentState) -> list[AnyMessage]:
    """Return the full logical history: compressed summary + messages since last compression, or raw history."""

    if state.get("compressed_history"):
        since = state["message_history"][state.get("compressed_at", 0):]
        return state["compressed_history"] + since
    return state["message_history"]


def _estimate_tokens(messages: list[AnyMessage]) -> int:

    return sum(len(str(m.content)) for m in messages) // 4


def _serialize_for_summary(messages: list[AnyMessage]) -> str:

    lines = []
    for msg in messages:
        if isinstance(msg, SystemMessage):
            lines.append(f"[Prior Summary]\n{msg.content}")
        elif isinstance(msg, HumanMessage):
            lines.append(f"Human: {msg.content}")
        elif isinstance(msg, AIMessage):
            lines.append(f"Agent: {msg.content if msg.content else '<said nothing>'}")
    return "\n\n".join(lines)


def summarize_memory(state: AgentState) -> dict:
    """Compresses message history into a structured summary when the token threshold is exceeded."""

    history = effective_history(state)

    if _estimate_tokens(history) < TOKEN_THRESHOLD:
        return {}

    to_summarize = history[:-TAIL_KEEP]
    tail = history[-TAIL_KEEP:]

    model = MODEL_CONFIG["summarize"]
    summary_text: str = model.invoke([
        SystemMessage(content=_SUMMARY_PROMPT),
        HumanMessage(content=_serialize_for_summary(to_summarize)),
    ]).content

    return {
        "compressed_history": [SystemMessage(content=summary_text), *tail],
        "compressed_at": len(state["message_history"]),
    }
