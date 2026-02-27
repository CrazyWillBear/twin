"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Copyright (c) 2026 William Chastain. All rights reserved.
"""

from pathlib import Path

from FS_CONFIG import AGENT_ROOT


def read_soul_md(path: Path | str = AGENT_ROOT / "soul.md") -> str:
    """Reads the soul.md file and returns its content as a string."""

    with open(path) as f:
        return f.read()
