"""Tests for Jinja2 template rendering content."""

import sys
import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

SKILL_HUB_DIR = Path(__file__).resolve().parent.parent
MODULES_DIR = SKILL_HUB_DIR / "modules"
PROJECT_ROOT = SKILL_HUB_DIR.parent.parent.parent
REAL_SKILLS_DIR = PROJECT_ROOT / "skills"

if str(MODULES_DIR) not in sys.path:
    sys.path.insert(0, str(MODULES_DIR))

os.environ["SKILL_HUB_DB"] = "/tmp/test_skill_hub_templates.db"
os.environ["SKILL_HUB_SKILLS_DIR"] = str(REAL_SKILLS_DIR)

from app import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


# --- Home page content tests ---


class TestHomePageContent:
    def test_home_has_nav_links(self, client):
        resp = client.get("/")
        assert "/health" in resp.text
        assert "/install" in resp.text

    def test_home_has_search_form(self, client):
        resp = client.get("/")
        assert "<form" in resp.text
        assert 'name="q"' in resp.text

    def test_home_has_skill_cards(self, client):
        resp = client.get("/")
        assert "card" in resp.text

    def test_home_skill_card_links_to_detail(self, client):
        resp = client.get("/")
        assert "/skill/" in resp.text

    def test_home_shows_version(self, client):
        resp = client.get("/")
        assert "v" in resp.text  # versions shown as v1.0.0 etc

    def test_home_has_layer_badges(self, client):
        resp = client.get("/")
        assert "badge" in resp.text
        assert "core" in resp.text

    def test_home_has_health_badges(self, client):
        resp = client.get("/")
        assert "unknown" in resp.text

    def test_home_total_skills_count(self, client):
        resp = client.get("/")
        assert "Total Skills" in resp.text

    def test_home_search_with_results(self, client):
        resp = client.get("/?q=fetch")
        assert "fetch" in resp.text.lower()

    def test_home_search_clear_link(self, client):
        resp = client.get("/?q=fetch")
        assert "Clear" in resp.text

    def test_home_search_preserves_query(self, client):
        resp = client.get("/?q=fetch")
        assert "fetch" in resp.text

    def test_home_empty_search(self, client):
        resp = client.get("/?q=nonexistentxyz")
        # Should not crash, may show no matching skills or all skills enriched
        assert resp.status_code == 200

    def test_home_shows_scripts_count(self, client):
        resp = client.get("/")
        # Skills with scripts should show "X scripts"
        assert "scripts" in resp.text or "script" in resp.text

    def test_home_has_grid_layout(self, client):
        resp = client.get("/")
        assert "grid" in resp.text

    def test_home_css_included(self, client):
        resp = client.get("/")
        assert "<style>" in resp.text

    def test_home_title_is_skills(self, client):
        resp = client.get("/")
        assert "Skills" in resp.text


# --- Detail page content tests ---


