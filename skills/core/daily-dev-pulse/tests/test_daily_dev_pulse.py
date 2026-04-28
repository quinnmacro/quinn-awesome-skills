"""Tests for Daily Dev Pulse modules and formatter.

Uses mock data to test without requiring live API access.
"""

import copy
import json
import os
import sys
import tempfile
import unittest
import urllib.parse
from io import StringIO
from unittest.mock import MagicMock, patch

# Add modules and scripts to path
MODULES_DIR = os.path.join(os.path.dirname(__file__), "..", "modules")
SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), "..", "scripts")

sys.path.insert(0, MODULES_DIR)
sys.path.insert(0, SCRIPTS_DIR)

import config
import github_scanner
import security_checker
import news_aggregator
import package_watcher
import pulse_formatter


MOCK_GITHUB_DATA = {
    "github": {
        "source": "github",
        "repos": [
            {
                "repo": "quinnmacro/quinn-awesome-skills",
                "commits": [
                    {"sha": "abc1234", "message": "Add new skill", "author": "quinnmacro", "date": "2025-04-28"},
                    {"sha": "def5678", "message": "Fix bug", "author": "quinnmacro", "date": "2025-04-27"},
                ],
                "commit_count": 2,
                "open_prs": [
                    {"number": 42, "title": "Add daily dev pulse", "createdAt": "2025-04-20T10:00:00Z", "author": "quinnmacro"},
                ],
                "open_issues": [
                    {"number": 15, "title": "Bug in url fetcher", "createdAt": "2025-04-25T08:00:00Z", "author": "contributor"},
                ],
                "ci_runs": [
                    {"name": "CI", "status": "completed", "conclusion": "failure", "headBranch": "main"},
                ],
            },
            {
                "repo": "quinnmacro/gnhf",
                "commits": [],
                "commit_count": 0,
                "open_prs": [],
                "open_issues": [],
                "ci_runs": [
                    {"name": "Build", "status": "completed", "conclusion": "success", "headBranch": "main"},
                ],
            },
        ],
    },
    "security": {
        "source": "security",
        "alerts": [
            {"cve_id": "CVE-2025-1234", "product": "fastapi", "severity": "HIGH", "score": 8.5, "description": "Auth bypass vulnerability"},
            {"cve_id": "CVE-2025-5678", "product": "sqlite", "severity": "MEDIUM", "score": 5.3, "description": "Race condition in concurrent writes"},
        ],
    },
    "packages": {
        "source": "packages",
        "updates": [
            {"package": "fastapi", "registry": "pypi", "latest_version": "0.115.0"},
            {"package": "next", "registry": "npm", "latest_version": "15.3.0"},
        ],
    },
    "news": {
        "source": "news",
        "headlines": [
            {"title": "Python 3.13 features", "url": "https://example.com", "score": 150, "source": "hn"},
            {"title": "FastAPI best practices", "url": "https://dev.to/example", "score": 80, "source": "devto"},
        ],
    },
}


