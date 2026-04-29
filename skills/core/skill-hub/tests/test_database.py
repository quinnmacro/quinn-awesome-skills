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
    get_recent_test_runs,
    get_health_stats,
    sync_skills,
    sync_dependencies,
    upsert_dependency,
    get_dependencies,
    record_version,
    get_versions,
    delete_skill,
    delete_test_runs,
    _row_to_skill,
    _row_to_test_run,
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


class TestSyncDependencies:
    @pytest.mark.asyncio
    async def test_sync_dependencies_from_discovered(self, db, tmp_skills_dir):
        from skill_discovery import discover_skills
        discovered = discover_skills(tmp_skills_dir)
        await sync_skills(db, discovered)
        await sync_dependencies(db, discovered)
        # Check that skill-hub (if discovered) has its deps
        for skill in discovered:
            if skill.get("dependencies"):
                deps = await get_dependencies(db, skill["name"])
                assert len(deps) >= len(skill["dependencies"])

    @pytest.mark.asyncio
    async def test_sync_dependencies_empty_list(self, db, mock_skill_data):
        await upsert_skill(db, mock_skill_data)
        discovered = [dict(mock_skill_data, dependencies=[])]
        await sync_dependencies(db, discovered)
        deps = await get_dependencies(db, "test-skill")
        assert deps == []

    @pytest.mark.asyncio
    async def test_sync_dependencies_with_pip_deps(self, db, mock_skill_data):
        await upsert_skill(db, mock_skill_data)
        discovered = [dict(mock_skill_data, dependencies=[
            {"dep_name": "fastapi", "dep_type": "pip"},
            {"dep_name": "uvicorn", "dep_type": "pip"},
        ])]
        await sync_dependencies(db, discovered)
        deps = await get_dependencies(db, "test-skill")
        assert len(deps) == 2
        names = [d["dep_name"] for d in deps]
        assert "fastapi" in names
        assert "uvicorn" in names


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

    @pytest.mark.asyncio
    async def test_dependency_dep_type_values(self, db, mock_skill_data):
        await upsert_skill(db, mock_skill_data)
        await upsert_dependency(db, "test-skill", "node", "npm", 1)
        deps = await get_dependencies(db, "test-skill")
        assert deps[0]["dep_type"] == "npm"

    @pytest.mark.asyncio
    async def test_get_dependencies_for_nonexistent_skill(self, db):
        deps = await get_dependencies(db, "no-such-skill")
        assert deps == []


# --- Additional database edge case tests ---


class TestUpsertSkillEdgeCases:
    @pytest.mark.asyncio
    async def test_skill_with_empty_scripts(self, db):
        skill = {"name": "empty-scripts", "path": "/tmp", "scripts": [], "modules": ["m.py"]}
        await upsert_skill(db, skill)
        result = await get_skill(db, "empty-scripts")
        assert result["scripts"] == []

    @pytest.mark.asyncio
    async def test_skill_with_empty_modules(self, db):
        skill = {"name": "empty-mods", "path": "/tmp", "scripts": ["s.sh"], "modules": []}
        await upsert_skill(db, skill)
        result = await get_skill(db, "empty-mods")
        assert result["modules"] == []

    @pytest.mark.asyncio
    async def test_skill_with_unicode_description(self, db):
        skill = {"name": "unicode-skill", "path": "/tmp", "description": "技能测试 中文描述"}
        await upsert_skill(db, skill)
        result = await get_skill(db, "unicode-skill")
        assert "中文" in result["description"]

    @pytest.mark.asyncio
    async def test_skill_with_long_description(self, db):
        long_desc = "A" * 5000
        skill = {"name": "long-desc", "path": "/tmp", "description": long_desc}
        await upsert_skill(db, skill)
        result = await get_skill(db, "long-desc")
        assert result["description"] == long_desc

    @pytest.mark.asyncio
    async def test_skill_with_special_chars_in_name(self, db):
        skill = {"name": "url-fetcher-v2", "path": "/tmp"}
        await upsert_skill(db, skill)
        result = await get_skill(db, "url-fetcher-v2")
        assert result["name"] == "url-fetcher-v2"

    @pytest.mark.asyncio
    async def test_upsert_preserves_discovered_at(self, db, mock_skill_data):
        await upsert_skill(db, mock_skill_data)
        first = await get_skill(db, "test-skill")
        first_discovered = first["discovered_at"]
        mock_skill_data["version"] = "5.0.0"
        await upsert_skill(db, mock_skill_data)
        second = await get_skill(db, "test-skill")
        assert second["discovered_at"] == first_discovered
        assert second["version"] == "5.0.0"


