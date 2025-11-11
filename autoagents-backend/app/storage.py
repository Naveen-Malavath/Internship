from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .agents import FeatureSpec, StorySpec

DATA_DIR = Path(__file__).resolve().parent / "data"
SNAPSHOT_FILE = DATA_DIR / "agent_snapshot.json"
MERMAID_FILE = DATA_DIR / "visualization.mermaid"
DOT_FILE = DATA_DIR / "visualization.dot"

_DEFAULT_SNAPSHOT: dict[str, Any] = {
    "stored_at": None,
    "prompt": "",
    "agent1": None,
    "agent2": None,
    "features": [],
    "stories": [],
}


def _load_snapshot() -> dict[str, Any]:
    if not SNAPSHOT_FILE.exists():
      return deepcopy(_DEFAULT_SNAPSHOT)
    try:
        data = json.loads(SNAPSHOT_FILE.read_text())
        base = deepcopy(_DEFAULT_SNAPSHOT)
        base.update(data)
        return base
    except json.JSONDecodeError:
        return deepcopy(_DEFAULT_SNAPSHOT)


def _save_snapshot(snapshot: dict[str, Any]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    snapshot = deepcopy(snapshot)
    snapshot["stored_at"] = datetime.now(timezone.utc).isoformat()
    SNAPSHOT_FILE.write_text(json.dumps(snapshot, indent=2))


def store_agent1_snapshot(run_id: str, prompt: str, features: list[FeatureSpec]) -> None:
    snapshot = _load_snapshot()
    snapshot["prompt"] = prompt or snapshot.get("prompt", "")
    snapshot["agent1"] = {
        "run_id": run_id,
        "prompt": snapshot["prompt"],
        "stored_at": datetime.now(timezone.utc).isoformat(),
    }
    snapshot["features"] = [feature.to_dict() for feature in features]
    snapshot["stories"] = snapshot.get("stories", [])
    _save_snapshot(snapshot)


def store_agent2_snapshot(
    run_id: str,
    prompt: str,
    features: list[FeatureSpec],
    stories: list[StorySpec],
) -> None:
    snapshot = _load_snapshot()
    snapshot["prompt"] = prompt or snapshot.get("prompt", "")
    snapshot["agent2"] = {
        "run_id": run_id,
        "prompt": snapshot["prompt"],
        "stored_at": datetime.now(timezone.utc).isoformat(),
    }
    snapshot["features"] = [feature.to_dict() for feature in features]
    snapshot["stories"] = [story.to_dict() for story in stories]
    _save_snapshot(snapshot)


def _timestamp(path: Path) -> str | None:
    if not path.exists():
        return None
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat()


def store_visualization_assets(mermaid: str | None, dot: str | None) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if mermaid is not None:
        MERMAID_FILE.write_text(mermaid)
    if dot is not None:
        DOT_FILE.write_text(dot)


def load_mermaid_asset() -> tuple[str, str | None, str | None]:
    if not MERMAID_FILE.exists():
        return ("", None, None)
    return (
        MERMAID_FILE.read_text(),
        str(MERMAID_FILE),
        _timestamp(MERMAID_FILE),
    )


def load_dot_asset() -> tuple[str, str | None, str | None]:
    if not DOT_FILE.exists():
        return ("", None, None)
    return (
        DOT_FILE.read_text(),
        str(DOT_FILE),
        _timestamp(DOT_FILE),
    )


def load_snapshot() -> dict[str, Any]:
    return _load_snapshot()


def load_agent1_features() -> list[FeatureSpec]:
    snapshot = _load_snapshot()
    return [FeatureSpec.from_dict(item) for item in snapshot.get("features", []) if isinstance(item, dict)]


def load_agent2_stories() -> list[StorySpec]:
    snapshot = _load_snapshot()
    return [StorySpec.from_dict(item) for item in snapshot.get("stories", []) if isinstance(item, dict)]


def load_prompt() -> str:
    snapshot = _load_snapshot()
    return snapshot.get("prompt", "")

