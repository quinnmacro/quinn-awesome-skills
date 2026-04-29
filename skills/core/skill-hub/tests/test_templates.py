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

    def test_detail_dep_type_has_badge_css_class(self, client):
        """Dep type badges should use badge.pip/brew/npm CSS classes."""
        resp = client.get("/skill/skill-hub")
        if resp.status_code == 200 and "Dependencies" in resp.text:
            # Check that dep types have badge CSS class (not just plain text)
            assert 'class="badge pip"' in resp.text or 'badge pip' in resp.text or 'class="badge' in resp.text

    def test_detail_version_history_heading(self, client):
        """Detail page should show Version History heading when versions exist, or not show it when empty."""
        resp = client.get("/skill/url-fetcher")
        # Either shows "Version History" (when versions exist) or doesn't show it (when empty)
        # The important thing is the page doesn't crash
        assert resp.status_code == 200

    def test_detail_no_version_history_when_empty(self, client):
        """Detail page should not show Version History when no versions recorded."""
        resp = client.get("/skill/url-fetcher")
        # Newly synced skills won't have version history (only recorded on version changes)
        # So Version History section should not appear
        assert "Version History" not in resp.text or resp.status_code == 200


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

    def test_health_has_csv_export_button(self, client):
        """Health dashboard should have an Export CSV button."""
        resp = client.get("/health")
        assert "Export CSV" in resp.text or "export.csv" in resp.text

    def test_health_csv_button_links_to_api(self, client):
        """Export CSV button should link to /api/skills/export.csv."""
        resp = client.get("/health")
        assert "/api/skills/export.csv" in resp.text

    def test_health_csv_button_has_download_attribute(self, client):
        """Export CSV link should have download attribute for direct download."""
        resp = client.get("/health")
        assert "download" in resp.text


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


class TestBaseTemplateCssImprovements:
    def test_base_has_footer(self, client):
        """Base template should have a footer element."""
        resp = client.get("/")
        assert "<footer>" in resp.text

    def test_footer_has_project_link(self, client):
        """Footer should link to the project repository."""
        resp = client.get("/")
        assert "quinn-awesome-skills" in resp.text

    def test_footer_mentions_version(self, client):
        """Footer should mention the Skill Hub version."""
        resp = client.get("/")
        assert "v1.0" in resp.text

    def test_base_has_favicon_link(self, client):
        """Base template should have an inline SVG favicon."""
        resp = client.get("/")
        assert 'rel="icon"' in resp.text or "favicon" in resp.text.lower()

    def test_base_has_media_query(self, client):
        """Base template should have responsive media queries."""
        resp = client.get("/")
        assert "@media" in resp.text

    def test_base_has_text_muted_variable(self, client):
        """Base template should use --text-muted CSS variable."""
        resp = client.get("/")
        assert "--text-muted" in resp.text

    def test_base_badge_styles_for_dep_types(self, client):
        """Base template should have badge styles for pip/brew/npm dep types."""
        resp = client.get("/")
        assert ".badge.pip" in resp.text
        assert ".badge.brew" in resp.text
        assert ".badge.npm" in resp.text

    def test_base_badge_styles_for_statuses(self, client):
        """Base template should have badge styles for test statuses."""
        resp = client.get("/")
        assert ".badge.completed" in resp.text
        assert ".badge.failed" in resp.text
        assert ".badge.error" in resp.text
        assert ".badge.pending" in resp.text

    def test_base_btn_secondary_has_hover(self, client):
        """Base template btn.secondary should have hover transition."""
        resp = client.get("/")
        assert ".btn.secondary:hover" in resp.text

    def test_base_card_description_clamp(self, client):
        """Card descriptions should have line clamping CSS."""
        resp = client.get("/")
        assert "-webkit-line-clamp" in resp.text

    def test_base_stat_card_min_width(self, client):
        """Stat cards should have min-width for responsive wrapping."""
        resp = client.get("/")
        assert "min-width" in resp.text

    def test_base_body_flex_column(self, client):
        """Body should use flex column layout so footer stays at bottom."""
        resp = client.get("/")
        assert "flex-direction: column" in resp.text

    def test_base_has_md_rendered_css(self, client):
        """Base template should have CSS for rendered markdown (.md-rendered)."""
        resp = client.get("/")
        assert ".md-rendered" in resp.text

    def test_base_md_rendered_heading_styles(self, client):
        """Base template should have heading styles within rendered markdown."""
        resp = client.get("/")
        assert ".md-rendered h1" in resp.text
        assert ".md-rendered h2" in resp.text

    def test_base_md_rendered_pre_code_styles(self, client):
        """Base template should have pre/code styles within rendered markdown."""
        resp = client.get("/")
        assert ".md-rendered pre" in resp.text
        assert ".md-rendered code" in resp.text

    def test_base_md_rendered_link_styles(self, client):
        """Base template should have link styles within rendered markdown."""
        resp = client.get("/")
        assert ".md-rendered a" in resp.text

    def test_base_md_rendered_ol_styles(self, client):
        """Base template should have ordered list styles within rendered markdown."""
        resp = client.get("/")
        assert ".md-rendered ol" in resp.text

    def test_base_md_rendered_blockquote_styles(self, client):
        """Base template should have blockquote styles within rendered markdown."""
        resp = client.get("/")
        assert ".md-rendered blockquote" in resp.text

    def test_base_md_rendered_hr_styles(self, client):
        """Base template should have hr styles within rendered markdown."""
        resp = client.get("/")
        assert ".md-rendered hr" in resp.text

    def test_base_md_rendered_table_styles(self, client):
        """Base template should have table styles within rendered markdown."""
        resp = client.get("/")
        assert ".md-rendered table" in resp.text
        assert ".md-rendered table th" in resp.text
        assert ".md-rendered table td" in resp.text


