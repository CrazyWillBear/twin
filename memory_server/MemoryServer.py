"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Copyright (c) 2026 William Chastain. All rights reserved.
"""

import uuid
from pathlib import Path

import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

from FS_CONFIG import MEMORY_ROOT
from agent.memory.Memory import Memory
from memory_server.config import DEFAULT_COLLECTION_NAME
from memory_server.serialization import chroma_to_memory, memory_to_chroma


class MemoryServer:
    """Wrapper for a ChromaDB-backed persistent memory store.

    Memories are vectorized using the default ChromaDB embedding function
    (all-MiniLM-L6-v2) so that semantic search is available via query_memories.
    """

    def __init__(
        self,
        persist_dir: Path | str = MEMORY_ROOT,
        collection_name: str = DEFAULT_COLLECTION_NAME,
    ):
        self._client = chromadb.PersistentClient(path=str(persist_dir))
        self._collection = self._client.get_or_create_collection(
            name=collection_name,
            embedding_function=DefaultEmbeddingFunction(),
        )

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def add_memory(self, memory: Memory) -> Memory:
        """Persist a memory.  If memory['id'] is empty a UUID is assigned.

        Returns the Memory with its final id populated.
        """
        mem_id = memory.get("id") or str(uuid.uuid4())
        memory = Memory(id=mem_id, **{k: memory[k] for k in ("timestamp", "content", "tags")})
        document, metadata = memory_to_chroma(memory)
        self._collection.add(ids=[mem_id], documents=[document], metadatas=[metadata])
        return memory

    def delete_memory(self, memory_id: str) -> None:
        """Delete a memory by its id."""
        self._collection.delete(ids=[memory_id])

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def query_memories(self, query: str, n_results: int = 10) -> list[tuple[Memory, float]]:
        """Semantic search over stored memories.

        Returns (Memory, L2_distance) pairs ordered by ascending distance
        (most similar first).
        """
        count = self._collection.count()
        if count == 0:
            return []

        results = self._collection.query(
            query_texts=[query],
            n_results=min(n_results, count),
            include=["documents", "metadatas", "distances"],
        )

        return [
            (chroma_to_memory(mem_id, doc, meta), dist)
            for mem_id, doc, meta, dist in zip(
                results["ids"][0],
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0],
            )
        ]

    def get_all(self) -> list[Memory]:
        """Return every stored memory (no semantic ranking)."""
        if self._collection.count() == 0:
            return []

        results = self._collection.get(include=["documents", "metadatas"])
        return [
            chroma_to_memory(mem_id, doc, meta)
            for mem_id, doc, meta in zip(
                results["ids"],
                results["documents"],
                results["metadatas"],
            )
        ]
