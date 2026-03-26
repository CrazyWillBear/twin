# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Twin is a general-purpose autonomous AI agent built with LangGraph (v1.0.9) and LangChain. It uses a designated directory (`~/.twin2/` by default, configured in `FS_CONFIG.py`) as its workspace. All three subdirectories (`AGENT_ROOT`, `MEMORY_ROOT`, `WORKSPACE_ROOT`) are created at import time.

LLM backends are via Groq (`langchain-groq`). `GROQ_API_KEY` must be in the environment. The main agent model is `openai/gpt-oss-120b`; lighter tasks (memory management, remember) use `qwen/qwen3-32b`.

## Running

```bash
source .venv/bin/activate
python main.py
```

The venv uses Python 3.14. There are no test files yet.

## Architecture

The agent is a **LangGraph `StateGraph`**. The graph runs one full turn per `agent.invoke()` call:

```
START → init → memory_manager → llm ──► tool_node → memory_manager → llm → ...
                                    │
                                    └──► remember → summarize_memory → END
```

`llm` routes to `tool_node` if the model emitted tool calls, otherwise to `remember`. After `tool_node` the loop returns to `memory_manager`.

- **`agent/AgentState.py`** — The shared state `TypedDict` passed between all nodes. Key fields:
  - `name`: agent's name string
  - `soul_md`: personality/identity markdown loaded from `~/.twin2/soul.md`
  - `long_term_memories`: list of `Memory` dicts currently in context (dynamically managed by `memory_manager`)
  - `notepad`: short-term scratchpad string the agent can freely read/write
  - `files_open`: files currently in context (agent-managed; never auto-evicted)
  - `files_total`: all files ever read (append-only via `operator.add`)
  - `tools`: list of `BaseTool` instances injected at graph construction time
  - `message_history`: the LangChain message list (append-only via `operator.add`)
  - `compressed_history`: summary `SystemMessage` + tail messages from the last compression
  - `compressed_at`: `len(message_history)` at the time of last compression (0 if never)

- **`agent/nodes/init.py`** — Loads `soul.md` into state at the start of every turn. Silently sets `soul_md=""` if the file is missing.

- **`agent/nodes/memory_manager.py`** — Runs before every `llm` call. Makes two LLM sub-calls (using `MODEL_CONFIG["memory_manager"]`): first generates semantic search queries from recent context, then fetches new memories from ChromaDB and prunes stale ones from `long_term_memories`.

- **`agent/nodes/llm.py`** — Builds the system prompt from state (soul, memories, notepad, open files, tools), calls `MODEL_CONFIG["review"]`, and appends the resulting `AIMessage` to `message_history`.

- **`agent/nodes/remember.py`** — After a turn ends (no tool calls), uses `MODEL_CONFIG["remember"]` with structured output to extract durable facts from the conversation turn and persist them to ChromaDB via `memory_client`.

- **`agent/nodes/summarize_memory.py`** — After `remember`, checks token count via `effective_history()`. If over `TOKEN_THRESHOLD` (80k tokens estimated), compresses everything except the last `TAIL_KEEP` (10) messages into a structured `SystemMessage` using `MODEL_CONFIG["summarize"]`. `effective_history()` is also used by `llm.py` and `memory_manager.py` to get the correct logical history.

- **`agent/tools/`** — LangGraph `@tool`-decorated functions. All tools use `InjectedState` and return `Command(update={...})` to mutate state directly:
  - `agent_notepad.py`: `add_to_notepad`, `replace_string_in_notepad`, `set_notepad`
  - `read_file.py`: reads a file from the workspace and adds it to `files_open` / `files_total`
  - `write_file.py`: writes a file to the workspace, updating `files_open` / `files_total`
  - `delete_file_from_context.py`: removes files from `files_open` by relative path
  - `memory.py`: `store_memory` (persist a memory), `query_memories` (semantic search into context)
  - `shell.py`: `run_command` (single shell command), `run_shell_script` (multi-line script via interpreter) — both prompt the user for approval before executing, run with `cwd=WORKSPACE_ROOT`

- **`agent/models/config.py`** — Maps model role names to model instances. Current keys: `"review"`, `"memory_manager"`, `"remember"`, `"summarize"`.

- **`agent/fs/File.py`** — `TypedDict` for file records (path, content, sha_256, last_modified).

- **`agent/memory/Memory.py`** — `TypedDict` for memory records (id, timestamp, content, tags).

- **`agent/memory/Soul.py`** — Reads `soul.md` from `AGENT_ROOT`.

- **`memory_server/`** — ChromaDB-backed long-term memory store. `memory_server/client.py` exposes a module-level singleton `memory_client = MemoryServer()` — import this instead of instantiating `MemoryServer()` directly. All file/path inputs to read/write tools are validated to be within `WORKSPACE_ROOT` before any disk operation.

## Conventions

- Tool docstrings should be a single line — no `Args:` sections, no multi-line/paragraph descriptions.
- Always leave a blank line between a docstring and the first line of code in a function.
- Write simple, modular, and minimal code.
- Write comments for every non-trivial or more complex sections of code.

## Key Design Patterns

- All tools return `Command(update={...})` rather than plain values, enabling direct state mutation from tool calls.
- `files_total` and `message_history` use `Annotated[List[X], operator.add]` so they accumulate across graph steps.
- The `Agent` class always injects `REQUIRED_TOOLS` (notepad, file tools, shell, memory) regardless of what additional tools are passed in.
- Model configuration is centralized in `agent/models/config.py` — add new role/model mappings there.
- Long-term memory is managed automatically each turn by `memory_manager` (fetch + prune) and `remember` (extract + persist). The agent also has `store_memory` and `query_memories` tools for explicit memory control.
- Use `effective_history(state)` (from `summarize_memory.py`) everywhere you need the logical message history — it transparently returns compressed + tail or raw history as appropriate.
