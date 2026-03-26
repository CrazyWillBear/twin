"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Copyright (c) 2026 William Chastain. All rights reserved.
"""

from pathlib import Path
from typing import Annotated

from langchain_core.messages import ToolMessage
from langchain_core.tools import tool, InjectedToolCallId
from langgraph.prebuilt import InjectedState
from langgraph.types import Command

from FS_CONFIG import AGENT_ROOT
from agent.AgentState import AgentState


@tool
def remove_file_from_context(paths: list[str], tool_call_id: Annotated[str, InjectedToolCallId], state: Annotated[AgentState, InjectedState]) -> Command:
    """Remove one or more files from the open file context by relative path."""

    resolved = [str(AGENT_ROOT / Path(p)) for p in paths]
    open_paths = {f["path"] for f in state["files_open"]}

    missing = [r for r in resolved if r not in open_paths]
    to_remove = set(resolved) - set(missing)

    # Tombstone entries (path-only dicts) signal the reducer to delete these paths.
    tombstones = [{"path": r} for r in to_remove]

    parts = []
    if to_remove:
        parts.append(f"Removed {len(to_remove)} file(s) from context.")
    if missing:
        parts.append(f"Not in open files: {', '.join(missing)}")

    return Command(update={
        "files_open": tombstones,
        "message_history": [ToolMessage(content=" ".join(parts), tool_call_id=tool_call_id)],
    })
