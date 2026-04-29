"""SQLite database for skill metadata and test history."""

import os
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import aiosqlite

DEFAULT_DB_PATH = os.path.expanduser("~/.quinn-skills/skill-hub.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS skills (
    name TEXT PRIMARY KEY,
    version TEXT NOT NULL DEFAULT '0.0.0',
    description TEXT DEFAULT '',
    layer TEXT DEFAULT 'core',
    category TEXT DEFAULT '',
    path TEXT NOT NULL,
    scripts_json TEXT DEFAULT '[]',
    modules_json TEXT DEFAULT '[]',
    author TEXT DEFAULT '',
    health TEXT DEFAULT 'unknown',
    discovered_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS test_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    total_tests INTEGER DEFAULT 0,
    passed INTEGER DEFAULT 0,
    failed INTEGER DEFAULT 0,
    errors INTEGER DEFAULT 0,
    skipped INTEGER DEFAULT 0,
    duration_seconds REAL DEFAULT 0.0,
    output TEXT DEFAULT '',
    started_at TEXT NOT NULL,
    finished_at TEXT,
    FOREIGN KEY (skill_name) REFERENCES skills(name)
);

CREATE TABLE IF NOT EXISTS dependencies (
    skill_name TEXT NOT NULL,
    dep_name TEXT NOT NULL,
    dep_type TEXT NOT NULL DEFAULT 'pip',
    installed INTEGER DEFAULT 0,
    FOREIGN KEY (skill_name) REFERENCES skills(name),
    PRIMARY KEY (skill_name, dep_name)
);

CREATE INDEX IF NOT EXISTS idx_test_runs_skill ON test_runs(skill_name);
CREATE INDEX IF NOT EXISTS idx_test_runs_started ON test_runs(started_at);
"""


async def init_db(db_path: str = DEFAULT_DB_PATH) -> aiosqlite.Connection:
    """Initialize database and create tables."""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    db = await aiosqlite.connect(db_path)
    await db.executescript(SCHEMA)
    await db.commit()
    return db


async def upsert_skill(db: aiosqlite.Connection, skill: dict) -> None:
    """Insert or update a skill record."""
    now = datetime.now(timezone.utc).isoformat()
    scripts_json = json.dumps(skill.get("scripts", []))
    modules_json = json.dumps(skill.get("modules", []))
    await db.execute(
        """INSERT INTO skills (name, version, description, layer, category, path,
           scripts_json, modules_json, author, health, discovered_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
           ON CONFLICT(name) DO UPDATE SET
           version=excluded.version, description=excluded.description,
           layer=excluded.layer, category=excluded.category, path=excluded.path,
           scripts_json=excluded.scripts_json, modules_json=excluded.modules_json,
           author=excluded.author, health=excluded.health, updated_at=excluded.updated_at""",
        (
            skill["name"],
            skill.get("version", "0.0.0"),
            skill.get("description", ""),
            skill.get("layer", "core"),
            skill.get("category", ""),
            skill.get("path", ""),
            scripts_json,
            modules_json,
            skill.get("author", ""),
            skill.get("health", "unknown"),
            now,
            now,
        ),
    )
    await db.commit()


async def get_all_skills(db: aiosqlite.Connection) -> list[dict]:
    """Return all skills from the database."""
    rows = await db.execute_fetchall("SELECT * FROM skills ORDER BY name")
    return [_row_to_skill(r) for r in rows]


async def get_skill(db: aiosqlite.Connection, name: str) -> Optional[dict]:
    """Return a single skill by name."""
    cursor = await db.execute("SELECT * FROM skills WHERE name = ?", (name,))
    row = await cursor.fetchone()
    if row is None:
        return None
    return _row_to_skill(row)


async def search_skills_db(db: aiosqlite.Connection, query: str) -> list[dict]:
    """Search skills by name or description substring."""
    q = f"%{query}%"
    cursor = await db.execute(
        "SELECT * FROM skills WHERE name LIKE ? OR description LIKE ? ORDER BY name",
        (q, q),
    )
    rows = await cursor.fetchall()
    return [_row_to_skill(r) for r in rows]


async def record_test_run(db: aiosqlite.Connection, result: dict) -> int:
    """Record a test run result. Returns the run ID."""
    now = datetime.now(timezone.utc).isoformat()
    cursor = await db.execute(
        """INSERT INTO test_runs (skill_name, status, total_tests, passed, failed,
           errors, skipped, duration_seconds, output, started_at, finished_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            result["skill_name"],
            result.get("status", "pending"),
            result.get("total_tests", 0),
            result.get("passed", 0),
            result.get("failed", 0),
            result.get("errors", 0),
            result.get("skipped", 0),
            result.get("duration_seconds", 0.0),
            result.get("output", ""),
            result.get("started_at", now),
            result.get("finished_at", now),
        ),
    )
    await db.commit()
    return cursor.lastrowid


