"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Copyright (c) 2026 William Chastain. All rights reserved.
"""
from langchain_core.messages import AIMessage
from langchain_core.tools import BaseTool
from langgraph.constants import START
from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode

from agent.AgentState import AgentState
from agent.nodes.context_manager import context_manager
from agent.nodes.llm import llm
from agent.tools.agent_notepad import add_to_notepad, replace_string_in_notepad, set_notepad
from agent.tools.read_file import read_file


REQUIRED_TOOLS = [read_file, replace_string_in_notepad, add_to_notepad, set_notepad]

class Agent:

    def __init__(self, name: str, tools: list[BaseTool] | None = None):
        self.name = name

        if tools:
            for tool in REQUIRED_TOOLS:
                if tool not in tools:
                    self.tools.append(tool)
            self.tools.extend(tools)
        else:
            self.tools = REQUIRED_TOOLS

        self.graph = self._build_graph()

    def invoke(self, initial_state: AgentState | None = None) -> AIMessage:
        if initial_state is None:
            initial_state = AgentState(
                name=self.name,
                soul_md="",
                long_term_memories=[],
                notepad="",
                files_open=[],
                files_total=[],
                tools=self.tools,
                message_history=[]
            )
        return self.graph.invoke(initial_state)

    def _build_graph(self) -> CompiledStateGraph:
        """Builds and returns the agent's compiled state graph."""

        graph = StateGraph(AgentState)

        graph.add_node("llm", llm)
        graph.add_node("tool_node", ToolNode(tools=self.tools, messages_key="message_history"))
        graph.add_node("context_manager", context_manager)

        graph.add_edge(START, "context_manager")  # to pull memories
        graph.add_edge("llm", "tool_node")
        graph.add_edge("tool_node", "context_manager")
        graph.add_edge("context_manager", "llm")

        return graph

        # TODO add conditional edge for llm to end node if no tool calls are made
