"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Copyright (c) 2026 William Chastain. All rights reserved.
"""

from langchain_core.messages import SystemMessage, AIMessage

from agent.AgentState import AgentState
from agent.models.config import MODEL_CONFIG
from agent.util.stringify import stringify_tool_list, stringify_file_list


def _system_prompt(state: AgentState) -> SystemMessage:
    """The prompt for the review node. This prompt should be designed to elicit a response that will help the agent to
    review its current state and make decisions about what to do next."""

    return SystemMessage(content=(
        "# Your current state:\n"
        f"## Name: '{state['name']}'\n"
        f"## Your 'Soul' (as defined by you and the user):\n```\n{state['soul_md']}\n```\n"
        f"## Your currently-relevant long-term memories:\n{[f"- {m['content']}" for m in state['long_term_memories']]}\n"
        f"## Your scratchpad (jot down all relevant short term memories / context you'd like to remember for your "
        f"current task here):\n```\n{state['notepad']}\n```\n"
        f"## Relevant files you've opened:\n```\n{'\n'.join(stringify_file_list(state['files_open']))}\n```\n"
        f"## Relevant tools you have access to:\n```\n{stringify_tool_list(state['tools'])}\n```\n\n"
        
        "# Instructions:\n"
        "1. Review the above information about your current state within the context of the conversation.\n"
        "2. Based on this information, decide on the best course of action to take next in order to achieve your goals "
        "and complete the user's task.\n"
        "3. If a plan doesn't exist in your scratchpad, create one and jot it down there. If a plan already exists, "
        "review it and update it as necessary.\n\n"
        
        "# Output"
        "You will output tool calls and a message to the user. If the task is complete and/or you need to ask the user "
        "for input and/or there's some kind of critical failure, output your response with no tool calls. Whenever you "
        "don't include a tool call, the message will be sent to the user and they'll have an opportunity to send a new "
        "message to you.\n"
    ))

def llm(state: AgentState) -> dict:
    """The review node. This node should be designed to elicit a response that will help the agent to review its
    current state and make decisions about what to do next."""

    message_history = state.get("message_history", [])
    prompt = [*message_history, _system_prompt(state)]

    res: AIMessage = MODEL_CONFIG.get("review").invoke(prompt)

    return {"message_history": message_history + [res]}
