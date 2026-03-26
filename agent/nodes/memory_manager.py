"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Copyright (c) 2026 William Chastain. All rights reserved.
"""

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from pydantic import BaseModel

from agent.AgentState import AgentState
from agent.memory.Memory import Memory
from agent.models.config import MODEL_CONFIG
from agent.nodes.summarize_memory import effective_history
from memory_server import MemoryServer

# Number of recent messages passed to the memory-manager LLM calls.
RECENT_MESSAGES_LIMIT = 10


# ── Structured-output schemas ──────────────────────────────────────────────────

class _QueriesOutput(BaseModel):
    queries: list[str] = []


class _PruneOutput(BaseModel):
    ids_to_remove: list[str] = []


# ── Helpers ────────────────────────────────────────────────────────────────────

def _history_message(messages: list) -> SystemMessage:
    """Serialize recent conversation history into a SystemMessage.

    Raw HumanMessage/AIMessage objects are converted to labeled text so the
    memory-manager LLM sees the history as data to reason about rather than
    as turns it participated in.
    """
    if not messages:
        return SystemMessage(content="Conversation history:\n(none)")

    lines = []
    for msg in messages:
        if isinstance(msg, HumanMessage):
            lines.append(f"**Human:** {msg.content}")
        elif isinstance(msg, AIMessage):
            lines.append(f"**Agent:** {msg.content}")

    return SystemMessage(content="# Conversation history:\n\n" + "\n\n".join(lines))


# ── Memory helpers ─────────────────────────────────────────────────────────────

def _prune_and_fetch_long_term(state: AgentState) -> list[Memory]:
    """Fetch newly relevant memories from the vector store and evict stale ones.

    Two LLM sub-calls are made:
      1. Generate up to 3 semantic search queries from recent context.
      2. Review the combined memory list and return IDs to evict.
    """
    model = MODEL_CONFIG["memory_manager"]
    recent_messages = effective_history(state)[-RECENT_MESSAGES_LIMIT:]
    notepad = state["notepad"] or "(empty)"
    existing: list[Memory] = state["long_term_memories"]

    # ── 1. Generate query strings ──────────────────────────────────────────────

    existing_summary = (
        "\n".join(f"- [{m['id']}] {m['content']}" for m in existing)
        if existing else "(none)"
    )

    query_instruction = SystemMessage(content=(
        "You are managing the long-term memory context for an AI agent.\n"
        "Based on the conversation history and the agent's scratchpad, "
        "generate up to 3 short search queries that would surface long-term memories "
        "useful for the current task. If it's the beginning of the conversation, query "
        "for who the user is and what their preferences are.\n\n"
        "Focus on topics, facts, preferences, and prior work directly relevant to "
        "what the agent is doing right now.\n"
        "Return an empty list if no additional memories seem needed.\n\n"
        f"Agent scratchpad:\n{notepad}\n\n"
        f"Memories already in context (do not generate queries for these):\n{existing_summary}\n\n"
        "## Output format\n"
        "Do not make any tool calls. Output only the JSON object described below.\n"
        "Respond with a JSON object matching this schema:\n"
        '  { "queries": [<string>, ...] }\n\n'
        "Example:\n"
        '  { "queries": ["user\'s preferred coding language", "recent project deadlines"] }'
    ))

    queries: list[str] = (
        model
        .with_structured_output(_QueriesOutput, method="json_mode")
        .invoke([_history_message(recent_messages), query_instruction])
        .queries[:3]
    )

    if not queries:
        return existing

    # ── 2. Fetch and deduplicate results ───────────────────────────────────────

    server = MemoryServer()
    seen_ids: set[str] = {m["id"] for m in existing}
    combined: list[Memory] = list(existing)

    for query in queries:
        for mem, _ in server.query_memories(query, n_results=5):
            if mem["id"] not in seen_ids:
                combined.append(mem)
                seen_ids.add(mem["id"])

    if len(combined) == len(existing):
        # Nothing new retrieved — skip prune call.
        return existing

    # ── 3. Prune irrelevant memories ───────────────────────────────────────────

    memory_lines = "\n".join(
        f"- id={m['id']} | {m['timestamp']} | tags={m['tags']} | {m['content']}"
        for m in combined
    )

    prune_instruction = SystemMessage(content=(
        "You are managing the long-term memory context for an AI agent.\n"
        "Review the memories currently loaded into the agent's context and identify "
        "any that are clearly irrelevant to the ongoing conversation.\n"
        "Be conservative — only evict memories that are definitely not needed right now.\n"
        "Return an empty list if all memories are still relevant.\n\n"
        f"Agent scratchpad:\n{notepad}\n\n"
        f"Loaded memories:\n{memory_lines}\n\n"
        "## Output format\n"
        "Do not make any tool calls. Output only the JSON object described below.\n"
        "Respond with a JSON object matching this schema:\n"
        '  { "ids_to_remove": [<memory_id_string>, ...] }\n\n'
        "Example:\n"
        '  { "ids_to_remove": ["3f2a1b4c-0000-0000-0000-000000000000", "9e8d7f6a-0000-0000-0000-000000000000"] }\n\n'
        "Use the exact id values shown in the loaded memories list above. "
        "Return an empty list if nothing should be evicted."
    ))

    ids_to_remove: set[str] = set(
        model
        .with_structured_output(_PruneOutput, method="json_mode")
        .invoke([_history_message(recent_messages), prune_instruction])
        .ids_to_remove
    )

    if not ids_to_remove:
        return combined

    return [m for m in combined if m["id"] not in ids_to_remove]


# ── Graph node ─────────────────────────────────────────────────────────────────

def memory_manager(state: AgentState) -> dict:
    """Fetches and prunes long-term memories relevant to the current context."""

    return {
        "long_term_memories": _prune_and_fetch_long_term(state),
    }
