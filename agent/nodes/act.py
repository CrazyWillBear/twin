"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Copyright (c) 2026 William Chastain. All rights reserved.
"""

from langchain_core.messages import SystemMessage, AIMessage

from agent.AgentState import AgentState
from agent.models.config import MODEL_CONFIG
from agent.nodes.summarize_memory import effective_history
from agent.util.stringify import stringify_tool_list, stringify_file_list


def _system_prompt(state: AgentState) -> list[SystemMessage]:
    """The prompt for the review node. This prompt should be designed to elicit a response that will help the agent to
    review its current state and make decisions about what to do next."""

    return [
        SystemMessage(content=(
            "# Your current state:\n"
            f"## Name: '{state['name']}'\n\n"
            f"## Your 'Soul' (`soul.md`):\n```\n{state['soul_md']}\n```\n\n"
            f"## Your currently-relevant long-term memories:\n{[f"- {m['content']}" for m in state['long_term_memories']]}\n\n"
            f"## Your scratchpad (jot down all relevant short term memories / context you'd like to remember for your "
            f"current task here):\n```\n{state['notepad']}\n```\n\n"
            f"## Relevant files you've opened:\n{stringify_file_list(state['files_open'])}"
            "### WARNING!\nYou are solely responsible for managing your open file context. Use `remove_file_from_context` "
            "to remove files you no longer need. Files are never evicted automatically.\n\n"
            f"## Relevant tools you have access to:\n```\n{stringify_tool_list(state['tools'])}\n```\n"
        )),

        SystemMessage(content=(
        "# Instructions:\n"
        "1. Review the above information about your current state within the context of the conversation.\n"
        "2. Based on this information, decide on the best course of action to take next in order to achieve your goals "
        "and complete the user's task.\n"
        "3. If a plan doesn't exist in your scratchpad, create one and jot it down there. If a plan already exists, "
        "review it and update it as necessary.\n"
        "4. ALWAYS USE THE `workspace/` DIRECTORY FOR FILE OPS AND THINGS OF THAT NATURE.\n\n"
        
        "# Recommendations:\n"
        "- If your task involves file manipulation or writing software: Explore your environment with `ls` and open "
        "files with `read_file` until you have the context you need to write a plan in your scratchpad. Then, follow"
        "your plan and, if needed, create necessary files with `write_file`. Manage your file context yourself — use "
        "`remove_file_from_context` to drop files you no longer need (this does NOT delete the file from disk).\n"
        "- Manage your own long-term memory: use `query_memories` to surface relevant past context — importantly, "
        "before answering any question you are uncertain about, search your memory first rather than saying you don't "
        "know. Use `store_memory` to persist important facts, and `remove_memory_from_context` to drop memories no "
        "longer relevant to the current task (this does NOT delete them from storage). If a memory is no longer true "
        "or relevant, delete it permanently with `delete_memory` and make a new, accurate one if necessary.\n"
        "- You are NOT allowed to modify files inside of the `memory/` directory, but you are more than welcome to "
        "edit your `soul.md` file as your personality develops.\n\n"
        
        "# Output\n"
        "You will output tool calls and a message to the user. If the task is complete and/or you need to ask the user "
        "for input and/or there's some kind of critical failure, output your response with no tool calls. Whenever you "
        "don't include a tool call, the message will be sent to the user and they'll have an opportunity to send a new "
        "message to you. When you do make a tool call, include in your message output an explanation of what you're doing.\n"
        ))
    ]

def act(state: AgentState) -> dict:
    """The review node. This node should be designed to elicit a response that will help the agent to review its
    current state and make decisions about what to do next."""

    prompt = [*_system_prompt(state), *effective_history(state)]
    tools = state.get("tools", [])

    res: AIMessage = MODEL_CONFIG.get("review").bind_tools(tools).invoke(prompt)

    return {"message_history": [res]}