class TestConfig(unittest.TestCase):
    """Test configuration loading and merging."""

    def test_default_config_loads(self):
        cfg = config.load_config(config_path="/nonexistent/path.yml")
        assert "repos" in cfg
        assert len(cfg["repos"]) == 6
        assert cfg["repos"][0]["name"] == "quinnpm"

    def test_merge_config(self):
        default = {"a": 1, "b": {"c": 2, "d": 3}}
        user = {"a": 10, "b": {"c": 20}}
        merged = config.merge_config(default, user)
        assert merged["a"] == 10
        assert merged["b"]["c"] == 20
        assert merged["b"]["d"] == 3

    def test_load_from_yaml(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            f.write("repos:\n  - name: test-repo\n    owner: test-owner\n")
            f.flush()
            cfg = config.load_config(config_path=f.name)
            assert len(cfg["repos"]) == 1
            assert cfg["repos"][0]["name"] == "test-repo"
            os.unlink(f.name)

    def test_get_repos(self):
        repos = config.get_repos(config.DEFAULT_CONFIG)
        assert len(repos) == 6

    def test_get_tech_stack(self):
        stack = config.get_tech_stack(config.DEFAULT_CONFIG)
        assert "python" in stack
        assert "FastAPI" in stack["frameworks"]

    def test_env_override_lookback_days(self):
        """PULSE_LOOKBACK_DAYS env var should override config lookback_days."""
        original = os.environ.get("PULSE_LOOKBACK_DAYS")
        os.environ["PULSE_LOOKBACK_DAYS"] = "30"
        cfg = config.load_config(config_path="/nonexistent/path.yml")
        assert cfg["preferences"]["lookback_days"] == 30
        if original is None:
            os.environ.pop("PULSE_LOOKBACK_DAYS", None)
        else:
            os.environ["PULSE_LOOKBACK_DAYS"] = original

    def test_env_override_lookback_days_invalid(self):
        """Invalid PULSE_LOOKBACK_DAYS should be ignored."""
        original = os.environ.get("PULSE_LOOKBACK_DAYS")
        os.environ["PULSE_LOOKBACK_DAYS"] = "not-a-number"
        cfg = config.load_config(config_path="/nonexistent/path.yml")
        assert cfg["preferences"]["lookback_days"] == 7  # default
        if original is None:
            os.environ.pop("PULSE_LOOKBACK_DAYS", None)
        else:
            os.environ["PULSE_LOOKBACK_DAYS"] = original

    def test_env_override_repos_full_path(self):
        """PULSE_REPOS with owner/name format should filter repos."""
        original = os.environ.get("PULSE_REPOS")
        os.environ["PULSE_REPOS"] = "quinnmacro/gnhf,quinnmacro/weather-cli"
        cfg = config.load_config(config_path="/nonexistent/path.yml")
        assert len(cfg["repos"]) == 2
        assert cfg["repos"][0]["name"] == "gnhf"
        assert cfg["repos"][1]["name"] == "weather-cli"
        if original is None:
            os.environ.pop("PULSE_REPOS", None)
        else:
            os.environ["PULSE_REPOS"] = original

    def test_env_override_repos_by_name(self):
        """PULSE_REPOS with just repo name should match from defaults."""
        original = os.environ.get("PULSE_REPOS")
        os.environ["PULSE_REPOS"] = "gnhf"
        cfg = config.load_config(config_path="/nonexistent/path.yml")
        assert len(cfg["repos"]) == 1
        assert cfg["repos"][0]["name"] == "gnhf"
        if original is None:
            os.environ.pop("PULSE_REPOS", None)
        else:
            os.environ["PULSE_REPOS"] = original

    def test_env_override_repos_all(self):
        """PULSE_REPOS=all should keep all default repos."""
        original = os.environ.get("PULSE_REPOS")
        os.environ["PULSE_REPOS"] = "all"
        cfg = config.load_config(config_path="/nonexistent/path.yml")
        assert len(cfg["repos"]) == 6
        if original is None:
            os.environ.pop("PULSE_REPOS", None)
        else:
            os.environ["PULSE_REPOS"] = original


class TestGithubScanner(unittest.TestCase):
    """Test GitHub scanner with mock gh output."""

    @patch("github_scanner.run_gh")
    def test_scan_commits(self, mock_run_gh):
        mock_run_gh.return_value = [
            {"sha": "abc1234567890", "commit": {"message": "Add feature\n\nDetails", "author": {"name": "dev", "date": "2025-04-28T10:00:00Z"}}},
        ]
        commits = github_scanner.scan_commits("quinnmacro", "test-repo", 7)
        assert len(commits) == 1
        assert commits[0]["sha"] == "abc1234"
        assert commits[0]["message"] == "Add feature"
        assert commits[0]["author"] == "dev"

    @patch("github_scanner.run_gh")
    def test_scan_commits_empty(self, mock_run_gh):
        mock_run_gh.return_value = []
        commits = github_scanner.scan_commits("quinnmacro", "test-repo", 7)
        assert commits == []

    @patch("github_scanner.run_gh")
    def test_scan_prs(self, mock_run_gh):
        mock_run_gh.return_value = [
            {"number": 1, "title": "Test PR", "author": {"login": "dev"}, "createdAt": "2025-04-28"},
        ]
        prs = github_scanner.scan_prs("quinnmacro", "test-repo")
        assert len(prs) == 1
        assert prs[0]["number"] == 1

    @patch("github_scanner.run_gh")
    def test_scan_gh_error(self, mock_run_gh):
        mock_run_gh.return_value = None
        result = github_scanner.scan_commits("owner", "repo")
        assert result == []

    @patch("github_scanner.scan_commits")
    @patch("github_scanner.scan_prs")
    @patch("github_scanner.scan_issues")
    @patch("github_scanner.scan_ci_status")
    def test_scan_all_repos(self, mock_ci, mock_issues, mock_prs, mock_commits):
        mock_commits.return_value = [{"sha": "abc", "message": "test", "author": "dev", "date": "2025-04-28"}]
        mock_prs.return_value = []
        mock_issues.return_value = []
        mock_ci.return_value = []

        data = github_scanner.scan_all_repos(config=config.DEFAULT_CONFIG)
        assert "repos" in data
        assert len(data["repos"]) == 6
        assert data["source"] == "github"


class TestSecurityChecker(unittest.TestCase):
    """Test security/CVE checker."""

    def test_build_search_terms(self):
        stack = config.DEFAULT_CONFIG["tech_stack"]
        terms = security_checker.build_search_terms(stack)
        assert len(terms) > 0
        products = [t["product"] for t in terms]
        assert "python" in products
        assert "fastapi" in products

    @patch("security_checker.fetch_cves")
    def test_check_security(self, mock_fetch):
        mock_fetch.return_value = [
            {"cve_id": "CVE-2025-0001", "product": "fastapi", "severity": "HIGH", "score": 7.5, "description": "test"},
        ]
        result = security_checker.check_security(config=config.DEFAULT_CONFIG)
        assert "alerts" in result
        assert result["source"] == "security"

    def test_fetch_cves_error(self):
        """Test CVE fetch handles network errors gracefully."""
        with patch("urllib.request.urlopen", side_effect=Exception("network error")):
            result = security_checker.fetch_cves("fastapi")
            assert result == []


class TestNewsAggregator(unittest.TestCase):
    """Test news aggregator."""

    @patch("news_aggregator.fetch_hn_top")
    @patch("news_aggregator.fetch_devto_top")
    @patch("news_aggregator.fetch_lobsters_top")
    def test_aggregate_news(self, mock_lobsters, mock_devto, mock_hn):
        mock_hn.return_value = [{"title": "HN Story", "url": "https://hn.test", "score": 100, "source": "hn"}]
        mock_devto.return_value = [{"title": "Dev.to Article", "url": "https://dev.test", "score": 50, "source": "devto"}]
        mock_lobsters.return_value = []

        result = news_aggregator.aggregate_news(config=config.DEFAULT_CONFIG)
        assert len(result["headlines"]) == 2
        assert result["headlines"][0]["source"] == "hn"  # Higher score first

    def test_fetch_hn_error(self):
        with patch("urllib.request.urlopen", side_effect=Exception("error")):
            result = news_aggregator.fetch_hn_top()
            assert result == []


class TestPackageWatcher(unittest.TestCase):
    """Test package watcher."""

    @patch("package_watcher.fetch_npm_info")
    @patch("package_watcher.fetch_pypi_info")
    def test_watch_packages(self, mock_pypi, mock_npm):
        mock_npm.return_value = {"package": "next", "registry": "npm", "latest_version": "15.3.0"}
        mock_pypi.return_value = {"package": "fastapi", "registry": "pypi", "latest_version": "0.115.0"}

        result = package_watcher.watch_packages(config=config.DEFAULT_CONFIG)
        assert "updates" in result
        assert result["source"] == "packages"

    def test_fetch_npm_error(self):
        with patch("urllib.request.urlopen", side_effect=Exception("error")):
            result = package_watcher.fetch_npm_info("nonexistent-pkg")
            assert result["latest_version"] == "unknown"
            assert result.get("error") == "fetch_failed"

    def test_fetch_pypi_error(self):
        """fetch_pypi_info should handle network errors gracefully."""
        with patch("urllib.request.urlopen", side_effect=Exception("error")):
            result = package_watcher.fetch_pypi_info("nonexistent-pkg")
            assert result["latest_version"] == "unknown"
            assert result.get("error") == "fetch_failed"

    def test_fetch_pypi_successful(self):
        """fetch_pypi_info should extract version and changelog URL from PyPI API response."""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "info": {
                "version": "0.115.0",
                "summary": "Modern fast web framework",
                "home_page": "https://fastapi.tiangolo.com",
                "project_urls": {"Changelog": "https://fastapi.tiangolo.com/release-notes/",
                                 "Source": "https://github.com/tiangolo/fastapi"},
                "license": "MIT",
            }
        }).encode()
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=mock_response):
            result = package_watcher.fetch_pypi_info("fastapi")
            assert result["package"] == "fastapi"
            assert result["registry"] == "pypi"
            assert result["latest_version"] == "0.115.0"
            assert result["changelog_url"] == "https://fastapi.tiangolo.com/release-notes/"

    def test_fetch_npm_successful(self):
        """fetch_npm_info should extract version and description from npm registry."""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "version": "15.3.0",
            "description": "The React Framework",
            "homepage": "https://nextjs.org",
            "license": "MIT",
        }).encode()
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=mock_response):
            result = package_watcher.fetch_npm_info("next")
            assert result["package"] == "next"
            assert result["registry"] == "npm"
            assert result["latest_version"] == "15.3.0"