class TestSearchEdgeCases:
    @pytest.mark.asyncio
    async def test_search_exact_name_match(self, db, mock_skill_data):
        await upsert_skill(db, mock_skill_data)
        results = await search_skills_db(db, "test-skill")
        assert len(results) >= 1

    @pytest.mark.asyncio
    async def test_search_case_sensitivity(self, db, mock_skill_data):
        mock_skill_data["description"] = "UPPERCASE Description"
        await upsert_skill(db, mock_skill_data)
        results = await search_skills_db(db, "UPPERCASE")
        assert len(results) >= 1

    @pytest.mark.asyncio
    async def test_search_partial_name(self, db, mock_skill_data):
        await upsert_skill(db, mock_skill_data)
        results = await search_skills_db(db, "test")
        assert len(results) >= 1


class TestHealthStatsEdgeCases:
    @pytest.mark.asyncio
    async def test_pass_rate_zero_with_no_tests(self, db):
        await upsert_skill(db, {"name": "no-tests", "path": "/tmp"})
        stats = await get_health_stats(db)
        assert stats["avg_pass_rate"] == 0.0

    @pytest.mark.asyncio
    async def test_multiple_skills_same_layer(self, db):
        for name in ["a", "b", "c"]:
            await upsert_skill(db, {"name": name, "path": "/tmp/" + name, "layer": "core"})
        stats = await get_health_stats(db)
        assert stats["layers"]["core"] == 3

    @pytest.mark.asyncio
    async def test_layers_dict_has_all_layers(self, db):
        await upsert_skill(db, {"name": "core1", "path": "/tmp", "layer": "core"})
        await upsert_skill(db, {"name": "ext1", "path": "/tmp", "layer": "external"})
        stats = await get_health_stats(db)
        assert "core" in stats["layers"]
        assert "external" in stats["layers"]

    @pytest.mark.asyncio
    async def test_dep_summary_in_stats(self, db, mock_skill_data):
        await upsert_skill(db, mock_skill_data)
        await upsert_dependency(db, "test-skill", "fastapi", "pip", 1)
        await upsert_dependency(db, "test-skill", "uvicorn", "pip", 1)
        stats = await get_health_stats(db)
        assert "dep_summary" in stats

    @pytest.mark.asyncio
    async def test_health_counts_in_stats(self, db):
        """get_health_stats should return health_counts with passing/failing/unknown counts."""
        await upsert_skill(db, {"name": "pass1", "path": "/tmp", "health": "passing"})
        await upsert_skill(db, {"name": "fail1", "path": "/tmp", "health": "failing"})
        await upsert_skill(db, {"name": "unk1", "path": "/tmp", "health": "unknown"})
        stats = await get_health_stats(db)
        assert "health_counts" in stats
        assert stats["health_counts"]["passing"] >= 1
        assert stats["health_counts"]["failing"] >= 1
        assert stats["health_counts"]["unknown"] >= 1

    @pytest.mark.asyncio
    async def test_health_counts_all_passing(self, db):
        """All passing skills should show passing count equal to total."""
        await upsert_skill(db, {"name": "p1", "path": "/tmp", "health": "passing"})
        await upsert_skill(db, {"name": "p2", "path": "/tmp", "health": "passing"})
        stats = await get_health_stats(db)
        assert stats["health_counts"]["passing"] == 2
        assert stats["health_counts"]["failing"] == 0

    @pytest.mark.asyncio
    async def test_health_counts_unknown_defaults(self, db):
        """Skills without explicit health should count as unknown."""
        await upsert_skill(db, {"name": "def1", "path": "/tmp"})
        stats = await get_health_stats(db)
        assert stats["health_counts"]["unknown"] >= 1

    @pytest.mark.asyncio
    async def test_dep_summary_empty_when_no_deps(self, db, mock_skill_data):
        await upsert_skill(db, mock_skill_data)
        stats = await get_health_stats(db)
        assert stats["dep_summary"] == {}

    @pytest.mark.asyncio
    async def test_dep_summary_with_installed_flag(self, db, mock_skill_data):
        await upsert_skill(db, mock_skill_data)
        await upsert_dependency(db, "test-skill", "fastapi", "pip", 1)
        await upsert_dependency(db, "test-skill", "requests", "pip", 0)
        stats = await get_health_stats(db)
        deps = stats["dep_summary"]["test-skill"]
        installed = [d for d in deps if d["installed"]]
        not_installed = [d for d in deps if not d["installed"]]
        assert len(installed) == 1
        assert len(not_installed) == 1


