"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Copyright (c) 2026 William Chastain. All rights reserved.
"""

from agent.fs.File import File


def merge_files_open(current: list[File], update: list[File]) -> list[File]:
    """Merge file updates into the current open-files list.

    Entries with only a "path" key are tombstones — they remove that path.
    All other entries are upserted (right wins per path).
    """
    by_path = {f["path"]: f for f in current}
    for f in update:
        if set(f.keys()) == {"path"}:
            by_path.pop(f["path"], None)
        else:
            by_path[f["path"]] = f
    return list(by_path.values())