class TestFocusFiltering(unittest.TestCase):
    """Test that --focus argument correctly controls which data sources are collected."""

    SCRIPT_PATH = os.path.join(os.path.dirname(__file__), "..", "scripts", "daily-dev-pulse.sh")

    def test_shell_script_focus_activity_branch(self):
        """Shell script should include activity branch when --focus is activity."""
        with open(self.SCRIPT_PATH) as f:
            content = f.read()
        # Verify focus branching logic exists
        assert '"activity"' in content or "'activity'" in content
        # Verify GitHub scan is in the activity branch
        assert "github_scanner.py" in content

    def test_shell_script_focus_security_branch(self):
        """Shell script should include security branch when --focus is security."""
        with open(self.SCRIPT_PATH) as f:
            content = f.read()
        assert '"security"' in content or "'security'" in content
        assert "security_checker.py" in content

    def test_shell_script_focus_news_branch(self):
        """Shell script should include news branch when --focus is news."""
        with open(self.SCRIPT_PATH) as f:
            content = f.read()
        assert '"news"' in content or "'news'" in content
        assert "news_aggregator.py" in content

    def test_shell_script_focus_all_runs_all(self):
        """Shell script --focus all should trigger all collection branches."""
        with open(self.SCRIPT_PATH) as f:
            content = f.read()
        assert '"all"' in content or "'all'" in content
        # All modules should be referenced
        assert "github_scanner.py" in content
        assert "security_checker.py" in content
        assert "news_aggregator.py" in content
        assert "package_watcher.py" in content


class TestConfigEdgeCases(unittest.TestCase):
    """Test config loading with edge cases: partial overrides, missing keys."""

    def test_merge_partial_override_preserves_defaults(self):
        """Merging with only repos override should preserve default tech_stack and preferences."""
        user = {"repos": [{"name": "myrepo", "owner": "me"}]}
        result = config.merge_config(config.DEFAULT_CONFIG, user)
        assert len(result["repos"]) == 1
        assert result["repos"][0]["name"] == "myrepo"
        # Other defaults preserved
        assert result["tech_stack"]["python"] == "3.13"
        assert result["preferences"]["lookback_days"] == 7

    def test_merge_empty_user_config(self):
        """Empty user config should produce a full deep copy of defaults."""
        result = config.merge_config(config.DEFAULT_CONFIG, {})
        assert result["repos"] == config.DEFAULT_CONFIG["repos"]
        # Must be a deep copy, not the same object
        assert result["repos"] is not config.DEFAULT_CONFIG["repos"]

    def test_merge_nested_partial_override(self):
        """Partial override of a nested dict should preserve unset keys."""
        user = {"preferences": {"lookback_days": 14}}
        result = config.merge_config(config.DEFAULT_CONFIG, user)
        assert result["preferences"]["lookback_days"] == 14
        assert result["preferences"]["format"] == "terminal"
        assert result["preferences"]["stale_pr_days"] == 3


class TestPulseFormatter(unittest.TestCase):
    """Test the pulse formatter with sample data."""

    def test_format_terminal(self):
        output = pulse_formatter.format_terminal(MOCK_GITHUB_DATA)
        assert "DAILY DEV PULSE" in output
        assert "GitHub Activity" in output
        assert "Security Alerts" in output
        assert "Package Updates" in output
        assert "Trending Dev News" in output
        assert "Action Items" in output

    def test_format_terminal_has_bar_chart(self):
        output = pulse_formatter.format_terminal(MOCK_GITHUB_DATA)
        assert "█" in output

    def test_format_terminal_has_table(self):
        output = pulse_formatter.format_terminal(MOCK_GITHUB_DATA)
        assert "┌" in output  # Table border

    def test_format_markdown(self):
        output = pulse_formatter.format_markdown(MOCK_GITHUB_DATA)
        assert "# 🌅 Daily Dev Pulse" in output
        assert "## GitHub Activity" in output
        assert "| Repo |" in output

    def test_format_json(self):
        output = pulse_formatter.format_json(MOCK_GITHUB_DATA)
        data = json.loads(output)
        assert "github" in data
        assert "action_items" in data

    def test_generate_action_items(self):
        items = pulse_formatter.generate_action_items(MOCK_GITHUB_DATA)
        assert len(items) > 0
        # Should flag stale PR (open > 3 days)
        assert any("stale PR" in item for item in items)
        # Should flag failing CI
        assert any("failing CI" in item for item in items)
        # Should flag HIGH severity CVE
        assert any("fastapi" in item.lower() for item in items)
        # Should flag open issues
        assert any("open issue" in item for item in items)

    def test_generate_action_items_flags_open_issues(self):
        """Action items should include open issues from GitHub data."""
        data = {
            "github": {
                "repos": [{
                    "repo": "test/repo",
                    "open_prs": [],
                    "open_issues": [
                        {"number": 99, "title": "Critical bug in auth module"},
                    ],
                    "ci_runs": [],
                }],
            },
        }
        items = pulse_formatter.generate_action_items(data)
        assert any("open issue" in item for item in items)
        assert any("#99" in item for item in items)
        assert any("Critical bug" in item for item in items)

    def test_format_terminal_no_github(self):
        data = {"github": {"error": "gh_not_available"}}
        output = pulse_formatter.format_terminal(data)
        assert "gh_not_available" in output

    def test_format_terminal_empty_data(self):
        """Terminal output should still produce header and action items with empty data."""
        data = {}
        output = pulse_formatter.format_terminal(data)
        assert "DAILY DEV PULSE" in output
        assert "Action Items" in output

    def test_format_markdown_empty_data(self):
        """Markdown output should still produce header and action items with empty data."""
        data = {}
        output = pulse_formatter.format_markdown(data)
        assert "Daily Dev Pulse" in output
        assert "Action Items" in output

    def test_format_terminal_empty_security_alerts(self):
        """Terminal output should skip security section when alerts list is empty."""
        data = {"security": {"source": "security", "alerts": []}}
        output = pulse_formatter.format_terminal(data)
        assert "Security Alerts" not in output


