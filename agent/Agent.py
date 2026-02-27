"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Copyright (c) 2026 William Chastain. All rights reserved.
"""

from langchain_core.tools import BaseTool
from langgraph.constants import START
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode

from agent.AgentState import AgentState
from agent.nodes.context_manager import context_manager
from agent.nodes.llm import llm


class Agent:

    def __init__(self, name: str, tools: list[BaseTool]):
        self.name = name
        self.tools = tools

    def build_graph(self):
        graph = StateGraph(AgentState)

        tool_node = ToolNode(graph, tools=self.tools, messages_key="message_history")

        graph.add_node("llm", llm)
        graph.add_node("tool_node", tool_node)
        graph.add_node("context_manager", context_manager)

        graph.add_edge(START, "context_manager")  # to pull memories
        graph.add_edge("llm", "tool_node")
        graph.add_edge("tool_node", "context_manager")
        graph.add_edge("context_manager", "llm")

        # TODO add conditional edge for llm to end node if no tool calls are made
