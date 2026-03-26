"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Copyright (c) 2026 William Chastain. All rights reserved.
"""

from agent.AgentState import AgentState
from agent.memory.Soul import read_soul_md


def init(state: AgentState) -> dict:
    """Loads soul.md into state."""
    try:
        soul_md = read_soul_md()
    except FileNotFoundError:
        soul_md = ""

    return {"soul_md": soul_md}