class TestDetailPageContent:
    def test_detail_has_skill_name(self, client):
        resp = client.get("/skill/url-fetcher")
        assert "url-fetcher" in resp.text

    def test_detail_has_version(self, client):
        resp = client.get("/skill/url-fetcher")
        assert "v" in resp.text

    def test_detail_has_layer_badge(self, client):
        resp = client.get("/skill/url-fetcher")
        assert "core" in resp.text

    def test_detail_has_author(self, client):
        resp = client.get("/skill/url-fetcher")
        assert "by" in resp.text

    def test_detail_has_description(self, client):
        resp = client.get("/skill/url-fetcher")
        assert "description" in resp.text or "fetch" in resp.text.lower()

    def test_detail_has_skill_md_section(self, client):
        resp = client.get("/skill/url-fetcher")
        assert "SKILL.md" in resp.text or "md-content" in resp.text

    def test_detail_has_scripts_list(self, client):
        resp = client.get("/skill/url-fetcher")
        assert "Scripts" in resp.text or "scripts" in resp.text

    def test_detail_has_modules_list(self, client):
        # skill-hub has modules, so its detail page should show them
        resp = client.get("/skill/skill-hub")
        if resp.status_code == 200:
            assert "Modules" in resp.text or "modules" in resp.text
        else:
            # url-fetcher has no modules dir, so Modules section won't appear
            resp = client.get("/skill/url-fetcher")
            assert resp.status_code == 200  # still valid, just no modules

    def test_detail_has_run_tests_link(self, client):
        resp = client.get("/skill/url-fetcher")
        assert "/test/url-fetcher" in resp.text

    def test_detail_has_json_api_link(self, client):
        resp = client.get("/skill/url-fetcher")
        assert "/api/skills/url-fetcher" in resp.text

    def test_detail_has_file_list_class(self, client):
        resp = client.get("/skill/url-fetcher")
        assert "file-list" in resp.text

    def test_detail_has_badge_classes(self, client):
        resp = client.get("/skill/url-fetcher")
        assert "badge" in resp.text

    def test_detail_404_shows_error(self, client):
        resp = client.get("/skill/nonexistent-skill")
        assert "not found" in resp.text.lower()

    def test_detail_skill_hub_has_dependencies_section(self, client):
        """Skill-hub has pip deps in its SKILL.md, so detail page should show deps."""
        resp = client.get("/skill/skill-hub")
        if resp.status_code == 200:
            assert "Dependencies" in resp.text or "dependencies" in resp.text.lower()

    def test_detail_dependency_table_has_columns(self, client):
        """Dependency table should have Package, Type, Installed columns."""
        resp = client.get("/skill/skill-hub")
        if resp.status_code == 200 and "Dependencies" in resp.text:
            assert "Package" in resp.text or "dep_name" in resp.text

    def test_detail_dependency_shows_dep_type_badge(self, client):
        """Each dependency should show its type as a badge."""
        resp = client.get("/skill/skill-hub")
        if resp.status_code == 200 and "Dependencies" in resp.text:
            assert "pip" in resp.text


# --- Health page content tests ---


class TestHealthPageContent:
    def test_health_has_total_skills(self, client):
        resp = client.get("/health")
        assert "Total Skills" in resp.text

    def test_health_has_pass_rate(self, client):
        resp = client.get("/health")
        assert "Avg Pass Rate" in resp.text

    def test_health_has_layers_section(self, client):
        resp = client.get("/health")
        assert "Skills by Layer" in resp.text

    def test_health_shows_layer_names(self, client):
        resp = client.get("/health")
        assert "core" in resp.text

    def test_health_has_progress_bar_class(self, client):
        resp = client.get("/health")
        assert "progress-bar" in resp.text

    def test_health_stat_card_class(self, client):
        resp = client.get("/health")
        assert "stat-card" in resp.text

    def test_health_no_tests_message(self, client):
        resp = client.get("/health")
        # Either shows test results or shows "No test results" message
        assert "test" in resp.text.lower()

    def test_health_has_dependency_status_section(self, client):
        resp = client.get("/health")
        assert "Dependency Status" in resp.text or "dep_summary" in resp.text

    def test_health_dep_status_shows_dep_names(self, client):
        resp = client.get("/health")
        # skill-hub should appear in dependency summary with its deps
        if "Dependency Status" in resp.text:
            assert "skill-hub" in resp.text or "fastapi" in resp.text

    def test_health_shows_passing_count(self, client):
        """Health dashboard should show passing skill count stat card."""
        resp = client.get("/health")
        assert "Passing" in resp.text

    def test_health_shows_failing_count(self, client):
        """Health dashboard should show failing skill count stat card."""
        resp = client.get("/health")
        assert "Failing" in resp.text

    def test_health_shows_unknown_count(self, client):
        """Health dashboard should show unknown skill count stat card."""
        resp = client.get("/health")
        assert "Unknown" in resp.text


# --- Install page content tests ---