class TestRecordTestRunEdgeCases:
    @pytest.mark.asyncio
    async def test_all_passed(self, db, mock_skill_data):
        await upsert_skill(db, mock_skill_data)
        result = {"skill_name": "test-skill", "status": "completed", "total_tests": 5, "passed": 5, "failed": 0, "errors": 0, "skipped": 0, "duration_seconds": 0.5, "output": "5 passed", "started_at": "2026-04-29", "finished_at": "2026-04-29"}
        run_id = await record_test_run(db, result)
        assert run_id > 0

    @pytest.mark.asyncio
    async def test_all_failed(self, db, mock_skill_data):
        await upsert_skill(db, mock_skill_data)
        result = {"skill_name": "test-skill", "status": "failed", "total_tests": 3, "passed": 0, "failed": 3, "errors": 0, "skipped": 0, "duration_seconds": 0.5, "output": "3 failed", "started_at": "2026-04-29", "finished_at": "2026-04-29"}
        run_id = await record_test_run(db, result)
        runs = await get_test_runs(db, "test-skill")
        assert runs[0]["failed"] == 3

    @pytest.mark.asyncio
    async def test_test_run_with_errors(self, db, mock_skill_data):
        await upsert_skill(db, mock_skill_data)
        result = {"skill_name": "test-skill", "status": "error", "total_tests": 5, "passed": 2, "failed": 1, "errors": 2, "skipped": 0, "duration_seconds": 1.0, "output": "", "started_at": "2026-04-29", "finished_at": "2026-04-29"}
        run_id = await record_test_run(db, result)
        runs = await get_test_runs(db, "test-skill")
        assert runs[0]["errors"] == 2


# --- Version history tests ---


class TestRecordVersion:
    @pytest.mark.asyncio
    async def test_record_version(self, db, mock_skill_data):
        await upsert_skill(db, mock_skill_data)
        vid = await record_version(db, "test-skill", "1.0.0")
        assert vid > 0

    @pytest.mark.asyncio
    async def test_record_multiple_versions(self, db, mock_skill_data):
        await upsert_skill(db, mock_skill_data)
        await record_version(db, "test-skill", "1.0.0")
        await record_version(db, "test-skill", "2.0.0")
        versions = await get_versions(db, "test-skill")
        assert len(versions) == 2

    @pytest.mark.asyncio
    async def test_version_has_version_and_date(self, db, mock_skill_data):
        await upsert_skill(db, mock_skill_data)
        await record_version(db, "test-skill", "1.0.0")
        versions = await get_versions(db, "test-skill")
        assert "version" in versions[0]
        assert "recorded_at" in versions[0]
        assert versions[0]["version"] == "1.0.0"


