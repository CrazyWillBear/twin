"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Copyright (c) 2026 William Chastain. All rights reserved.
"""

from typing import Annotated

from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState
from langgraph.types import Command


@tool
def replace_string_in_notepad(str_to_replace: str, replacement: str, state: Annotated[dict, InjectedState]) -> Command:
    """Replaces `str_to_replace` in the notepad with `replacement`."""

    notepad: str = state["notepad"]
    if notepad.strip() == "":
        return Command(update={"notepad": replacement})
    notepad.replace(str_to_replace, replacement)
    return Command(update={"notepad": notepad})

@tool
def add_to_notepad(str_to_add: str, state: Annotated[dict, InjectedState]) -> Command:
    """Appends `str_to_add` to the end of the current notepad. Does NOT inject a newline before content."""

    notepad: str = state["notepad"]
    notepad += str_to_add
    return Command(update={"notepad": notepad})

@tool
def set_notepad(notepad_content: str) -> Command:
    """Replaces entirety of notepad with the passed string."""

    return Command(update={"notepad", notepad_content})