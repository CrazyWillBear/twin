"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Copyright (c) 2026 William Chastain. All rights reserved.
"""

import hashlib
from pathlib import Path
from typing import Annotated

from langchain_core.messages import ToolMessage
from langchain_core.tools import tool, InjectedToolCallId
from langgraph.prebuilt import InjectedState
from langgraph.types import Command

from FS_CONFIG import AGENT_ROOT
from agent.AgentState import AgentState
from agent.fs.File import File

@tool
def write_file(path: str, content: str, tool_call_id: Annotated[str, InjectedToolCallId], state: Annotated[AgentState, InjectedState]) -> Command:
    """Write content to a file in the workspace, creating parent directories as needed. Path should be relative to the workspace root."""

    resolved = (AGENT_ROOT / path).resolve()
    if not resolved.is_relative_to(AGENT_ROOT.resolve()):
        return Command(update={
            "message_history": [ToolMessage(content="Access denied: path outside workspace.", tool_call_id=tool_call_id)],
        })
    resolved.parent.mkdir(parents=True, exist_ok=True)
    resolved.write_text(content, encoding="utf-8")

    sha_256 = hashlib.sha256(content.encode("utf-8")).hexdigest()
    file: File = {
        "path": str(resolved),
        "last_modified": str(resolved.stat().st_mtime),
        "content": content,
        "sha_256": sha_256,
    }

    files_open = [f for f in state["files_open"] if f["path"] != str(resolved)] + [file]

    return Command(update={
        "files_total": [file],
        "files_open": files_open,
        "message_history": [ToolMessage(content=f"Wrote {resolved} ({len(content)} chars).", tool_call_id=tool_call_id)],
    })
