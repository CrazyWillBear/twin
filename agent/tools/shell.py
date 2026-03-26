"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Copyright (c) 2026 William Chastain. All rights reserved.
"""

import subprocess
import tempfile
import os

from langchain_core.tools import tool

from FS_CONFIG import AGENT_ROOT

TIMEOUT = 120  # seconds before the command is killed


def _run_subprocess(command: str, shell: bool = True, **kwargs) -> str:
    try:
        result = subprocess.run(
            command,
            shell=shell,
            capture_output=True,
            text=True,
            timeout=TIMEOUT,
            cwd=AGENT_ROOT,
            **kwargs
        )
    except subprocess.TimeoutExpired:
        return f"Timed out after {TIMEOUT} seconds."

    parts = []
    if result.stdout:
        parts.append(result.stdout)
    if result.stderr:
        parts.append(f"stderr:\n{result.stderr}")
    if result.returncode != 0:
        parts.append(f"Return code: {result.returncode}")

    return "\n".join(parts) if parts else "(no output)"



@tool
def run_command(command: str) -> str:
    """Run a single shell command in the workspace. The user will be prompted to approve before it runs."""

    print(f"\n  Command requested: {command}")
    try:
        response = input("  Allow? [y/N]: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        return "User declined the command."

    if response != "y":
        return "User declined to run the command."

    return _run_subprocess(command, shell=True)


@tool
def run_shell_script(interpreter: str, script: str) -> str:
    """Run a multi-line script with the given interpreter. The user will be prompted to approve before it runs."""
    print(f"\n  Script execution requested (interpreter: {interpreter}):")
    print("  ---")
    for line in script.splitlines():
        print(f"  {line}")
    print("  ---")
    try:
        response = input("  Allow? [y/N]: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        return "User declined the script."

    if response != "y":
        return "User declined to run the script."

    suffix_map = {"python3": ".py", "python": ".py", "bash": ".sh", "sh": ".sh"}
    suffix = suffix_map.get(interpreter, ".sh")

    with tempfile.NamedTemporaryFile(mode="w", suffix=suffix, delete=False) as f:
        f.write(script)
        tmp_path = f.name

    try:
        return _run_subprocess([interpreter, tmp_path], shell=False)
    finally:
        os.unlink(tmp_path)
