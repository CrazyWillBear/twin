"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Copyright (c) 2026 William Chastain. All rights reserved.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from FS_CONFIG import MEMORY_ROOT
from memory_server import MemoryServer
from memory_server.config import DEFAULT_COLLECTION_NAME

server = MemoryServer()
server._client.delete_collection(DEFAULT_COLLECTION_NAME)
server._client.create_collection(DEFAULT_COLLECTION_NAME)
print(f"Cleared memory collection '{DEFAULT_COLLECTION_NAME}' at {MEMORY_ROOT}")