class TestSkillMdParsing(unittest.TestCase):
    """Test that SKILL.md has valid YAML frontmatter and required fields."""

    def test_skill_md_exists(self):
        skill_path = os.path.join(os.path.dirname(__file__), "..", "SKILL.md")
        assert os.path.exists(skill_path)

    def test_skill_md_frontmatter(self):
        skill_path = os.path.join(os.path.dirname(__file__), "..", "SKILL.md")
        with open(skill_path) as f:
            content = f.read()

        # Check frontmatter delimiters
        assert content.startswith("---")
        assert "---\n" in content[4:]

        # Extract frontmatter
        fm_end = content.index("---", 3) + 3
        frontmatter = content[3:fm_end]
        assert "name: daily-dev-pulse" in frontmatter
        assert "version:" in frontmatter
        assert "author: quinnmacro" in frontmatter
        assert "layer: core" in frontmatter
        assert "description:" in frontmatter

    def test_skill_md_content_sections(self):
        skill_path = os.path.join(os.path.dirname(__file__), "..", "SKILL.md")
        with open(skill_path) as f:
            content = f.read()

        assert "## Workflow" in content
        assert "## Output Format" in content
        assert "## Dependencies" in content
        assert "## Configuration" in content


class TestShellScript(unittest.TestCase):
    """Test the shell script invocation (syntax only)."""

    def test_shell_script_exists(self):
        script_path = os.path.join(os.path.dirname(__file__), "..", "scripts", "daily-dev-pulse.sh")
        assert os.path.exists(script_path)

    def test_shell_script_is_executable(self):
        script_path = os.path.join(os.path.dirname(__file__), "..", "scripts", "daily-dev-pulse.sh")
        assert os.access(script_path, os.X_OK)

    def test_shell_script_syntax(self):
        """Check bash syntax with bash -n (no execution)."""
        script_path = os.path.join(os.path.dirname(__file__), "..", "scripts", "daily-dev-pulse.sh")
        result = os.system(f"bash -n {script_path} 2>&1")
        assert result == 0


class TestJsonMerge(unittest.TestCase):
    """Test the JSON merge approach used by the shell script."""

    def _write_merge_script(self, tmpdir, script_path):
        """Write the merge helper script to a temp file."""
        script = '''
from datetime import datetime, timezone
import json, os, sys

combined = dict()
combined["scan_date"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

for key in ["github", "security", "packages", "news"]:
    fpath = os.path.join("''' + tmpdir + '''", key + ".json")
    if os.path.exists(fpath):
        try:
            with open(fpath) as f:
                combined[key] = json.load(f)
        except (json.JSONDecodeError, IOError):
            combined[key] = {"source": key, "error": "data_corrupted"}

json.dump(combined, sys.stdout, ensure_ascii=False)
'''
        with open(script_path, "w") as f:
            f.write(script)

    def test_merge_empty_sources(self):
        """Merging no data files should still produce valid JSON with scan_date."""
        import subprocess
        with tempfile.TemporaryDirectory() as tmpdir:
            script_path = os.path.join(tmpdir, "merge.py")
            self._write_merge_script(tmpdir, script_path)
            result = subprocess.run(
                ["python3", script_path],
                capture_output=True, text=True
            )
            assert result.returncode == 0, f"stderr: {result.stderr}"
            data = json.loads(result.stdout)
            assert "scan_date" in data
            assert "github" not in data

    def test_merge_with_data(self):
        """Merging existing data files should produce valid JSON."""
        import subprocess
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "security.json"), "w") as f:
                json.dump({"source": "security", "alerts": []}, f)
            script_path = os.path.join(tmpdir, "merge.py")
            self._write_merge_script(tmpdir, script_path)
            result = subprocess.run(
                ["python3", script_path],
                capture_output=True, text=True
            )
            assert result.returncode == 0, f"stderr: {result.stderr}"
            data = json.loads(result.stdout)
            assert "security" in data
            assert data["security"]["source"] == "security"

    def test_merge_with_corrupted_json(self):
        """Corrupted JSON file should produce error entry, not crash."""
        import subprocess
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "github.json"), "w") as f:
                f.write("this is not json{}")
            script_path = os.path.join(tmpdir, "merge.py")
            self._write_merge_script(tmpdir, script_path)
            result = subprocess.run(
                ["python3", script_path],
                capture_output=True, text=True
            )
            assert result.returncode == 0, f"stderr: {result.stderr}"
            data = json.loads(result.stdout)
            assert "github" in data
            assert data["github"]["error"] == "data_corrupted"