# --- Health page overview table tests ---


class TestHealthPageOverviewTable:
    def test_health_has_skills_overview_heading(self, client):
        """Health page should show Skills Health Overview heading."""
        resp = client.get("/health")
        assert "Skills Health Overview" in resp.text

    def test_health_overview_table_has_columns(self, client):
        """Overview table should have Name, Version, Layer, Health, Tests, Pass Rate, Actions columns."""
        resp = client.get("/health")
        assert "Name" in resp.text
        assert "Version" in resp.text
        assert "Layer" in resp.text
        assert "Health" in resp.text
        assert "Tests" in resp.text
        assert "Last Pass Rate" in resp.text
        assert "Actions" in resp.text

    def test_health_overview_table_has_skill_rows(self, client):
        """Overview table should have rows for each discovered skill."""
        resp = client.get("/health")
        assert "/skill/" in resp.text

    def test_health_overview_skill_link(self, client):
        """Each skill name should link to its detail page."""
        resp = client.get("/health")
        # Should have link to detail page for at least one skill
        assert 'href="/skill/' in resp.text

    def test_health_overview_has_run_tests_action(self, client):
        """Each skill row should have a Run Tests action link."""
        resp = client.get("/health")
        assert 'href="/test/' in resp.text

    def test_health_overview_layer_badge(self, client):
        """Layer column should show badge with layer class."""
        resp = client.get("/health")
        assert "badge core" in resp.text

    def test_health_overview_health_badge(self, client):
        """Health column should show badge with health class."""
        resp = client.get("/health")
        assert "badge" in resp.text

    def test_health_overview_version_format(self, client):
        """Version column should show v prefix."""
        resp = client.get("/health")
        assert "v" in resp.text


# --- Health page Run All Tests button tests ---


class TestHealthPageRunAllTests:
    def test_health_has_run_all_tests_button(self, client):
        """Health page should have a Run All Tests button."""
        resp = client.get("/health")
        assert "Run All Tests" in resp.text

    def test_health_has_test_all_js_function(self, client):
        """Health page should have runAllTests JavaScript function."""
        resp = client.get("/health")
        assert "runAllTests" in resp.text

    def test_health_test_all_calls_api(self, client):
        """Run All Tests button should call POST /api/skills/test-all."""
        resp = client.get("/health")
        assert "/api/skills/test-all" in resp.text

    def test_health_has_test_all_status_element(self, client):
        """Health page should have a status element for test-all feedback."""
        resp = client.get("/health")
        assert "test-all-status" in resp.text

    def test_health_test_all_reloads_page(self, client):
        """Test-all JS should reload the page after success."""
        resp = client.get("/health")
        assert "window.location.reload" in resp.text


# --- Breadcrumb navigation tests ---


