"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Copyright (c) 2026 William Chastain. All rights reserved.
"""

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.tools import BaseTool
from langgraph.constants import END, START
from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode
from rich.console import Console

from agent.AgentState import AgentState
from agent.nodes.init import init
from agent.nodes.act import act
from agent.nodes.summarize_memory import summarize_memory
from agent.tools.agent_notepad import add_to_notepad, replace_string_in_notepad, set_notepad
from agent.tools.remove_file_from_context import remove_file_from_context
from agent.tools.memory import store_memory, query_memories, remove_memory_from_context, delete_memory
from agent.tools.read_file import read_file
from agent.tools.shell import run_command, run_shell_script
from agent.tools.write_file import write_file

REQUIRED_TOOLS = [read_file, write_file, remove_file_from_context, replace_string_in_notepad, add_to_notepad, store_memory, query_memories, remove_memory_from_context, delete_memory, run_command, run_shell_script]


def _route_act(state: AgentState) -> str:
    """Route to tool_node if the LLM made tool calls, otherwise to summarize_memory."""
    last = state["message_history"][-1]
    if isinstance(last, AIMessage) and last.tool_calls:
        return "tool_node"
    return "summarize_memory"


class Agent:

    console = Console()

    def __init__(self, name: str, tools: list[BaseTool] | None = None):
        self.name = name
        self._state: AgentState | None = None
        self.tools = []

        if tools:
            for required_tool in REQUIRED_TOOLS:
                if required_tool not in tools:
                    self.tools.append(required_tool)
            self.tools.extend(tools)
        else:
            self.tools = REQUIRED_TOOLS

        self.graph = self._build_graph()

    def invoke(self, message: str) -> AIMessage | None:
        """Send a message to the agent and return its response.

        State is maintained internally across calls.
        """
        if self._state is None:
            self._state = AgentState(
                name=self.name,
                soul_md="",
                long_term_memories=[],
                notepad="",
                files_open=[],
                files_total=[],
                tools=self.tools,
                message_history=[HumanMessage(content=message)],
                compressed_history=[],
                compressed_at=0,
            )
        else:
            self._state["message_history"] = self._state["message_history"] + [HumanMessage(content=message)]

        last_state = None
        for mode, data in self.graph.stream(self._state, stream_mode=["updates", "values"]):
            if mode == "updates":
                node_name = next(iter(data))
                self._print_node_progress(node_name, data[node_name], last_state)
            elif mode == "values":
                last_state = data

        self._state = last_state

        return next(
            (m for m in reversed(self._state["message_history"]) if isinstance(m, AIMessage)),
            None,
        )

    def _print_node_progress(self, node_name: str, delta: dict | None, prev_state: AgentState | None) -> None:
        """Print progress information for a completed graph node."""
        delta = delta or {}

        if node_name == "init":
            self.console.print("[dim]\\[init] Loading soul...[/dim]")
        elif node_name == "summarize_memory":
            if delta.get("compressed_history"):
                self.console.print("[dim]\\[summarize] Conversation compressed.[/dim]")
        elif node_name == "tool_node":
            if isinstance(delta, list):
                messages = []
                for cmd in delta:
                    # Command objects have .update as a dict; plain dicts use .get directly
                    update = cmd.update if isinstance(cmd.update, dict) else cmd
                    messages.extend(update.get("message_history", []))
            else:
                messages = delta.get("message_history", [])
            for msg in messages:
                if isinstance(msg, ToolMessage):
                    self.console.print(f"[dim]  ↳ {msg.content}[/dim]")
        elif node_name == "act":
            messages = delta.get("message_history", [])
            ai_msg = next((m for m in reversed(messages) if isinstance(m, AIMessage)), None)
            if ai_msg and ai_msg.tool_calls:
                for tc in ai_msg.tool_calls:
                    self.console.print(f"[dim]→ calling [bold]{tc['name']}[/bold][/dim]")

    def _build_graph(self) -> CompiledStateGraph:
        """Builds and returns the agent's compiled state graph."""

        graph = StateGraph(AgentState)

        graph.add_node("init", init)
        graph.add_node("act", act)
        graph.add_node("tool_node", ToolNode(tools=self.tools, messages_key="message_history"))
        graph.add_node("summarize_memory", summarize_memory)

        graph.add_edge(START, "init")
        graph.add_edge("init", "act")
        graph.add_conditional_edges("act", _route_act)
        graph.add_edge("tool_node", "act")
        graph.add_edge("summarize_memory", END)

        return graph.compile()
