"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Copyright (c) 2026 William Chastain. All rights reserved.
"""

import json

from langchain_core.tools import BaseTool, Tool, StructuredTool

from agent.fs.File import File
from agent.memory.Memory import Memory


def stringify_tool_list(tools: list[BaseTool]) -> str:

    res = ""
    for tool in tools:
        if not isinstance(tool, BaseTool) and not isinstance(tool, Tool) and not isinstance(tool, StructuredTool):
            raise ValueError(f"Expected a list of StructuredTool/Tool/BaseTool instances, but got {type(tool)}")
        res += f"- `{tool.name}`\n\tArgs: {tool.args}\n\tDescription: {tool.description}\n\n"
    return res

def stringify_file_list(files: list[File]) -> str:

    res = ""
    for file in files:
        res += "```\n" + json.dumps(file, indent=2, ensure_ascii=True) + "```\n\n"
    return res

def stringify_memory_list(memories: list[Memory]) -> str:

    res = ""
    for memory in memories:
        res += "```\n" + json.dumps(memory, indent=2, ensure_ascii=True) + "```\n\n"
    return res