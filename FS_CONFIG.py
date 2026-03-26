from pathlib import Path

AGENT_ROOT = Path("/home/will/.twin2")
MEMORY_ROOT = AGENT_ROOT / "memory"

AGENT_ROOT.mkdir(parents=True, exist_ok=True)
MEMORY_ROOT.mkdir(parents=True, exist_ok=True)