class TestGetVersions:
    @pytest.mark.asyncio
    async def test_no_versions(self, db, mock_skill_data):
        await upsert_skill(db, mock_skill_data)
        versions = await get_versions(db, "test-skill")
        assert versions == []

    @pytest.mark.asyncio
    async def test_versions_ordered_desc(self, db, mock_skill_data):
        await upsert_skill(db, mock_skill_data)
        await record_version(db, "test-skill", "1.0.0")
        await record_version(db, "test-skill", "2.0.0")
        versions = await get_versions(db, "test-skill")
        assert versions[0]["version"] == "2.0.0"

    @pytest.mark.asyncio
    async def test_versions_limit(self, db, mock_skill_data):
        await upsert_skill(db, mock_skill_data)
        for v in ["1.0", "2.0", "3.0", "4.0", "5.0"]:
            await record_version(db, "test-skill", v)
        versions = await get_versions(db, "test-skill", limit=3)
        assert len(versions) == 3

    @pytest.mark.asyncio
    async def test_versions_for_nonexistent_skill(self, db):
        versions = await get_versions(db, "no-such-skill")
        assert versions == []


class TestSyncSkillsVersionRecording:
    @pytest.mark.asyncio
    async def test_sync_records_version_change(self, db, mock_skill_data):
        """Sync should record version changes when version differs from DB."""
        await upsert_skill(db, mock_skill_data)  # version 1.0.0
        updated = dict(mock_skill_data, version="2.0.0")
        await sync_skills(db, [updated])
        versions = await get_versions(db, "test-skill")
        assert len(versions) == 1
        assert versions[0]["version"] == "2.0.0"

    @pytest.mark.asyncio
    async def test_sync_no_version_change_not_recorded(self, db, mock_skill_data):
        """Sync should NOT record version when version is unchanged."""
        await upsert_skill(db, mock_skill_data)  # version 1.0.0
        same = dict(mock_skill_data, version="1.0.0")
        await sync_skills(db, [same])
        versions = await get_versions(db, "test-skill")
        assert versions == []

    @pytest.mark.asyncio
    async def test_sync_new_skill_no_version_recorded(self, db):
        """New skill (not in DB) should NOT record a version history entry."""
        new_skill = {"name": "brand-new", "version": "1.0.0", "path": "/tmp/new"}
        await sync_skills(db, [new_skill])
        versions = await get_versions(db, "brand-new")
        assert versions == []


