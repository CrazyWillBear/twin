# Twin

A general-purpose autonomous AI agent built with [LangGraph](https://github.com/langchain-ai/langgraph) and LangChain, backed by Groq-hosted models.

## AI Use Notice

This project was developed with the assistance of AI coding tools (Claude Code). While the design, architecture, and review of all code is done by me, portions of the implementation were written or accelerated using AI assistance. [CLAUDE.md](CLAUDE.md) is included so others can use similar tools under consistent guidelines.

## Features

- **LangGraph orchestration** — stateful, cyclical graph with tool-call loops and automatic routing
- **Long-term memory** — agent access to ChromaDB-backed semantic memory store
- **Short-term memory** — an in-context notepad the agent can freely read and write onto
- **File workspace** — read/write/delete tools scoped to `~/.twin` (or configured agent root) with custom agent-managed context management for open files
- **Shell access** — single commands and multi-line scripts, with user approval before execution
- **Soul/personality system** — a `soul.md` personality file loaded at the start of every turn, inspired by [OpenClaw](https://github.com/Clad3815/open-claw)
- **Context compression** — automatic summarization when the message history exceeds ~80k tokens
- **Web search** — DuckDuckGo search tool included by default

## Graph Architecture


| Node | Role |
|---|---|
| `init` | Loads `soul.md` into state |
| `act` | Builds the system prompt and calls the main model |
| `tool_node` | Executes any tool calls emitted by the model |
| `summarize_memory` | Compresses history if token count exceeds threshold |

## Requirements

- Python 3.14
- A [Groq](https://console.groq.com/) API key
- (optional) An [OpenAI](https://platform.openai.com/) API key if you want to use their models, which can be configured in [`agent/models/config.py`](agent/models/config.py)

## Setup

```bash
git clone https://github.com/CrazyWillBear/twin
cd twin
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Set your API key:

```bash
export GROQ_API_KEY=your_key_here
# or add it to a .env file
```

Optionally, create a soul file to give the agent a personality (there is a default if you don't):

```bash
mkdir -p ~/.twin2
echo "You are Twin, a helpful and curious assistant..." > ~/.twin/soul.md
```

## Running

```bash
source .venv/bin/activate
python main.py
```

Type `exit` or `quit` to end the session.

## Configuration

| Path | Purpose |
|---|---|
| `~/.twin/soul.md` | Agent personality/identity (loaded each turn) |
| `~/.twin/workspace/` | Agent's file workspace |
| `~/.twin/memory/` | ChromaDB long-term memory store |
| `FS_CONFIG.py` | Root path configuration |
| `agent/models/config.py` | Model role assignments |

## License

This project is licensed under the [Mozilla Public License 2.0](LICENSE).

> This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
> If a copy of the MPL was not distributed with this file, you can obtain one at https://mozilla.org/MPL/2.0/.