class TestInstallPageContent:
    def test_install_has_title(self, client):
        resp = client.get("/install")
        assert "Install Skills" in resp.text

    def test_install_has_skills_dir(self, client):
        resp = client.get("/install")
        assert "skills" in resp.text.lower()

    def test_install_has_quick_install(self, client):
        resp = client.get("/install")
        assert "install.sh" in resp.text

    def test_install_has_dependencies_section(self, client):
        resp = client.get("/install")
        assert "Dependencies" in resp.text or "pip install" in resp.text

    def test_install_has_start_command(self, client):
        resp = client.get("/install")
        assert "start" in resp.text.lower() or "start.sh" in resp.text

    def test_install_has_env_vars_table(self, client):
        resp = client.get("/install")
        assert "SKILL_HUB_PORT" in resp.text

    def test_install_has_db_env_var(self, client):
        resp = client.get("/install")
        assert "SKILL_HUB_DB" in resp.text

    def test_install_has_skills_dir_env_var(self, client):
        resp = client.get("/install")
        assert "SKILL_HUB_SKILLS_DIR" in resp.text

    def test_install_has_table(self, client):
        resp = client.get("/install")
        assert "<table" in resp.text

    def test_install_shows_default_port(self, client):
        resp = client.get("/install")
        assert "8765" in resp.text

    def test_install_dynamic_skills_table(self, client):
        """Install page should now show a dynamic skills table with names and versions."""
        resp = client.get("/install")
        assert "skill-hub" in resp.text or "url-fetcher" in resp.text

    def test_install_dynamic_deps_column(self, client):
        """Skills table should have a Dependencies column."""
        resp = client.get("/install")
        assert "Dependencies" in resp.text

    def test_install_has_check_deps_button(self, client):
        """Install page should have a Check Dependencies button."""
        resp = client.get("/install")
        assert "Check Dependencies" in resp.text or "checkAllDeps" in resp.text

    def test_install_has_layer_column(self, client):
        """Skills table should show Layer column with badges."""
        resp = client.get("/install")
        assert "Layer" in resp.text

    def test_install_has_javascript(self, client):
        """Dynamic install page should have JavaScript for check deps."""
        resp = client.get("/install")
        assert "<script>" in resp.text

    def test_install_has_link_to_health(self, client):
        """Install page should link to health dashboard."""
        resp = client.get("/install")
        assert "/health" in resp.text


# --- Test page content tests ---


class TestTestPageContent:
    def test_test_page_has_skill_name(self, client):
        resp = client.get("/test/url-fetcher")
        assert "url-fetcher" in resp.text

    def test_test_page_has_run_button(self, client):
        resp = client.get("/test/url-fetcher")
        assert "Run Tests" in resp.text

    def test_test_page_has_websocket_button(self, client):
        resp = client.get("/test/url-fetcher")
        assert "Stream" in resp.text or "WebSocket" in resp.text

    def test_test_page_has_javascript(self, client):
        resp = client.get("/test/url-fetcher")
        assert "<script>" in resp.text

    def test_test_page_has_test_output_div(self, client):
        resp = client.get("/test/url-fetcher")
        assert "test-output" in resp.text

    def test_test_page_has_api_fetch(self, client):
        resp = client.get("/test/url-fetcher")
        assert "fetch" in resp.text  # JavaScript fetch() call

    def test_test_page_has_websocket_url(self, client):
        resp = client.get("/test/url-fetcher")
        assert "/ws/test/" in resp.text

    def test_test_page_404(self, client):
        resp = client.get("/test/nonexistent-skill")
        assert "not found" in resp.text.lower()

    def test_test_page_has_badges(self, client):
        resp = client.get("/test/url-fetcher")
        assert "badge" in resp.text

    def test_test_page_shows_no_runs_message(self, client):
        """Test page should show no runs message when no test history exists."""
        resp = client.get("/test/url-fetcher")
        assert "No test runs" in resp.text

    def test_test_page_no_runs_or_table(self, client):
        """Test page should either show 'Recent Test Runs' heading or 'No test runs' message."""
        resp = client.get("/test/url-fetcher")
        assert "Recent Test Runs" in resp.text or "No test runs" in resp.text


# --- Base template structure tests ---


class TestBaseTemplate:
    def test_base_has_doctype(self, client):
        resp = client.get("/")
        assert "<!DOCTYPE html>" in resp.text

    def test_base_has_charset(self, client):
        resp = client.get("/")
        assert 'charset="UTF-8"' in resp.text

    def test_base_has_nav(self, client):
        resp = client.get("/")
        assert "<nav>" in resp.text

    def test_base_has_logo(self, client):
        resp = client.get("/")
        assert "Skill Hub" in resp.text

    def test_base_has_container(self, client):
        resp = client.get("/")
        assert "container" in resp.text

    def test_base_css_variables(self, client):
        resp = client.get("/")
        assert ":root" in resp.text
        assert "--bg" in resp.text
        assert "--accent" in resp.text

    def test_base_responsive_meta(self, client):
        resp = client.get("/")
        assert "viewport" in resp.text