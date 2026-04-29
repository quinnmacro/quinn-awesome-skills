"""Skill Hub test configuration."""

import sys
import os
import tempfile
import asyncio
from pathlib import Path

import pytest
import pytest_asyncio

# Add skill-hub modules to sys.path
SKILL_HUB_DIR = Path(__file__).resolve().parent.parent
MODULES_DIR = SKILL_HUB_DIR / "modules"
if str(MODULES_DIR) not in sys.path:
    sys.path.insert(0, str(MODULES_DIR))

# Project root for real skills directory
PROJECT_ROOT = SKILL_HUB_DIR.parent.parent.parent
REAL_SKILLS_DIR = PROJECT_ROOT / "skills"


@pytest.fixture
def tmp_skills_dir(tmp_path):
    """Create a temporary skills directory with mock skills."""
    core_dir = tmp_path / "core"
    core_dir.mkdir()

    # Create mock skill: mock-fetcher
    fetcher_dir = core_dir / "mock-fetcher"
    fetcher_dir.mkdir()
    (fetcher_dir / "SKILL.md").write_text(
        "---\n"
        "name: mock-fetcher\n"
        "version: 2.0.0\n"
        "author: testauthor\n"
        "layer: core\n"
        "description: Mock URL fetcher for testing\n"
        "---\n\n"
        "# Mock Fetcher\n\nA test skill."
    )
    scripts_dir = fetcher_dir / "scripts"
    scripts_dir.mkdir()
    (scripts_dir / "fetch.sh").write_text("#!/bin/bash\necho mock")
    (scripts_dir / "search.py").write_text("print('search')")
    modules_dir = fetcher_dir / "modules"
    modules_dir.mkdir()
    (modules_dir / "core.py").write_text("pass")

    # Create mock skill: mock-pulse
    pulse_dir = core_dir / "mock-pulse"
    pulse_dir.mkdir()
    (pulse_dir / "SKILL.md").write_text(
        "---\n"
        "name: mock-pulse\n"
        "version: 1.5.0\n"
        "author: testauthor\n"
        "layer: core\n"
        "description: |\n"
        "  Mock developer pulse for testing.\n"
        "  Triggers: test pulse.\n"
        "---\n\n"
        "# Mock Pulse\n\nAnother test skill."
    )

    # Create external skill
    ext_dir = tmp_path / "external"
    ext_dir.mkdir()
    bloomberg_dir = ext_dir / "mock-bloomberg"
    bloomberg_dir.mkdir()
    (bloomberg_dir / "SKILL.md").write_text(
        "---\n"
        "name: mock-bloomberg\n"
        "version: 0.1.0\n"
        "author: external\n"
        "layer: external\n"
        "description: Bloomberg mock prompts for testing\n"
        "---\n\n"
        "# Mock Bloomberg"
    )

    return tmp_path


@pytest.fixture
def tmp_skills_dir_with_hidden(tmp_skills_dir):
    """Add hidden directories that should be skipped."""
    core = tmp_skills_dir / "core"
    hidden = core / ".hidden-skill"
    hidden.mkdir()
    (hidden / "SKILL.md").write_text("---\nname: should-not-appear\n---\n")
    return tmp_skills_dir


@pytest.fixture
def tmp_skills_dir_nested(tmp_skills_dir):
    """Add nested external skills (like bloomberg/company/company-snapshot)."""
    ext = tmp_skills_dir / "external"
    bloomberg = ext / "nested-bloomberg"
    bloomberg.mkdir()
    company = bloomberg / "company"
    company.mkdir()
    snapshot = company / "company-snapshot"
    snapshot.mkdir()
    (snapshot / "template.md").write_text(
        "---\n"
        "name: company-snapshot\n"
        "version: 1.0.0\n"
        "description: Company snapshot template\n"
        "---\n\n"
        "# Snapshot"
    )
    return tmp_skills_dir


@pytest_asyncio.fixture
async def db(tmp_path):
    """Create a test database connection."""
    from database import init_db
    db_path = str(tmp_path / "test_skill_hub.db")
    conn = await init_db(db_path)
    yield conn
    await conn.close()


@pytest.fixture
def mock_skill_data():
    """Return mock skill data for database tests."""
    return {
        "name": "test-skill",
        "version": "1.0.0",
        "description": "A test skill for unit tests",
        "layer": "core",
        "category": "core",
        "path": "/tmp/test-skill",
        "scripts": ["run.sh", "process.py"],
        "modules": ["core.py", "utils.py"],
        "author": "testauthor",
        "health": "unknown",
    }


@pytest.fixture
def mock_test_result():
    """Return mock test run result data."""
    return {
        "skill_name": "test-skill",
        "status": "completed",
        "total_tests": 10,
        "passed": 8,
        "failed": 2,
        "errors": 0,
        "skipped": 0,
        "duration_seconds": 1.5,
        "output": "8 passed, 2 failed in 1.50s",
        "started_at": "2026-04-29T00:00:00+00:00",
        "finished_at": "2026-04-29T00:00:02+00:00",
    }