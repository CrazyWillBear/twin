"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Copyright (c) 2026 William Chastain. All rights reserved.
"""

from agent.memory.Memory import Memory


def memory_to_chroma(memory: Memory) -> tuple[str, dict]:
    """Serialize a Memory to a (document, metadata) pair for ChromaDB storage.

    Tags are stored as a comma-separated string because ChromaDB metadata
    values must be scalar.
    """
    document = memory["content"]
    metadata = {
        "timestamp": memory["timestamp"],
        "tags": ",".join(memory["tags"]),
    }
    return document, metadata


def chroma_to_memory(mem_id: str, document: str, metadata: dict) -> Memory:
    """Deserialize a ChromaDB result row back into a Memory."""
    return Memory(
        id=mem_id,
        timestamp=metadata["timestamp"],
        content=document,
        tags=[t for t in metadata["tags"].split(",") if t],
    )
