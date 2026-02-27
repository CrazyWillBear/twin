"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Copyright (c) 2026 William Chastain. All rights reserved.
"""

import operator
from typing import TypedDict, Annotated, List

from langchain_core.messages import AnyMessage
from langchain_core.tools import BaseTool

from agent.fs.File import File
from agent.memory.Memory import Memory


class AgentState(TypedDict):

    name: str
    soul_md: str
    long_term_memories: list[Memory]
    notepad: str
    files_open: list[File]
    files_total: Annotated[List[File], operator.add]
    tools: list[BaseTool]

    message_history: Annotated[List[AnyMessage], operator.add]