async def get_test_runs(db: aiosqlite.Connection, skill_name: str, limit: int = 20) -> list[dict]:
    """Get recent test runs for a skill."""
    cursor = await db.execute(
        "SELECT * FROM test_runs WHERE skill_name = ? ORDER BY started_at DESC LIMIT ?",
        (skill_name, limit),
    )
    rows = await cursor.fetchall()
    return [_row_to_test_run(r) for r in rows]


async def get_health_stats(db: aiosqlite.Connection) -> dict:
    """Aggregate health statistics across all skills."""
    skills = await get_all_skills(db)
    total = len(skills)
    layers = {}
    for s in skills:
        layer = s.get("layer", "unknown")
        layers[layer] = layers.get(layer, 0) + 1

    # Get latest test results per skill
    cursor = await db.execute(
        """SELECT skill_name, status, passed, failed, errors, total_tests
           FROM test_runs WHERE id IN (
               SELECT MAX(id) FROM test_runs GROUP BY skill_name
           )"""
    )
    test_rows = await cursor.fetchall()
    test_summary = {}
    pass_rate = 0.0
    for r in test_rows:
        name = r[0]
        total_t = r[5] or 0
        passed_t = r[2] or 0
        rate = passed_t / total_t if total_t > 0 else 0.0
        test_summary[name] = {"status": r[1], "pass_rate": rate, "total": total_t, "passed": passed_t}
        pass_rate += rate

    avg_pass_rate = pass_rate / len(test_rows) if test_rows else 0.0

    # Get dependency summary
    dep_cursor = await db.execute(
        "SELECT skill_name, dep_name, dep_type, installed FROM dependencies ORDER BY skill_name, dep_name"
    )
    dep_rows = await dep_cursor.fetchall()
    dep_summary = {}
    for r in dep_rows:
        skill_name = r[0]
        if skill_name not in dep_summary:
            dep_summary[skill_name] = []
        dep_summary[skill_name].append({
            "dep_name": r[1],
            "dep_type": r[2],
            "installed": bool(r[3]),
        })

    return {
        "total_skills": total,
        "layers": layers,
        "test_summary": test_summary,
        "avg_pass_rate": avg_pass_rate,
        "dep_summary": dep_summary,
    }


async def upsert_dependency(db: aiosqlite.Connection, skill_name: str, dep_name: str, dep_type: str = "pip", installed: int = 0) -> None:
    """Record a dependency status."""
    await db.execute(
        """INSERT INTO dependencies (skill_name, dep_name, dep_type, installed)
           VALUES (?, ?, ?, ?)
           ON CONFLICT(skill_name, dep_name) DO UPDATE SET installed=excluded.installed""",
        (skill_name, dep_name, dep_type, installed),
    )
    await db.commit()


async def get_dependencies(db: aiosqlite.Connection, skill_name: str) -> list[dict]:
    """Get dependencies for a skill."""
    cursor = await db.execute(
        "SELECT dep_name, dep_type, installed FROM dependencies WHERE skill_name = ?",
        (skill_name,),
    )
    rows = await cursor.fetchall()
    return [{"dep_name": r[0], "dep_type": r[1], "installed": bool(r[2])} for r in rows]


async def sync_skills(db: aiosqlite.Connection, discovered: list[dict]) -> None:
    """Sync discovered skills into the database."""
    for skill in discovered:
        await upsert_skill(db, skill)


async def sync_dependencies(db: aiosqlite.Connection, discovered: list[dict]) -> None:
    """Sync discovered skill dependencies into the database."""
    for skill in discovered:
        for dep in skill.get("dependencies", []):
            await upsert_dependency(
                db,
                skill_name=skill["name"],
                dep_name=dep["dep_name"],
                dep_type=dep.get("dep_type", "pip"),
                installed=0,
            )


def _row_to_skill(row: Any) -> dict:
    """Convert a database row to a skill dict."""
    return {
        "name": row[0],
        "version": row[1],
        "description": row[2],
        "layer": row[3],
        "category": row[4],
        "path": row[5],
        "scripts": json.loads(row[6]),
        "modules": json.loads(row[7]),
        "author": row[8],
        "health": row[9],
        "discovered_at": row[10],
        "updated_at": row[11],
    }


def _row_to_test_run(row: Any) -> dict:
    """Convert a database row to a test run dict."""
    return {
        "id": row[0],
        "skill_name": row[1],
        "status": row[2],
        "total_tests": row[3],
        "passed": row[4],
        "failed": row[5],
        "errors": row[6],
        "skipped": row[7],
        "duration_seconds": row[8],
        "output": row[9],
        "started_at": row[10],
        "finished_at": row[11],
    }