class TestDeleteSkill:
    @pytest.mark.asyncio
    async def test_delete_existing_skill(self, db, mock_skill_data):
        """delete_skill removes skill and all associated data."""
        await upsert_skill(db, mock_skill_data)
        await record_test_run(db, {"skill_name": "test-skill", "status": "completed", "total_tests": 5, "passed": 5, "failed": 0, "errors": 0, "skipped": 0, "duration_seconds": 1.0, "output": "", "started_at": "2026-01-01T00:00:00", "finished_at": "2026-01-01T00:00:01"})
        await upsert_dependency(db, "test-skill", "pytest", "pip", 1)
        await record_version(db, "test-skill", "1.0.0")
        result = await delete_skill(db, "test-skill")
        assert result is True
        assert await get_skill(db, "test-skill") is None
        assert await get_test_runs(db, "test-skill") == []
        assert await get_dependencies(db, "test-skill") == []
        assert await get_versions(db, "test-skill") == []

    @pytest.mark.asyncio
    async def test_delete_nonexistent_skill(self, db):
        """delete_skill returns False for nonexistent skill."""
        result = await delete_skill(db, "no-such-skill")
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_skill_removes_from_all_skills(self, db, mock_skill_data):
        """delete_skill removes skill from get_all_skills."""
        await upsert_skill(db, mock_skill_data)
        await delete_skill(db, "test-skill")
        all_skills = await get_all_skills(db)
        assert not any(s["name"] == "test-skill" for s in all_skills)

    @pytest.mark.asyncio
    async def test_delete_skill_cascades_to_test_runs(self, db, mock_skill_data):
        """delete_skill removes all associated test runs."""
        await upsert_skill(db, mock_skill_data)
        for i in range(3):
            await record_test_run(db, {"skill_name": "test-skill", "status": "completed", "total_tests": 5, "passed": 5, "failed": 0, "errors": 0, "skipped": 0, "duration_seconds": 1.0, "output": "", "started_at": "2026-01-01T00:00:0" + str(i), "finished_at": "2026-01-01T00:00:0" + str(i)})
        await delete_skill(db, "test-skill")
        runs = await get_test_runs(db, "test-skill")
        assert runs == []

    @pytest.mark.asyncio
    async def test_delete_skill_cascades_to_dependencies(self, db, mock_skill_data):
        """delete_skill removes all associated dependencies."""
        await upsert_skill(db, mock_skill_data)
        await upsert_dependency(db, "test-skill", "pytest", "pip", 1)
        await upsert_dependency(db, "test-skill", "curl", "brew", 1)
        await delete_skill(db, "test-skill")
        deps = await get_dependencies(db, "test-skill")
        assert deps == []

    @pytest.mark.asyncio
    async def test_delete_skill_cascades_to_versions(self, db, mock_skill_data):
        """delete_skill removes all associated version records."""
        await upsert_skill(db, mock_skill_data)
        await record_version(db, "test-skill", "1.0.0")
        await record_version(db, "test-skill", "2.0.0")
        await delete_skill(db, "test-skill")
        versions = await get_versions(db, "test-skill")
        assert versions == []

    @pytest.mark.asyncio
    async def test_delete_skill_does_not_affect_other_skills(self, db, mock_skill_data):
        """Deleting one skill does not affect other skills."""
        await upsert_skill(db, mock_skill_data)
        other = dict(mock_skill_data, name="other-skill", path="/tmp/other")
        await upsert_skill(db, other)
        await delete_skill(db, "test-skill")
        assert await get_skill(db, "other-skill") is not None


class TestDeleteTestRuns:
    @pytest.mark.asyncio
    async def test_delete_all_test_runs(self, db, mock_skill_data, mock_test_result):
        """delete_test_runs removes all test runs for a skill."""
        await upsert_skill(db, mock_skill_data)
        await record_test_run(db, mock_test_result)
        await record_test_run(db, mock_test_result)
        count = await delete_test_runs(db, "test-skill")
        assert count == 2
        assert await get_test_runs(db, "test-skill") == []

    @pytest.mark.asyncio
    async def test_delete_test_runs_zero_when_none(self, db, mock_skill_data):
        """delete_test_runs returns 0 when no test runs exist."""
        await upsert_skill(db, mock_skill_data)
        count = await delete_test_runs(db, "test-skill")
        assert count == 0

    @pytest.mark.asyncio
    async def test_delete_test_runs_does_not_affect_other_skill(self, db, mock_skill_data):
        """Deleting test runs for one skill doesn't affect another."""
        await upsert_skill(db, mock_skill_data)
        other = dict(mock_skill_data, name="other-skill", path="/tmp/other")
        await upsert_skill(db, other)
        await record_test_run(db, {"skill_name": "test-skill", "status": "completed", "total_tests": 1, "passed": 1, "failed": 0, "errors": 0, "skipped": 0, "duration_seconds": 0.5, "output": "", "started_at": "2026-01-01T00:00:00", "finished_at": "2026-01-01T00:00:01"})
        await record_test_run(db, {"skill_name": "other-skill", "status": "completed", "total_tests": 3, "passed": 3, "failed": 0, "errors": 0, "skipped": 0, "duration_seconds": 0.5, "output": "", "started_at": "2026-01-01T00:00:00", "finished_at": "2026-01-01T00:00:01"})
        count = await delete_test_runs(db, "test-skill")
        assert count == 1
        assert await get_test_runs(db, "other-skill") != []

    @pytest.mark.asyncio
    async def test_delete_test_runs_preserves_skill(self, db, mock_skill_data):
        """delete_test_runs does not remove the skill itself."""
        await upsert_skill(db, mock_skill_data)
        await delete_test_runs(db, "test-skill")
        assert await get_skill(db, "test-skill") is not None


