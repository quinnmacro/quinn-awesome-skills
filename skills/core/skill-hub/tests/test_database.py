"""Tests for database module."""

import pytest
import pytest_asyncio
import json

from database import (
    init_db,
    upsert_skill,
    get_all_skills,
    get_skill,
    search_skills_db,
    record_test_run,
    get_test_runs,
    get_health_stats,
    sync_skills,
    upsert_dependency,
    get_dependencies,
)


# --- init_db tests ---


class TestInitDb:
    @pytest.mark.asyncio
    async def test_init_creates_tables(self, db):
        cursor = await db.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [r[0] for r in await cursor.fetchall()]
        assert "skills" in tables
        assert "test_runs" in tables
        assert "dependencies" in tables

    @pytest.mark.asyncio
    async def test_init_creates_indexes(self, db):
        cursor = await db.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = [r[0] for r in await cursor.fetchall()]
        assert "idx_test_runs_skill" in indexes
        assert "idx_test_runs_started" in indexes

    @pytest.mark.asyncio
    async def test_init_db_creates_directory(self, tmp_path):
        db_path = str(tmp_path / "subdir" / "test.db")
        conn = await init_db(db_path)
        assert (tmp_path / "subdir").is_dir()
        await conn.close()


# --- upsert_skill tests ---


class TestUpsertSkill:
    @pytest.mark.asyncio
    async def test_insert_skill(self, db, mock_skill_data):
        await upsert_skill(db, mock_skill_data)
        skill = await get_skill(db, "test-skill")
        assert skill is not None
        assert skill["name"] == "test-skill"

    @pytest.mark.asyncio
    async def test_update_skill(self, db, mock_skill_data):
        await upsert_skill(db, mock_skill_data)
        mock_skill_data["version"] = "2.0.0"
        mock_skill_data["description"] = "Updated description"
        await upsert_skill(db, mock_skill_data)
        skill = await get_skill(db, "test-skill")
        assert skill["version"] == "2.0.0"
        assert skill["description"] == "Updated description"

    @pytest.mark.asyncio
    async def test_scripts_stored_as_json(self, db, mock_skill_data):
        mock_skill_data["scripts"] = ["a.sh", "b.py"]
        await upsert_skill(db, mock_skill_data)
        cursor = await db.execute("SELECT scripts_json FROM skills WHERE name='test-skill'")
        row = await cursor.fetchone()
        assert json.loads(row[0]) == ["a.sh", "b.py"]

    @pytest.mark.asyncio
    async def test_modules_stored_as_json(self, db, mock_skill_data):
        mock_skill_data["modules"] = ["core.py"]
        await upsert_skill(db, mock_skill_data)
        cursor = await db.execute("SELECT modules_json FROM skills WHERE name='test-skill'")
        row = await cursor.fetchone()
        assert json.loads(row[0]) == ["core.py"]

    @pytest.mark.asyncio
    async def test_default_values(self, db):
        minimal = {"name": "minimal-skill", "path": "/tmp/min"}
        await upsert_skill(db, minimal)
        skill = await get_skill(db, "minimal-skill")
        assert skill["version"] == "0.0.0"
        assert skill["layer"] == "core"
        assert skill["health"] == "unknown"

    @pytest.mark.asyncio
    async def test_multiple_skills(self, db, mock_skill_data):
        await upsert_skill(db, mock_skill_data)
        second = dict(mock_skill_data, name="second-skill", version="0.1.0")
        await upsert_skill(db, second)
        all_skills = await get_all_skills(db)
        assert len(all_skills) >= 2


# --- get_all_skills tests ---


class TestGetAllSkills:
    @pytest.mark.asyncio
    async def test_empty_db(self, db):
        skills = await get_all_skills(db)
        assert skills == []

    @pytest.mark.asyncio
    async def test_returns_all_inserted(self, db, mock_skill_data):
        await upsert_skill(db, mock_skill_data)
        second = dict(mock_skill_data, name="second-skill")
        await upsert_skill(db, second)
        skills = await get_all_skills(db)
        assert len(skills) == 2

    @pytest.mark.asyncio
    async def test_sorted_by_name(self, db, mock_skill_data):
        names = ["z-skill", "a-skill", "m-skill"]
        for n in names:
            d = dict(mock_skill_data, name=n)
            await upsert_skill(db, d)
        skills = await get_all_skills(db)
        assert [s["name"] for s in skills] == sorted(names)