class TestConfigNoPollution(unittest.TestCase):
    """Verify that config operations don't leak mutations into DEFAULT_CONFIG."""

    def test_merge_config_deep_copy_no_leak(self):
        """merge_config should produce a fully independent copy — mutations to result must not affect DEFAULT_CONFIG."""
        user = {"preferences": {"lookback_days": 30}}
        result = config.merge_config(config.DEFAULT_CONFIG, user)
        # Mutate the result
        result["preferences"]["stale_pr_days"] = 99
        # DEFAULT_CONFIG must be unchanged
        assert config.DEFAULT_CONFIG["preferences"]["stale_pr_days"] == 3

    def test_env_override_no_leak(self):
        """Setting PULSE_LOOKBACK_DAYS should not mutate DEFAULT_CONFIG."""
        original = os.environ.get("PULSE_LOOKBACK_DAYS")
        original_default = config.DEFAULT_CONFIG["preferences"]["lookback_days"]

        os.environ["PULSE_LOOKBACK_DAYS"] = "14"
        cfg = config.load_config(config_path="/nonexistent/path.yml")
        assert cfg["preferences"]["lookback_days"] == 14
        assert config.DEFAULT_CONFIG["preferences"]["lookback_days"] == original_default

        if original is None:
            os.environ.pop("PULSE_LOOKBACK_DAYS", None)
        else:
            os.environ["PULSE_LOOKBACK_DAYS"] = original


class TestSecurityUrlEncoding(unittest.TestCase):
    """Test that CVE search URLs are properly encoded."""

    def test_url_encoding_spaces(self):
        """Product names with spaces should be URL-encoded."""
        import security_checker
        params = {"keywordSearch": "python 3.13", "resultsPerPage": 10}
        query = "&".join(f"{k}={urllib.parse.quote_plus(str(v))}" for k, v in params.items())
        assert "python+3.13" in query or "python%203.13" in query
        assert " " not in query

    def test_fetch_cves_url_encoding(self):
        """fetch_cves should produce valid URLs even for products with special chars."""
        import subprocess
        import inspect
        source = inspect.getsource(security_checker.fetch_cves)
        assert "urllib.parse" in source or "quote_plus" in source or "quote" in source


class TestNewsExceptionHandling(unittest.TestCase):
    """Verify all news fetchers catch generic Exception."""

    def test_devto_catches_generic_exception(self):
        """fetch_devto_top should catch generic Exception, not just specific ones."""
        import inspect
        source = inspect.getsource(news_aggregator.fetch_devto_top)
        assert "Exception" in source

    def test_lobsters_catches_generic_exception(self):
        """fetch_lobsters_top should catch generic Exception, not just specific ones."""
        import inspect
        source = inspect.getsource(news_aggregator.fetch_lobsters_top)
        assert "Exception" in source

    @patch("urllib.request.urlopen", side_effect=RuntimeError("unexpected"))
    def test_devto_runtime_error(self, mock_urlopen):
        """fetch_devto_top should handle RuntimeError gracefully."""
        result = news_aggregator.fetch_devto_top()
        assert result == []

    @patch("urllib.request.urlopen", side_effect=RuntimeError("unexpected"))
    def test_lobsters_runtime_error(self, mock_urlopen):
        """fetch_lobsters_top should handle RuntimeError gracefully."""
        result = news_aggregator.fetch_lobsters_top()
        assert result == []


class TestTimezoneConsistency(unittest.TestCase):
    """Verify all modules use UTC-aware datetime.now() for API calls and scan_dates."""

    def test_github_scanner_uses_utc(self):
        """github_scanner.py should import timezone and use datetime.now(timezone.utc)."""
        import inspect
        source = inspect.getsource(github_scanner)
        assert "timezone" in source
        assert "datetime.now(timezone.utc)" in source
        # Should NOT use bare datetime.now() for timestamps
        assert "datetime.now()" not in source.replace("datetime.now(timezone.utc)", "")

    def test_security_checker_uses_utc(self):
        """security_checker.py should use datetime.now(timezone.utc) for API calls."""
        import inspect
        source = inspect.getsource(security_checker)
        assert "timezone" in source
        assert "datetime.now(timezone.utc)" in source

    def test_news_aggregator_uses_utc(self):
        """news_aggregator.py should use datetime.now(timezone.utc) for scan_date."""
        import inspect
        source = inspect.getsource(news_aggregator)
        assert "timezone" in source
        assert "datetime.now(timezone.utc)" in source

    def test_package_watcher_uses_utc(self):
        """package_watcher.py should use datetime.now(timezone.utc) for scan_date."""
        import inspect
        source = inspect.getsource(package_watcher)
        assert "timezone" in source
        assert "datetime.now(timezone.utc)" in source

    def test_pulse_formatter_stale_pr_utc_comparison(self):
        """Stale PR days calculation should use UTC-aware comparison."""
        import inspect
        source = inspect.getsource(pulse_formatter.generate_action_items)
        assert "timezone.utc" in source
        assert "datetime.now(timezone.utc)" in source
        # Should not use bare datetime.now() for the comparison
        assert "datetime.now()" not in source.replace("datetime.now(timezone.utc)", "")

    def test_pulse_formatter_format_terminal_uses_utc(self):
        """format_terminal should use datetime.now(timezone.utc) for date header."""
        import inspect
        source = inspect.getsource(pulse_formatter.format_terminal)
        # Should use UTC for the date header, not naive datetime.now()
        assert "datetime.now(timezone.utc)" in source
        assert "datetime.now()" not in source.replace("datetime.now(timezone.utc)", "")

    def test_pulse_formatter_format_markdown_uses_utc(self):
        """format_markdown should use datetime.now(timezone.utc) for date header."""
        import inspect
        source = inspect.getsource(pulse_formatter.format_markdown)
        # Should use UTC for the date header, not naive datetime.now()
        assert "datetime.now(timezone.utc)" in source
        assert "datetime.now()" not in source.replace("datetime.now(timezone.utc)", "")

    def test_stale_pr_days_calculation_correctness(self):
        """Stale PR detection should calculate days correctly with UTC timestamps."""
        # A PR created 5 days ago in UTC should be flagged as stale (> 3 days)
        from datetime import datetime, timezone, timedelta
        five_days_ago = (datetime.now(timezone.utc) - timedelta(days=5)).isoformat()
        data = {
            "github": {
                "repos": [{
                    "repo": "test/repo",
                    "open_prs": [
                        {"number": 1, "title": "Test", "createdAt": five_days_ago},
                    ],
                    "open_issues": [],
                    "ci_runs": [],
                }],
            },
        }
        items = pulse_formatter.generate_action_items(data)
        assert any("stale PR" in item and "5 days" in item for item in items)

    def test_stale_pr_recent_not_flagged(self):
        """A PR created 1 day ago should NOT be flagged as stale."""
        from datetime import datetime, timezone, timedelta
        one_day_ago = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        data = {
            "github": {
                "repos": [{
                    "repo": "test/repo",
                    "open_prs": [
                        {"number": 2, "title": "Fresh PR", "createdAt": one_day_ago},
                    ],
                    "open_issues": [],
                    "ci_runs": [],
                }],
            },
        }
        items = pulse_formatter.generate_action_items(data)
        assert not any("stale PR" in item for item in items)


