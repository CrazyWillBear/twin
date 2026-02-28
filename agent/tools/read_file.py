"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Copyright (c) 2026 William Chastain. All rights reserved.
"""

import hashlib
from pathlib import Path

from langchain_core.tools import tool
from langgraph.types import Command

from agent.fs.File import File

NON_EXISTENT_FILE: File = {
    "path": "",
    "last_modified": "null",
    "content": "null",
    "sha_256": "null"
}

@tool
def read_file(path: str) -> Command:
    """Tool that reads a file and appends it to the state's files_total variable."""

    path = Path(path)
    if path.exists():
        content = path.read_text(encoding="utf-8")
        sha_256_obj =  hashlib.sha256(content.encode("utf-8"))
        sha_256 = sha_256_obj.hexdigest()
        file: File = {
            "path": str(path),
            "last_modified": str(path.stat().st_mtime),
            "content": content,
            "sha_256": sha_256
        }
        return Command(update={"files_total": [file]})
    else:
        file: File = NON_EXISTENT_FILE.copy()
        file["path"] = str(path)
        return Command(update={"files_total": [file]})