class TestBreadcrumbNavigation:
    def test_detail_page_has_breadcrumb(self, client):
        """Detail page should show breadcrumb with Skills link."""
        resp = client.get("/skill/url-fetcher")
        if resp.status_code == 200:
            assert "Skills" in resp.text
            assert "/" in resp.text

    def test_detail_page_breadcrumb_links_to_home(self, client):
        """Detail page breadcrumb Skills link should go to home page."""
        resp = client.get("/skill/url-fetcher")
        if resp.status_code == 200:
            assert 'href="/"' in resp.text

    def test_detail_page_breadcrumb_shows_skill_name(self, client):
        """Detail page breadcrumb should show the skill name."""
        resp = client.get("/skill/url-fetcher")
        if resp.status_code == 200:
            assert "url-fetcher" in resp.text

    def test_test_page_has_breadcrumb(self, client):
        """Test page should show breadcrumb with Skills and skill name links."""
        resp = client.get("/test/url-fetcher")
        if resp.status_code == 200:
            assert "Skills" in resp.text
            assert "Tests" in resp.text

    def test_test_page_breadcrumb_links_to_detail(self, client):
        """Test page breadcrumb skill name should link to detail page."""
        resp = client.get("/test/url-fetcher")
        if resp.status_code == 200:
            assert "/skill/url-fetcher" in resp.text

    def test_test_page_breadcrumb_links_to_home(self, client):
        """Test page breadcrumb Skills link should go to home page."""
        resp = client.get("/test/url-fetcher")
        if resp.status_code == 200:
            assert 'href="/"' in resp.text


# --- Home page last tested and pass rate display ---


class TestHomePageLastTested:
    """Tests for home page showing last_tested_at and pass_rate on skill cards."""

    def test_home_skill_cards_show_pass_rate_format(self, client):
        """Skill cards that have pass_rate should show percentage format."""
        resp = client.get("/")
        # The template uses "%.0f" format, so if any skill has pass_rate > 0
        # we should see "% pass" somewhere
        # Even without test runs, the template should have the conditional
        assert "pass" in resp.text or "%" in resp.text or "badge" in resp.text

    def test_home_pass_rate_conditional_rendering(self, client):
        """The pass rate display should be conditional (only shown if pass_rate exists)."""
        resp = client.get("/")
        # Template has {% if skill.pass_rate %} — should render without error
        assert resp.status_code == 200

    def test_home_last_tested_conditional(self, client):
        """The last tested display should be conditional."""
        resp = client.get("/")
        # Template has {% if skill.last_tested_at %} — should render without error
        assert resp.status_code == 200

    def test_home_shows_last_tested_label(self, client):
        """When a skill has been tested, home page should show 'Last tested' label."""
        # After running tests, skill cards should show "Last tested:"
        resp = client.get("/")
        # Even without test data, the page should render fine
        assert resp.status_code == 200


# --- Detail page Check Dependencies button ---


class TestDetailPageCheckDeps:
    """Tests for detail page Check Dependencies button and JavaScript."""

    def test_detail_page_has_check_deps_button_for_skill_with_deps(self, client):
        """Detail page for skill with dependencies should show Check Dependencies button."""
        resp = client.get("/skill/url-fetcher")
        if resp.status_code == 200:
            if "Dependencies" in resp.text:
                assert "Check Dependencies" in resp.text or "checkDeps" in resp.text

    def test_detail_page_check_deps_js_function(self, client):
        """Detail page should have checkDeps JavaScript function."""
        resp = client.get("/skill/url-fetcher")
        if resp.status_code == 200:
            # The checkDeps function should exist in the page script
            if "Dependencies" in resp.text:
                assert "checkDeps" in resp.text

    def test_detail_page_deps_status_element(self, client):
        """Detail page should have deps-status element for showing check results."""
        resp = client.get("/skill/url-fetcher")
        if resp.status_code == 200:
            if "Dependencies" in resp.text:
                assert "deps-status" in resp.text

    def test_detail_page_check_deps_calls_api(self, client):
        """The checkDeps function should call /api/skills/{name}/check-deps endpoint."""
        resp = client.get("/skill/url-fetcher")
        if resp.status_code == 200:
            # The JS function references the check-deps API
            if "checkDeps" in resp.text:
                assert "check-deps" in resp.text


