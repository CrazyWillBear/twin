# Twin: A general purpose autonomous AI agent

## EARLY STAGES OF DEVELOPMENT NOTICE

This project is in very early stages of development. The code is not stable and doesn't even work yet. Everything about
this project is a work-in-progress, including this README.

## Summary

Twin is a general purpose AI agent orchestrated with LangGraph. It's designed to use a designated directory as its
workspace with the ability to create, modify, and delete files in its workspace. Furthermore, it will feature a
multi-tier memory system that allows for short-term session based memory, long-term persistent memory, and a "soul",
which is inspired by OpenClaw and allows the agent to be assigned and form its own personality over time. Right now,
Twin is in the *very* early stages of development as noted above.

## Future Goals

I want Twin to have access to a multitude of tools, specifically provided by an MCP server. I've already created some
custom tools for Twin to write to its notepad (short term memory) and to read files (as file context is managed via a
context manager LLM). Other tools, like searching the internet, editing a Google Calendar, or things of that nature will
be done through said MCP server. I also want to implement the multi-tier memory system mentioned above, and the "soul"
concept. I'm also considering implementing A-MEM, which I recently read about in an arxiv paper, as a way to manage the
agent's long term memory.

## License

This project is licenced under the Mozilla Public License Version 2.0 (MPL-2.0). See [LICENSE](LICENSE) for more
details.