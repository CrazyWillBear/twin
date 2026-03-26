"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Copyright (c) 2026 William Chastain. All rights reserved.
"""

from typing import Annotated

from langchain_core.messages import ToolMessage
from langchain_core.tools import tool, InjectedToolCallId
from langgraph.prebuilt import InjectedState
from langgraph.types import Command


@tool
def replace_string_in_notepad(
    str_to_replace: str,
    replacement: str,
    state: Annotated[dict, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """Replaces `str_to_replace` in the notepad with `replacement`."""

    notepad: str = state["notepad"]
    if notepad.strip() == "":
        new_notepad = replacement
    else:
        new_notepad = notepad.replace(str_to_replace, replacement)
    return Command(update={
        "notepad": new_notepad,
        "message_history": [ToolMessage(content="Notepad updated.", tool_call_id=tool_call_id)],
    })

@tool
def add_to_notepad(
    str_to_add: str,
    state: Annotated[dict, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """Appends `str_to_add` to the end of the current notepad. Does NOT inject a newline before content."""

    notepad: str = state["notepad"]
    return Command(update={
        "notepad": notepad + str_to_add,
        "message_history": [ToolMessage(content="Notepad updated.", tool_call_id=tool_call_id)],
    })

@tool
def set_notepad(
    notepad_content: str,
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """Replaces entirety of notepad with the passed string."""

    return Command(update={
        "notepad": notepad_content,
        "message_history": [ToolMessage(content="Notepad set.", tool_call_id=tool_call_id)],
    })