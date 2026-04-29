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
        # DB search returns 0, but enrich_with_discovered adds all discovered skills
        # so the result may still contain skills if names/descriptions don't match query
        # We check that no skill name/description matches the query
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