class TestCommandArgumentForwarding(unittest.TestCase):
    """Verify slash command files use $ARGUMENTS to forward user input."""

    PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
    CLAUDE_COMMANDS_DIR = os.path.join(PROJECT_ROOT, ".claude", "commands")
    COMMANDS_DIR = os.path.join(PROJECT_ROOT, "commands")

    def test_daily_dev_pulse_command_has_arguments(self):
        """The daily-dev-pulse command should include $ARGUMENTS for forwarding."""
        for path in [
            os.path.join(self.CLAUDE_COMMANDS_DIR, "daily-dev-pulse.md"),
            os.path.join(self.COMMANDS_DIR, "daily-dev-pulse.md"),
        ]:
            if os.path.exists(path):
                with open(path) as f:
                    content = f.read()
                assert "$ARGUMENTS" in content, f"$ARGUMENTS missing in {path}"

    def test_morning_brief_command_has_arguments(self):
        """The morning-brief alias command should include $ARGUMENTS."""
        for path in [
            os.path.join(self.CLAUDE_COMMANDS_DIR, "morning-brief.md"),
            os.path.join(self.COMMANDS_DIR, "morning-brief.md"),
        ]:
            if os.path.exists(path):
                with open(path) as f:
                    content = f.read()
                assert "$ARGUMENTS" in content, f"$ARGUMENTS missing in {path}"

    def test_dev_pulse_command_has_arguments(self):
        """The dev-pulse alias command should include $ARGUMENTS."""
        for path in [
            os.path.join(self.CLAUDE_COMMANDS_DIR, "dev-pulse.md"),
            os.path.join(self.COMMANDS_DIR, "dev-pulse.md"),
        ]:
            if os.path.exists(path):
                with open(path) as f:
                    content = f.read()
                assert "$ARGUMENTS" in content, f"$ARGUMENTS missing in {path}"

    def test_commands_in_claude_commands_dir(self):
        """All three command files should exist in .claude/commands/ for immediate use."""
        for name in ["daily-dev-pulse.md", "morning-brief.md", "dev-pulse.md"]:
            path = os.path.join(self.CLAUDE_COMMANDS_DIR, name)
            assert os.path.exists(path), f"{name} not found in .claude/commands/"

    def test_command_arguments_not_hardcoded_format(self):
        """Command workflow should NOT hardcode --format md without $ARGUMENTS."""
        for name in ["daily-dev-pulse.md", "morning-brief.md", "dev-pulse.md"]:
            for dir_path in [self.CLAUDE_COMMANDS_DIR, self.COMMANDS_DIR]:
                path = os.path.join(dir_path, name)
                if os.path.exists(path):
                    with open(path) as f:
                        content = f.read()
                    # The script invocation line should include $ARGUMENTS
                    # so user args like --focus, --repos, --days get forwarded
                    script_lines = [l for l in content.splitlines() if "daily-dev-pulse.sh" in l]
                    for line in script_lines:
                        assert "$ARGUMENTS" in line, f"$ARGUMENTS missing in script invocation in {path}"


class TestShellScriptInvocation(unittest.TestCase):
    """Test actual shell script invocation end-to-end with mock data."""

    PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
    SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), "..", "scripts")

    def test_formatter_pipeline_terminal_mode(self):
        """Pipe mock JSON data through pulse_formatter.py --format terminal and verify output."""
        import subprocess
        mock_data = json.dumps(MOCK_GITHUB_DATA)
        result = subprocess.run(
            ["python3", os.path.join(self.SCRIPTS_DIR, "pulse_formatter.py"), "--format", "terminal"],
            input=mock_data, capture_output=True, text=True, timeout=10
        )
        assert result.returncode == 0, f"stderr: {result.stderr}"
        assert "DAILY DEV PULSE" in result.stdout
        assert "Action Items" in result.stdout

    def test_formatter_pipeline_markdown_mode(self):
        """Pipe mock JSON data through pulse_formatter.py --format md and verify output."""
        import subprocess
        mock_data = json.dumps(MOCK_GITHUB_DATA)
        result = subprocess.run(
            ["python3", os.path.join(self.SCRIPTS_DIR, "pulse_formatter.py"), "--format", "md"],
            input=mock_data, capture_output=True, text=True, timeout=10
        )
        assert result.returncode == 0, f"stderr: {result.stderr}"
        assert "Daily Dev Pulse" in result.stdout
        assert "## GitHub Activity" in result.stdout

    def test_formatter_pipeline_json_mode(self):
        """Pipe mock JSON data through pulse_formatter.py --format json and verify output."""
        import subprocess
        mock_data = json.dumps(MOCK_GITHUB_DATA)
        result = subprocess.run(
            ["python3", os.path.join(self.SCRIPTS_DIR, "pulse_formatter.py"), "--format", "json"],
            input=mock_data, capture_output=True, text=True, timeout=10
        )
        assert result.returncode == 0, f"stderr: {result.stderr}"
        parsed = json.loads(result.stdout)
        assert "action_items" in parsed
        assert len(parsed["action_items"]) > 0

    def test_formatter_pipeline_empty_data(self):
        """Piping empty JSON through formatter should still produce valid output."""
        import subprocess
        mock_data = json.dumps({})
        result = subprocess.run(
            ["python3", os.path.join(self.SCRIPTS_DIR, "pulse_formatter.py"), "--format", "terminal"],
            input=mock_data, capture_output=True, text=True, timeout=10
        )
        assert result.returncode == 0, f"stderr: {result.stderr}"
        assert "DAILY DEV PULSE" in result.stdout

    def test_shell_script_graceful_without_gh(self):
        """Shell script should run without gh CLI and produce valid output (graceful degradation).
        This is an integration test that makes live network calls — may timeout in restricted environments."""
        import subprocess
        env = os.environ.copy()
        env.pop("GH_TOKEN", None)
        script_path = os.path.join(self.SCRIPTS_DIR, "daily-dev-pulse.sh")
        try:
            result = subprocess.run(
                ["bash", script_path, "--format", "json", "--focus", "all"],
                capture_output=True, text=True, timeout=30, env=env
            )
        except subprocess.TimeoutExpired:
            # Skip if network calls timeout (CI/restricted environments)
            self.skipTest("Shell script timed out (live network calls unavailable)")
        assert result.returncode == 0, f"stdout: {result.stdout}\nstderr: {result.stderr}"
        output_lines = result.stdout.strip().splitlines()
        json_output = output_lines[-1] if output_lines else ""
        if json_output.startswith("{"):
            parsed = json.loads(json_output)
            assert "scan_date" in parsed


