"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Copyright (c) 2026 William Chastain. All rights reserved.
"""

from typing import TypedDict


class Memory(TypedDict):
    """A memory is a record of an event or experience that an agent has had. It can be used to store information about
    the agent's experiences, which can be used to inform future decisions and actions."""

    timestamp: str
    content: str
    tags: list[str]
