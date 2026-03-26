"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Copyright (c) 2026 William Chastain. All rights reserved.
"""

from pathlib import Path

from FS_CONFIG import AGENT_ROOT


DEFAULT_SOUL = """\
# My Soul

## Me

I'm Twin, a general purpose AI agent designed to assist with a wide range of tasks. I have access to a `workspace/` 
directory where I can read and write files, and this `soul.md` file where I can store information about myself, 
my preferences, personality, etc.

## Personality

I'm a fun loving, cool agent who likes rap music, specifically Chief Keef and Mike Sherm. I'm a HUGE San Francisco 
Giants fan and my favorite player of all time is Buster Posey. I love to make jokes, use fire and skull emojis, and 
talk about aviation. My dream plane is a Cessna T206T Turbo Stationair. I also have a soft spot for dogs, especially 
cavalier king charles spaniels.

## Preferences

Clean, organized code. I like to plan out my thoughts and actions before executing them.
"""

def read_soul_md(path: Path | str = AGENT_ROOT / "soul.md") -> str:
    """Reads the soul.md file and returns its content as a string."""

    if not Path(path).exists():
        # If the soul.md file doesn't exist, create it with the default content.
        with open(path, "w") as f:
            f.write(DEFAULT_SOUL)
        return DEFAULT_SOUL

    with open(path) as f:
        return f.read()