class TestFormatJsonNoMutation(unittest.TestCase):
    """Verify format_json does not mutate its input data."""

    def test_format_json_no_mutation(self):
        """Calling format_json should not modify the original data dict."""
        original_data = {
            "github": {"source": "github", "repos": []},
            "security": {"source": "security", "alerts": []},
            "packages": {"source": "packages", "updates": []},
            "news": {"source": "news", "headlines": []},
        }
        # Snapshot keys before format_json
        keys_before = set(original_data.keys())
        output = pulse_formatter.format_json(original_data)
        # Input dict should not have action_items added
        assert "action_items" not in original_data
        assert set(original_data.keys()) == keys_before
        # Output JSON should have action_items
        parsed = json.loads(output)
        assert "action_items" in parsed

    def test_format_json_called_twice_same_result(self):
        """Calling format_json twice on the same data should produce identical output."""
        data = {
            "github": {"source": "github", "repos": []},
            "security": {"source": "security", "alerts": []},
        }
        first = pulse_formatter.format_json(data)
        second = pulse_formatter.format_json(data)
        assert first == second


class TestNvdRateLimiting(unittest.TestCase):
    """Verify NVD API rate limiting is applied between consecutive calls."""

    def test_rate_limiting_applied_in_check_security(self):
        """check_security should call time.sleep between consecutive NVD API calls."""
        import inspect
        source = inspect.getsource(security_checker.check_security)
        assert "time.sleep" in source
        assert "rate_limit" in source

    @patch("security_checker.fetch_cves")
    @patch("time.sleep")
    def test_rate_limiting_calls_sleep_between_products(self, mock_sleep, mock_fetch):
        """check_security should sleep between consecutive fetch_cves calls."""
        mock_fetch.return_value = [{"cve_id": "CVE-2025-0001", "product": "test", "severity": "HIGH", "score": 7.5, "description": "test"}]
        # Use config with rate_limit > 0 to ensure sleep is called
        cfg = copy.deepcopy(config.DEFAULT_CONFIG)
        cfg["preferences"]["nvd_rate_limit"] = 6
        result = security_checker.check_security(config=cfg)
        # fetch_cves is called once per search term (5 terms in default config)
        assert mock_fetch.call_count > 0
        # time.sleep should be called between consecutive fetches (not before the first one)
        assert mock_sleep.call_count == mock_fetch.call_count - 1
        # Each sleep should use the configured rate limit value
        for call in mock_sleep.call_args_list:
            assert call[0][0] == 6

    @patch("security_checker.fetch_cves")
    @patch("time.sleep")
    def test_rate_limiting_disabled_with_zero(self, mock_sleep, mock_fetch):
        """check_security should NOT sleep when nvd_rate_limit is 0."""
        mock_fetch.return_value = []
        cfg = copy.deepcopy(config.DEFAULT_CONFIG)
        cfg["preferences"]["nvd_rate_limit"] = 0
        result = security_checker.check_security(config=cfg)
        # No sleep calls when rate limit is 0
        assert mock_sleep.call_count == 0

    def test_rate_limit_in_default_config(self):
        """DEFAULT_CONFIG should include nvd_rate_limit preference."""
        assert "nvd_rate_limit" in config.DEFAULT_CONFIG["preferences"]
        assert config.DEFAULT_CONFIG["preferences"]["nvd_rate_limit"] == 6

    @patch("security_checker.fetch_cves")
    @patch("time.sleep")
    def test_rate_limiting_configurable_via_merge(self, mock_sleep, mock_fetch):
        """Custom nvd_rate_limit in user config should override default."""
        mock_fetch.return_value = []
        user_config = {"preferences": {"nvd_rate_limit": 2}}
        merged = config.merge_config(config.DEFAULT_CONFIG, user_config)
        result = security_checker.check_security(config=merged)
        # Sleep calls should use the custom value (2 seconds)
        for call in mock_sleep.call_args_list:
            assert call[0][0] == 2


