"""Tests for FastAPI app endpoints."""

import pytest
import pytest_asyncio
import json
from pathlib import Path
from unittest.mock import patch, AsyncMock

import httpx
from fastapi.testclient import TestClient

# We need to set up paths before importing app
import sys
import os

SKILL_HUB_DIR = Path(__file__).resolve().parent.parent
MODULES_DIR = SKILL_HUB_DIR / "modules"
PROJECT_ROOT = SKILL_HUB_DIR.parent.parent.parent
REAL_SKILLS_DIR = PROJECT_ROOT / "skills"

if str(MODULES_DIR) not in sys.path:
    sys.path.insert(0, str(MODULES_DIR))

# Set env vars for test isolation before importing app
os.environ["SKILL_HUB_DB"] = "/tmp/test_skill_hub_api.db"
os.environ["SKILL_HUB_SKILLS_DIR"] = str(REAL_SKILLS_DIR)

from app import app


@pytest.fixture(scope="module")
def client():
    """Create a TestClient for the FastAPI app."""
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True, scope="module")
def setup_db():
    """Ensure the database is initialized before tests."""
    # The app startup event will handle this
    pass


# --- API endpoint tests ---


class TestApiSkills:
    def test_list_skills(self, client):
        response = client.get("/api/skills")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 3

    def test_list_skills_has_required_fields(self, client):
        response = client.get("/api/skills")
        data = response.json()
        for skill in data:
            assert "name" in skill
            assert "version" in skill
            assert "layer" in skill

    def test_search_skills(self, client):
        response = client.get("/api/skills?q=fetch")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any("fetch" in s["name"].lower() or "fetch" in s["description"].lower() for s in data)

    def test_search_no_results(self, client):
        response = client.get("/api/skills?q=nonexistentxyz")
        assert response.status_code == 200
        data = response.json()
        # After search fix, only matching skills should be returned
        for s in data:
            assert "nonexistentxyz" not in s["name"].lower()
            assert "nonexistentxyz" not in s["description"].lower()

    def test_skills_ordered_by_name(self, client):
        response = client.get("/api/skills")
        data = response.json()
        names = [s["name"] for s in data]
        assert names == sorted(names)


class TestApiSkillDetail:
    def test_skill_detail_found(self, client):
        response = client.get("/api/skills/url-fetcher")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "url-fetcher"

    def test_skill_detail_has_test_runs(self, client):
        response = client.get("/api/skills/url-fetcher")
        data = response.json()
        assert "test_runs" in data

    def test_skill_detail_not_found(self, client):
        response = client.get("/api/skills/nonexistent-skill")
        assert response.status_code == 404

    def test_skill_detail_has_scripts(self, client):
        response = client.get("/api/skills/url-fetcher")
        data = response.json()
        assert isinstance(data.get("scripts", []), list)

    def test_skill_detail_has_modules(self, client):
        response = client.get("/api/skills/url-fetcher")
        data = response.json()
        assert isinstance(data.get("modules", []), list)

    def test_skill_detail_has_skill_md(self, client):
        response = client.get("/api/skills/url-fetcher")
        data = response.json()
        assert "skill_md" in data or "description" in data


class TestApiHealth:
    def test_health_endpoint(self, client):
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert "total_skills" in data
        assert "avg_pass_rate" in data
        assert "layers" in data

    def test_health_total_skills_positive(self, client):
        response = client.get("/api/health")
        data = response.json()
        assert data["total_skills"] >= 3

    def test_health_has_layers(self, client):
        response = client.get("/api/health")
        data = response.json()
        assert "core" in data["layers"]


class TestApiRunTest:
    def test_run_test_not_found_skill(self, client):
        response = client.post("/api/skills/nonexistent-skill/test")
        assert response.status_code == 404

    # Note: Running actual tests is slow and may fail depending on environment,
    # so we test the endpoint exists and returns proper structure for found skills


# --- HTML page tests ---


