"""Tests for __init__.py exports and start.sh script behavior."""

import sys
import os
import subprocess
from pathlib import Path

import pytest

SKILL_HUB_DIR = Path(__file__).resolve().parent.parent
MODULES_DIR = SKILL_HUB_DIR / "modules"
SCRIPTS_DIR = SKILL_HUB_DIR / "scripts"
PROJECT_ROOT = SKILL_HUB_DIR.parent.parent.parent

if str(MODULES_DIR) not in sys.path:
    sys.path.insert(0, str(MODULES_DIR))
if str(SKILL_HUB_DIR) not in sys.path:
    sys.path.insert(0, str(SKILL_HUB_DIR))

import modules as _modules_pkg


# --- __init__.py export tests ---


class TestModuleExports:
    """Verify all public functions are exported from __init__.py."""

    def test_skill_discovery_exports(self):
        assert hasattr(_modules_pkg, 'discover_skills')
        assert hasattr(_modules_pkg, 'get_skill_by_name')
        assert hasattr(_modules_pkg, 'search_skills')
        assert hasattr(_modules_pkg, '_yaml_frontmatter')
        assert hasattr(_modules_pkg, '_extract_dependencies')
        assert hasattr(_modules_pkg, '_parse_description')
        assert hasattr(_modules_pkg, '_list_scripts')
        assert hasattr(_modules_pkg, '_list_modules')
        assert hasattr(_modules_pkg, '_layer_from_category')
        assert hasattr(_modules_pkg, 'check_dep_installed')
        assert hasattr(_modules_pkg, 'check_all_deps')

    def test_database_exports(self):
        assert hasattr(_modules_pkg, 'init_db')
        assert hasattr(_modules_pkg, 'upsert_skill')
        assert hasattr(_modules_pkg, 'get_all_skills')
        assert hasattr(_modules_pkg, 'get_skill')
        assert hasattr(_modules_pkg, 'search_skills_db')
        assert hasattr(_modules_pkg, 'record_test_run')
        assert hasattr(_modules_pkg, 'get_test_runs')
        assert hasattr(_modules_pkg, 'get_recent_test_runs')
        assert hasattr(_modules_pkg, 'get_health_stats')
        assert hasattr(_modules_pkg, 'sync_skills')
        assert hasattr(_modules_pkg, 'sync_dependencies')
        assert hasattr(_modules_pkg, 'upsert_dependency')
        assert hasattr(_modules_pkg, 'get_dependencies')
        assert hasattr(_modules_pkg, 'record_version')
        assert hasattr(_modules_pkg, 'get_versions')
        assert hasattr(_modules_pkg, 'delete_skill')
        assert hasattr(_modules_pkg, 'delete_test_runs')
        assert hasattr(_modules_pkg, 'DEFAULT_DB_PATH')

    def test_discover_skills_callable(self):
        assert callable(_modules_pkg.discover_skills)

    def test_init_db_callable(self):
        assert callable(_modules_pkg.init_db)

    def test_check_dep_installed_callable(self):
        assert callable(_modules_pkg.check_dep_installed)

    def test_check_all_deps_callable(self):
        assert callable(_modules_pkg.check_all_deps)

    def test_extract_dependencies_callable(self):
        assert callable(_modules_pkg._extract_dependencies)

    def test_sync_dependencies_callable(self):
        assert callable(_modules_pkg.sync_dependencies)

    def test_record_version_callable(self):
        assert callable(_modules_pkg.record_version)

    def test_get_versions_callable(self):
        assert callable(_modules_pkg.get_versions)

    def test_upsert_dependency_callable(self):
        assert callable(_modules_pkg.upsert_dependency)

    def test_get_dependencies_callable(self):
        assert callable(_modules_pkg.get_dependencies)

    def test_default_db_path_is_string(self):
        assert isinstance(_modules_pkg.DEFAULT_DB_PATH, str)
        assert _modules_pkg.DEFAULT_DB_PATH.endswith('skill-hub.db')

    def test_layer_from_category_callable(self):
        assert callable(_modules_pkg._layer_from_category)

    def test_parse_description_callable(self):
        assert callable(_modules_pkg._parse_description)

    def test_delete_skill_callable(self):
        assert callable(_modules_pkg.delete_skill)

    def test_delete_test_runs_callable(self):
        assert callable(_modules_pkg.delete_test_runs)

    def test_get_recent_test_runs_callable(self):
        assert callable(_modules_pkg.get_recent_test_runs)


# --- start.sh script tests ---


