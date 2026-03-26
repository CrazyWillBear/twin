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
NON_EXISTENT_FILE: File = {
    "path": "",
    "last_modified": "null",
    "content": "null",
    "sha_256": "null",
}

@tool
def read_file(path: str, tool_call_id: Annotated[str, InjectedToolCallId], state: Annotated[AgentState, InjectedState]) -> Command:
    """Tool that reads a file and appends it to the state's files_total variable. Path should be relative to the agent's
    workspace which is your root. Don't use `/<path>`, just `<path>/<more path if necessary>`."""

    resolved = (AGENT_ROOT / path).resolve()
    if not resolved.is_relative_to(AGENT_ROOT.resolve()):
        return Command(update={
            "message_history": [ToolMessage(content="Access denied: path outside workspace.", tool_call_id=tool_call_id)],
        })
    if resolved.exists():
        content = resolved.read_text(encoding="utf-8")
        sha_256 = hashlib.sha256(content.encode("utf-8")).hexdigest()
        file: File = {
            "path": str(resolved),
            "last_modified": str(resolved.stat().st_mtime),
            "content": content,
            "sha_256": sha_256,
        }
        files_open = [f for f in state["files_open"] if f["path"] != str(resolved)] + [file]
        msg = f"Read {resolved} ({len(content)} chars)."
        return Command(update={
            "files_total": [file],
            "files_open": files_open,
            "message_history": [ToolMessage(content=msg, tool_call_id=tool_call_id)],
        })
    else:
        file: File = NON_EXISTENT_FILE.copy()
        file["path"] = str(resolved)
        return Command(update={
            "files_total": [file],
            "message_history": [ToolMessage(content=f"File not found: {resolved}", tool_call_id=tool_call_id)],
        })
