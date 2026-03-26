"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Copyright (c) 2026 William Chastain. All rights reserved.
"""

from datetime import datetime, timezone
from typing import Annotated

from langchain_core.messages import ToolMessage
from langchain_core.tools import tool, InjectedToolCallId
from langgraph.prebuilt import InjectedState
from langgraph.types import Command

from agent.memory.Memory import Memory
from memory_server import memory_client


@tool
def store_memory(
        content: str,
        tags: list[str],
        state: Annotated[dict, InjectedState],
        tool_call_id: Annotated[str, InjectedToolCallId]  # Add this line
) -> Command:

    """Store a memory in long-term memory, embedded and persisted for semantic retrieval in future queries."""

    memory = memory_client.add_memory(Memory(
        id="",
        timestamp=datetime.now(timezone.utc).isoformat(),
        content=content,
        tags=tags,
    ))

    existing: list[Memory] = state.get("long_term_memories", [])

    return Command(
        update={
            "long_term_memories": existing + [memory],
            "message_history": [
                ToolMessage(
                    content=f"Uploaded memory: {content}",
                    tool_call_id=tool_call_id
                )
            ]
        }
    )


@tool
def remove_memory_from_context(
    memory_ids: list[str],
    state: Annotated[dict, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:

    """Remove one or more memories from the active context by ID. Does not delete them from long-term storage."""

    existing: list[Memory] = state.get("long_term_memories", [])
    id_set = set(memory_ids)
    new_memories = [m for m in existing if m["id"] not in id_set]
    removed = len(existing) - len(new_memories)

    return Command(update={
        "long_term_memories": new_memories,
        "message_history": [ToolMessage(
            content=f"Removed {removed} memory/memories from context.",
            tool_call_id=tool_call_id,
        )],
    })


@tool
def delete_memory(
    memory_ids: list[str],
    state: Annotated[dict, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:

    """Permanently delete one or more memories from long-term storage and remove them from the active context."""

    for memory_id in memory_ids:
        memory_client.delete_memory(memory_id)

    id_set = set(memory_ids)
    existing: list[Memory] = state.get("long_term_memories", [])
    new_memories = [m for m in existing if m["id"] not in id_set]

    return Command(update={
        "long_term_memories": new_memories,
        "message_history": [ToolMessage(
            content=f"Permanently deleted {len(memory_ids)} memory/memories.",
            tool_call_id=tool_call_id,
        )],
    })


@tool
def query_memories(
    query: str,
    state: Annotated[dict, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
    n_results: int = 5,
) -> Command:

    """Search long-term memory database by semantic similarity."""

    results = memory_client.query_memories(query, n_results=n_results)

    existing: list[Memory] = state["long_term_memories"] if state else []
    existing_ids = {m["id"] for m in existing}
    new_memories = [mem for mem, _ in results if mem["id"] not in existing_ids]

    return Command(update={
        "long_term_memories": existing + new_memories,
        "message_history": [ToolMessage(
            content=f"Found {len(new_memories)} new memories.",
            tool_call_id=tool_call_id,
        )],
    })