# --- get_skill tests ---


class TestGetSkill:
    @pytest.mark.asyncio
    async def test_found(self, db, mock_skill_data):
        await upsert_skill(db, mock_skill_data)
        skill = await get_skill(db, "test-skill")
        assert skill["name"] == "test-skill"

    @pytest.mark.asyncio
    async def test_not_found(self, db):
        skill = await get_skill(db, "nonexistent")
        assert skill is None

    @pytest.mark.asyncio
    async def test_returns_all_fields(self, db, mock_skill_data):
        await upsert_skill(db, mock_skill_data)
        skill = await get_skill(db, "test-skill")
        assert "name" in skill
        assert "version" in skill
        assert "description" in skill
        assert "layer" in skill
        assert "category" in skill
        assert "path" in skill
        assert "scripts" in skill
        assert "modules" in skill
        assert "author" in skill
        assert "health" in skill
        assert "discovered_at" in skill
        assert "updated_at" in skill


# --- search_skills_db tests ---


class TestSearchSkillsDb:
    @pytest.mark.asyncio
    async def test_search_by_name(self, db, mock_skill_data):
        await upsert_skill(db, mock_skill_data)
        results = await search_skills_db(db, "test")
        assert len(results) >= 1

    @pytest.mark.asyncio
    async def test_search_by_description(self, db, mock_skill_data):
        mock_skill_data["description"] = "Unique keyword xyzzy"
        await upsert_skill(db, mock_skill_data)
        results = await search_skills_db(db, "xyzzy")
        assert len(results) >= 1

    @pytest.mark.asyncio
    async def test_no_results(self, db, mock_skill_data):
        await upsert_skill(db, mock_skill_data)
        results = await search_skills_db(db, "nonexistent")
        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_wildcard_match(self, db, mock_skill_data):
        await upsert_skill(db, mock_skill_data)
        results = await search_skills_db(db, "test-s")
        assert len(results) >= 1


# --- record_test_run tests ---


class TestRecordTestRun:
    @pytest.mark.asyncio
    async def test_record_run(self, db, mock_skill_data, mock_test_result):
        await upsert_skill(db, mock_skill_data)
        run_id = await record_test_run(db, mock_test_result)
        assert run_id > 0

    @pytest.mark.asyncio
    async def test_run_has_all_fields(self, db, mock_skill_data, mock_test_result):
        await upsert_skill(db, mock_skill_data)
        await record_test_run(db, mock_test_result)
        runs = await get_test_runs(db, "test-skill")
        assert len(runs) == 1
        run = runs[0]
        assert run["skill_name"] == "test-skill"
        assert run["status"] == "completed"
        assert run["total_tests"] == 10
        assert run["passed"] == 8
        assert run["failed"] == 2

    @pytest.mark.asyncio
    async def test_multiple_runs(self, db, mock_skill_data, mock_test_result):
        await upsert_skill(db, mock_skill_data)
        await record_test_run(db, mock_test_result)
        second = dict(mock_test_result, passed=10, failed=0)
        await record_test_run(db, second)
        runs = await get_test_runs(db, "test-skill")
        assert len(runs) == 2

    @pytest.mark.asyncio
    async def test_default_status(self, db, mock_skill_data):
        await upsert_skill(db, mock_skill_data)
        minimal = {"skill_name": "test-skill"}
        run_id = await record_test_run(db, minimal)
        assert run_id > 0
        runs = await get_test_runs(db, "test-skill")
        assert runs[0]["status"] == "pending"


# --- get_test_runs tests ---


class TestGetTestRuns:
    @pytest.mark.asyncio
    async def test_no_runs(self, db, mock_skill_data):
        await upsert_skill(db, mock_skill_data)
        runs = await get_test_runs(db, "test-skill")
        assert runs == []

    @pytest.mark.asyncio
    async def test_limit(self, db, mock_skill_data, mock_test_result):
        await upsert_skill(db, mock_skill_data)
        for _ in range(25):
            await record_test_run(db, mock_test_result)
        runs = await get_test_runs(db, "test-skill", limit=5)
        assert len(runs) == 5

    @pytest.mark.asyncio
    async def test_ordered_by_started_desc(self, db, mock_skill_data, mock_test_result):
        await upsert_skill(db, mock_skill_data)
        await record_test_run(db, dict(mock_test_result, started_at="2026-01-01"))
        await record_test_run(db, dict(mock_test_result, started_at="2026-04-29"))
        runs = await get_test_runs(db, "test-skill")
        assert runs[0]["started_at"] == "2026-04-29"


