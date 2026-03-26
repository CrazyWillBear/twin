"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Copyright (c) 2026 William Chastain. All rights reserved.
"""

import tempfile
import unittest
from unittest.mock import MagicMock, patch

from agent.memory.Memory import Memory
from agent.tools.memory import query_memories, remove_memory_from_context, store_memory
from memory_server.MemoryServer import MemoryServer


def _mem(content: str, tags: list[str] | None = None, id: str = "") -> Memory:
    return Memory(id=id, timestamp="2026-01-01T00:00:00+00:00", content=content, tags=tags or [])


# ── MemoryServer ───────────────────────────────────────────────────────────────

class TestMemoryServerAddMemory(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.server = MemoryServer(persist_dir=self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_assigns_id_when_empty(self):
        result = self.server.add_memory(_mem("hello"))
        self.assertNotEqual(result["id"], "")

    def test_preserves_explicit_id(self):
        result = self.server.add_memory(_mem("hello", id="my-id"))
        self.assertEqual(result["id"], "my-id")

    def test_content_and_tags_round_trip(self):
        result = self.server.add_memory(_mem("Will is the user", tags=["user", "name"]))
        self.assertEqual(result["content"], "Will is the user")
        self.assertEqual(result["tags"], ["user", "name"])


class TestMemoryServerGetAll(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.server = MemoryServer(persist_dir=self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_empty_store(self):
        self.assertEqual(self.server.get_all(), [])

    def test_returns_all_added(self):
        self.server.add_memory(_mem("first"))
        self.server.add_memory(_mem("second"))
        self.assertEqual(len(self.server.get_all()), 2)


class TestMemoryServerDeleteMemory(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.server = MemoryServer(persist_dir=self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_delete_removes_entry(self):
        mem = self.server.add_memory(_mem("to delete"))
        self.server.delete_memory(mem["id"])
        self.assertEqual(self.server.get_all(), [])

    def test_delete_leaves_others(self):
        keep = self.server.add_memory(_mem("keep"))
        remove = self.server.add_memory(_mem("remove"))
        self.server.delete_memory(remove["id"])
        remaining = self.server.get_all()
        self.assertEqual(len(remaining), 1)
        self.assertEqual(remaining[0]["id"], keep["id"])


class TestMemoryServerQueryMemories(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.server = MemoryServer(persist_dir=self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_query_empty_store(self):
        self.assertEqual(self.server.query_memories("anything"), [])

    def test_query_returns_memory_and_distance(self):
        self.server.add_memory(_mem("The user's name is Will", tags=["user"]))
        results = self.server.query_memories("user name")
        self.assertEqual(len(results), 1)
        mem, dist = results[0]
        self.assertIn("Will", mem["content"])
        self.assertIsInstance(dist, float)

    def test_query_respects_n_results(self):
        for i in range(5):
            self.server.add_memory(_mem(f"memory number {i}"))
        results = self.server.query_memories("memory", n_results=2)
        self.assertLessEqual(len(results), 2)

    def test_query_returns_most_similar_first(self):
        self.server.add_memory(_mem("The user loves Python programming"))
        self.server.add_memory(_mem("The weather is sunny today"))
        results = self.server.query_memories("Python programming language")
        self.assertIn("Python", results[0][0]["content"])


# ── store_memory tool ──────────────────────────────────────────────────────────

class TestStoreMemoryTool(unittest.TestCase):

    def _fake_memory(self, content: str) -> Memory:
        return Memory(id="abc123", timestamp="2026-01-01T00:00:00+00:00", content=content, tags=["t"])

    def test_calls_client_add_memory(self):
        mock_client = MagicMock()
        mock_client.add_memory.return_value = self._fake_memory("test")

        with patch("agent.tools.memory.memory_client", mock_client):
            store_memory.func(
                content="test", tags=["t"],
                state={"long_term_memories": []},
                tool_call_id="tid",
            )

        mock_client.add_memory.assert_called_once()

    def test_appends_to_existing_memories(self):
        existing = _mem("old memory", id="old-id")
        new_mem = self._fake_memory("new memory")
        mock_client = MagicMock()
        mock_client.add_memory.return_value = new_mem

        with patch("agent.tools.memory.memory_client", mock_client):
            result = store_memory.func(
                content="new memory", tags=[],
                state={"long_term_memories": [existing]},
                tool_call_id="tid",
            )

        ids = [m["id"] for m in result.update["long_term_memories"]]
        self.assertIn("old-id", ids)
        self.assertIn("abc123", ids)

    def test_returns_tool_message(self):
        mock_client = MagicMock()
        mock_client.add_memory.return_value = self._fake_memory("x")

        with patch("agent.tools.memory.memory_client", mock_client):
            result = store_memory.func(
                content="x", tags=[],
                state={"long_term_memories": []},
                tool_call_id="my-tool-call-id",
            )

        messages = result.update["message_history"]
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].tool_call_id, "my-tool-call-id")


# ── query_memories tool ────────────────────────────────────────────────────────

class TestQueryMemoriesTool(unittest.TestCase):

    def test_merges_new_memories_into_state(self):
        existing = _mem("old", id="existing-id")
        new_mem = _mem("new content", id="new-id")
        mock_client = MagicMock()
        mock_client.query_memories.return_value = [(new_mem, 0.1), (existing, 0.2)]

        with patch("agent.tools.memory.memory_client", mock_client):
            result = query_memories.func(
                query="test",
                state={"long_term_memories": [existing]},
                tool_call_id="tid",
                n_results=5,
            )

        ids = [m["id"] for m in result.update["long_term_memories"]]
        self.assertIn("new-id", ids)
        self.assertEqual(ids.count("existing-id"), 1)  # not duplicated

    def test_no_duplicates_when_all_already_in_context(self):
        mem = _mem("already here", id="dup-id")
        mock_client = MagicMock()
        mock_client.query_memories.return_value = [(mem, 0.0)]

        with patch("agent.tools.memory.memory_client", mock_client):
            result = query_memories.func(
                query="test",
                state={"long_term_memories": [mem]},
                tool_call_id="tid",
            )

        self.assertEqual(len(result.update["long_term_memories"]), 1)

    def test_tool_message_reports_count(self):
        new_mem = _mem("something new", id="n1")
        mock_client = MagicMock()
        mock_client.query_memories.return_value = [(new_mem, 0.1)]

        with patch("agent.tools.memory.memory_client", mock_client):
            result = query_memories.func(
                query="test",
                state={"long_term_memories": []},
                tool_call_id="tid",
            )

        self.assertIn("1", result.update["message_history"][0].content)


# ── remove_memory_from_context tool ───────────────────────────────────────────

class TestRemoveMemoryFromContextTool(unittest.TestCase):

    def test_removes_specified_id(self):
        mem1 = _mem("keep", id="id1")
        mem2 = _mem("remove", id="id2")

        result = remove_memory_from_context.func(
            memory_ids=["id2"],
            state={"long_term_memories": [mem1, mem2]},
            tool_call_id="tid",
        )

        remaining = result.update["long_term_memories"]
        self.assertEqual(len(remaining), 1)
        self.assertEqual(remaining[0]["id"], "id1")

    def test_empty_ids_removes_nothing(self):
        mem = _mem("stay", id="id1")

        result = remove_memory_from_context.func(
            memory_ids=[],
            state={"long_term_memories": [mem]},
            tool_call_id="tid",
        )

        self.assertEqual(len(result.update["long_term_memories"]), 1)

    def test_removes_multiple_ids(self):
        mems = [_mem(f"m{i}", id=f"id{i}") for i in range(4)]

        result = remove_memory_from_context.func(
            memory_ids=["id0", "id2"],
            state={"long_term_memories": mems},
            tool_call_id="tid",
        )

        ids = [m["id"] for m in result.update["long_term_memories"]]
        self.assertEqual(sorted(ids), ["id1", "id3"])

    def test_unknown_id_is_ignored(self):
        mem = _mem("stay", id="real-id")

        result = remove_memory_from_context.func(
            memory_ids=["nonexistent"],
            state={"long_term_memories": [mem]},
            tool_call_id="tid",
        )

        self.assertEqual(len(result.update["long_term_memories"]), 1)

    def test_tool_message_has_correct_call_id(self):
        result = remove_memory_from_context.func(
            memory_ids=[],
            state={"long_term_memories": []},
            tool_call_id="my-call-id",
        )

        self.assertEqual(result.update["message_history"][0].tool_call_id, "my-call-id")


if __name__ == "__main__":
    unittest.main()