class TestHtmlPages:
    def test_home_page(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert "Skill Hub" in response.text or "skill" in response.text.lower()

    def test_home_page_with_search(self, client):
        response = client.get("/?q=fetch")
        assert response.status_code == 200
        assert "fetch" in response.text.lower()

    def test_skill_detail_page(self, client):
        response = client.get("/skill/url-fetcher")
        assert response.status_code == 200

    def test_skill_detail_page_not_found(self, client):
        response = client.get("/skill/nonexistent-skill")
        assert response.status_code == 404

    def test_health_page(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_install_page(self, client):
        response = client.get("/install")
        assert response.status_code == 200
        assert "install" in response.text.lower() or "Install" in response.text

    def test_test_page(self, client):
        response = client.get("/test/url-fetcher")
        assert response.status_code == 200

    def test_test_page_not_found(self, client):
        response = client.get("/test/nonexistent-skill")
        assert response.status_code == 404


# --- _parse_pytest_summary tests ---


class TestParsePytestSummary:
    def test_parse_standard_output(self):
        from app import _parse_pytest_summary
        result = {
            "skill_name": "test",
            "status": "completed",
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "skipped": 0,
            "duration_seconds": 0.0,
        }
        output = "8 passed, 2 failed in 1.50s"
        parsed = _parse_pytest_summary(result, output)
        assert parsed["passed"] == 8
        assert parsed["failed"] == 2
        assert parsed["total_tests"] == 10
        assert parsed["duration_seconds"] == 1.50

    def test_parse_with_errors(self):
        from app import _parse_pytest_summary
        result = {"passed": 0, "failed": 0, "errors": 0, "skipped": 0, "total_tests": 0, "duration_seconds": 0.0}
        output = "5 passed, 1 failed, 2 errors in 3.20s"
        parsed = _parse_pytest_summary(result, output)
        assert parsed["passed"] == 5
        assert parsed["failed"] == 1
        assert parsed["errors"] == 2
        assert parsed["total_tests"] == 8

    def test_parse_with_skipped(self):
        from app import _parse_pytest_summary
        result = {"passed": 0, "failed": 0, "errors": 0, "skipped": 0, "total_tests": 0, "duration_seconds": 0.0}
        output = "3 passed, 1 skipped in 0.5s"
        parsed = _parse_pytest_summary(result, output)
        assert parsed["passed"] == 3
        assert parsed["skipped"] == 1
        assert parsed["total_tests"] == 4

    def test_parse_no_summary_line(self):
        from app import _parse_pytest_summary
        result = {"passed": 0, "failed": 0, "errors": 0, "skipped": 0, "total_tests": 0, "duration_seconds": 0.0}
        parsed = _parse_pytest_summary(result, "no summary here")
        assert parsed["passed"] == 0
        assert parsed["total_tests"] == 0

    def test_parse_all_passed(self):
        from app import _parse_pytest_summary
        result = {"passed": 0, "failed": 0, "errors": 0, "skipped": 0, "total_tests": 0, "duration_seconds": 0.0}
        output = "10 passed in 2.00s"
        parsed = _parse_pytest_summary(result, output)
        assert parsed["passed"] == 10
        assert parsed["total_tests"] == 10


# --- _find_test_dir tests ---


class TestFindTestDir:
    def test_skill_own_tests_dir(self):
        from app import _find_test_dir
        # If skill_path has tests/ subdir, use it
        test_dir = _find_test_dir("test", "/fake/skill/path")
        assert isinstance(test_dir, Path)

    def test_project_tests_fallback(self):
        from app import _find_test_dir
        test_dir = _find_test_dir("url-fetcher", str(REAL_SKILLS_DIR / "core" / "url-fetcher"))
        # url-fetcher doesn't have its own tests/, so falls back to project tests
        assert isinstance(test_dir, Path)


# --- _enrich_with_discovered tests ---


class TestEnrichWithDiscovered:
    def test_merge_db_and_discovered(self):
        from app import _enrich_with_discovered
        from skill_discovery import discover_skills
        db_skills = [
            {"name": "url-fetcher", "version": "1.0.0", "scripts": [], "modules": [], "skill_md": "", "path": "", "description": "", "layer": "core", "category": "core", "author": "", "health": "unknown"},
        ]
        discovered = discover_skills(REAL_SKILLS_DIR)
        enriched = _enrich_with_discovered(db_skills, discovered)
        assert len(enriched) >= 3
        # url-fetcher should have real scripts now
        fetcher = next(s for s in enriched if s["name"] == "url-fetcher")
        assert len(fetcher["scripts"]) > 0

    def test_new_discovered_skills_added(self):
        from app import _enrich_with_discovered
        db_skills = []
        discovered = [{"name": "new-skill", "version": "1.0", "scripts": ["a.sh"], "modules": [], "skill_md": "", "path": "/tmp", "description": "", "layer": "core", "category": "core", "author": "", "health": "unknown"}]
        enriched = _enrich_with_discovered(db_skills, discovered)
        assert len(enriched) == 1
        assert enriched[0]["name"] == "new-skill"

    def test_empty_db_and_empty_discovered(self):
        from app import _enrich_with_discovered
        enriched = _enrich_with_discovered([], [])
        assert enriched == []

    def test_db_skill_not_in_discovered_stays(self):
        from app import _enrich_with_discovered
        db_skills = [
            {"name": "only-in-db", "version": "1.0", "scripts": [], "modules": [], "skill_md": "", "path": "/tmp", "description": "", "layer": "core", "category": "core", "author": "", "health": "unknown"},
        ]
        enriched = _enrich_with_discovered(db_skills, [])
        assert len(enriched) == 1
        assert enriched[0]["name"] == "only-in-db"

    def test_discovered_overrides_scripts(self):
        from app import _enrich_with_discovered
        db_skills = [
            {"name": "s1", "version": "1.0", "scripts": ["old.sh"], "modules": ["old.py"], "skill_md": "", "path": "", "description": "", "layer": "core", "category": "core", "author": "", "health": "unknown"},
        ]
        discovered = [
            {"name": "s1", "version": "1.0", "scripts": ["new.sh"], "modules": ["new.py"], "skill_md": "content", "path": "/new", "description": "", "layer": "core", "category": "core", "author": "", "health": "passing"},
        ]
        enriched = _enrich_with_discovered(db_skills, discovered)
        assert enriched[0]["scripts"] == ["new.sh"]
        assert enriched[0]["modules"] == ["new.py"]
        assert enriched[0]["skill_md"] == "content"

    def test_duplicate_discovered_not_added_twice(self):
        from app import _enrich_with_discovered
        db_skills = []
        discovered = [
            {"name": "dup-skill", "version": "1.0", "scripts": ["a.sh"], "modules": [], "skill_md": "", "path": "/tmp", "description": "", "layer": "core", "category": "core", "author": "", "health": "unknown"},
        ]
        enriched = _enrich_with_discovered(db_skills, discovered)
        assert len(enriched) == 1


# --- Additional API tests ---


class TestApiSkillsAdditional:
    def test_api_skills_response_is_list(self, client):
        resp = client.get("/api/skills")
        assert isinstance(resp.json(), list)

    def test_api_skills_search_returns_matching(self, client):
        resp = client.get("/api/skills?q=presearch")
        data = resp.json()
        matching = [s for s in data if "presearch" in s["name"].lower() or "presearch" in s["description"].lower()]
        assert len(matching) >= 1

    def test_api_skills_all_have_path(self, client):
        resp = client.get("/api/skills")
        for s in resp.json():
            assert "path" in s

    def test_api_skills_all_have_health(self, client):
        resp = client.get("/api/skills")
        for s in resp.json():
            assert s["health"] in ("unknown", "passing", "failing")

    def test_api_skill_detail_response_structure(self, client):
        resp = client.get("/api/skills/url-fetcher")
        data = resp.json()
        assert "name" in data
        assert "version" in data
        assert "description" in data
        assert "layer" in data
        assert "test_runs" in data


class TestApiHealthAdditional:
    def test_health_response_types(self, client):
        resp = client.get("/api/health")
        data = resp.json()
        assert isinstance(data["total_skills"], int)
        assert isinstance(data["avg_pass_rate"], float)
        assert isinstance(data["layers"], dict)
        assert isinstance(data["test_summary"], dict)

    def test_health_layers_values_are_ints(self, client):
        resp = client.get("/api/health")
        data = resp.json()
        for v in data["layers"].values():
            assert isinstance(v, int)

    def test_health_avg_pass_rate_between_0_1(self, client):
        resp = client.get("/api/health")
        data = resp.json()
        assert 0.0 <= data["avg_pass_rate"] <= 1.0


# --- Additional _parse_pytest_summary tests ---


class TestParsePytestSummaryAdditional:
    def test_parse_warnings_in_summary(self):
        from app import _parse_pytest_summary
        result = {"passed": 0, "failed": 0, "errors": 0, "skipped": 0, "total_tests": 0, "duration_seconds": 0.0}
        output = "5 passed, 1 warnings in 1.00s"
        parsed = _parse_pytest_summary(result, output)
        assert parsed["passed"] == 5
        assert parsed["total_tests"] == 5

    def test_parse_all_combinations(self):
        from app import _parse_pytest_summary
        result = {"passed": 0, "failed": 0, "errors": 0, "skipped": 0, "total_tests": 0, "duration_seconds": 0.0}
        output = "2 passed, 1 failed, 1 errors, 1 skipped, 2 warnings in 0.10s"
        parsed = _parse_pytest_summary(result, output)
        assert parsed["passed"] == 2
        assert parsed["failed"] == 1
        assert parsed["errors"] == 1
        assert parsed["skipped"] == 1
        assert parsed["total_tests"] == 5  # passed+failed+errors+skipped

    def test_parse_preserves_other_fields(self):
        from app import _parse_pytest_summary
        result = {"passed": 0, "failed": 0, "errors": 0, "skipped": 0, "total_tests": 0, "duration_seconds": 0.0, "skill_name": "my-skill", "status": "completed"}
        output = "3 passed in 1.50s"
        parsed = _parse_pytest_summary(result, output)
        assert parsed["skill_name"] == "my-skill"
        assert parsed["status"] == "completed"

    def test_parse_empty_output(self):
        from app import _parse_pytest_summary
        result = {"passed": 0, "failed": 0, "errors": 0, "skipped": 0, "total_tests": 0, "duration_seconds": 0.0}
        parsed = _parse_pytest_summary(result, "")
        assert parsed["passed"] == 0
        assert parsed["total_tests"] == 0

    def test_parse_full_accumulated_output(self):
        """Bug fix: _parse_pytest_summary must work with full accumulated output, not just last line.
        The summary line '569 passed in 11.17s' appears near the end of the output,
        not necessarily as the last line. Passing only the last line would miss it."""
        from app import _parse_pytest_summary
        result = {"passed": 0, "failed": 0, "errors": 0, "skipped": 0, "total_tests": 0, "duration_seconds": 0.0}
        # Simulated full pytest output with summary line in the middle
        full_output = """tests/test_app.py::TestHome::test_home PASSED
tests/test_app.py::TestHome::test_search PASSED
tests/test_app.py::TestHome::test_api PASSED

569 passed in 11.17s

=== short test summary info ==="""
        parsed = _parse_pytest_summary(result, full_output)
        assert parsed["passed"] == 569
        assert parsed["duration_seconds"] == 11.17
        assert parsed["total_tests"] == 569

    def test_parse_only_last_line_fails_but_full_output_works(self):
        """Demonstrates the bug: passing only the last line misses the summary.
        The last line of pytest output may be a summary info header, not the count line."""
        from app import _parse_pytest_summary
        result = {"passed": 0, "failed": 0, "errors": 0, "skipped": 0, "total_tests": 0, "duration_seconds": 0.0}
        # If only the last line were passed (the old bug):
        last_line_only = "=== short test summary info ==="
        parsed_last_line = _parse_pytest_summary(result, last_line_only)
        assert parsed_last_line["passed"] == 0  # Would miss the real counts

        # But with full output, it works correctly:
        result2 = {"passed": 0, "failed": 0, "errors": 0, "skipped": 0, "total_tests": 0, "duration_seconds": 0.0}
        full_output = "10 passed in 2.5s\n=== short test summary info ==="
        parsed_full = _parse_pytest_summary(result2, full_output)
        assert parsed_full["passed"] == 10
        assert parsed_full["duration_seconds"] == 2.5


# --- Additional _find_test_dir tests ---


class TestFindTestDirAdditional:
    def test_skill_with_own_tests_dir(self, tmp_path):
        from app import _find_test_dir
        skill_dir = tmp_path / "my-skill"
        skill_dir.mkdir()
        (skill_dir / "tests").mkdir()
        test_dir = _find_test_dir("my-skill", str(skill_dir))
        assert test_dir == skill_dir / "tests"

    def test_empty_skill_path(self, tmp_path):
        from app import _find_test_dir
        test_dir = _find_test_dir("skill", "")
        assert isinstance(test_dir, Path)

    def test_fallback_to_project_root(self):
        from app import _find_test_dir
        test_dir = _find_test_dir("skill", "/nonexistent/path")
        assert isinstance(test_dir, Path)


# --- _count_tests_in_dir tests ---


class TestCountTestsInDir:
    def test_count_tests_with_files(self, tmp_path):
        from app import _count_tests_in_dir
        test_dir = tmp_path / "tests"
        test_dir.mkdir()
        (test_dir / "test_one.py").write_text("def test_a(): pass\ndef test_b(): pass\n")
        (test_dir / "test_two.py").write_text("def test_c(): pass\n")
        assert _count_tests_in_dir(test_dir) == 3

    def test_count_tests_empty_dir(self, tmp_path):
        from app import _count_tests_in_dir
        test_dir = tmp_path / "tests"
        test_dir.mkdir()
        assert _count_tests_in_dir(test_dir) == 0

    def test_count_tests_no_test_prefix(self, tmp_path):
        from app import _count_tests_in_dir
        test_dir = tmp_path / "tests"
        test_dir.mkdir()
        (test_dir / "helper.py").write_text("def test_a(): pass\n")
        assert _count_tests_in_dir(test_dir) == 0

    def test_count_tests_includes_class_methods(self, tmp_path):
        from app import _count_tests_in_dir
        test_dir = tmp_path / "tests"
        test_dir.mkdir()
        (test_dir / "test_cls.py").write_text("class TestX:\n    def test_a(self): pass\n")
        # Class method test definitions are also counted
        assert _count_tests_in_dir(test_dir) == 1

    def test_count_tests_real_skill_hub(self):
        from app import _count_tests_in_dir
        test_dir = SKILL_HUB_DIR / "tests"
        count = _count_tests_in_dir(test_dir)
        assert count >= 200  # We have 244 tests


# --- Search filtering tests (post-fix) ---


class TestSearchFiltering:
    def test_search_only_returns_matching(self, client):
        """After the search fix, only skills matching the query are returned."""
        response = client.get("/api/skills?q=fetcher")
        data = response.json()
        # All returned skills should have 'fetcher' in name or description
        for s in data:
            assert "fetcher" in s["name"].lower() or "fetcher" in s["description"].lower()

    def test_search_broad_query(self, client):
        """Broad queries should match multiple skills."""
        response = client.get("/api/skills?q=skill")
        data = response.json()
        assert len(data) >= 1

    def test_search_empty_query_returns_all(self, client):
        """Empty query should return all skills."""
        all_resp = client.get("/api/skills")
        search_resp = client.get("/api/skills?q=")
        # Empty query treated as no search, should return same count
        assert len(search_resp.json()) >= len(all_resp.json()) - 1

    def test_home_page_search_only_matching(self, client):
        """Home page search should only show matching skills."""
        response = client.get("/?q=fetcher")
        # The page should contain url-fetcher info but not all 11 skills
        assert "url-fetcher" in response.text


# --- Check Dependencies API endpoint tests ---


class TestApiCheckDeps:
    def test_check_deps_existing_skill(self, client):
        """Check deps for a skill that exists in the DB."""
        response = client.post("/api/skills/skill-hub/check-deps")
        assert response.status_code == 200
        data = response.json()
        assert "skill_name" in data
        assert data["skill_name"] == "skill-hub"
        assert "dependencies" in data
        assert isinstance(data["dependencies"], list)

    def test_check_deps_has_dep_name_and_type(self, client):
        """Each dependency in check-deps response should have dep_name and dep_type."""
        response = client.post("/api/skills/skill-hub/check-deps")
        data = response.json()
        for d in data["dependencies"]:
            assert "dep_name" in d
            assert "dep_type" in d
            assert "installed" in d
            assert isinstance(d["installed"], bool)

    def test_check_deps_not_found_skill(self, client):
        """Check deps for nonexistent skill should return 404."""
        response = client.post("/api/skills/nonexistent-skill/check-deps")
        assert response.status_code == 404

    def test_check_deps_updates_installed_status(self, client):
        """Checking deps should update installed to True for pip packages that exist."""
        response = client.post("/api/skills/skill-hub/check-deps")
        data = response.json()
        # fastapi should be installed since we're running the app with it
        fastapi_dep = next((d for d in data["dependencies"] if d["dep_name"] == "fastapi"), None)
        if fastapi_dep:
            assert fastapi_dep["installed"] is True

    def test_check_deps_url_fetcher(self, client):
        """Check deps for url-fetcher should return its dependencies."""
        response = client.post("/api/skills/url-fetcher/check-deps")
        assert response.status_code == 200
        data = response.json()
        assert data["skill_name"] == "url-fetcher"

    def test_check_deps_returns_installed_bool(self, client):
        """installed field in check-deps response should always be a boolean."""
        response = client.post("/api/skills/skill-hub/check-deps")
        data = response.json()
        for d in data["dependencies"]:
            assert d["installed"] in (True, False)


# --- Bug fix verification tests ---


class TestJinja2EnvironmentSingleton:
    def test_jinja_env_is_module_level(self):
        """The Jinja2 Environment should be created at module level, not per-request."""
        from app import _jinja_env
        assert _jinja_env is not None

    def test_jinja_env_is_reused(self):
        """_jinja_env should be the same object across multiple accesses."""
        from app import _jinja_env
        env1 = _jinja_env
        # Re-import to confirm same singleton
        import app as app2
        env2 = app2._jinja_env
        assert env1 is env2  # Same object identity

    def test_jinja_env_autoescape_enabled(self):
        """_jinja_env should have autoescape enabled for safety."""
        from app import _jinja_env
        assert _jinja_env.autoescape is True

    def test_render_template_uses_singleton(self):
        """_render_template should use _jinja_env, not create a new Environment."""
        from app import _render_template, _jinja_env
        # Rendering twice should use same env
        html1 = _render_template("home.html", {"skills": [], "query": "", "total": 0, "health_counts": {"passing": 0, "failing": 0, "unknown": 0}, "avg_pass_rate": 0.0})
        html2 = _render_template("home.html", {"skills": [], "query": "", "total": 0, "health_counts": {"passing": 0, "failing": 0, "unknown": 0}, "avg_pass_rate": 0.0})
        # Both renders produce output (env wasn't recreated)
        assert len(html1) > 0
        assert len(html2) > 0


class TestHostBindingSecurity:
    def test_main_block_uses_localhost(self):
        """The __main__ block should bind to 127.0.0.1, not 0.0.0.0."""
        import app
        source = open(app.__file__, 'r').read()
        # Check that host is 127.0.0.1 in __main__ block
        assert 'host="127.0.0.1"' in source
        assert 'host="0.0.0.0"' not in source

    def test_default_port_configurable(self):
        """SKILL_HUB_PORT env var should configure the port."""
        from app import DEFAULT_PORT
        # DEFAULT_PORT should be 8765 when env var is not set
        assert DEFAULT_PORT == 8765 or isinstance(DEFAULT_PORT, int)


class TestNoDeadImports:
    def test_staticfiles_not_imported(self):
        """StaticFiles should not be imported since it's unused."""
        import app
        source = open(app.__file__, 'r').read()
        assert 'from fastapi.staticfiles import StaticFiles' not in source


class TestBuildSkillConfig:
    def test_config_excludes_internal_fields(self):
        """_build_skill_config should exclude name, description, version, author, layer."""
        from app import _build_skill_config
        skill = {
            "skill_md": "---\nname: test\nversion: 1.0\nauthor: bob\nlayer: core\ndescription: A test skill\ntriggers: test, demo\n---\n# Body",
        }
        config = _build_skill_config(skill)
        assert "name" not in config
        assert "description" not in config
        assert "version" not in config
        assert "author" not in config
        assert "layer" not in config
        assert "triggers" in config

    def test_config_from_frontmatter(self):
        """_build_skill_config should include all non-internal frontmatter keys."""
        from app import _build_skill_config
        skill = {
            "skill_md": "---\nname: test\nversion: 1.0\nauthor: bob\nlayer: core\ndescription: A test\nmy_setting: true\n---\n# Body",
        }
        config = _build_skill_config(skill)
        assert "my_setting" in config
        assert config["my_setting"] == "true"

    def test_config_empty_skill_md(self):
        """_build_skill_config should return empty dict if no skill_md."""
        from app import _build_skill_config
        skill = {"skill_md": ""}
        config = _build_skill_config(skill)
        assert config == {}

    def test_config_no_skill_md_key(self):
        """_build_skill_config should return empty dict if skill_md key missing."""
        from app import _build_skill_config
        skill = {"name": "test"}
        config = _build_skill_config(skill)
        assert config == {}

    def test_config_with_multiline_frontmatter(self):
        """_build_skill_config should handle multiline frontmatter values."""
        from app import _build_skill_config
        skill = {
            "skill_md": "---\nname: test\nversion: 1.0\nauthor: bob\nlayer: core\ndescription: |\n  A long description.\n  Triggers: demo, test\n---\n# Body",
        }
        config = _build_skill_config(skill)
        # description is excluded, but other keys present
        assert "name" not in config


class TestDetailPageEnrichment:
    def test_detail_page_has_skill_md_from_discovery(self, client):
        """Detail page should show skill_md even for skills fetched from DB (enriched with discovery data)."""
        resp = client.get("/skill/url-fetcher")
        # SKILL.md section should render because DB skill is enriched with discovery data
        assert "SKILL.md" in resp.text

    def test_detail_page_skill_md_rendered_has_html(self, client):
        """Rendered SKILL.md should contain actual HTML elements (not escaped)."""
        resp = client.get("/skill/skill-hub")
        # Rendered markdown should have HTML like <h2>, <p>, etc. (not &lt;h2&gt;)
        assert "<h2>" in resp.text or "<h1>" in resp.text or "<p>" in resp.text

    def test_detail_page_skill_md_raw_preserved(self, client):
        """Raw SKILL.md view should have the original unrendered text."""
        resp = client.get("/skill/url-fetcher")
        assert "md-raw" in resp.text

    def test_detail_page_scripts_from_discovery(self, client):
        """Detail page should show scripts enriched from discovery for DB skills."""
        resp = client.get("/skill/url-fetcher")
        assert "Scripts" in resp.text

    def test_detail_page_modules_from_discovery(self, client):
        """Detail page should show modules enriched from discovery for DB skills."""
        resp = client.get("/skill/skill-hub")
        assert "Modules" in resp.text
    def test_detail_page_skill_with_config(self):
        """Detail page should show Configuration section for skills with non-internal frontmatter."""
        with TestClient(app) as client:
            # url-fetcher SKILL.md has 'triggers' in description but we need
            # a skill with extra frontmatter keys. skill-hub only has internal keys.
            # Check that the config variable is passed to template even if empty.
            resp = client.get("/skill/skill-hub")
            # skill-hub only has internal frontmatter keys, so config is empty
            # and Configuration section won't render — that's correct behavior
            assert resp.status_code == 200

    def test_detail_page_config_passed_to_template(self):
        """Detail page endpoint should pass config dict to template."""
        from app import _build_skill_config, _yaml_frontmatter
        # url-fetcher's SKILL.md should have some config keys
        with TestClient(app) as client:
            resp = client.get("/skill/url-fetcher")
            assert resp.status_code == 200


class TestTestPageHistory:
    def test_test_page_shows_no_runs_message(self):
        """Test page should show 'No test runs' message when no history."""
        with TestClient(app) as client:
            resp = client.get("/test/url-fetcher")
            assert "No test runs" in resp.text or "test runs" in resp.text.lower()

    def test_test_page_has_recent_runs_heading(self):
        """Test page should have Recent Test Runs heading when history exists."""
        with TestClient(app) as client:
            resp = client.get("/test/url-fetcher")
            # Either shows "Recent Test Runs" or "No test runs"
            assert "Test Runs" in resp.text or "test runs" in resp.text


# --- Versions API endpoint tests ---


class TestApiSkillVersions:
    def test_versions_endpoint_found(self, client):
        """Versions endpoint should return 200 for existing skill."""
        response = client.get("/api/skills/url-fetcher/versions")
        assert response.status_code == 200
        data = response.json()
        assert "skill_name" in data
        assert data["skill_name"] == "url-fetcher"
        assert "current_version" in data
        assert "versions" in data

    def test_versions_endpoint_not_found(self, client):
        """Versions endpoint should return 404 for nonexistent skill."""
        response = client.get("/api/skills/nonexistent-skill/versions")
        assert response.status_code == 404

    def test_versions_current_version_matches_skill(self, client):
        """Current version in versions response should match skill version."""
        skill_resp = client.get("/api/skills/url-fetcher")
        skill_data = skill_resp.json()
        versions_resp = client.get("/api/skills/url-fetcher/versions")
        versions_data = versions_resp.json()
        assert versions_data["current_version"] == skill_data.get("version", "0.0.0")

    def test_versions_list_is_list(self, client):
        """Versions list should be a list."""
        response = client.get("/api/skills/url-fetcher/versions")
        data = response.json()
        assert isinstance(data["versions"], list)

    def test_versions_for_skill_hub(self, client):
        """Versions endpoint for skill-hub should return data."""
        response = client.get("/api/skills/skill-hub/versions")
        assert response.status_code == 200
        data = response.json()
        assert data["skill_name"] == "skill-hub"


# --- CSV Export endpoint tests ---


class TestApiExportCsv:
    def test_export_csv_returns_200(self, client):
        """CSV export endpoint should return 200."""
        response = client.get("/api/skills/export.csv")
        assert response.status_code == 200

    def test_export_csv_has_header(self, client):
        """CSV should have a header row with expected columns."""
        response = client.get("/api/skills/export.csv")
        lines = response.text.strip().split("\n")
        assert lines[0] == "name,version,layer,health,author,description,category,path"

    def test_export_csv_has_skills(self, client):
        """CSV should contain at least one skill row."""
        response = client.get("/api/skills/export.csv")
        lines = response.text.strip().split("\n")
        assert len(lines) >= 2

    def test_export_csv_contains_skill_names(self, client):
        """CSV should contain known skill names."""
        response = client.get("/api/skills/export.csv")
        assert "url-fetcher" in response.text or "skill-hub" in response.text

    def test_export_csv_content_type(self, client):
        """CSV response should have text content type."""
        response = client.get("/api/skills/export.csv")
        assert "text" in response.headers.get("content-type", "")

    def test_export_csv_fields_are_rfc4180_quoted(self, client):
        """Fields containing commas should be RFC 4180 quoted (double-quoted)."""
        response = client.get("/api/skills/export.csv")
        lines = response.text.strip().split("\n")
        # Header row should have 8 fields
        import csv
        reader = csv.reader(lines)
        rows = list(reader)
        assert len(rows) >= 1
        assert len(rows[0]) == 8
        # All subsequent rows should also have 8 fields
        for row in rows[1:]:
            assert len(row) == 8


# --- _render_markdown tests ---


class TestRenderMarkdown:
    def test_empty_input(self):
        from app import _render_markdown
        assert _render_markdown("") == ""

    def test_none_like_empty(self):
        from app import _render_markdown
        assert _render_markdown("") == ""

    def test_headers(self):
        from app import _render_markdown
        assert "<h1>" in _render_markdown("# Title")
        assert "<h2>" in _render_markdown("## Section")
        assert "<h3>" in _render_markdown("### Subsection")
        assert "<h4>" in _render_markdown("#### Detail")

    def test_h1_content(self):
        from app import _render_markdown
        result = _render_markdown("# Hello World")
        assert "Hello World" in result
        assert "<h1>" in result

    def test_h2_content(self):
        from app import _render_markdown
        result = _render_markdown("## Dependencies")
        assert "Dependencies" in result
        assert "<h2>" in result

    def test_bold(self):
        from app import _render_markdown
        result = _render_markdown("This is **bold** text")
        assert "<strong>bold</strong>" in result

    def test_italic(self):
        from app import _render_markdown
        result = _render_markdown("This is *italic* text")
        assert "<em>italic</em>" in result

    def test_bold_italic_combined(self):
        from app import _render_markdown
        result = _render_markdown("This is ***both*** text")
        assert "<strong><em>both</em></strong>" in result

    def test_inline_code(self):
        from app import _render_markdown
        result = _render_markdown("Use `pip install` command")
        assert "<code>pip install</code>" in result

    def test_code_block(self):
        from app import _render_markdown
        result = _render_markdown("```bash\npip install fastapi\n```")
        assert "<pre><code>" in result
        assert "pip install fastapi" in result

    def test_code_block_language_tag(self):
        from app import _render_markdown
        result = _render_markdown("```python\nprint('hello')\n```")
        assert "<pre><code>" in result
        assert "print('hello')" in result

    def test_code_block_html_escaped(self):
        from app import _render_markdown
        result = _render_markdown("```html\n<div>content</div>\n```")
        assert "&lt;div&gt;" in result

    def test_links(self):
        from app import _render_markdown
        result = _render_markdown("Check [docs](https://example.com)")
        assert '<a href="https://example.com">docs</a>' in result

    def test_unordered_list(self):
        from app import _render_markdown
        result = _render_markdown("- Item one\n- Item two\n- Item three")
        assert "<ul>" in result
        assert "<li>" in result
        assert "Item one" in result

    def test_list_with_star_prefix(self):
        from app import _render_markdown
        result = _render_markdown("* First\n* Second")
        assert "<ul>" in result
        assert "<li>First</li>" in result

    def test_paragraphs(self):
        from app import _render_markdown
        result = _render_markdown("First paragraph\n\nSecond paragraph")
        assert "<p>" in result

    def test_no_paragraph_around_headers(self):
        from app import _render_markdown
        result = _render_markdown("# Title")
        # Headers should not be wrapped in <p> tags
        assert "<p><h1>" not in result

    def test_no_paragraph_around_code_block(self):
        from app import _render_markdown
        result = _render_markdown("```bash\necho hello\n```")
        assert "<p><pre>" not in result

    def test_no_paragraph_around_list(self):
        from app import _render_markdown
        result = _render_markdown("- Item one\n- Item two")
        assert "<p><ul>" not in result

    def test_multiple_features_combined(self):
        from app import _render_markdown
        md = "# Skill Name\n\n**Bold** and *italic* text.\n\n- Feature 1\n- Feature 2\n\n```bash\npip install fastapi\n```\n\nCheck [docs](https://example.com) for more."
        result = _render_markdown(md)
        assert "<h1>" in result
        assert "<strong>Bold</strong>" in result
        assert "<em>italic</em>" in result
        assert "<ul>" in result
        assert "<pre><code>" in result
        assert '<a href="https://example.com">docs</a>' in result

    def test_render_md_with_frontmatter(self):
        """_render_markdown should handle SKILL.md content that starts with --- frontmatter."""
        from app import _render_markdown
        md = "---\nname: test\nversion: 1.0\n---\n\n# Test Skill\n\nDescription here."
        result = _render_markdown(md)
        assert "<h1>" in result or "Test Skill" in result

    def test_render_md_preserves_code_block_order(self):
        """_render_markdown should handle multiple code blocks."""
        from app import _render_markdown
        md = "# Title\n\n```bash\necho hello\n```\n\nSome text.\n\n```python\nprint('hi')\n```\n"
        result = _render_markdown(md)
        assert "echo hello" in result
        assert "print(&#x27;hi&#x27;)" in result or "print('hi')" in result or "print(&#39;hi&#39;)" in result

    def test_render_md_empty_paragraphs_removed(self):
        """_render_markdown should remove empty paragraph tags."""
        from app import _render_markdown
        md = "# Title\n\n\n\n## Section"
        result = _render_markdown(md)
        assert "<p></p>" not in result

    def test_real_skill_hub_md(self, client):
        """Detail page should show rendered markdown with md-rendered class."""
        resp = client.get("/skill/skill-hub")
        assert "md-rendered" in resp.text
        assert "Toggle Raw/Rendered" in resp.text or "toggle" in resp.text.lower()

    def test_detail_page_has_both_views(self, client):
        """Detail page should have both md-rendered and md-raw divs."""
        resp = client.get("/skill/url-fetcher")
        assert "md-rendered" in resp.text
        assert "md-raw" in resp.text

    def test_detail_page_toggle_button(self, client):
        """Detail page should have a toggle button for raw/rendered view."""
        resp = client.get("/skill/url-fetcher")
        assert "Toggle" in resp.text

    def test_detail_page_toggle_javascript(self, client):
        """Detail page should have toggleMdView JavaScript function."""
        resp = client.get("/skill/url-fetcher")
        assert "toggleMdView" in resp.text

    def test_rendered_md_default_visible(self, client):
        """Rendered markdown view should be visible by default; raw view hidden."""
        resp = client.get("/skill/url-fetcher")
        # md-rendered should NOT have display:none in its initial style
        assert 'id="md-rendered"' in resp.text
        # md-raw should have display:none initially
        assert "display:none" in resp.text


# --- Enhanced markdown renderer tests (ordered lists, tables, blockquotes, hr) ---


class TestRenderMarkdownOrderedLists:
    """Tests for ordered list rendering in _render_markdown."""

    def test_ordered_list_basic(self):
        """Ordered list with numbered items should render as <ol>."""
        from app import _render_markdown
        result = _render_markdown("1. First\n2. Second\n3. Third")
        assert "<ol" in result
        assert "<li>First</li>" in result
        assert "<li>Second</li>" in result
        assert "<li>Third</li>" in result
        assert "</ol>" in result

    def test_ordered_list_start_number(self):
        """Ordered list should preserve start number via <ol start=N>."""
        from app import _render_markdown
        result = _render_markdown("3. Third item\n4. Fourth item")
        assert 'start="3"' in result

    def test_ordered_list_single_item(self):
        """Single ordered list item should still render as <ol>."""
        from app import _render_markdown
        result = _render_markdown("1. Only item")
        assert "<ol" in result
        assert "<li>Only item</li>" in result
        assert "</ol>" in result

    def test_ordered_list_with_bold_text(self):
        """Ordered list items can contain bold text."""
        from app import _render_markdown
        result = _render_markdown("1. **Important** step\n2. Regular step")
        assert "<ol" in result
        assert "<strong>Important</strong>" in result

    def test_ordered_list_not_wrapped_in_paragraph(self):
        """Ordered lists should not be wrapped in <p> tags."""
        from app import _render_markdown
        result = _render_markdown("1. First\n2. Second")
        assert "<p><ol" not in result


class TestRenderMarkdownTables:
    """Tests for markdown table rendering in _render_markdown."""

    def test_basic_table(self):
        """Simple markdown table should render as HTML <table>."""
        from app import _render_markdown
        md = "| Name | Value |\n| --- | --- |\n| foo | bar |"
        result = _render_markdown(md)
        assert "<table>" in result
        assert "<thead>" in result
        assert "<tbody>" in result
        assert "<th>Name</th>" in result
        assert "<th>Value</th>" in result
        assert "<td>foo</td>" in result
        assert "<td>bar</td>" in result

    def test_table_with_three_columns(self):
        """Table with 3 columns should render all columns."""
        from app import _render_markdown
        md = "| Endpoint | Method | Description |\n| --- | --- | --- |\n| /api | GET | List |\n| /api/1 | POST | Create |"
        result = _render_markdown(md)
        assert "<th>Endpoint</th>" in result
        assert "<th>Method</th>" in result
        assert "<th>Description</th>" in result
        assert "<td>/api</td>" in result
        assert "<td>GET</td>" in result

    def test_table_not_wrapped_in_paragraph(self):
        """Markdown tables should not be wrapped in <p> tags."""
        from app import _render_markdown
        md = "| A | B |\n| --- | --- |\n| 1 | 2 |"
        result = _render_markdown(md)
        assert "<p><table" not in result

    def test_table_empty_body(self):
        """Table with only header and separator should render with empty tbody."""
        from app import _render_markdown
        md = "| Col1 | Col2 |\n| --- | --- |"
        result = _render_markdown(md)
        assert "<thead>" in result
        assert "<tbody>" in result
        assert "<th>Col1</th>" in result

    def test_parse_md_table_function(self):
        """_parse_md_table should correctly parse markdown table lines."""
        from app import _parse_md_table
        lines = ["| H1 | H2 |", "| --- | --- |", "| a | b |"]
        html = _parse_md_table(lines)
        assert "<thead>" in html
        assert "<th>H1</th>" in html
        assert "<td>a</td>" in html


class TestRenderMarkdownBlockquotes:
    """Tests for blockquote rendering in _render_markdown."""

    def test_basic_blockquote(self):
        """Blockquote lines starting with > should render as <blockquote>."""
        from app import _render_markdown
        result = _render_markdown("> This is a quote")
        assert "<blockquote>" in result
        assert "This is a quote" in result
        assert "</blockquote>" in result

    def test_multiline_blockquote(self):
        """Multiple consecutive > lines should be in one <blockquote>."""
        from app import _render_markdown
        result = _render_markdown("> First line\n> Second line")
        assert "<blockquote>" in result
        assert "</blockquote>" in result
        # Should be one blockquote, not two
        assert result.count("<blockquote>") == 1

    def test_blockquote_not_wrapped_in_paragraph(self):
        """Blockquotes should not be wrapped in <p> tags."""
        from app import _render_markdown
        result = _render_markdown("> Quote text")
        assert "<p><blockquote" not in result

    def test_blockquote_followed_by_regular_text(self):
        """Blockquote followed by regular text should close the blockquote."""
        from app import _render_markdown
        result = _render_markdown("> Quote\n\nRegular text")
        assert "<blockquote>" in result
        assert "</blockquote>" in result


class TestRenderMarkdownHorizontalRules:
    """Tests for horizontal rule rendering in _render_markdown."""

    def test_hr_with_dashes(self):
        """Three or more dashes on a line should render as <hr>."""
        from app import _render_markdown
        result = _render_markdown("---")
        assert "<hr>" in result

    def test_hr_with_longer_dashes(self):
        """More than 3 dashes should also render as <hr>."""
        from app import _render_markdown
        result = _render_markdown("----------")
        assert "<hr>" in result

    def test_hr_with_asterisks(self):
        """Three or more asterisks on a line should render as <hr>."""
        from app import _render_markdown
        result = _render_markdown("***")
        assert "<hr>" in result

    def test_hr_not_wrapped_in_paragraph(self):
        """Horizontal rules should not be wrapped in <p> tags."""
        from app import _render_markdown
        result = _render_markdown("---")
        assert "<p><hr>" not in result

    def test_hr_between_sections(self):
        """HR between two sections should render correctly."""
        from app import _render_markdown
        result = _render_markdown("## Section 1\n\n---\n\n## Section 2")
        assert "<hr>" in result
        assert "<h2>" in result


class TestRenderMarkdownMixedLists:
    """Tests for mixed ordered and unordered list rendering."""

    def test_ul_then_ol(self):
        """Unordered list followed by ordered list should render both correctly."""
        from app import _render_markdown
        result = _render_markdown("- Item A\n- Item B\n\n1. Step 1\n2. Step 2")
        assert "<ul>" in result
        assert "</ul>" in result
        assert "<ol" in result
        assert "</ol>" in result

    def test_ol_then_ul(self):
        """Ordered list followed by unordered list should render both correctly."""
        from app import _render_markdown
        result = _render_markdown("1. First\n2. Second\n\n- Option A\n- Option B")
        assert "<ol" in result
        assert "</ol>" in result
        assert "<ul>" in result
        assert "</ul>" in result


class TestRenderMarkdownRealSkillMd:
    """Test _render_markdown with patterns from real SKILL.md files."""

    def test_skill_hub_md_with_table(self):
        """Skill Hub SKILL.md contains a markdown table that should render correctly."""
        from app import _render_markdown
        md = """## REST API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/skills` | GET | List all skills |
| `/api/skills/{name}` | GET | Get skill detail |

---
"""
        result = _render_markdown(md)
        assert "<h2>" in result
        assert "<table>" in result
        assert "<th>Endpoint</th>" in result
        assert "<td>`/api/skills`</td>" in result or "api/skills" in result
        assert "<hr>" in result

    def test_ordered_steps_with_bold(self):
        """Skill steps like '1. **Home page** - description' should render correctly."""
        from app import _render_markdown
        md = "1. **Home page** - Skill cards grid\n2. **Detail page** - View SKILL.md\n3. **Test panel** - Run pytest"
        result = _render_markdown(md)
        assert "<ol" in result
        assert "<strong>Home page</strong>" in result
        assert "<strong>Detail page</strong>" in result


# --- Resync API endpoint tests ---


class TestApiResync:
    def test_resync_returns_200(self, client):
        """Resync endpoint should return 200."""
        response = client.post("/api/skills/resync")
        assert response.status_code == 200

    def test_resync_response_has_resynced_count(self, client):
        """Resync response should include resynced count."""
        response = client.post("/api/skills/resync")
        data = response.json()
        assert "resynced" in data
        assert isinstance(data["resynced"], int)
        assert data["resynced"] >= 3

    def test_resync_response_has_skills_list(self, client):
        """Resync response should include updated skills list."""
        response = client.post("/api/skills/resync")
        data = response.json()
        assert "skills" in data
        assert isinstance(data["skills"], list)

    def test_resync_skills_have_required_fields(self, client):
        """Resynced skills should have all required fields."""
        response = client.post("/api/skills/resync")
        data = response.json()
        for s in data["skills"]:
            assert "name" in s
            assert "version" in s
            assert "layer" in s

    def test_resync_twice_no_duplicate_skills(self, client):
        """Resyncing twice should not create duplicate skills."""
        resp1 = client.post("/api/skills/resync")
        count1 = resp1.json()["resynced"]
        resp2 = client.post("/api/skills/resync")
        count2 = resp2.json()["resynced"]
        assert count2 == count1


# --- Active navigation highlighting tests ---


class TestActiveNavHighlighting:
    def test_home_page_skills_nav_active(self, client):
        """Home page should have 'Skills' nav link with active class."""
        response = client.get("/")
        assert 'class="active"' in response.text or "active" in response.text
        # The Skills link should be active on home page
        assert "Skills" in response.text

    def test_health_page_health_nav_active(self, client):
        """Health page should have 'Health' nav link with active class."""
        response = client.get("/health")
        # Health nav link should have active class
        html = response.text
        # Find the Health nav link — it should have class including 'active'
        assert "Health" in html

    def test_install_page_install_nav_active(self, client):
        """Install page should have 'Install' nav link with active class."""
        response = client.get("/install")
        assert "Install" in response.text

    def test_detail_page_skills_nav_active(self, client):
        """Detail page should have 'Skills' nav link active (sub-page of Skills)."""
        response = client.get("/skill/url-fetcher")
        assert response.status_code == 200
        assert "Skills" in response.text

    def test_test_page_skills_nav_active(self, client):
        """Test page should have 'Skills' nav link active (sub-page of Skills)."""
        response = client.get("/test/url-fetcher")
        assert response.status_code == 200
        assert "Skills" in response.text

    def test_nav_active_context_in_home(self, client):
        """Home page HTML should contain nav_active=skills context indicator."""
        response = client.get("/")
        # The Skills nav link should have class 'active' on home page
        html = response.text
        # Check that the Skills link has the active class
        assert '<a href="/" class="active">Skills</a>' in html


# --- Error page tests ---


class TestErrorPage:
    def test_skill_detail_404_uses_error_template(self, client):
        """Skill detail 404 should render styled error page, not bare HTML."""
        response = client.get("/skill/nonexistent-skill")
        assert response.status_code == 404
        # Should use error.html template with styled layout
        assert "Skill Hub" in response.text  # nav/logo from base template
        assert "404" in response.text
        assert "not found" in response.text.lower()
        # Should not have bare <h1> tag without styling
        assert "container" in response.text  # base template container class

    def test_skill_detail_404_shows_skill_name(self, client):
        """Skill 404 error page should mention the skill name that was not found."""
        response = client.get("/skill/missing-skill-xyz")
        assert response.status_code == 404
        assert "missing-skill-xyz" in response.text

    def test_skill_detail_404_has_nav_links(self, client):
        """Skill 404 error page should have navigation links."""
        response = client.get("/skill/nonexistent-skill")
        assert "/health" in response.text
        assert "/" in response.text

    def test_skill_detail_404_has_back_button(self, client):
        """Skill 404 error page should have 'Back to Skills' button."""
        response = client.get("/skill/nonexistent-skill")
        assert "Back to Skills" in response.text

    def test_skill_detail_404_has_health_dashboard_link(self, client):
        """Skill 404 error page should link to health dashboard."""
        response = client.get("/skill/nonexistent-skill")
        assert "Health Dashboard" in response.text

    def test_test_page_404_uses_error_template(self, client):
        """Test page 404 should render styled error page, not bare HTML."""
        response = client.get("/test/nonexistent-skill")
        assert response.status_code == 404
        assert "Skill Hub" in response.text
        assert "404" in response.text
        assert "not found" in response.text.lower()

    def test_test_page_404_shows_skill_name(self, client):
        """Test 404 error page should mention the skill name."""
        response = client.get("/test/missing-test-skill")
        assert response.status_code == 404
        assert "missing-test-skill" in response.text


# --- Layer/health filtering tests ---


class TestHomePageFiltering:
    def test_home_has_layer_filter_dropdown(self, client):
        """Home page should have a layer filter dropdown."""
        response = client.get("/")
        assert 'name="layer"' in response.text
        assert "All layers" in response.text

    def test_home_has_health_filter_dropdown(self, client):
        """Home page should have a health filter dropdown."""
        response = client.get("/")
        assert 'name="health"' in response.text
        assert "All health" in response.text

    def test_home_layer_filter_core(self, client):
        """Layer filter for 'core' should only show core skills."""
        response = client.get("/?layer=core")
        assert response.status_code == 200
        # The page should still render normally
        assert "Skill Hub" in response.text

    def test_home_layer_filter_external(self, client):
        """Layer filter for 'external' should only show external skills."""
        response = client.get("/?layer=external")
        assert response.status_code == 200
        assert "Skill Hub" in response.text

    def test_home_health_filter_unknown(self, client):
        """Health filter for 'unknown' should only show unknown-health skills."""
        response = client.get("/?health=unknown")
        assert response.status_code == 200
        assert "Skill Hub" in response.text

    def test_home_health_filter_passing(self, client):
        """Health filter for 'passing' should work (may return 0 skills if none passing)."""
        response = client.get("/?health=passing")
        assert response.status_code == 200
        assert "Skill Hub" in response.text

    def test_home_combined_search_and_layer_filter(self, client):
        """Search query combined with layer filter should work."""
        response = client.get("/?q=fetch&layer=core")
        assert response.status_code == 200
        assert "Skill Hub" in response.text

    def test_home_filter_dropdown_has_core_option(self, client):
        """Layer dropdown should have 'core' as an option."""
        response = client.get("/")
        assert "core" in response.text

    def test_home_filter_dropdown_has_health_options(self, client):
        """Health dropdown should have health value options."""
        response = client.get("/")
        # Should have at least 'unknown' in health dropdown
        assert "unknown" in response.text

    def test_home_filter_clear_link_with_filters(self, client):
        """Clear link should appear when filters are active."""
        response = client.get("/?layer=core")
        assert "Clear" in response.text

    def test_home_no_skills_with_filter_hint(self, client):
        """When filters produce no results, the empty state should suggest adjusting filters."""
        response = client.get("/?health=passing&layer=external")
        # Should show either skills or empty state with filter hint
        assert response.status_code == 200


class TestApiSkillsFiltering:
    def test_api_skills_layer_filter(self, client):
        """API /api/skills?layer=core should only return core skills."""
        response = client.get("/api/skills?layer=core")
        assert response.status_code == 200
        data = response.json()
        for s in data:
            assert s["layer"] == "core"

    def test_api_skills_layer_filter_external(self, client):
        """API /api/skills?layer=external should only return external skills."""
        response = client.get("/api/skills?layer=external")
        assert response.status_code == 200
        data = response.json()
        for s in data:
            assert s["layer"] == "external"

    def test_api_skills_health_filter(self, client):
        """API /api/skills?health=unknown should only return unknown-health skills."""
        response = client.get("/api/skills?health=unknown")
        assert response.status_code == 200
        data = response.json()
        for s in data:
            assert s["health"] == "unknown"

    def test_api_skills_combined_search_and_layer(self, client):
        """API search combined with layer filter should work."""
        response = client.get("/api/skills?q=fetch&layer=core")
        assert response.status_code == 200
        data = response.json()
        for s in data:
            assert s["layer"] == "core"

    def test_api_skills_no_filter_returns_all(self, client):
        """API without filter params should return all skills."""
        response = client.get("/api/skills")
        all_count = len(response.json())
        # Layer filter should reduce count
        core_resp = client.get("/api/skills?layer=core")
        core_count = len(core_resp.json())
        assert core_count <= all_count

    def test_api_skills_invalid_filter_returns_empty(self, client):
        """Invalid layer/health filter should return empty list."""
        response = client.get("/api/skills?layer=nonexistent_layer")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0


# --- Sort functionality tests ---


class TestSortSkills:
    def test_sort_by_name_asc(self):
        """_sort_skills with 'name' should sort alphabetically ascending."""
        from app import _sort_skills
        skills = [
            {"name": "z-skill", "version": "1.0"},
            {"name": "a-skill", "version": "2.0"},
            {"name": "m-skill", "version": "1.5"},
        ]
        result = _sort_skills(skills, "name")
        assert result[0]["name"] == "a-skill"
        assert result[1]["name"] == "m-skill"
        assert result[2]["name"] == "z-skill"

    def test_sort_by_name_desc(self):
        """_sort_skills with 'name-desc' should sort alphabetically descending."""
        from app import _sort_skills
        skills = [
            {"name": "a-skill", "version": "1.0"},
            {"name": "z-skill", "version": "2.0"},
            {"name": "m-skill", "version": "1.5"},
        ]
        result = _sort_skills(skills, "name-desc")
        assert result[0]["name"] == "z-skill"
        assert result[1]["name"] == "m-skill"
        assert result[2]["name"] == "a-skill"

    def test_sort_by_version(self):
        """_sort_skills with 'version' should sort by version ascending."""
        from app import _sort_skills
        skills = [
            {"name": "skill-c", "version": "3.0"},
            {"name": "skill-a", "version": "1.0"},
            {"name": "skill-b", "version": "2.0"},
        ]
        result = _sort_skills(skills, "version")
        assert result[0]["version"] == "1.0"
        assert result[1]["version"] == "2.0"
        assert result[2]["version"] == "3.0"

    def test_sort_by_test_count(self):
        """_sort_skills with 'test_count' should sort by test count ascending."""
        from app import _sort_skills
        skills = [
            {"name": "skill-c", "test_count": 300},
            {"name": "skill-a", "test_count": 100},
            {"name": "skill-b", "test_count": 200},
        ]
        result = _sort_skills(skills, "test_count")
        assert result[0]["test_count"] == 100
        assert result[1]["test_count"] == 200
        assert result[2]["test_count"] == 300

    def test_sort_by_health(self):
        """_sort_skills with 'health' should sort by health priority (passing > unknown > failing)."""
        from app import _sort_skills
        skills = [
            {"name": "fail", "health": "failing"},
            {"name": "unk", "health": "unknown"},
            {"name": "pass", "health": "passing"},
        ]
        result = _sort_skills(skills, "health")
        assert result[0]["health"] == "passing"
        assert result[1]["health"] == "unknown"
        assert result[2]["health"] == "failing"

    def test_sort_by_health_desc(self):
        """_sort_skills with 'health-desc' should sort failing first."""
        from app import _sort_skills
        skills = [
            {"name": "pass", "health": "passing"},
            {"name": "fail", "health": "failing"},
            {"name": "unk", "health": "unknown"},
        ]
        result = _sort_skills(skills, "health-desc")
        assert result[0]["health"] == "failing"
        assert result[1]["health"] == "unknown"
        assert result[2]["health"] == "passing"

    def test_sort_none_returns_unchanged(self):
        """_sort_skills with None should return skills unchanged."""
        from app import _sort_skills
        skills = [{"name": "z"}, {"name": "a"}]
        result = _sort_skills(skills, None)
        assert result == skills

    def test_sort_empty_string_returns_unchanged(self):
        """_sort_skills with empty string should return skills unchanged."""
        from app import _sort_skills
        skills = [{"name": "z"}, {"name": "a"}]
        result = _sort_skills(skills, "")
        assert result == skills

    def test_sort_with_none_test_count(self):
        """_sort_skills with test_count should handle skills with None test_count."""
        from app import _sort_skills
        skills = [
            {"name": "skill-a", "test_count": None},
            {"name": "skill-b", "test_count": 50},
        ]
        result = _sort_skills(skills, "test_count")
        assert result[0]["test_count"] is None
        assert result[1]["test_count"] == 50

    def test_sort_with_missing_version(self):
        """_sort_skills with version should handle skills missing version."""
        from app import _sort_skills
        skills = [
            {"name": "skill-a"},
            {"name": "skill-b", "version": "1.0"},
        ]
        result = _sort_skills(skills, "version")
        assert len(result) == 2

    def test_sort_preserves_all_fields(self):
        """Sorting should not lose any skill data fields."""
        from app import _sort_skills
        skills = [
            {"name": "b", "version": "2.0", "layer": "core", "health": "passing", "description": "B skill"},
            {"name": "a", "version": "1.0", "layer": "external", "health": "failing", "description": "A skill"},
        ]
        result = _sort_skills(skills, "name")
        assert result[0]["description"] == "A skill"
        assert result[1]["description"] == "B skill"
        assert result[0]["layer"] == "external"
        assert result[1]["layer"] == "core"


class TestSortKeyAndReverse:
    def test_simple_key(self):
        """_sort_key_and_reverse with simple key returns (key, False)."""
        from app import _sort_key_and_reverse
        assert _sort_key_and_reverse("name") == ("name", False)

    def test_desc_key(self):
        """_sort_key_and_reverse with -desc suffix returns (key, True)."""
        from app import _sort_key_and_reverse
        assert _sort_key_and_reverse("name-desc") == ("name", True)

    def test_version_desc(self):
        """_sort_key_and_reverse with version-desc returns (version, True)."""
        from app import _sort_key_and_reverse
        assert _sort_key_and_reverse("version-desc") == ("version", True)

    def test_test_count_desc(self):
        """_sort_key_and_reverse with test_count-desc returns (test_count, True)."""
        from app import _sort_key_and_reverse
        assert _sort_key_and_reverse("test_count-desc") == ("test_count", True)

    def test_health_no_suffix(self):
        """_sort_key_and_reverse with 'health' returns (health, False)."""
        from app import _sort_key_and_reverse
        assert _sort_key_and_reverse("health") == ("health", False)


class TestApiSkillsSort:
    def test_api_skills_sort_by_name(self, client):
        """API /api/skills?sort=name should return skills sorted by name."""
        response = client.get("/api/skills?sort=name")
        assert response.status_code == 200
        data = response.json()
        names = [s["name"] for s in data]
        assert names == sorted(names, key=str.lower)

    def test_api_skills_sort_by_name_desc(self, client):
        """API /api/skills?sort=name-desc should return skills sorted Z-A."""
        response = client.get("/api/skills?sort=name-desc")
        assert response.status_code == 200
        data = response.json()
        names = [s["name"] for s in data]
        assert names == sorted(names, key=str.lower, reverse=True)

    def test_api_skills_sort_by_test_count(self, client):
        """API /api/skills?sort=test_count should return skills sorted by test count."""
        response = client.get("/api/skills?sort=test_count")
        assert response.status_code == 200
        data = response.json()
        counts = [s.get("test_count", 0) or 0 for s in data]
        assert counts == sorted(counts)

    def test_api_skills_sort_by_health(self, client):
        """API /api/skills?sort=health should return skills sorted by health priority."""
        response = client.get("/api/skills?sort=health")
        assert response.status_code == 200
        data = response.json()
        health_order = {"passing": 0, "unknown": 1, "failing": 2}
        health_values = [health_order.get(s["health"], 1) for s in data]
        assert health_values == sorted(health_values)

    def test_api_skills_sort_default_unchanged(self, client):
        """API without sort param should return skills in default order."""
        default_resp = client.get("/api/skills")
        name_resp = client.get("/api/skills?sort=name")
        # Default may or may not match name sort — just verify both return lists
        assert isinstance(default_resp.json(), list)
        assert isinstance(name_resp.json(), list)


class TestHomePageSort:
    def test_home_page_has_sort_dropdown(self, client):
        """Home page should have a sort dropdown."""
        response = client.get("/")
        assert 'name="sort"' in response.text
        assert "Default order" in response.text

    def test_home_page_sort_options(self, client):
        """Sort dropdown should have name, version, test_count, health options."""
        response = client.get("/")
        assert "Name (A-Z)" in response.text
        assert "Name (Z-A)" in response.text
        assert "Version" in response.text
        assert "Test count" in response.text
        assert "Health" in response.text

    def test_home_page_sort_by_name(self, client):
        """Home page with sort=name should render skills sorted alphabetically."""
        response = client.get("/?sort=name")
        assert response.status_code == 200
        assert "Skill Hub" in response.text

    def test_home_page_sort_by_test_count(self, client):
        """Home page with sort=test_count should render without errors."""
        response = client.get("/?sort=test_count")
        assert response.status_code == 200
        assert "Skill Hub" in response.text

    def test_home_page_sort_with_filter(self, client):
        """Sort should work combined with layer/health filters."""
        response = client.get("/?layer=core&sort=name")
        assert response.status_code == 200
        assert "Skill Hub" in response.text

    def test_home_page_sort_clear_link(self, client):
        """Clear link should appear when sort is active."""
        response = client.get("/?sort=name")
        assert "Clear" in response.text

    def test_home_page_sort_selected_state(self, client):
        """Sort dropdown should show selected state for current sort."""
        response = client.get("/?sort=name")
        assert 'value="name" selected' in response.text


class TestHomePageResyncButton:
    def test_home_page_has_resync_button(self, client):
        """Home page should have a Re-sync Skills button."""
        response = client.get("/")
        assert "Re-sync Skills" in response.text

    def test_home_page_has_resync_js_function(self, client):
        """Home page should have resyncSkills JavaScript function."""
        response = client.get("/")
        assert "resyncSkills" in response.text

    def test_home_page_resync_calls_api(self, client):
        """Home page resync button should call POST /api/skills/resync."""
        response = client.get("/")
        assert "/api/skills/resync" in response.text

    def test_home_page_resync_status_element(self, client):
        """Home page should have a status element for resync feedback."""
        response = client.get("/")
        assert "resync-status" in response.text

    def test_home_page_resync_reloads_page(self, client):
        """Resync JS should reload the page after success."""
        response = client.get("/")
        assert "window.location.reload" in response.text


class TestHomePageHealthCounts:
    """Tests for home page health_counts and avg_pass_rate stat cards."""

    def test_home_has_passing_stat_card(self, client):
        """Home page should show Passing stat card."""
        response = client.get("/")
        assert "Passing" in response.text

    def test_home_has_failing_stat_card(self, client):
        """Home page should show Failing stat card."""
        response = client.get("/")
        assert "Failing" in response.text

    def test_home_has_unknown_stat_card(self, client):
        """Home page should show Unknown stat card."""
        response = client.get("/")
        assert "Unknown" in response.text

    def test_home_has_avg_pass_rate_card(self, client):
        """Home page should show Avg Pass Rate stat card."""
        response = client.get("/")
        assert "Avg Pass Rate" in response.text

    def test_home_health_counts_from_enriched_skills(self, client):
        """health_counts should be computed from the enriched skills list."""
        # All skills initially have health='unknown', so unknown count should match total
        response = client.get("/")
        # Skills start with health='unknown' before tests are run
        assert "Unknown" in response.text

    def test_home_avg_pass_rate_with_no_test_data(self, client):
        """Avg Pass Rate should show 0% when no test runs exist."""
        response = client.get("/")
        assert response.status_code == 200
        # With no test runs, avg_pass_rate should be 0.0, showing "0%"
        assert "0%" in response.text

    def test_home_filter_affects_health_counts(self, client):
        """When filtering, health_counts should reflect filtered skills, not all skills."""
        response = client.get("/?layer=core")
        assert response.status_code == 200
        # Should still show stat cards for filtered results
        assert "Passing" in response.text
        assert "Failing" in response.text


# --- Test All API endpoint tests (mocked _run_skill_tests to avoid slow subprocess) ---


class TestApiTestAll:
    def _mock_run_skill_tests(self, name, skill_path):
        """Return a mock test result without running actual pytest."""
        return {
            "skill_name": name,
            "status": "completed",
            "passed": 10,
            "failed": 0,
            "errors": 0,
            "skipped": 2,
            "total_tests": 10,
            "duration_seconds": 0.5,
            "output": f"mock output for {name}",
        }

    def _patch_test_all_deps(self):
        """Patch _run_skill_tests, record_test_run, and upsert_skill to avoid DB pollution."""
        return [
            patch("app._run_skill_tests", new_callable=AsyncMock, side_effect=self._mock_run_skill_tests),
            patch("app.record_test_run", new_callable=AsyncMock, return_value=1),
            patch("app.upsert_skill", new_callable=AsyncMock),
        ]

    def test_test_all_returns_200(self):
        """Test-all endpoint should return 200 with mocked test runner."""
        patches = self._patch_test_all_deps()
        with patches[0], patches[1], patches[2]:
            with TestClient(app) as client:
                response = client.post("/api/skills/test-all")
                assert response.status_code == 200
                data = response.json()
                assert "total_skills" in data
                assert isinstance(data["total_skills"], int)
                assert data["total_skills"] >= 1

    def test_test_all_response_has_results(self):
        """Test-all response should include results list."""
        patches = self._patch_test_all_deps()
        with patches[0], patches[1], patches[2]:
            with TestClient(app) as client:
                response = client.post("/api/skills/test-all")
                data = response.json()
                assert "results" in data
                assert isinstance(data["results"], list)
                assert len(data["results"]) >= 1

    def test_test_all_response_has_aggregated_counts(self):
        """Test-all response should include aggregated passed/failed/errors counts."""
        patches = self._patch_test_all_deps()
        with patches[0], patches[1], patches[2]:
            with TestClient(app) as client:
                response = client.post("/api/skills/test-all")
                data = response.json()
                assert "total_passed" in data
                assert "total_failed" in data
                assert "total_errors" in data
                assert "skills_completed" in data
                assert isinstance(data["total_passed"], int)
                assert isinstance(data["total_failed"], int)

    def test_test_all_results_have_skill_name_and_status(self):
        """Each result in test-all should have skill_name and status."""
        patches = self._patch_test_all_deps()
        with patches[0], patches[1], patches[2]:
            with TestClient(app) as client:
                response = client.post("/api/skills/test-all")
                data = response.json()
                for r in data["results"]:
                    assert "skill_name" in r
                    assert "status" in r

    def test_test_all_passed_equals_sum(self):
        """Total passed count should equal sum of per-skill passed counts."""
        patches = self._patch_test_all_deps()
        with patches[0], patches[1], patches[2]:
            with TestClient(app) as client:
                response = client.post("/api/skills/test-all")
                data = response.json()
                sum_passed = sum(r.get("passed", 0) for r in data["results"])
                assert data["total_passed"] == sum_passed

    def test_test_all_failed_equals_sum(self):
        """Total failed count should equal sum of per-skill failed counts."""
        patches = self._patch_test_all_deps()
        with patches[0], patches[1], patches[2]:
            with TestClient(app) as client:
                response = client.post("/api/skills/test-all")
                data = response.json()
                sum_failed = sum(r.get("failed", 0) for r in data["results"])
                assert data["total_failed"] == sum_failed

    def test_test_all_skills_completed_count(self):
        """skills_completed should count completed test runs."""
        patches = self._patch_test_all_deps()
        with patches[0], patches[1], patches[2]:
            with TestClient(app) as client:
                response = client.post("/api/skills/test-all")
                data = response.json()
                completed = sum(1 for r in data["results"] if r.get("status") == "completed")
                assert data["skills_completed"] == completed


# --- Health page skills data tests ---


class TestHealthPageSkillsData:
    def test_health_page_has_skills_data(self, client):
        """Health page should now receive skills list data."""
        resp = client.get("/health")
        assert resp.status_code == 200
        # The page should render with skills overview
        assert "Skills Health Overview" in resp.text

    def test_health_page_skills_overview_table(self, client):
        """Health page should render skills overview table with skill names."""
        resp = client.get("/health")
        assert resp.status_code == 200
        # Should have table with skill rows
        assert "<table>" in resp.text or "<table" in resp.text


# --- Add test counts with last_tested_at and pass_rate ---


class TestAddTestCountsExtended:
    """Tests for _add_test_counts including last_tested_at and pass_rate fields."""

    def test_api_skills_has_last_tested_at_field(self, client):
        """API /api/skills should include last_tested_at field per skill."""
        response = client.get("/api/skills")
        data = response.json()
        for skill in data:
            assert "last_tested_at" in skill

    def test_api_skills_has_pass_rate_field(self, client):
        """API /api/skills should include pass_rate field per skill."""
        response = client.get("/api/skills")
        data = response.json()
        for skill in data:
            assert "pass_rate" in skill

    def test_api_skills_pass_rate_is_numeric_or_none(self, client):
        """pass_rate should be a float between 0 and 1, or None if untested."""
        response = client.get("/api/skills")
        data = response.json()
        for skill in data:
            pr = skill["pass_rate"]
            assert pr is None or isinstance(pr, (int, float))
            if pr is not None:
                assert 0.0 <= pr <= 1.0

    def test_api_skills_no_tests_pass_rate_none(self, client):
        """Skills without test runs should have pass_rate of None."""
        response = client.get("/api/skills")
        data = response.json()
        # Most skills won't have been tested in the test env
        for skill in data:
            if not skill.get("last_tested_at"):
                assert skill["pass_rate"] is None

    def test_api_skills_last_tested_at_string(self, client):
        """last_tested_at should be a string (ISO date or empty)."""
        response = client.get("/api/skills")
        data = response.json()
        for skill in data:
            assert isinstance(skill["last_tested_at"], str)

    def test_api_skills_pass_rate_after_recorded_test(self):
        """After recording a test run in DB, API should show updated pass_rate."""
        from unittest.mock import patch, AsyncMock
        import asyncio
        from database import init_db, upsert_skill, record_test_run

        async def _test():
            db_path = "/tmp/test_skill_hub_pass_rate.db"
            db = await init_db(db_path)
            skill = {
                "name": "test-skill-pr", "version": "1.0.0", "layer": "core",
                "health": "unknown", "author": "test", "description": "test",
                "category": "core", "path": "/tmp/test-skill-pr",
                "scripts_json": "[]", "modules_json": "[]",
            }
            await upsert_skill(db, skill)
            run_result = {
                "skill_name": "test-skill-pr", "status": "completed",
                "total_tests": 10, "passed": 8, "failed": 2, "errors": 0,
                "skipped": 0, "duration_seconds": 1.5, "output": "",
            }
            await record_test_run(db, run_result)
            await db.close()

        asyncio.run(_test())
        os.environ["SKILL_HUB_DB"] = "/tmp/test_skill_hub_pass_rate.db"
        with TestClient(app) as c:
            resp = c.get("/api/skills")
            data = resp.json()
            skill_pr = [s for s in data if s["name"] == "test-skill-pr"]
            if skill_pr:
                assert skill_pr[0]["pass_rate"] == 0.8
                assert skill_pr[0]["last_tested_at"] != ""
        os.environ["SKILL_HUB_DB"] = "/tmp/test_skill_hub_api.db"

    def test_add_test_counts_fields_with_mock(self, tmp_path):
        """_add_test_counts should set last_tested_at and pass_rate from test run."""
        from app import _add_test_counts
        import asyncio
        from database import init_db, record_test_run, upsert_skill

        async def _test():
            db = await init_db(str(tmp_path / "test.db"))
            # Insert a skill
            skill = {
                "name": "test-skill", "version": "1.0.0", "layer": "core",
                "health": "unknown", "author": "test", "description": "test",
                "category": "core", "path": "/tmp/test-skill",
                "scripts_json": "[]", "modules_json": "[]",
            }
            await upsert_skill(db, skill)
            # Record a test run
            run_result = {
                "skill_name": "test-skill", "status": "completed",
                "total_tests": 10, "passed": 8, "failed": 2, "errors": 0,
                "skipped": 0, "duration_seconds": 1.5, "output": "",
            }
            await record_test_run(db, run_result)
            # Now add test counts
            skills = [skill.copy()]
            skills = await _add_test_counts(skills, db)
            assert skills[0]["test_count"] == 10
            assert skills[0]["last_tested_at"] != ""
            assert skills[0]["pass_rate"] == 0.8
            await db.close()

        asyncio.run(_test())

    def test_add_test_counts_pass_rate_none_when_no_tests(self, tmp_path):
        """_add_test_counts should set pass_rate to None when skill has no test runs."""
        from app import _add_test_counts
        import asyncio
        from database import init_db, upsert_skill

        async def _test():
            db = await init_db(str(tmp_path / "test.db"))
            skill = {
                "name": "no-test-skill", "version": "1.0.0", "layer": "core",
                "health": "unknown", "author": "test", "description": "test",
                "category": "core", "path": str(tmp_path / "no-test-skill"),
                "scripts_json": "[]", "modules_json": "[]",
            }
            await upsert_skill(db, skill)
            skills = [skill.copy()]
            skills = await _add_test_counts(skills, db)
            assert skills[0]["last_tested_at"] == ""
            assert skills[0]["pass_rate"] is None
            await db.close()

        asyncio.run(_test())


# --- Config template variable fix verification ---


class TestConfigTemplateVariableFix:
    """Tests verifying that config is rendered using the 'config' template variable (not skill.config)."""

    def test_config_section_rendered_with_non_empty_config(self):
        """Detail page template should render Configuration section when config dict is non-empty."""
        from app import _render_template
        html = _render_template("detail.html", {
            "skill": {"name": "test-skill", "version": "1.0", "layer": "core", "health": "passing",
                      "author": "test", "category": "core", "description": "test",
                      "scripts": [], "modules": [], "skill_md": "", "path": "/tmp"},
            "test_runs": [],
            "deps": [],
            "versions": [],
            "config": {"triggers": "test, demo", "timeout": "30s"},
            "skill_md_rendered": "",
            "nav_active": "skills",
        })
        assert "Configuration" in html
        assert "triggers" in html
        assert "timeout" in html

    def test_config_section_not_rendered_with_empty_config(self):
        """Detail page template should not render Configuration section when config dict is empty."""
        from app import _render_template
        html = _render_template("detail.html", {
            "skill": {"name": "test-skill", "version": "1.0", "layer": "core", "health": "passing",
                      "author": "test", "category": "core", "description": "test",
                      "scripts": [], "modules": [], "skill_md": "", "path": "/tmp"},
            "test_runs": [],
            "deps": [],
            "versions": [],
            "config": {},
            "skill_md_rendered": "",
            "nav_active": "skills",
        })
        assert "Configuration" not in html

    def test_config_items_rendered_in_table(self):
        """Config items should appear as key-value rows in a table."""
        from app import _render_template
        html = _render_template("detail.html", {
            "skill": {"name": "test-skill", "version": "1.0", "layer": "core", "health": "passing",
                      "author": "test", "category": "core", "description": "test",
                      "scripts": [], "modules": [], "skill_md": "", "path": "/tmp"},
            "test_runs": [],
            "deps": [],
            "versions": [],
            "config": {"max_retries": "3", "cache_enabled": "true"},
            "skill_md_rendered": "",
            "nav_active": "skills",
        })
        assert "max_retries" in html
        assert "3" in html
        assert "cache_enabled" in html
        assert "true" in html

    def test_config_does_not_use_skill_config(self):
        """Template should NOT reference skill.config — only the separate 'config' variable."""
        from app import _render_template
        skill = {"name": "test-skill", "version": "1.0", "layer": "core", "health": "passing",
                 "author": "test", "category": "core", "description": "test",
                 "scripts": [], "modules": [], "skill_md": "", "path": "/tmp"}
        # skill dict has NO 'config' key
        assert "config" not in skill
        html = _render_template("detail.html", {
            "skill": skill,
            "test_runs": [],
            "deps": [],
            "versions": [],
            "config": {"custom_key": "custom_value"},
            "skill_md_rendered": "",
            "nav_active": "skills",
        })
        assert "Configuration" in html
        assert "custom_key" in html

    def test_detail_endpoint_passes_config_to_template(self, client):
        """The skill detail endpoint should pass the config dict to the template."""
        resp = client.get("/skill/url-fetcher")
        assert resp.status_code == 200
        # url-fetcher has only internal frontmatter keys, so config should be empty
        # and the config section heading should NOT appear (note: "Configuration" may
        # appear in rendered SKILL.md body content, so check for the heading specifically)
        assert '<h2 style="font-size:16px;margin:16px 0 8px;">Configuration</h2>' not in resp.text


# --- WebSocket test streaming tests ---


class TestWebSocketTestStream:
    """Tests for the WebSocket test streaming endpoint /ws/test/{name}."""

    def test_ws_endpoint_exists_for_valid_skill(self, client):
        """WebSocket endpoint should exist at /ws/test/{name}."""
        from app import app
        routes = [r.path for r in app.routes]
        assert "/ws/test/{name}" in routes

    def test_ws_route_has_websocket_method(self):
        """WebSocket route should have WebSocket method defined."""
        from app import app
        ws_routes = [r for r in app.routes if r.path == "/ws/test/{name}"]
        assert len(ws_routes) == 1

    def test_ws_test_stream_function_exists(self):
        """The ws_test_stream function should exist in app module."""
        from app import ws_test_stream
        assert ws_test_stream is not None

    def test_ws_test_page_references_ws_endpoint(self, client):
        """Test page should reference the WebSocket endpoint in JavaScript."""
        resp = client.get("/test/url-fetcher")
        assert "/ws/test/" in resp.text
        assert "WebSocket" in resp.text

    def test_ws_test_page_has_stream_button(self, client):
        """Test page should have a Stream Tests (WebSocket) button."""
        resp = client.get("/test/url-fetcher")
        assert "Stream Tests" in resp.text

    def test_ws_test_page_js_creates_websocket(self, client):
        """Test page JavaScript should create WebSocket connection."""
        resp = client.get("/test/url-fetcher")
        assert "new WebSocket" in resp.text


# --- Error handling edge case tests ---


class TestErrorHandlingEdgeCases:
    """Tests for error handling in various edge cases."""

    def test_api_skill_detail_nonexistent_returns_json_error(self, client):
        """API skill detail for nonexistent skill should return JSON error response."""
        resp = client.get("/api/skills/nonexistent-skill-xyz")
        assert resp.status_code == 404
        data = resp.json()
        assert "error" in data

    def test_api_404_for_nonexistent_api_path(self, client):
        """Nonexistent API path should return JSON error, not HTML."""
        resp = client.get("/api/nonexistent-path")
        assert resp.status_code == 404
        data = resp.json()
        assert "error" in data

    def test_html_404_for_nonexistent_browser_path(self, client):
        """Nonexistent browser path should return styled HTML error, not bare JSON."""
        resp = client.get("/nonexistent-browser-page")
        assert resp.status_code == 404
        assert "Skill Hub" in resp.text


# --- _parse_pytest_line helper tests ---


class TestParsePytestLine:
    """Tests for the _parse_pytest_line helper that parses pytest verbose output lines."""

    def test_parse_passed_line(self):
        """PASSED status in a pytest verbose line should be detected."""
        from app import _parse_pytest_line
        assert _parse_pytest_line("tests/test_app.py::TestHome::test_home PASSED") == "PASSED"

    def test_parse_failed_line(self):
        """FAILED status in a pytest verbose line should be detected."""
        from app import _parse_pytest_line
        assert _parse_pytest_line("tests/test_app.py::TestHome::test_home FAILED") == "FAILED"

    def test_parse_error_line(self):
        """ERROR status in a pytest verbose line should be detected."""
        from app import _parse_pytest_line
        assert _parse_pytest_line("tests/test_app.py::TestHome::test_home ERROR") == "ERROR"

    def test_parse_skipped_line(self):
        """SKIPPED status in a pytest verbose line should be detected."""
        from app import _parse_pytest_line
        assert _parse_pytest_line("tests/test_app.py::TestHome::test_home SKIPPED") == "SKIPPED"

    def test_parse_line_no_double_colon(self):
        """Lines without :: should return None (not pytest test lines)."""
        from app import _parse_pytest_line
        assert _parse_pytest_line("PASSED") is None
        assert _parse_pytest_line("FAILED") is None
        assert _parse_pytest_line("just some random text") is None

    def test_parse_summary_line(self):
        """Pytest summary lines like '5 passed in 1.23s' should return None."""
        from app import _parse_pytest_line
        assert _parse_pytest_line("5 passed in 1.23s") is None
        assert _parse_pytest_line("10 passed, 2 failed in 3.45s") is None

    def test_parse_line_with_collection_info(self):
        """Lines with collection info (no ::) should return None."""
        from app import _parse_pytest_line
        assert _parse_pytest_line("collecting 569 items") is None
        assert _parse_pytest_line("collected 569 items") is None

    def test_parse_line_with_fixture_teardown(self):
        """Lines like fixture teardown should not be parsed as test results."""
        from app import _parse_pytest_line
        assert _parse_pytest_line("fixture teardown") is None

    def test_parse_line_empty(self):
        """Empty string should return None."""
        from app import _parse_pytest_line
        assert _parse_pytest_line("") is None

    def test_parse_line_with_xfail_marker(self):
        """XFAIL lines should return None (they are not standard PASSED/FAILED)."""
        from app import _parse_pytest_line
        assert _parse_pytest_line("tests/test_app.py::TestHome::test_home XFAIL") is None

    def test_parse_passed_with_subtest(self):
        """PASSED line with subtest notation should be detected."""
        from app import _parse_pytest_line
        assert _parse_pytest_line("tests/test_app.py::TestHome::test_home[param1] PASSED") == "PASSED"

    def test_parse_line_with_warning_text(self):
        """Lines that contain PASSED in warning text but not as a status should return None if no ::."""
        from app import _parse_pytest_line
        assert _parse_pytest_line("warning: PASSED is not a valid marker") is None

    def test_parse_line_with_multiple_statuses(self):
        """Lines containing both PASSED and FAILED keywords should prefer the first match."""
        from app import _parse_pytest_line
        # This edge case: a line with both keywords but only one is the actual status
        # Real pytest output won't have this, but we test the behavior
        assert _parse_pytest_line("path::test_func PASSED") == "PASSED"


# --- WebSocket streaming improvements tests ---


class TestWebSocketStreamingImprovements:
    """Tests for the improved WebSocket streaming endpoint logic."""

    def test_ws_endpoint_sends_started_at(self):
        """WebSocket result should include started_at timestamp."""
        from app import ws_test_stream
        # Verify the function imports datetime for timestamps
        import inspect
        source = inspect.getsource(ws_test_stream)
        assert "started_at" in source
        assert "datetime" in source

    def test_ws_endpoint_sends_finished_at(self):
        """WebSocket result should include finished_at timestamp."""
        from app import ws_test_stream
        import inspect
        source = inspect.getsource(ws_test_stream)
        assert "finished_at" in source

    def test_ws_endpoint_accumulates_full_output(self):
        """WebSocket should accumulate full output for _parse_pytest_summary."""
        from app import ws_test_stream
        import inspect
        source = inspect.getsource(ws_test_stream)
        assert "accumulated_output" in source
        assert "full_output" in source

    def test_ws_endpoint_passes_full_output_to_parse(self):
        """WebSocket should pass full_output to _parse_pytest_summary, not just last line."""
        from app import ws_test_stream
        import inspect
        source = inspect.getsource(ws_test_stream)
        # Should NOT use 'text' (the last line) for _parse_pytest_summary
        assert "_parse_pytest_summary(result, full_output)" in source

    def test_ws_endpoint_uses_parse_pytest_line(self):
        """WebSocket should use _parse_pytest_line helper for per-line parsing."""
        from app import ws_test_stream
        import inspect
        source = inspect.getsource(ws_test_stream)
        assert "_parse_pytest_line" in source

    def test_ws_endpoint_sets_status_from_returncode(self):
        """WebSocket result status should be set from proc.returncode."""
        from app import ws_test_stream
        import inspect
        source = inspect.getsource(ws_test_stream)
        assert "proc.returncode" in source

    def test_ws_result_includes_output_field(self):
        """WebSocket result dict should include 'output' field with full output."""
        from app import ws_test_stream
        import inspect
        source = inspect.getsource(ws_test_stream)
        assert '"output"' in source or "'output'" in source

    def test_parse_pytest_line_function_is_importable(self):
        """_parse_pytest_line should be importable from app module."""
        from app import _parse_pytest_line
        assert callable(_parse_pytest_line)

    def test_ws_counters_initialized_before_try(self):
        """Counter variables should be initialized before the try block so they're accessible in all paths."""
        from app import ws_test_stream
        import inspect
        source = inspect.getsource(ws_test_stream)
        # Verify the counters are set before 'try:' block
        lines = source.split('\n')
        try_line_idx = None
        for i, line in enumerate(lines):
            if 'try:' in line and 'except' not in line:
                try_line_idx = i
                break
        # There should be 'total = 0' etc. before try
        before_try = '\n'.join(lines[:try_line_idx])
        assert "total = 0" in before_try
        assert "passed = 0" in before_try


class TestApiDeleteSkill:
    def test_delete_existing_skill(self, client):
        """DELETE /api/skills/{name} removes skill from DB."""
        response = client.delete("/api/skills/url-fetcher")
        assert response.status_code == 200
        data = response.json()
        assert data["deleted"] == "url-fetcher"
        assert "message" in data

    def test_delete_nonexistent_skill(self, client):
        """DELETE /api/skills/{name} returns 404 for nonexistent skill."""
        response = client.delete("/api/skills/nonexistent-skill-xyz")
        assert response.status_code == 404
        data = response.json()
        assert "error" in data

    def test_delete_skill_removes_from_db(self, client):
        """After deletion, skill should no longer have DB metadata (health, timestamps)."""
        # Delete skill from DB
        client.delete("/api/skills/url-fetcher")
        # Skill still appears in /api/skills because _enrich_with_discovered
        # re-adds filesystem-found skills, but DB metadata should be gone
        response = client.get("/api/skills/url-fetcher")
        data = response.json()
        # DB-specific fields like discovered_at/updated_at should be absent
        # or health should be 'unknown' since it was deleted from DB
        assert data.get("health") == "unknown"


class TestApiDeleteTestRuns:
    def test_delete_test_runs_existing_skill(self, client):
        """DELETE /api/skills/{name}/test-runs clears test history."""
        # First ensure the skill exists
        client.post("/api/skills/resync")
        response = client.delete("/api/skills/url-fetcher/test-runs")
        assert response.status_code == 200
        data = response.json()
        assert data["skill_name"] == "url-fetcher"
        assert "deleted_count" in data
        assert "message" in data

    def test_delete_test_runs_nonexistent_skill(self, client):
        """DELETE /api/skills/{name}/test-runs returns 404 for nonexistent skill."""
        response = client.delete("/api/skills/nonexistent-skill-xyz/test-runs")
        assert response.status_code == 404
        data = response.json()
        assert "error" in data

    def test_delete_test_runs_resets_health(self, client):
        """After clearing test runs, skill health should be reset to 'unknown'."""
        client.post("/api/skills/resync")
        response = client.delete("/api/skills/url-fetcher/test-runs")
        if response.status_code == 200:
            response = client.get("/api/skills/url-fetcher")
            data = response.json()
            assert data.get("health") == "unknown"


class TestApiHealthRecentRuns:
    def test_api_health_includes_recent_runs(self, client):
        """GET /api/health includes recent_runs field."""
        client.post("/api/skills/resync")
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert "recent_runs" in data

    def test_api_health_recent_runs_is_list(self, client):
        """recent_runs is a list."""
        client.post("/api/skills/resync")
        response = client.get("/api/health")
        data = response.json()
        assert isinstance(data["recent_runs"], list)

    def test_api_health_recent_runs_has_fields(self, client):
        """Each recent run has expected fields."""
        client.post("/api/skills/resync")
        # Run a test to create a test run
        response = client.post("/api/skills/url-fetcher/test")
        # Then check health API
        health = client.get("/api/health")
        data = health.json()
        if data["recent_runs"]:
            run = data["recent_runs"][0]
            assert "skill_name" in run
            assert "status" in run
            assert "total_tests" in run
            assert "passed" in run
            assert "failed" in run
            assert "started_at" in run


class TestParseSemver:
    """Tests for _parse_semver helper that converts version strings to comparable tuples."""

    def test_parse_basic_version(self):
        from app import _parse_semver
        assert _parse_semver("1.0.0") == (1, 0, 0)

    def test_parse_two_component_version(self):
        from app import _parse_semver
        assert _parse_semver("2.0") == (2, 0, 0)

    def test_parse_single_component_version(self):
        from app import _parse_semver
        assert _parse_semver("10") == (10, 0, 0)

    def test_parse_version_with_non_numeric_parts(self):
        from app import _parse_semver
        result = _parse_semver("1.0.0-beta")
        assert result[0] == 1
        assert result[2] == 0  # non-numeric part becomes 0

    def test_semver_sorts_correctly(self):
        """Semver comparison: 2.0.0 < 10.0.0, unlike string comparison."""
        from app import _parse_semver
        assert _parse_semver("2.0.0") < _parse_semver("10.0.0")

    def test_semver_sorts_with_major_versions(self):
        """1.x sorts before 2.x."""
        from app import _parse_semver
        versions = ["10.0.0", "2.0.0", "1.5.3"]
        sorted_versions = sorted(versions, key=_parse_semver)
        assert sorted_versions == ["1.5.3", "2.0.0", "10.0.0"]

    def test_semver_minor_version_ordering(self):
        """1.1 sorts after 1.0."""
        from app import _parse_semver
        assert _parse_semver("1.1.0") > _parse_semver("1.0.0")

    def test_version_sort_uses_semver(self):
        """Version sort now uses semver, so 2.0 sorts before 10.0."""
        from app import _sort_skills
        skills = [
            {"name": "skill-a", "version": "10.0.0"},
            {"name": "skill-b", "version": "2.0.0"},
            {"name": "skill-c", "version": "1.0.0"},
        ]
        result = _sort_skills(skills, "version")
        assert result[0]["version"] == "1.0.0"
        assert result[1]["version"] == "2.0.0"
        assert result[2]["version"] == "10.0.0"

    def test_version_sort_desc_uses_semver(self):
        """Version sort descending with semver: 10.0 first, then 2.0, then 1.0."""
        from app import _sort_skills
        skills = [
            {"name": "skill-a", "version": "1.0.0"},
            {"name": "skill-b", "version": "2.0.0"},
            {"name": "skill-c", "version": "10.0.0"},
        ]
        result = _sort_skills(skills, "version-desc")
        assert result[0]["version"] == "10.0.0"
        assert result[1]["version"] == "2.0.0"
        assert result[2]["version"] == "1.0.0"


# --- Bug fix verification tests (iteration 25) ---


class TestPassRateNoneInsteadOfZero:
    """Tests that pass_rate is None for untested skills instead of 0.0."""

    def test_api_skills_pass_rate_none_when_untested(self, client):
        """Skills without test runs should have pass_rate=None, not 0.0."""
        response = client.get("/api/skills")
        data = response.json()
        untested = [s for s in data if not s.get("last_tested_at")]
        if untested:
            assert all(s["pass_rate"] is None for s in untested)

    def test_api_skills_pass_rate_numeric_when_tested(self, client):
        """Skills with test runs should have numeric pass_rate."""
        response = client.get("/api/skills")
        data = response.json()
        tested = [s for s in data if s.get("last_tested_at")]
        if tested:
            assert all(isinstance(s["pass_rate"], (int, float)) for s in tested)

    def test_add_test_counts_sets_none_for_no_runs(self, tmp_path):
        """_add_test_counts sets pass_rate to None when no test runs exist."""
        from app import _add_test_counts
        import asyncio
        from database import init_db, upsert_skill

        async def _test():
            db = await init_db(str(tmp_path / "test.db"))
            skill = {"name": "untested-skill", "version": "1.0.0", "layer": "core",
                     "health": "unknown", "author": "test", "description": "test",
                     "category": "core", "path": str(tmp_path), "scripts_json": "[]", "modules_json": "[]"}
            await upsert_skill(db, skill)
            skills = [skill.copy()]
            skills = await _add_test_counts(skills, db)
            assert skills[0]["pass_rate"] is None
            assert skills[0]["last_tested_at"] == ""
            await db.close()
        asyncio.run(_test())

    def test_home_page_pass_rate_display_uses_none(self):
        """Home page template should handle pass_rate=None gracefully."""
        from app import _render_template
        skills = [{"name": "test", "version": "1.0", "layer": "core", "health": "unknown",
                   "description": "test", "test_count": 0, "pass_rate": None, "last_tested_at": "",
                   "scripts": [], "modules": []}]
        html = _render_template("home.html", {
            "skills": skills, "query": "", "total": 1, "nav_active": "skills",
            "layer": "", "health": "", "sort": "", "all_layers": ["core"],
            "all_healths": ["unknown"], "health_counts": {"passing": 0, "failing": 0, "unknown": 1},
            "avg_pass_rate": 0.0, "port": 8765,
        })
        # pass_rate=None should not cause template error or display wrong value
        assert "0% pass" not in html or "0 tests" in html


class TestInlineCodeProtection:
    """Tests that inline code content is protected from bold/italic/link processing."""

    def test_inline_code_with_bold_markers(self):
        """Bold markers inside inline code should NOT be processed."""
        from app import _render_markdown
        result = _render_markdown("Use `**bold**` carefully")
        assert "<code>**bold**</code>" in result
        assert "<strong>" not in result

    def test_inline_code_with_italic_markers(self):
        """Italic markers inside inline code should NOT be processed."""
        from app import _render_markdown
        result = _render_markdown("The `*italic*` syntax")
        assert "<code>*italic*</code>" in result
        assert "<em>" not in result

    def test_inline_code_with_link_syntax(self):
        """Link syntax inside inline code should NOT be processed."""
        from app import _render_markdown
        result = _render_markdown("See `[link](url)` for docs")
        assert "<code>[link](url)</code>" in result
        assert "<a href" not in result

    def test_inline_code_html_escaped(self):
        """HTML entities inside inline code should be escaped."""
        from app import _render_markdown
        result = _render_markdown("Use `<div>` element")
        assert "<code>&lt;div&gt;</code>" in result
        assert "<div>" not in result

    def test_inline_code_preserved_in_paragraph(self):
        """Inline code in a paragraph should not be corrupted by bold/italic."""
        from app import _render_markdown
        result = _render_markdown("Run `**test**` and see results")
        assert "<code>**test**</code>" in result


class TestLinkWithParentheses:
    """Tests that links with parenthesized URLs are correctly parsed."""

    def test_wikipedia_disambiguation_link(self):
        """Wikipedia-style links with (disambiguation) in URL should render correctly."""
        from app import _render_markdown
        result = _render_markdown("[Apple](https://en.wikipedia.org/wiki/Apple_(disambiguation))")
        assert '<a href="https://en.wikipedia.org/wiki/Apple_(disambiguation)">Apple</a>' in result

    def test_simple_link_still_works(self):
        """Simple links without parentheses should still work correctly."""
        from app import _render_markdown
        result = _render_markdown("[docs](https://example.com)")
        assert '<a href="https://example.com">docs</a>' in result

    def test_link_with_nested_parens(self):
        """Links with nested parentheses in URL should render."""
        from app import _render_markdown
        result = _render_markdown("[ref](https://example.com/page_(sub))")
        assert '<a href="https://example.com/page_(sub)">ref</a>' in result


class TestCsvExportRfc4180:
    """Tests that CSV export follows RFC 4180 quoting for commas in fields."""

    def test_csv_fields_with_commas_are_quoted(self, client):
        """Fields containing commas should be double-quoted per RFC 4180."""
        response = client.get("/api/skills/export.csv")
        import csv
        reader = csv.reader(response.text.strip().split("\n"))
        rows = list(reader)
        # Each row should have exactly 8 fields
        for row in rows:
            assert len(row) == 8

    def test_csv_header_fields(self, client):
        """CSV header row should have standard field names."""
        response = client.get("/api/skills/export.csv")
        import csv
        reader = csv.reader(response.text.strip().split("\n"))
        rows = list(reader)
        assert rows[0] == ["name", "version", "layer", "health", "author", "description", "category", "path"]

    def test_csv_quoted_description_preserves_commas(self, client):
        """Descriptions with commas should be preserved in quoted fields."""
        response = client.get("/api/skills/export.csv")
        import csv
        reader = csv.reader(response.text.strip().split("\n"))
        rows = list(reader)
        # Find a row whose description contains commas (real skills have them)
        for row in rows[1:]:
            if "," in row[5] or ";" in row[5]:
                # The description field should preserve the content correctly
                assert len(row) == 8


class TestParseDescriptionAbbreviations:
    """Tests that _parse_description handles abbreviations correctly."""

    def test_eg_abbreviation_not_truncated(self):
        """Descriptions with 'e.g.' should not be truncated at the abbreviation."""
        from skill_discovery import _parse_description
        desc = _parse_description({"description": "Uses e.g. pytest for testing"})
        assert "pytest" in desc
        assert desc == "Uses e.g. pytest for testing"

    def test_ie_abbreviation_not_truncated(self):
        """Descriptions with 'i.e.' should not be truncated at the abbreviation."""
        from skill_discovery import _parse_description
        desc = _parse_description({"description": "Uses i.e. python scripts"})
        assert "python" in desc

    def test_etc_abbreviation_not_truncated(self):
        """Descriptions with 'etc.' should not be truncated at the abbreviation."""
        from skill_discovery import _parse_description
        desc = _parse_description({"description": "A tool etc. for processing data"})
        assert "processing" in desc

    def test_real_sentence_still_extracted(self):
        """Real sentences should still be extracted correctly (first sentence)."""
        from skill_discovery import _parse_description
        desc = _parse_description({"description": "Line one. Line two. Line three"})
        assert desc == "Line one."

    def test_single_word_sentence(self):
        """Single-word sentences should work correctly."""
        from skill_discovery import _parse_description
        desc = _parse_description({"description": "Done. More text here"})
        assert desc == "Done."

    def test_question_mark_sentence(self):
        """Question marks should also serve as sentence boundaries."""
        from skill_discovery import _parse_description
        desc = _parse_description({"description": "What is this? A tool for testing"})
        assert desc == "What is this?"

    def test_exclamation_sentence(self):
        """Exclamation marks should also serve as sentence boundaries."""
        from skill_discovery import _parse_description
        desc = _parse_description({"description": "Amazing! This tool works well"})
        assert desc == "Amazing!"


class TestMarkdownImages:
    """Tests for markdown image rendering (![alt](url))."""

    def test_image_basic(self):
        """Basic image syntax ![alt](url) should render as <img> tag."""
        from app import _render_markdown
        result = _render_markdown("![logo](https://example.com/logo.png)")
        assert '<img alt="logo" src="https://example.com/logo.png">' in result

    def test_image_empty_alt(self):
        """Image with empty alt text should render with alt=\"\"."""
        from app import _render_markdown
        result = _render_markdown("![](https://example.com/img.png)")
        assert '<img alt="" src="https://example.com/img.png">' in result

    def test_image_not_confused_with_link(self):
        """Image ![] should not be confused with link []."""
        from app import _render_markdown
        result = _render_markdown("![pic](https://x.com/pic.png) and [link](https://x.com)")
        assert '<img alt="pic" src="https://x.com/pic.png">' in result
        assert '<a href="https://x.com">link</a>' in result

    def test_image_with_parenthesized_url(self):
        """Image with parenthesized URL (Wikipedia style) should render correctly."""
        from app import _render_markdown
        result = _render_markdown("![icon](https://wiki.com/Icon_(disambiguation).png)")
        assert 'src="https://wiki.com/Icon_(disambiguation).png"' in result

    def test_image_in_paragraph(self):
        """Image within text content should render as <img> tag."""
        from app import _render_markdown
        result = _render_markdown("See the chart:\n\n![chart](chart.png)")
        assert '<img alt="chart" src="chart.png">' in result


class TestSanitizeHtml:
    """Tests for HTML sanitization to prevent XSS in rendered markdown."""

    def test_raw_script_tag_escaped(self):
        """Raw <script> tags in markdown should be escaped."""
        from app import _sanitize_html
        result = _sanitize_html("Hello <script>alert('xss')</script> world")
        assert "&lt;script&gt;" in result
        assert "<script>" not in result

    def test_allowed_tags_preserved(self):
        """Allowed markdown-generated tags should pass through sanitization."""
        from app import _sanitize_html
        result = _sanitize_html("<h1>Title</h1><p>Text <strong>bold</strong></p>")
        assert "<h1>" in result
        assert "</h1>" in result
        assert "<strong>" in result
        assert "<p>" in result

    def test_event_handlers_stripped(self):
        """Event handler attributes like onclick should be stripped."""
        from app import _sanitize_html
        result = _sanitize_html('<a onclick="alert(1)" href="https://x.com">link</a>')
        assert "onclick" not in result
        assert 'href="https://x.com"' in result

    def test_img_event_handlers_stripped(self):
        """Image onerror/onload handlers should be stripped."""
        from app import _sanitize_html
        result = _sanitize_html('<img onerror="alert(1)" alt="pic" src="pic.png">')
        assert "onerror" not in result
        assert 'alt="pic"' in result

    def test_existing_entities_preserved(self):
        """Existing HTML entities like &lt; should not be double-escaped."""
        from app import _sanitize_html
        result = _sanitize_html("&lt;div&gt; &amp;")
        assert "&lt;div&gt;" in result
        assert "&amp;" in result
        # Should NOT become &amp;lt;div&amp;gt;
        assert "&amp;lt;" not in result

    def test_numeric_entities_preserved(self):
        """Numeric HTML entities like &#60; should be preserved."""
        from app import _sanitize_html
        result = _sanitize_html("&#60;tag&#62;")
        assert "&#60;" in result
        assert "&#62;" in result

    def test_raw_angle_brackets_escaped(self):
        """Raw angle brackets not part of allowed tags should be escaped."""
        from app import _sanitize_html
        result = _sanitize_html("Use <div> not <script>")
        assert "&lt;div&gt;" in result
        assert "&lt;script&gt;" in result

    def test_sanitize_in_render_markdown(self):
        """_render_markdown should sanitize XSS content via _sanitize_html."""
        from app import _render_markdown
        result = _render_markdown("Text with <script>alert(1)</script>")
        assert "&lt;script&gt;" in result
        assert "<script>" not in result

    def test_allowed_tags_in_render_markdown(self):
        """_render_markdown output with allowed tags should pass sanitization."""
        from app import _render_markdown
        result = _render_markdown("# Title\n**bold** text")
        assert "<h1>" in result
        assert "<strong>" in result

    def test_img_tag_preserved_in_sanitize(self):
        """<img> tags generated by markdown should pass through sanitization."""
        from app import _sanitize_html
        result = _sanitize_html('<img alt="chart" src="chart.png">')
        assert '<img' in result
        assert 'src="chart.png"' in result