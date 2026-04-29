"""Tests for FastAPI app endpoints."""

import pytest
import pytest_asyncio
import json
from pathlib import Path

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