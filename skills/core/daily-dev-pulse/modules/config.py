"""Configuration loader for Daily Dev Pulse.

Reads ~/.quinn-skills/pulse-config.yml or falls back to defaults.
Supports env var overrides for CLI arguments (--days, --repos).
"""

import copy
import os
import sys
from pathlib import Path

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

CONFIG_PATH = Path(os.environ.get(
    "PULSE_CONFIG_PATH",
    str(Path.home() / ".quinn-skills" / "pulse-config.yml")
))

DEFAULT_CONFIG = {
    "repos": [
        {"name": "quinnpm", "owner": "quinnmacro"},
        {"name": "SanctionList", "owner": "quinnmacro"},
        {"name": "quinn-awesome-skills", "owner": "quinnmacro"},
        {"name": "quinnweb", "owner": "quinnmacro"},
        {"name": "gnhf", "owner": "quinnmacro"},
        {"name": "weather-cli", "owner": "quinnmacro"},
    ],
    "tech_stack": {
        "python": "3.13",
        "frameworks": ["FastAPI", "Next.js"],
        "databases": ["SQLite"],
        "libraries": ["LangGraph"],
    },
    "dependencies": {
        "npm": ["next", "react", "tailwindcss"],
        "pypi": ["fastapi", "uvicorn", "langgraph", "sqlalchemy", "pyyaml", "requests"],
    },
    "preferences": {
        "news_sources": ["hn", "devto", "lobsters"],
        "format": "terminal",
        "lookback_days": 7,
        "stale_pr_days": 3,
        "security_lookback_days": 30,
        "nvd_rate_limit": 6,
        "max_issues_per_repo": 3,
        "max_action_items": 10,
    },
}


def load_config(config_path=None):
    """Load configuration from YAML file or return defaults, with env var overrides."""
    path = Path(config_path) if config_path else CONFIG_PATH

    if path.exists():
        if not YAML_AVAILABLE:
            print("Error: PyYAML required to load config file. Install with: pip install pyyaml", file=sys.stderr)
            sys.exit(1)
        with open(path) as f:
            user_config = yaml.safe_load(f) or {}
        result = merge_config(DEFAULT_CONFIG, user_config)
    else:
        result = copy.deepcopy(DEFAULT_CONFIG)

    # Apply CLI overrides from environment variables
    lookback_days = os.environ.get("PULSE_LOOKBACK_DAYS")
    if lookback_days:
        try:
            result["preferences"]["lookback_days"] = int(lookback_days)
        except ValueError:
            pass

    repos_filter = os.environ.get("PULSE_REPOS")
    if repos_filter and repos_filter != "all":
        requested = []
        for entry in repos_filter.split(","):
            parts = entry.strip().split("/")
            if len(parts) == 2:
                requested.append({"owner": parts[0], "name": parts[1]})
            elif len(parts) == 1:
                for r in result.get("repos", []):
                    if r.get("name") == parts[0].strip():
                        requested.append(r)
        if requested:
            result["repos"] = requested

    return result


def merge_config(default, user):
    """Merge user config into defaults, preserving unset default values."""
    result = copy.deepcopy(default)

    for key, value in user.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_config(result[key], value)
        else:
            result[key] = value

    return result


def get_repos(config=None):
    """Return list of {owner, name} dicts from config."""
    cfg = config or load_config()
    return cfg.get("repos", DEFAULT_CONFIG["repos"])


def get_tech_stack(config=None):
    """Return tech stack dict from config."""
    cfg = config or load_config()
    return cfg.get("tech_stack", DEFAULT_CONFIG["tech_stack"])


def get_dependencies(config=None):
    """Return npm/pypi dependency lists from config."""
    cfg = config or load_config()
    return cfg.get("dependencies", DEFAULT_CONFIG["dependencies"])


def get_preferences(config=None):
    """Return preferences dict from config."""
    cfg = config or load_config()
    return cfg.get("preferences", DEFAULT_CONFIG["preferences"])


if __name__ == "__main__":
    config = load_config()
    if YAML_AVAILABLE:
        print(yaml.dump(config, default_flow_style=False))
    else:
        import json
        print(json.dumps(config, indent=2))