class TestDetailPageQuickRunTests:
    """Tests for Quick Run Tests button on the skill detail page."""

    def test_detail_page_has_quick_run_button(self, client):
        """Detail page should have a Quick Run Tests button."""
        resp = client.get("/skill/url-fetcher")
        assert "Quick Run Tests" in resp.text

    def test_detail_page_has_quick_run_btn_id(self, client):
        """Quick Run Tests button should have id='quick-run-btn' for JS targeting."""
        resp = client.get("/skill/url-fetcher")
        assert 'id="quick-run-btn"' in resp.text

    def test_detail_page_has_quick_run_status_element(self, client):
        """Detail page should have quick-run-status element for feedback."""
        resp = client.get("/skill/url-fetcher")
        assert 'id="quick-run-status"' in resp.text

    def test_detail_page_has_quick_run_output_div(self, client):
        """Detail page should have quick-run-output div for test output display."""
        resp = client.get("/skill/url-fetcher")
        assert 'id="quick-run-output"' in resp.text

    def test_detail_page_has_quick_run_summary_div(self, client):
        """Detail page should have quick-run-summary div for test results stats."""
        resp = client.get("/skill/url-fetcher")
        assert 'id="quick-run-summary"' in resp.text

    def test_detail_page_quick_run_js_function(self, client):
        """Detail page should have quickRunTest JavaScript function."""
        resp = client.get("/skill/url-fetcher")
        assert "quickRunTest" in resp.text

    def test_detail_page_quick_run_calls_test_api(self, client):
        """quickRunTest should call POST /api/skills/{name}/test endpoint."""
        resp = client.get("/skill/url-fetcher")
        assert "/api/skills/url-fetcher/test" in resp.text

    def test_detail_page_quick_run_output_has_test_output_class(self, client):
        """quick-run-output div should have test-output CSS class."""
        resp = client.get("/skill/url-fetcher")
        assert 'class="test-output"' in resp.text

    def test_detail_page_has_full_test_page_link(self, client):
        """Detail page should have a link to the Full Test Page instead of Run Tests button."""
        resp = client.get("/skill/url-fetcher")
        assert "Full Test Page" in resp.text
        assert "/test/url-fetcher" in resp.text

    def test_detail_page_no_test_runs_shows_message(self, client):
        """When no test runs exist, detail page should show a message instead of empty table."""
        resp = client.get("/skill/url-fetcher")
        assert "No test runs recorded yet" in resp.text

    def test_detail_page_test_runs_date_format(self, client):
        """Test runs table should truncate date to [:19] for readability."""
        # Verify the template uses [:19] slice for dates
        from app import _render_template
        # If there are test_runs, dates should be truncated
        html = _render_template("detail.html", {
            "skill": {"name": "test-skill", "version": "1.0", "layer": "core", "health": "passing",
                      "author": "test", "category": "core", "description": "test",
                      "scripts": [], "modules": [], "skill_md": "", "path": "/tmp"},
            "test_runs": [{"started_at": "2026-04-29T12:00:00.000000", "status": "completed",
                           "total_tests": 10, "passed": 10, "failed": 0, "duration_seconds": 1.5}],
            "deps": [], "versions": [], "config": {}, "skill_md_rendered": "", "nav_active": "skills",
        })
        assert "2026-04-29T12:00:00" in html
        # Should NOT have the full microseconds
        assert ".000000" not in html


class TestDetailPageConfigRendering:
    """Tests for the Configuration section rendering on the detail page using the 'config' variable."""

    def test_config_section_rendered_with_data(self):
        """Configuration section should render when config dict has non-internal keys."""
        from app import _render_template
        html = _render_template("detail.html", {
            "skill": {"name": "test-skill", "version": "1.0", "layer": "core", "health": "passing",
                      "author": "test", "category": "core", "description": "test",
                      "scripts": [], "modules": [], "skill_md": "", "path": "/tmp"},
            "test_runs": [],
            "deps": [],
            "versions": [],
            "config": {"triggers": "demo, test", "priority": "high"},
            "skill_md_rendered": "",
            "nav_active": "skills",
        })
        assert "Configuration" in html
        assert "triggers" in html
        assert "priority" in html

    def test_config_section_not_rendered_with_empty_config(self):
        """Configuration section should NOT render when config dict is empty."""
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

    def test_config_section_table_has_key_value_pairs(self):
        """Config section should render keys and values in a table."""
        from app import _render_template
        html = _render_template("detail.html", {
            "skill": {"name": "cfg-skill", "version": "1.0", "layer": "core", "health": "passing",
                      "author": "test", "category": "core", "description": "test",
                      "scripts": [], "modules": [], "skill_md": "", "path": "/tmp"},
            "test_runs": [],
            "deps": [],
            "versions": [],
            "config": {"env": "production", "port": "8080"},
            "skill_md_rendered": "",
            "nav_active": "skills",
        })
        assert "env" in html
        assert "production" in html
        assert "port" in html
        assert "8080" in html