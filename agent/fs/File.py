"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Copyright (c) 2026 William Chastain. All rights reserved.
"""

from typing import TypedDict

class File(TypedDict):
    """A file is a record of a file that an agent has interacted with. It can be used to store information about the
    file, such as its name, last modified date, and content."""

    path: str
    last_modified: str
    content: str
    sha_256: str