class TestGetRecentTestRuns:
    @pytest.mark.asyncio
    async def test_empty_when_no_runs(self, db):
        """get_recent_test_runs returns empty list when no test runs exist."""
        runs = await get_recent_test_runs(db)
        assert runs == []

    @pytest.mark.asyncio
    async def test_returns_recent_runs_across_skills(self, db, mock_skill_data):
        """get_recent_test_runs returns runs across multiple skills."""
        await upsert_skill(db, mock_skill_data)
        other = dict(mock_skill_data, name="other-skill", path="/tmp/other")
        await upsert_skill(db, other)
        await record_test_run(db, {"skill_name": "test-skill", "status": "completed", "total_tests": 10, "passed": 8, "failed": 2, "errors": 0, "skipped": 0, "duration_seconds": 1.5, "output": "", "started_at": "2026-04-29T10:00:00", "finished_at": "2026-04-29T10:00:02"})
        await record_test_run(db, {"skill_name": "other-skill", "status": "completed", "total_tests": 5, "passed": 5, "failed": 0, "errors": 0, "skipped": 0, "duration_seconds": 0.5, "output": "", "started_at": "2026-04-29T11:00:00", "finished_at": "2026-04-29T11:00:01"})
        runs = await get_recent_test_runs(db)
        assert len(runs) == 2
        # Most recent first
        assert runs[0]["skill_name"] == "other-skill"
        assert runs[1]["skill_name"] == "test-skill"

    @pytest.mark.asyncio
    async def test_respects_limit(self, db, mock_skill_data):
        """get_recent_test_runs respects the limit parameter."""
        await upsert_skill(db, mock_skill_data)
        for i in range(15):
            await record_test_run(db, {"skill_name": "test-skill", "status": "completed", "total_tests": 5, "passed": 5, "failed": 0, "errors": 0, "skipped": 0, "duration_seconds": 0.5, "output": "", "started_at": f"2026-04-29T10:00:{i:02d}", "finished_at": f"2026-04-29T10:00:{i+1:02d}"})
        runs = await get_recent_test_runs(db, limit=5)
        assert len(runs) == 5

    @pytest.mark.asyncio
    async def test_run_has_expected_fields(self, db, mock_skill_data):
        """Each recent run has all expected fields."""
        await upsert_skill(db, mock_skill_data)
        await record_test_run(db, {"skill_name": "test-skill", "status": "completed", "total_tests": 10, "passed": 8, "failed": 2, "errors": 0, "skipped": 0, "duration_seconds": 1.5, "output": "some output", "started_at": "2026-04-29T10:00:00", "finished_at": "2026-04-29T10:00:02"})
        runs = await get_recent_test_runs(db)
        run = runs[0]
        assert "id" in run
        assert "skill_name" in run
        assert "status" in run
        assert "total_tests" in run
        assert "passed" in run
        assert "failed" in run
        assert "errors" in run
        assert "skipped" in run
        assert "duration_seconds" in run
        assert "started_at" in run
        assert "finished_at" in run

    @pytest.mark.asyncio
    async def test_ordered_by_started_at_desc(self, db, mock_skill_data):
        """get_recent_test_runs returns runs ordered by started_at DESC."""
        await upsert_skill(db, mock_skill_data)
        await record_test_run(db, {"skill_name": "test-skill", "status": "completed", "total_tests": 5, "passed": 5, "failed": 0, "errors": 0, "skipped": 0, "duration_seconds": 0.5, "output": "", "started_at": "2026-04-29T08:00:00", "finished_at": "2026-04-29T08:00:01"})
        await record_test_run(db, {"skill_name": "test-skill", "status": "completed", "total_tests": 6, "passed": 5, "failed": 1, "errors": 0, "skipped": 0, "duration_seconds": 0.5, "output": "", "started_at": "2026-04-29T12:00:00", "finished_at": "2026-04-29T12:00:01"})
        runs = await get_recent_test_runs(db)
        assert runs[0]["started_at"] == "2026-04-29T12:00:00"
        assert runs[1]["started_at"] == "2026-04-29T08:00:00"

    @pytest.mark.asyncio
    async def test_default_limit_is_10(self, db, mock_skill_data):
        """Default limit is 10 when not specified."""
        await upsert_skill(db, mock_skill_data)
        for i in range(12):
            await record_test_run(db, {"skill_name": "test-skill", "status": "completed", "total_tests": 1, "passed": 1, "failed": 0, "errors": 0, "skipped": 0, "duration_seconds": 0.1, "output": "", "started_at": f"2026-04-29T10:{i:02d}:00", "finished_at": f"2026-04-29T10:{i:02d}:01"})
        runs = await get_recent_test_runs(db)
        assert len(runs) == 10


