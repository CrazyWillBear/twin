"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Copyright (c) 2026 William Chastain. All rights reserved.
"""

from agent.AgentState import AgentState
from agent.fs.File import File


def _prune_and_fetch_long_term(state: AgentState):
    """Prunes irrelevant long term memories and adds new ones if relevant. Returns a list of memories that the agent
    should have in its context."""

    long_term_memories = state['long_term_memories']

    # TODO: implement LLM call to query memories for new ones which are added to the list. Then another to remove all
    # irrelevant memories from that list. This should be moderately strict, it should be careful though.

def _prune_and_fetch_files(state: AgentState):
    """Prunes irrelevant files and adds new ones if relevant. Returns a list of open_files, files that the LLM should
    see in its context."""

    all_files = state['files_total']
    open_files = state['files_open']

    def _update_files(files: list[File]):
        for file in files:
            # TODO: implement hashing to check if file has been modified, updating it if so.
            pass

    # TODO: implement LLM call to decide what files are relevant given the conversation history and to remove irrelevant
    # files from open_files. This should be quite loose, only removing files that are definitely not relevant. This
    # should ignore (meaning always include in relevant files) all non-existent files so that the agent knows not to
    # try to get them again.

def context_manager(state: AgentState):
    """Refreshes the agent's context by pruning irrelevant long term memories and files and fetching new ones if relevant"""

    long_term_memories, open_files = _prune_and_fetch_long_term(state), _prune_and_fetch_files(state)

    return {'long_term_memories': long_term_memories, 'open_files': open_files}