class TestStartScript:
    """Test start.sh script structure and behavior."""

    def test_start_script_exists(self):
        script = SCRIPTS_DIR / "start.sh"
        assert script.exists()

    def test_start_script_is_executable(self):
        script = SCRIPTS_DIR / "start.sh"
        assert os.access(script, os.X_OK)

    def test_start_script_has_shebang(self):
        script = SCRIPTS_DIR / "start.sh"
        content = script.read_text()
        assert content.startswith("#!/usr/bin/env bash")

    def test_start_script_has_set_euo_pipefail(self):
        script = SCRIPTS_DIR / "start.sh"
        content = script.read_text()
        assert "set -euo pipefail" in content

    def test_start_script_handles_stop_flag(self):
        script = SCRIPTS_DIR / "start.sh"
        content = script.read_text()
        assert "--stop" in content or "stop)" in content

    def test_start_script_handles_status_flag(self):
        script = SCRIPTS_DIR / "start.sh"
        content = script.read_text()
        assert "--status" in content or "status)" in content

    def test_start_script_handles_port_argument(self):
        script = SCRIPTS_DIR / "start.sh"
        content = script.read_text()
        assert "SKILL_HUB_PORT" in content
        # Port argument: numeric check
        assert "[0-9]" in content

    def test_start_script_has_pid_file(self):
        script = SCRIPTS_DIR / "start.sh"
        content = script.read_text()
        assert "PID_FILE" in content

    def test_start_script_uses_nohup(self):
        script = SCRIPTS_DIR / "start.sh"
        content = script.read_text()
        assert "nohup" in content

    def test_start_script_has_lsof_fallback(self):
        script = SCRIPTS_DIR / "start.sh"
        content = script.read_text()
        assert "lsof" in content

    def test_start_script_checks_already_running(self):
        script = SCRIPTS_DIR / "start.sh"
        content = script.read_text()
        assert "already running" in content

    def test_start_script_default_port(self):
        script = SCRIPTS_DIR / "start.sh"
        content = script.read_text()
        assert "8765" in content

    def test_start_script_clean_stale_pid(self):
        script = SCRIPTS_DIR / "start.sh"
        content = script.read_text()
        assert "stale" in content.lower()


class TestStartScriptExecution:
    """Test start.sh actual execution behavior (non-destructive)."""

    def test_status_flag_when_not_running(self):
        script = SCRIPTS_DIR / "start.sh"
        result = subprocess.run(
            ["bash", str(script), "--status"],
            capture_output=True, text=True, timeout=5,
            env={**os.environ, "SKILL_HUB_PID_FILE": "/tmp/test_skill_hub_status.pid"},
        )
        assert "not running" in result.stdout.lower() or "no pid file" in result.stdout.lower()

    def test_stop_flag_when_not_running(self):
        script = SCRIPTS_DIR / "start.sh"
        result = subprocess.run(
            ["bash", str(script), "--stop"],
            capture_output=True, text=True, timeout=5,
            env={**os.environ, "SKILL_HUB_PID_FILE": "/tmp/test_skill_hub_stop.pid"},
        )
        # Should either say "No PID file" or "not running" or "cleaned"
        output = result.stdout.lower()
        assert "no pid" in output or "not running" in output or "cleaned" in output or "stopped" in output


class TestStartScriptLogging:
    """Test start.sh server log output configuration."""

    def test_start_script_has_log_dir(self):
        script = SCRIPTS_DIR / "start.sh"
        content = script.read_text()
        assert "LOG_DIR" in content

    def test_start_script_has_log_file(self):
        script = SCRIPTS_DIR / "start.sh"
        content = script.read_text()
        assert "LOG_FILE" in content

    def test_start_script_log_file_path(self):
        """Log file path uses .quinn-skills directory."""
        script = SCRIPTS_DIR / "start.sh"
        content = script.read_text()
        assert ".quinn-skills" in content

    def test_start_script_no_dev_null_redirect(self):
        """Start.sh no longer redirects all output to /dev/null."""
        script = SCRIPTS_DIR / "start.sh"
        content = script.read_text()
        # The old pattern was &>/dev/null — the new pattern uses log file
        assert "&>/dev/null" not in content

    def test_start_script_redirects_to_log_file(self):
        """Start.sh redirects output to log file instead of /dev/null."""
        script = SCRIPTS_DIR / "start.sh"
        content = script.read_text()
        assert "$LOG_FILE" in content

    def test_start_script_creates_log_dir(self):
        """Start.sh creates log directory before starting server."""
        script = SCRIPTS_DIR / "start.sh"
        content = script.read_text()
        assert "mkdir -p \"$LOG_DIR\"" in content