# --- _row_to_skill tests ---


class TestRowToSkill:
    """Direct unit tests for _row_to_skill helper."""

    def test_converts_all_fields(self):
        row = ("my-skill", "1.0.0", "A skill desc", "core", "core", "/path", '["run.sh"]', '["mod.py"]', "quinn", "passing", "2026-01-01", "2026-04-01")
        result = _row_to_skill(row)
        assert result["name"] == "my-skill"
        assert result["version"] == "1.0.0"
        assert result["description"] == "A skill desc"
        assert result["layer"] == "core"
        assert result["scripts"] == ["run.sh"]
        assert result["modules"] == ["mod.py"]
        assert result["author"] == "quinn"
        assert result["health"] == "passing"

    def test_deserializes_scripts_json(self):
        row = ("s", "0.0.0", "", "core", "core", "/p", '["a.sh","b.sh"]', '[]', "", "unknown", "", "")
        result = _row_to_skill(row)
        assert result["scripts"] == ["a.sh", "b.sh"]

    def test_deserializes_empty_modules_json(self):
        row = ("s", "0.0.0", "", "core", "core", "/p", '[]', '[]', "", "unknown", "", "")
        result = _row_to_skill(row)
        assert result["modules"] == []

    def test_preserves_all_12_fields(self):
        row = ("n", "v", "d", "l", "c", "/p", '[]', '[]', "a", "h", "da", "ua")
        result = _row_to_skill(row)
        assert len(result) == 12

    def test_json_roundtrip_for_scripts(self):
        import json
        scripts = ["fetch.sh", "search.sh", "convert.sh"]
        row = ("s", "0.0.0", "", "core", "core", "/p", json.dumps(scripts), '[]', "", "unknown", "", "")
        result = _row_to_skill(row)
        assert result["scripts"] == scripts


# --- _row_to_test_run tests ---


class TestRowToTestRun:
    """Direct unit tests for _row_to_test_run helper."""

    def test_converts_all_fields(self):
        row = (1, "my-skill", "completed", 10, 8, 1, 0, 1, 1.5, "output text", "2026-04-29T08:00", "2026-04-29T08:01")
        result = _row_to_test_run(row)
        assert result["id"] == 1
        assert result["skill_name"] == "my-skill"
        assert result["status"] == "completed"
        assert result["total_tests"] == 10
        assert result["passed"] == 8
        assert result["failed"] == 1
        assert result["duration_seconds"] == 1.5

    def test_preserves_all_12_fields(self):
        row = (0, "n", "s", 0, 0, 0, 0, 0, 0.0, "o", "sa", "fa")
        result = _row_to_test_run(row)
        assert len(result) == 12

    def test_failed_and_errors_fields(self):
        row = (1, "s", "failed", 5, 2, 2, 1, 0, 3.0, "", "", "")
        result = _row_to_test_run(row)
        assert result["failed"] == 2
        assert result["errors"] == 1
        assert result["status"] == "failed"

    def test_skipped_field(self):
        row = (1, "s", "completed", 10, 7, 0, 0, 3, 0.5, "", "", "")
        result = _row_to_test_run(row)
        assert result["skipped"] == 3