# --- get_health_stats tests ---


class TestGetHealthStats:
    @pytest.mark.asyncio
    async def test_empty_stats(self, db):
        stats = await get_health_stats(db)
        assert stats["total_skills"] == 0
        assert stats["avg_pass_rate"] == 0.0

    @pytest.mark.asyncio
    async def test_skills_count(self, db, mock_skill_data):
        await upsert_skill(db, mock_skill_data)
        stats = await get_health_stats(db)
        assert stats["total_skills"] == 1

    @pytest.mark.asyncio
    async def test_layer_distribution(self, db, mock_skill_data):
        await upsert_skill(db, mock_skill_data)
        second = dict(mock_skill_data, name="ext-skill", layer="external")
        await upsert_skill(db, second)
        stats = await get_health_stats(db)
        assert stats["layers"]["core"] == 1
        assert stats["layers"]["external"] == 1

    @pytest.mark.asyncio
    async def test_pass_rate_with_tests(self, db, mock_skill_data, mock_test_result):
        await upsert_skill(db, mock_skill_data)
        await record_test_run(db, mock_test_result)
        stats = await get_health_stats(db)
        assert "test-skill" in stats["test_summary"]
        assert stats["test_summary"]["test-skill"]["pass_rate"] == 0.8

    @pytest.mark.asyncio
    async def test_avg_pass_rate(self, db, mock_skill_data, mock_test_result):
        await upsert_skill(db, mock_skill_data)
        await record_test_run(db, mock_test_result)
        stats = await get_health_stats(db)
        assert stats["avg_pass_rate"] == 0.8


# --- sync_skills tests ---


class TestSyncSkills:
    @pytest.mark.asyncio
    async def test_sync_inserts_skills(self, db, tmp_skills_dir):
        from skill_discovery import discover_skills
        discovered = discover_skills(tmp_skills_dir)
        await sync_skills(db, discovered)
        all_skills = await get_all_skills(db)
        assert len(all_skills) >= 3

    @pytest.mark.asyncio
    async def test_sync_updates_existing(self, db, mock_skill_data):
        await upsert_skill(db, mock_skill_data)
        updated = dict(mock_skill_data, version="3.0.0")
        await sync_skills(db, [updated])
        skill = await get_skill(db, "test-skill")
        assert skill["version"] == "3.0.0"


# --- dependency tests ---


class TestDependencies:
    @pytest.mark.asyncio
    async def test_upsert_dependency(self, db, mock_skill_data):
        await upsert_skill(db, mock_skill_data)
        await upsert_dependency(db, "test-skill", "fastapi", "pip", 1)
        deps = await get_dependencies(db, "test-skill")
        assert len(deps) == 1
        assert deps[0]["dep_name"] == "fastapi"
        assert deps[0]["installed"] is True

    @pytest.mark.asyncio
    async def test_uninstalled_dependency(self, db, mock_skill_data):
        await upsert_skill(db, mock_skill_data)
        await upsert_dependency(db, "test-skill", "playwright", "pip", 0)
        deps = await get_dependencies(db, "test-skill")
        assert deps[0]["installed"] is False

    @pytest.mark.asyncio
    async def test_update_dependency_status(self, db, mock_skill_data):
        await upsert_skill(db, mock_skill_data)
        await upsert_dependency(db, "test-skill", "fastapi", "pip", 0)
        await upsert_dependency(db, "test-skill", "fastapi", "pip", 1)
        deps = await get_dependencies(db, "test-skill")
        assert deps[0]["installed"] is True

    @pytest.mark.asyncio
    async def test_multiple_dependencies(self, db, mock_skill_data):
        await upsert_skill(db, mock_skill_data)
        await upsert_dependency(db, "test-skill", "fastapi", "pip", 1)
        await upsert_dependency(db, "test-skill", "uvicorn", "pip", 1)
        await upsert_dependency(db, "test-skill", "gh", "brew", 1)
        deps = await get_dependencies(db, "test-skill")
        assert len(deps) == 3

    @pytest.mark.asyncio
    async def test_no_dependencies(self, db, mock_skill_data):
        await upsert_skill(db, mock_skill_data)
        deps = await get_dependencies(db, "test-skill")
        assert deps == []