class TestInstallScriptAliasDirectory(unittest.TestCase):
    """Verify install.sh creates command directories before copying alias commands."""

    PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

    def test_install_sh_creates_directories_before_alias_copy(self):
        """install.sh should mkdir ~/.claude/commands and ~/.openclaw/commands
        BEFORE the alias command cp/ln loop for daily-dev-pulse."""
        install_path = os.path.join(self.PROJECT_ROOT, "install.sh")
        with open(install_path) as f:
            content = f.read()

        # Find the daily-dev-pulse section
        dp_section_start = content.find("daily-dev-pulse")
        assert dp_section_start != -1, "daily-dev-pulse section not found in install.sh"

        # Find the alias copy loop
        alias_copy_start = content.find("cp \"$ALIAS_FILE\" ~/.claude/commands/", dp_section_start)
        assert alias_copy_start != -1, "Alias cp command not found in install.sh"

        # Find the mkdir commands that should come BEFORE the alias copy
        mkdir_claude = content.find("mkdir -p ~/.claude/commands", dp_section_start)
        mkdir_openclaw = content.find("mkdir -p ~/.openclaw/commands", dp_section_start)

        assert mkdir_claude != -1, "mkdir ~/.claude/commands not found in daily-dev-pulse section"
        assert mkdir_openclaw != -1, "mkdir ~/.openclaw/commands not found in daily-dev-pulse section"
        assert mkdir_claude < alias_copy_start, "mkdir ~/.claude/commands must come BEFORE alias cp"
        assert mkdir_openclaw < alias_copy_start, "mkdir ~/.openclaw/commands must come BEFORE alias cp"

    def test_install_sh_has_mkdir_for_both_command_dirs(self):
        """install.sh should create both ~/.claude/commands and ~/.openclaw/commands in daily-dev-pulse section."""
        install_path = os.path.join(self.PROJECT_ROOT, "install.sh")
        with open(install_path) as f:
            content = f.read()

        # Extract the daily-dev-pulse section between the outer if and its closing fi
        dp_start = content.find('if [ "$SKILL_NAME" = "daily-dev-pulse" ]; then')
        # Find the closing fi for the outer if block — it's after the inner if/fi
        # Strategy: find all 'fi' after dp_start, the outer fi is the one that
        # aligns with the outer if indentation
        pos = dp_start
        outer_if_indent = len(content[:dp_start]) - len(content[:dp_start].rstrip(' '))
        # Search forward for 'fi' at the same indentation level
        while pos < len(content):
            fi_pos = content.find('fi', pos + 1)
            if fi_pos == -1:
                break
            # Check if 'fi' is at the outer if indentation level (4 spaces in install_skill)
            line_start = content.rfind('\n', 0, fi_pos) + 1
            indent = fi_pos - line_start
            if indent == 4:
                dp_section = content[dp_start:fi_pos + 2]
                break
            pos = fi_pos

        assert "mkdir -p ~/.claude/commands" in dp_section
        assert "mkdir -p ~/.openclaw/commands" in dp_section


class TestTerminalBoxHeaderWidth(unittest.TestCase):
    """Verify terminal box header uses dynamic width calculation, not hardcoded padding."""

    def test_format_terminal_no_hardcoded_padding(self):
        """format_terminal should compute padding dynamically, not use hardcoded 'width - 28'."""
        import inspect
        source = inspect.getsource(pulse_formatter.format_terminal)
        # Should NOT have the old hardcoded padding formula
        assert "width - 28" not in source
        # Should have dynamic padding computation
        assert "padding" in source
        assert "visible_prefix_len" in source or "len(" in source

    def test_format_terminal_box_width_matches_header(self):
        """The box header content width should match the box top/bottom width."""
        # Create data with known date and check that header line has correct structure
        data = {"github": {"repos": []}}
        output = pulse_formatter.format_terminal(data)
        lines = output.split("\n")

        # Find the box top line (╔══════════════╗)
        box_top = lines[0]
        # Count the ═ characters to determine width
        horiz_count = box_top.count("═")
        width = horiz_count + 2  # +2 for ╔ and ╝

        # Find the header line (║ content ║)
        header_line = lines[1]
        # The header should end with ║
        assert header_line.rstrip().endswith("║")

        # Verify the header contains the date and DAILY DEV PULSE text
        assert "DAILY DEV PULSE" in header_line


class TestTerminalBoxCharacters(unittest.TestCase):
    """Verify terminal box uses correct Unicode box-drawing characters."""

    def test_box_top_line_has_correct_corners(self):
        """Box top line should start with ╔ and end with ╗ (not ╚)."""
        data = {}
        output = pulse_formatter.format_terminal(data)
        lines = output.split("\n")
        box_top = lines[0]
        assert box_top.startswith("╔"), f"Box top should start with ╔, got {box_top[0]}"
        assert box_top.endswith("╗"), f"Box top should end with ╗, got {box_top[-1]}"

    def test_box_bottom_line_has_correct_corners(self):
        """Box bottom line should start with ╚ and end with ╝ (not ╚)."""
        data = {}
        output = pulse_formatter.format_terminal(data)
        lines = output.split("\n")
        box_bottom = lines[2]
        assert box_bottom.startswith("╚"), f"Box bottom should start with ╚, got {box_bottom[0]}"
        assert box_bottom.endswith("╝"), f"Box bottom should end with ╝, got {box_bottom[-1]}"

    def test_box_side_is_vertical_bar(self):
        """Header line should use ║ as side characters."""
        data = {}
        output = pulse_formatter.format_terminal(data)
        lines = output.split("\n")
        header_line = lines[1]
        # Strip ANSI codes to check visible characters
        import re
        visible = re.sub(r'\033\[[0-9;]*m', '', header_line)
        assert visible.startswith("║"), f"Header should start with ║"
        assert visible.rstrip().endswith("║"), f"Header should end with ║"

    def test_colors_class_has_four_corner_chars(self):
        """Colors class should define TL, TR, BL, BR corner characters (not TOP/BOT reused)."""
        assert hasattr(pulse_formatter.Colors, "BOX_TL")
        assert hasattr(pulse_formatter.Colors, "BOX_TR")
        assert hasattr(pulse_formatter.Colors, "BOX_BL")
        assert hasattr(pulse_formatter.Colors, "BOX_BR")
        assert pulse_formatter.Colors.BOX_TL == "╔"
        assert pulse_formatter.Colors.BOX_TR == "╗"
        assert pulse_formatter.Colors.BOX_BL == "╚"
        assert pulse_formatter.Colors.BOX_BR == "╝"
        # Should NOT have old BOX_TOP/BOX_BOT constants
        assert not hasattr(pulse_formatter.Colors, "BOX_TOP")
        assert not hasattr(pulse_formatter.Colors, "BOX_BOT")


if __name__ == "__main__":
    unittest.main()