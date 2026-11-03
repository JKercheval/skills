"""Make the repo's scripts importable: scripts/skills.py as `skills`, and skill scripts by name."""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "skills" / "my-reflect" / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "hooks"))
