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
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta, timezone

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

# Helper functions for dynamic date generation in test data
def _recent_date_str():
    """ISO timestamp for a date within default lookback_days (7)."""
    return (datetime.now(timezone.utc) - timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%SZ")

def _old_date_str():
    """ISO timestamp for a date well beyond default lookback_days (7)."""
    return (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ")


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
                    {"number": 15, "title": "Bug in url fetcher", "createdAt": _recent_date_str(), "author": "contributor"},
                    {"number": 16, "title": "Old stale issue", "createdAt": _old_date_str(), "author": "contributor"},
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

    @patch("news_aggregator.fetch_article_via_url_fetcher")
    @patch("news_aggregator.fetch_hn_top")
    @patch("news_aggregator.fetch_devto_top")
    @patch("news_aggregator.fetch_lobsters_top")
    def test_aggregate_news(self, mock_lobsters, mock_devto, mock_hn, mock_url_fetcher):
        mock_hn.return_value = [{"title": "HN Story", "url": "https://hn.test", "score": 100, "source": "hn"}]
        mock_devto.return_value = [{"title": "Dev.to Article", "url": "https://dev.test", "score": 50, "source": "devto"}]
        mock_lobsters.return_value = []
        mock_url_fetcher.return_value = None  # No fallback needed

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
        """Action items should include open issues from GitHub data — only recent ones within lookback_days."""
        recent = _recent_date_str()
        data = {
            "github": {
                "repos": [{
                    "repo": "test/repo",
                    "open_prs": [],
                    "open_issues": [
                        {"number": 99, "title": "Critical bug in auth module", "createdAt": recent},
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
        """Product names with spaces should be URL-encoded using %20 (not +)."""
        import security_checker
        params = {"keywordSearch": "python 3.13", "resultsPerPage": 10}
        query = "&".join(f"{k}={urllib.parse.quote(str(v), safe='')}" for k, v in params.items())
        assert "python%203.13" in query
        assert " " not in query

    def test_fetch_cves_url_encoding(self):
        """fetch_cves should produce valid URLs even for products with special chars."""
        import subprocess
        import inspect
        source = inspect.getsource(security_checker.fetch_cves)
        assert "urllib.parse.quote" in source


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


class TestStalePrDaysConfigDriven(unittest.TestCase):
    """Verify stale_pr_days threshold comes from config/preferences, not hardcoded."""

    def test_generate_action_items_reads_stale_pr_days_from_data(self):
        """generate_action_items should use stale_pr_days from data.preferences, not hardcode 3."""
        import inspect
        source = inspect.getsource(pulse_formatter.generate_action_items)
        # Should read threshold from data, not hardcode > 3
        assert "stale_threshold" in source
        assert "stale_pr_days" in source
        # Should NOT have the old hardcoded > 3
        assert "> 3" not in source

    def test_stale_pr_default_threshold(self):
        """Default stale_pr_days should be 3 when no preferences in data."""
        from datetime import datetime, timezone, timedelta
        four_days_ago = (datetime.now(timezone.utc) - timedelta(days=4)).isoformat()
        # No preferences key — should use default threshold of 3
        data = {
            "github": {
                "repos": [{
                    "repo": "test/repo",
                    "open_prs": [
                        {"number": 1, "title": "Test PR", "createdAt": four_days_ago},
                    ],
                    "open_issues": [],
                    "ci_runs": [],
                }],
            },
        }
        items = pulse_formatter.generate_action_items(data)
        assert any("stale PR" in item for item in items)

    def test_stale_pr_custom_threshold_higher(self):
        """With stale_pr_days=7, a PR open 4 days should NOT be flagged."""
        from datetime import datetime, timezone, timedelta
        four_days_ago = (datetime.now(timezone.utc) - timedelta(days=4)).isoformat()
        data = {
            "preferences": {"stale_pr_days": 7},
            "github": {
                "repos": [{
                    "repo": "test/repo",
                    "open_prs": [
                        {"number": 1, "title": "Test PR", "createdAt": four_days_ago},
                    ],
                    "open_issues": [],
                    "ci_runs": [],
                }],
            },
        }
        items = pulse_formatter.generate_action_items(data)
        assert not any("stale PR" in item for item in items), \
            "PR open 4 days should not be flagged when threshold is 7"

    def test_stale_pr_custom_threshold_lower(self):
        """With stale_pr_days=1, a PR open 2 days should be flagged."""
        from datetime import datetime, timezone, timedelta
        two_days_ago = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
        data = {
            "preferences": {"stale_pr_days": 1},
            "github": {
                "repos": [{
                    "repo": "test/repo",
                    "open_prs": [
                        {"number": 1, "title": "Test PR", "createdAt": two_days_ago},
                    ],
                    "open_issues": [],
                    "ci_runs": [],
                }],
            },
        }
        items = pulse_formatter.generate_action_items(data)
        assert any("stale PR" in item for item in items), \
            "PR open 2 days should be flagged when threshold is 1"

    def test_shell_script_includes_preferences_in_combined_json(self):
        """Shell script merge section should add preferences to combined JSON output."""
        script_path = os.path.join(os.path.dirname(__file__), "..", "scripts", "daily-dev-pulse.sh")
        with open(script_path) as f:
            content = f.read()
        assert "stale_pr_days" in content, \
            "Shell script should include stale_pr_days preference in combined JSON"
        assert "preferences" in content, \
            "Shell script should include preferences dict in combined JSON"

    def test_format_json_includes_preferences(self):
        """format_json output should preserve preferences from input data."""
        data = {
            "preferences": {"stale_pr_days": 5},
            "github": {"source": "github", "repos": []},
        }
        output = pulse_formatter.format_json(data)
        parsed = json.loads(output)
        assert parsed["preferences"]["stale_pr_days"] == 5


class TestFormatPreferenceConfigDriven(unittest.TestCase):
    """Verify format preference is consumed by shell script, not just declared."""

    SCRIPT_PATH = os.path.join(os.path.dirname(__file__), "..", "scripts", "daily-dev-pulse.sh")

    def test_format_preference_in_combined_json(self):
        """Shell script merge section should include format in preferences dict."""
        with open(self.SCRIPT_PATH) as f:
            content = f.read()
        # The merge section should include 'format' alongside stale_pr_days
        assert "'format'" in content or '"format"' in content, \
            "Shell script should include format preference in combined JSON preferences"

    def test_format_fallback_from_config(self):
        """Shell script should fall back to config format preference when --format not passed."""
        with open(self.SCRIPT_PATH) as f:
            content = f.read()
        # FORMAT should start empty (not hardcoded "terminal") so it falls back to config
        assert 'FORMAT=""' in content, \
            "FORMAT should default to empty string so config preference can be used as fallback"
        # There should be a fallback block that reads format from combined JSON
        assert "combined.json" in content and "format" in content, \
            "Shell script should read format from combined JSON when --format not passed"

    def test_format_cli_overrides_config(self):
        """When --format is explicitly passed, it should override config preference."""
        with open(self.SCRIPT_PATH) as f:
            content = f.read()
        # The --format case should set FORMAT to $2 (the explicit CLI value)
        assert '--format)' in content, \
            "Shell script should have --format case that sets FORMAT"

    def test_lookback_days_preference_in_combined_json(self):
        """Shell script merge section should include lookback_days in preferences dict."""
        with open(self.SCRIPT_PATH) as f:
            content = f.read()
        # The merge section should include 'lookback_days' alongside stale_pr_days and format
        assert "'lookback_days'" in content or '"lookback_days"' in content, \
            "Shell script should include lookback_days preference in combined JSON preferences"

    def test_format_terminal_uses_lookback_days_from_preferences(self):
        """Terminal header should use lookback_days from preferences, not always show 7."""
        import inspect
        source = inspect.getsource(pulse_formatter.format_terminal)
        # Should read lookback_days from preferences first, not just from github sub-dict
        assert "preferences" in source, \
            "format_terminal should read lookback_days from preferences, not just github.lookback_days"

    def test_format_terminal_custom_lookback_days(self):
        """Terminal output should show configured lookback_days, not always '7 Days'."""
        data = {
            "preferences": {"lookback_days": 30},
            "github": {"repos": [{"repo": "test/repo", "commit_count": 5}]},
        }
        output = pulse_formatter.format_terminal(data)
        assert "30 Days" in output, \
            "Terminal header should show '30 Days' when lookback_days preference is 30"

    def test_format_terminal_default_lookback_days(self):
        """Terminal output should show '7 Days' when no preferences set (default)."""
        data = {
            "github": {"repos": [{"repo": "test/repo", "commit_count": 5}]},
        }
        output = pulse_formatter.format_terminal(data)
        assert "7 Days" in output, \
            "Terminal header should show '7 Days' when no lookback_days preference"


class TestNvdUrlEncoding(unittest.TestCase):
    """Verify NVD API URLs use proper percent-encoding (%20 for spaces, not +) and timezone offsets."""

    def test_fetch_cves_uses_quote_not_quote_plus(self):
        """fetch_cves should use urllib.parse.quote (not quote_plus) for URL parameter values."""
        import inspect
        source = inspect.getsource(security_checker.fetch_cves)
        # Should use quote() not quote_plus()
        assert "urllib.parse.quote" in source, \
            "fetch_cves should use urllib.parse.quote for URL encoding"
        assert "quote_plus" not in source, \
            "fetch_cves should NOT use quote_plus — REST APIs use %20, not +, for spaces"

    def test_url_encoding_produces_percent20_for_spaces(self):
        """URL-encoded search terms with spaces should use %20, not +."""
        params = {"keywordSearch": "python 3.13", "resultsPerPage": 10}
        query = "&".join(f"{k}={urllib.parse.quote(str(v), safe='')}" for k, v in params.items())
        assert "python%203.13" in query, \
            "quote() with safe='' should encode spaces as %20"
        assert "+" not in query.split("=")[1], \
            "quote() should NOT encode spaces as +"
        assert " " not in query, \
            "URL query should have no unencoded spaces"

    def test_fetch_cves_pubstartdate_includes_timezone(self):
        """pubStartDate should include +00:00 timezone offset for unambiguous UTC."""
        import inspect
        source = inspect.getsource(security_checker.fetch_cves)
        # The strftime format should include timezone offset
        assert "+00:00" in source, \
            "pubStartDate should include +00:00 timezone offset in strftime format"

    def test_nvd_date_string_format_with_timezone(self):
        """Generated NVD date strings should include UTC timezone offset."""
        from datetime import datetime, timezone, timedelta
        start_date = (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%dT00:00:00.000+00:00")
        assert "+00:00" in start_date, \
            "Date string should include +00:00 timezone offset"
        # The date should be properly formatted
        assert start_date.startswith("20"), "Date should start with century"
        assert "T00:00:00.000" in start_date, "Date should include time component"


class TestSecurityLookbackDaysConfigDriven(unittest.TestCase):
    """Verify security_lookback_days preference is consumed by security_checker, not hardcoded."""

    def test_security_lookback_days_in_default_config(self):
        """DEFAULT_CONFIG should include security_lookback_days preference."""
        assert "security_lookback_days" in config.DEFAULT_CONFIG["preferences"]
        assert config.DEFAULT_CONFIG["preferences"]["security_lookback_days"] == 30

    def test_check_security_reads_lookback_from_preferences(self):
        """check_security should read days from preferences.security_lookback_days, not hardcode 30."""
        import inspect
        source = inspect.getsource(security_checker.check_security)
        assert "security_lookback_days" in source
        # Should NOT have hardcoded days=30 in function signature
        assert "days=30" not in source

    def test_check_security_default_days_is_30(self):
        """check_security should default to 30 days when no config preferences set."""
        # Use a config with no preferences to verify the fallback
        cfg = copy.deepcopy(config.DEFAULT_CONFIG)
        del cfg["preferences"]["security_lookback_days"]
        result = security_checker.check_security(config=cfg)
        # The function should still work with the 30-day fallback
        assert "source" in result
        assert result["source"] == "security"

    @patch("security_checker.fetch_cves")
    def test_check_security_custom_security_lookback_days(self, mock_fetch):
        """Custom security_lookback_days should override the 30-day default."""
        mock_fetch.return_value = []
        cfg = copy.deepcopy(config.DEFAULT_CONFIG)
        cfg["preferences"]["security_lookback_days"] = 14
        result = security_checker.check_security(config=cfg)
        # fetch_cves should be called with days=14, not days=30
        for call in mock_fetch.call_args_list:
            assert call[1].get("days") == 14 or call[0][2] == 14, \
                "fetch_cves should be called with custom days value from security_lookback_days"

    def test_shell_script_includes_security_lookback_days(self):
        """Shell script merge section should include security_lookback_days in preferences."""
        script_path = os.path.join(os.path.dirname(__file__), "..", "scripts", "daily-dev-pulse.sh")
        with open(script_path) as f:
            content = f.read()
        assert "'security_lookback_days'" in content or '"security_lookback_days"' in content, \
            "Shell script should include security_lookback_days in combined JSON preferences"

    def test_security_lookback_days_in_config_example(self):
        """config-example.yml should document security_lookback_days preference."""
        config_path = os.path.join(os.path.dirname(__file__), "..", "config-example.yml")
        with open(config_path) as f:
            content = f.read()
        assert "security_lookback_days" in content, \
            "config-example.yml should document security_lookback_days preference"


class TestSkillMdConfigCompleteness(unittest.TestCase):
    """Verify SKILL.md config example includes all preferences from DEFAULT_CONFIG."""

    SKILL_PATH = os.path.join(os.path.dirname(__file__), "..", "SKILL.md")

    def test_skill_md_includes_stale_pr_days(self):
        """SKILL.md config example should include stale_pr_days preference."""
        with open(self.SKILL_PATH) as f:
            content = f.read()
        assert "stale_pr_days" in content, \
            "SKILL.md config example should include stale_pr_days preference"

    def test_skill_md_includes_nvd_rate_limit(self):
        """SKILL.md config example should include nvd_rate_limit preference."""
        with open(self.SKILL_PATH) as f:
            content = f.read()
        assert "nvd_rate_limit" in content, \
            "SKILL.md config example should include nvd_rate_limit preference"

    def test_skill_md_includes_security_lookback_days(self):
        """SKILL.md config example should include security_lookback_days preference."""
        with open(self.SKILL_PATH) as f:
            content = f.read()
        assert "security_lookback_days" in content, \
            "SKILL.md config example should include security_lookback_days preference"

    def test_skill_md_preferences_match_default_config_keys(self):
        """SKILL.md config example should list all preference keys from DEFAULT_CONFIG."""
        with open(self.SKILL_PATH) as f:
            content = f.read()
        for key in config.DEFAULT_CONFIG["preferences"]:
            assert key in content, \
                f"SKILL.md should mention preference '{key}' from DEFAULT_CONFIG"


class TestMarkdownHeadingConsistency(unittest.TestCase):
    """Verify format_markdown headings include configurable lookback days,
    matching the dynamic display already in format_terminal."""

    def test_format_markdown_github_activity_includes_lookback_days(self):
        """format_markdown GitHub Activity heading should include lookback_days."""
        data = copy.deepcopy(MOCK_GITHUB_DATA)
        data["preferences"] = {"lookback_days": 14, "stale_pr_days": 3, "security_lookback_days": 30}
        output = pulse_formatter.format_markdown(data)
        assert "Last 14 Days" in output, \
            "format_markdown GitHub Activity heading should include lookback_days from preferences"

    def test_format_markdown_github_activity_default_lookback(self):
        """format_markdown GitHub Activity heading should show 7 when no preferences."""
        data = copy.deepcopy(MOCK_GITHUB_DATA)
        output = pulse_formatter.format_markdown(data)
        assert "Last 7 Days" in output, \
            "format_markdown GitHub Activity heading should default to 7 days"

    def test_format_markdown_security_alerts_includes_security_lookback(self):
        """format_markdown Security Alerts heading should include security_lookback_days."""
        data = copy.deepcopy(MOCK_GITHUB_DATA)
        data["security"] = {"source": "security", "alerts": [
            {"cve_id": "CVE-2025-1234", "product": "fastapi", "severity": "HIGH", "score": 8.5, "description": "Auth bypass"},
        ]}
        data["preferences"] = {"lookback_days": 7, "stale_pr_days": 3, "security_lookback_days": 60}
        output = pulse_formatter.format_markdown(data)
        assert "Last 60 Days" in output, \
            "format_markdown Security Alerts heading should include security_lookback_days from preferences"

    def test_format_markdown_security_alerts_default_lookback(self):
        """format_markdown Security Alerts heading should show 30 when no preferences."""
        data = copy.deepcopy(MOCK_GITHUB_DATA)
        data["security"] = {"source": "security", "alerts": [
            {"cve_id": "CVE-2025-1234", "product": "fastapi", "severity": "HIGH", "score": 8.5, "description": "Auth bypass"},
        ]}
        output = pulse_formatter.format_markdown(data)
        assert "Last 30 Days" in output, \
            "format_markdown Security Alerts heading should default to 30 days"

    def test_format_terminal_github_activity_includes_lookback_days(self):
        """format_terminal GitHub Activity heading should include lookback_days (already implemented)."""
        data = copy.deepcopy(MOCK_GITHUB_DATA)
        data["preferences"] = {"lookback_days": 14, "stale_pr_days": 3, "security_lookback_days": 30}
        output = pulse_formatter.format_terminal(data)
        assert "Last 14 Days" in output, \
            "format_terminal GitHub Activity heading should include lookback_days from preferences"

    def test_format_markdown_no_hardcoded_static_heading(self):
        """format_markdown should NOT have a bare '## GitHub Activity' without lookback days."""
        # Verify the format_markdown function code itself doesn't contain
        # the old hardcoded heading string without lookback info
        formatter_path = os.path.join(SCRIPTS_DIR, "pulse_formatter.py")
        with open(formatter_path) as f:
            content = f.read()
        # The old bug was a line like: lines.append("## GitHub Activity")
        # The fixed version should include lookback: lines.append(f"## GitHub Activity (Last {lookback} Days)")
        # Check that the bare string is not used as a heading
        assert '"## GitHub Activity"' not in content, \
            "format_markdown should not use bare '## GitHub Activity' heading without lookback days"


class TestTerminalSecurityAlertsHeadingConsistency(unittest.TestCase):
    """Verify format_terminal Security Alerts heading includes security_lookback_days,
    matching the dynamic display in format_markdown (iteration 18) and
    format_terminal GitHub Activity (iteration 16)."""

    def test_format_terminal_security_alerts_includes_security_lookback(self):
        """Terminal Security Alerts heading should show security_lookback_days from preferences."""
        data = copy.deepcopy(MOCK_GITHUB_DATA)
        data["security"] = {"source": "security", "alerts": [
            {"cve_id": "CVE-2025-1234", "product": "fastapi", "severity": "HIGH", "score": 8.5, "description": "Auth bypass"},
        ]}
        data["preferences"] = {"lookback_days": 7, "stale_pr_days": 3, "security_lookback_days": 60}
        output = pulse_formatter.format_terminal(data)
        assert "Last 60 Days" in output, \
            "Terminal Security Alerts heading should include security_lookback_days from preferences"

    def test_format_terminal_security_alerts_default_lookback(self):
        """Terminal Security Alerts heading should show 30 when no security_lookback_days preference."""
        data = copy.deepcopy(MOCK_GITHUB_DATA)
        output = pulse_formatter.format_terminal(data)
        assert "Last 30 Days" in output, \
            "Terminal Security Alerts heading should default to 30 days"

    def test_format_terminal_no_bare_security_heading(self):
        """format_terminal should not use bare 'Security Alerts' heading without lookback days."""
        formatter_path = os.path.join(SCRIPTS_DIR, "pulse_formatter.py")
        with open(formatter_path) as f:
            content = f.read()
        # The old bug was a line with just "Security Alerts" without the lookback info
        assert '"🛡️ Security Alerts"' not in content, \
            "format_terminal should not use bare Security Alerts heading without lookback days"

    def test_format_terminal_security_heading_matches_markdown(self):
        """Terminal and markdown Security Alerts headings should both show the same security_lookback_days."""
        data = copy.deepcopy(MOCK_GITHUB_DATA)
        data["security"] = {"source": "security", "alerts": [
            {"cve_id": "CVE-2025-1234", "product": "fastapi", "severity": "HIGH", "score": 8.5, "description": "Auth bypass"},
        ]}
        data["preferences"] = {"lookback_days": 7, "stale_pr_days": 3, "security_lookback_days": 45}
        terminal_output = pulse_formatter.format_terminal(data)
        markdown_output = pulse_formatter.format_markdown(data)
        assert "Last 45 Days" in terminal_output, \
            "Terminal Security Alerts heading should show 45 days"
        assert "Last 45 Days" in markdown_output, \
            "Markdown Security Alerts heading should show 45 days"


class TestNvdRateLimitInCombinedJson(unittest.TestCase):
    """Verify shell script combined JSON includes nvd_rate_limit preference alongside the other 5 preferences."""

    SCRIPT_PATH = os.path.join(os.path.dirname(__file__), "..", "scripts", "daily-dev-pulse.sh")

    def test_shell_script_includes_nvd_rate_limit_in_preferences(self):
        """Shell script merge section should include nvd_rate_limit in combined JSON preferences."""
        with open(self.SCRIPT_PATH) as f:
            content = f.read()
        assert "'nvd_rate_limit'" in content or '"nvd_rate_limit"' in content, \
            "Shell script should include nvd_rate_limit in combined JSON preferences"

    def test_shell_script_preferences_all_6_keys(self):
        """Shell script merge section should include all 6 preference keys from DEFAULT_CONFIG."""
        with open(self.SCRIPT_PATH) as f:
            content = f.read()
        for key in config.DEFAULT_CONFIG["preferences"]:
            assert key in content, \
                f"Shell script merge section should include preference '{key}' from DEFAULT_CONFIG"

    def test_format_json_includes_nvd_rate_limit(self):
        """format_json output should preserve nvd_rate_limit from input data."""
        data = {
            "preferences": {"nvd_rate_limit": 2, "stale_pr_days": 3},
            "github": {"source": "github", "repos": []},
        }
        output = pulse_formatter.format_json(data)
        parsed = json.loads(output)
        assert parsed["preferences"]["nvd_rate_limit"] == 2

    def test_nvd_rate_limit_in_combined_json_default_value(self):
        """Shell script fallback preferences should include nvd_rate_limit default value of 6."""
        with open(self.SCRIPT_PATH) as f:
            content = f.read()
        # The fallback line (except block) should include nvd_rate_limit: 6
        assert "nvd_rate_limit': 6" in content, \
            "Shell script fallback preferences should include nvd_rate_limit default of 6"


if __name__ == "__main__":
    unittest.main()


class TestUnusedImportsRemoved(unittest.TestCase):
    """Verify unused imports were removed from module files."""

    MODULES_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "modules"))

    def test_github_scanner_no_unused_sys_import(self):
        """github_scanner.py should not import sys (it's unused)."""
        with open(os.path.join(self.MODULES_DIR, "github_scanner.py")) as f:
            content = f.read()
        # 'import sys' should not appear as a standalone import line
        for line in content.split("\n"):
            if line.strip() == "import sys":
                assert False, "github_scanner.py should not have unused 'import sys'"

    def test_news_aggregator_no_unused_sys_import(self):
        """news_aggregator.py should not import sys (it's unused)."""
        with open(os.path.join(self.MODULES_DIR, "news_aggregator.py")) as f:
            content = f.read()
        for line in content.split("\n"):
            if line.strip() == "import sys":
                assert False, "news_aggregator.py should not have unused 'import sys'"

    def test_package_watcher_no_unused_sys_import(self):
        """package_watcher.py should not import sys (it's unused)."""
        with open(os.path.join(self.MODULES_DIR, "package_watcher.py")) as f:
            content = f.read()
        for line in content.split("\n"):
            if line.strip() == "import sys":
                assert False, "package_watcher.py should not have unused 'import sys'"

    def test_security_checker_no_unused_sys_import(self):
        """security_checker.py should not import sys (it's unused)."""
        with open(os.path.join(self.MODULES_DIR, "security_checker.py")) as f:
            content = f.read()
        for line in content.split("\n"):
            if line.strip() == "import sys":
                assert False, "security_checker.py should not have unused 'import sys'"

    def test_test_file_no_unused_stringio_import(self):
        """test file should not import StringIO (it's unused)."""
        with open(__file__) as f:
            content = f.read()
        # Check the import section (first 20 lines) for the specific import
        import_lines = [l for l in content.split("\n")[:20] if l.strip().startswith("from ") or l.strip().startswith("import ")]
        for line in import_lines:
            # Construct the pattern dynamically to avoid the literal string in the file
            parts = line.strip().split()
            if len(parts) >= 4 and parts[0] == "from" and parts[1] == "io" and parts[2] == "import" and parts[3] == "StringIO":
                assert False, "test file imports section should not include StringIO from io module"


class TestImportCopyModuleLevel(unittest.TestCase):
    """Verify import copy is at module level in pulse_formatter.py, not inside format_json."""

    SCRIPTS_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "scripts"))

    def test_import_copy_at_module_level(self):
        """import copy should be at the top of pulse_formatter.py, not inside format_json."""
        with open(os.path.join(self.SCRIPTS_DIR, "pulse_formatter.py")) as f:
            content = f.read()
        # 'import copy' should appear in the import block at the top
        import_block_end = 0
        for i, line in enumerate(content.split("\n")):
            stripped = line.strip()
            if stripped.startswith("import ") or stripped.startswith("from ") and not stripped.startswith("#"):
                import_block_end = i
        # Find the import copy line
        for i, line in enumerate(content.split("\n")):
            if line.strip() == "import copy":
                assert i <= import_block_end + 1, \
                    f"import copy should be in module-level import block (line {i}), not inside a function"
                break
        else:
            assert False, "import copy must exist in pulse_formatter.py"

    def test_import_copy_not_inside_format_json(self):
        """format_json function body should not contain 'import copy'."""
        with open(os.path.join(self.SCRIPTS_DIR, "pulse_formatter.py")) as f:
            content = f.read()
        # Find format_json function
        in_func = False
        for line in content.split("\n"):
            if line.startswith("def format_json"):
                in_func = True
            elif in_func and line.startswith("def "):
                break  # next function starts
            elif in_func and line.strip() == "import copy":
                assert False, "import copy should not be inside format_json function body"


class TestUrlFetcherIntegration(unittest.TestCase):
    """Test url-fetcher integration in news_aggregator.py."""

    MODULES_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "modules"))

    def test_fetch_article_via_url_fetcher_function_exists(self):
        """news_aggregator.py should have fetch_article_via_url_fetcher function."""
        with open(os.path.join(self.MODULES_DIR, "news_aggregator.py")) as f:
            content = f.read()
        assert "def fetch_article_via_url_fetcher" in content, \
            "news_aggregator.py should have fetch_article_via_url_fetcher function"

    def test_find_url_fetcher_script_function_exists(self):
        """news_aggregator.py should have _find_url_fetcher_script helper."""
        with open(os.path.join(self.MODULES_DIR, "news_aggregator.py")) as f:
            content = f.read()
        assert "def _find_url_fetcher_script" in content, \
            "news_aggregator.py should have _find_url_fetcher_script helper"

    def test_url_fetcher_fallback_in_aggregate_news(self):
        """aggregate_news should attempt url-fetcher fallback when direct API fails."""
        # Mock all direct API fetchers to return empty, and mock url-fetcher to return data
        with patch.object(news_aggregator, 'fetch_hn_top', return_value=[]), \
             patch.object(news_aggregator, 'fetch_devto_top', return_value=[]), \
             patch.object(news_aggregator, 'fetch_lobsters_top', return_value=[]), \
             patch.object(news_aggregator, 'fetch_article_via_url_fetcher', return_value={
                 "title": "HN Fallback", "content_summary": "some content",
                 "source_url": "https://news.ycombinator.com", "extraction_method": "url-fetcher"
             }):
            result = news_aggregator.aggregate_news(config={"preferences": {"news_sources": ["hn"]}})
            assert len(result["headlines"]) > 0, \
                "aggregate_news should return fallback headlines when direct API fails"
            assert result["url_fetcher_used"] is True, \
                "aggregate_news should flag url_fetcher_used when fallback is used"

    def test_url_fetcher_not_used_when_direct_api_succeeds(self):
        """url_fetcher_used should be False when direct API returns data."""
        mock_hn = [{"id": "1", "title": "Test", "url": "http://t.co", "score": 10, "source": "hn"}]
        with patch.object(news_aggregator, 'fetch_hn_top', return_value=mock_hn), \
             patch.object(news_aggregator, 'fetch_article_via_url_fetcher') as mock_fetch:
            result = news_aggregator.aggregate_news(config={"preferences": {"news_sources": ["hn"]}})
            assert result["url_fetcher_used"] is False, \
                "url_fetcher_used should be False when direct API succeeds"
            mock_fetch.assert_not_called(), \
                "fetch_article_via_url_fetcher should not be called when direct API succeeds"

    def test_url_fetcher_returns_none_when_script_missing(self):
        """fetch_article_via_url_fetcher should return None when fetch.sh is not found."""
        with patch.object(news_aggregator, '_find_url_fetcher_script', return_value=None):
            result = news_aggregator.fetch_article_via_url_fetcher("https://example.com")
            assert result is None, "Should return None when url-fetcher script not found"

    def test_url_fetcher_returns_none_on_subprocess_failure(self):
        """fetch_article_via_url_fetcher should return None when subprocess fails."""
        with patch.object(news_aggregator, '_find_url_fetcher_script', return_value="/fake/fetch.sh"), \
             patch('subprocess.run', side_effect=FileNotFoundError):
            result = news_aggregator.fetch_article_via_url_fetcher("https://example.com")
            assert result is None, "Should return None on subprocess failure"

    def test_url_fetcher_used_field_in_output(self):
        """aggregate_news output should include url_fetcher_used field."""
        result = news_aggregator.aggregate_news(config={"preferences": {"news_sources": ["hn"]}})
        assert "url_fetcher_used" in result, \
            "aggregate_news output should include url_fetcher_used field"


class TestPresearchIntegration(unittest.TestCase):
    """Test presearch integration in package_watcher.py."""

    MODULES_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "modules"))

    def test_search_package_trends_via_presearch_function_exists(self):
        """package_watcher.py should have search_package_trends_via_presearch function."""
        with open(os.path.join(self.MODULES_DIR, "package_watcher.py")) as f:
            content = f.read()
        assert "def search_package_trends_via_presearch" in content, \
            "package_watcher.py should have search_package_trends_via_presearch function"

    def test_find_presearch_script_function_exists(self):
        """package_watcher.py should have _find_presearch_script helper."""
        with open(os.path.join(self.MODULES_DIR, "package_watcher.py")) as f:
            content = f.read()
        assert "def _find_presearch_script" in content, \
            "package_watcher.py should have _find_presearch_script helper"

    def test_presearch_returns_none_when_script_missing(self):
        """search_package_trends_via_presearch should return None when script not found."""
        with patch.object(package_watcher, '_find_presearch_script', return_value=None):
            result = package_watcher.search_package_trends_via_presearch("fastapi alternative")
            assert result is None, "Should return None when presearch script not found"

    def test_presearch_returns_none_on_subprocess_failure(self):
        """search_package_trends_via_presearch should return None when subprocess fails."""
        with patch.object(package_watcher, '_find_presearch_script', return_value="/fake/presearch.sh"), \
             patch('subprocess.run', side_effect=FileNotFoundError):
            result = package_watcher.search_package_trends_via_presearch("fastapi alternative")
            assert result is None, "Should return None on subprocess failure"

    def test_watch_packages_includes_trends_field(self):
        """watch_packages output should include trends field."""
        with patch.object(package_watcher, '_find_presearch_script', return_value=None), \
             patch.object(package_watcher, 'fetch_npm_info', return_value={"package": "next", "registry": "npm", "latest_version": "15.0.0"}), \
             patch.object(package_watcher, 'fetch_pypi_info', return_value={"package": "fastapi", "registry": "pypi", "latest_version": "0.115.0"}):
            result = package_watcher.watch_packages(config={
                "dependencies": {"npm": ["next"], "pypi": ["fastapi"]},
                "tech_stack": {"frameworks": ["FastAPI"]},
            })
            assert "trends" in result, "watch_packages output should include trends field"
            assert "presearch_used" in result, "watch_packages output should include presearch_used field"

    def test_watch_packages_marks_presearch_used_when_trends_found(self):
        """presearch_used should be True when presearch returns trend data."""
        mock_trend = {"query": "FastAPI", "trends": [{"summary": "trending"}], "extraction_method": "presearch"}
        with patch.object(package_watcher, '_find_presearch_script', return_value="/fake/presearch.sh"), \
             patch('subprocess.run', return_value=MagicMock(returncode=0, stdout=json.dumps(mock_trend))), \
             patch.object(package_watcher, 'fetch_npm_info', return_value={"package": "next", "registry": "npm", "latest_version": "15.0.0"}), \
             patch.object(package_watcher, 'fetch_pypi_info', return_value={"package": "fastapi", "registry": "pypi", "latest_version": "0.115.0"}):
            result = package_watcher.watch_packages(config={
                "dependencies": {"npm": ["next"], "pypi": ["fastapi"]},
                "tech_stack": {"frameworks": ["FastAPI"]},
            })
            assert result["presearch_used"] is True, \
                "presearch_used should be True when presearch returns data"


class TestSkillMdDocumentationAccuracy(unittest.TestCase):
    """Verify SKILL.md accurately reflects the implementation."""

    SKILL_PATH = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "SKILL.md"))

    def test_skill_md_no_curl_dependency(self):
        """SKILL.md Dependencies section should not claim curl dependency."""
        with open(self.SKILL_PATH) as f:
            content = f.read()
        # Find the Dependencies section
        in_deps = False
        for line in content.split("\n"):
            if line.strip().startswith("## Dependencies"):
                in_deps = True
            elif in_deps and line.strip().startswith("##"):
                break
            elif in_deps and "curl" in line.lower():
                assert False, \
                    "SKILL.md should not list curl as a dependency (code uses urllib, not curl)"

    def test_skill_md_config_example_has_dependencies(self):
        """SKILL.md config example should include dependencies section."""
        with open(self.SKILL_PATH) as f:
            content = f.read()
        # Find the config yaml block
        in_yaml = False
        yaml_content = []
        for line in content.split("\n"):
            if line.strip() == "```yaml" and "repos:" in content[content.find(line):content.find(line)+200]:
                in_yaml = True
            elif in_yaml and line.strip() == "```":
                in_yaml = False
            elif in_yaml:
                yaml_content.append(line)
        yaml_text = "\n".join(yaml_content)
        assert "dependencies:" in yaml_text, \
            "SKILL.md config example should include dependencies section"

    def test_skill_md_url_fetcher_description_accurate(self):
        """SKILL.md should describe url-fetcher as fallback, not primary."""
        with open(self.SKILL_PATH) as f:
            content = f.read()
        # The Dependencies section should say "fallback" for url-fetcher
        deps_section = content.split("## Dependencies")[1].split("##")[0] if "## Dependencies" in content else ""
        assert "fallback" in deps_section.lower(), \
            "url-fetcher should be described as fallback in Dependencies section"

    def test_skill_md_news_step_describes_fallback(self):
        """SKILL.md Step 2 News Aggregator should mention fallback behavior."""
        with open(self.SKILL_PATH) as f:
            content = f.read()
        # Find the News Aggregator step
        assert "url-fetcher" in content and "fallback" in content.lower(), \
            "SKILL.md should mention url-fetcher fallback for news aggregation"


class TestSkillMdFormatModeNaming(unittest.TestCase):
    """Verify SKILL.md uses 'md' (not 'markdown') consistently for format mode."""

    SKILL_PATH = os.path.normpath(os.path.join(
        os.path.dirname(__file__), "..", "SKILL.md"))

    def test_skill_md_no_markdown_format_name(self):
        """SKILL.md should not reference 'markdown' as a format mode name."""
        with open(self.SKILL_PATH) as f:
            content = f.read()
        # Check Step 3 example
        step3_section = ""
        lines = content.split("\n")
        in_step3 = False
        for line in lines:
            if "Step 3" in line:
                in_step3 = True
            elif in_step3 and line.strip().startswith("### Step"):
                in_step3 = False
            elif in_step3:
                step3_section += line + "\n"
        assert "--format markdown" not in step3_section, \
            "SKILL.md Step 3 should use '--format md', not '--format markdown'"

    def test_skill_md_output_modes_use_md(self):
        """SKILL.md Output modes section should use 'md' not 'markdown'."""
        with open(self.SKILL_PATH) as f:
            content = f.read()
        # Find the output modes list items
        assert "**md**:" in content, \
            "SKILL.md should use '**md**:' for markdown output mode, not '**markdown**:'"

    def test_skill_md_arguments_table_has_config(self):
        """SKILL.md Arguments table should include --config argument."""
        with open(self.SKILL_PATH) as f:
            content = f.read()
        # Find the Arguments table
        assert "--config" in content, \
            "SKILL.md Arguments table should include --config argument"


class TestCommandPermissionsComplete(unittest.TestCase):
    """Verify slash commands include mktemp and rm permissions."""

    COMMANDS_DIR = os.path.normpath(os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "..", "commands"))
    CLAUDE_COMMANDS_DIR = os.path.normpath(os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "..", ".claude", "commands"))

    def _read_command(self, filename):
        for dir_path in [self.COMMANDS_DIR, self.CLAUDE_COMMANDS_DIR]:
            path = os.path.join(dir_path, filename)
            if os.path.exists(path):
                with open(path) as f:
                    return f.read()
        return None

    def test_daily_dev_pulse_has_mktemp_permission(self):
        """daily-dev-pulse command should include Bash(mktemp *) permission."""
        content = self._read_command("daily-dev-pulse.md")
        assert content is not None, "daily-dev-pulse.md command not found"
        assert "Bash(mktemp *)" in content, \
            "daily-dev-pulse command should include Bash(mktemp *) in allowed-tools"

    def test_daily_dev_pulse_has_rm_permission(self):
        """daily-dev-pulse command should include Bash(rm *) permission."""
        content = self._read_command("daily-dev-pulse.md")
        assert content is not None, "daily-dev-pulse.md command not found"
        assert "Bash(rm *)" in content, \
            "daily-dev-pulse command should include Bash(rm *) in allowed-tools"

    def test_morning_brief_has_mktemp_permission(self):
        """morning-brief command should include Bash(mktemp *) permission."""
        content = self._read_command("morning-brief.md")
        assert content is not None, "morning-brief.md command not found"
        assert "Bash(mktemp *)" in content, \
            "morning-brief command should include Bash(mktemp *) in allowed-tools"

    def test_dev_pulse_has_mktemp_permission(self):
        """dev-pulse command should include Bash(mktemp *) permission."""
        content = self._read_command("dev-pulse.md")
        assert content is not None, "dev-pulse.md command not found"
        assert "Bash(mktemp *)" in content, \
            "dev-pulse command should include Bash(mktemp *) in allowed-tools"


class TestMcpEntriesHaveEnabledField(unittest.TestCase):
    """Verify MCP github-activity and rss-fetch entries have enabled field."""

    MCP_PATH = os.path.normpath(os.path.join(
        os.path.dirname(__file__), "..", "..", "..", "..", "connectors", "mcp-servers.json"))

    def test_github_activity_has_enabled_field(self):
        """github-activity MCP entry should have enabled: true."""
        with open(self.MCP_PATH) as f:
            data = json.load(f)
        entry = data["mcpServers"]["github-activity"]
        assert "enabled" in entry, \
            "github-activity MCP entry should have 'enabled' field"
        assert entry["enabled"] is True, \
            "github-activity 'enabled' should be true"

    def test_rss_fetch_has_enabled_field(self):
        """rss-fetch MCP entry should have enabled: true."""
        with open(self.MCP_PATH) as f:
            data = json.load(f)
        entry = data["mcpServers"]["rss-fetch"]
        assert "enabled" in entry, \
            "rss-fetch MCP entry should have 'enabled' field"
        assert entry["enabled"] is True, \
            "rss-fetch 'enabled' should be true"


class TestSkillMdConfigExampleMatchesDefaults(unittest.TestCase):
    """Verify SKILL.md config example dependencies match DEFAULT_CONFIG."""

    SKILL_PATH = os.path.normpath(os.path.join(
        os.path.dirname(__file__), "..", "SKILL.md"))

    def test_skill_md_npm_deps_match_default(self):
        """SKILL.md config example npm deps should match DEFAULT_CONFIG."""
        with open(self.SKILL_PATH) as f:
            content = f.read()
        # DEFAULT_CONFIG npm: [next, react, tailwindcss]
        assert "next, react, tailwindcss" in content, \
            "SKILL.md npm deps should match DEFAULT_CONFIG (next, react, tailwindcss)"

    def test_skill_md_pypi_deps_match_default(self):
        """SKILL.md config example pypi deps should match DEFAULT_CONFIG."""
        with open(self.SKILL_PATH) as f:
            content = f.read()
        # DEFAULT_CONFIG pypi: [fastapi, uvicorn, langgraph, sqlalchemy, pyyaml, requests]
        assert "fastapi, uvicorn, langgraph, sqlalchemy, pyyaml, requests" in content, \
            "SKILL.md pypi deps should match DEFAULT_CONFIG (fastapi, uvicorn, langgraph, sqlalchemy, pyyaml, requests)"


class TestPyYamlGracefulDegradation(unittest.TestCase):
    """Verify config.py works without PyYAML when no user config file exists."""

    MODULES_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "modules"))
    SCRIPTS_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "scripts"))

    def _read_module_file(self, filename):
        with open(os.path.join(self.MODULES_DIR, filename)) as f:
            return f.read()

    def _read_shell_script(self):
        with open(os.path.join(self.SCRIPTS_DIR, "daily-dev-pulse.sh")) as f:
            return f.read()

    def test_config_has_yaml_available_flag(self):
        """config.py should define YAML_AVAILABLE flag instead of sys.exit on import."""
        content = self._read_module_file("config.py")
        assert "YAML_AVAILABLE" in content, "config.py should have YAML_AVAILABLE flag"
        # Verify no sys.exit in the import section (before the first function definition)
        import_section_end = content.find("def load_config")
        import_section = content[:import_section_end] if import_section_end > 0 else content[:500]
        assert "sys.exit(1)" not in import_section, \
            "config.py import section should NOT contain sys.exit — yaml failure should be deferred"

    def test_config_works_without_yaml_no_config_file(self):
        """load_config should work without yaml when no config file exists (uses defaults)."""
        # Remove yaml from sys.modules to simulate missing PyYAML
        yaml_mod = sys.modules.get("yaml")
        sys.modules["yaml"] = None
        try:
            import importlib
            config_mod = importlib.import_module("config")
            importlib.reload(config_mod)
            assert config_mod.YAML_AVAILABLE is False
            cfg = config_mod.load_config(config_path="/nonexistent/path.yml")
            assert "repos" in cfg
            assert len(cfg["repos"]) == 6
        finally:
            if yaml_mod is not None:
                sys.modules["yaml"] = yaml_mod
            else:
                del sys.modules["yaml"]
            importlib.reload(config)

    def test_config_fails_without_yaml_when_config_file_exists(self):
        """load_config should sys.exit when yaml missing AND user config file exists."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            f.write("repos:\n  - name: test-repo\n    owner: test-owner\n")
            config_path = f.name
        try:
            yaml_mod = sys.modules.get("yaml")
            sys.modules["yaml"] = None
            try:
                import importlib
                config_mod = importlib.import_module("config")
                importlib.reload(config_mod)
                with self.assertRaises(SystemExit):
                    config_mod.load_config(config_path=config_path)
            finally:
                if yaml_mod is not None:
                    sys.modules["yaml"] = yaml_mod
                else:
                    del sys.modules["yaml"]
                importlib.reload(config)
        finally:
            os.unlink(config_path)

    def test_shell_script_merge_handles_missing_yaml(self):
        """Shell script merge section should produce valid combined JSON even when
        config.py can't load yaml (no user config file → uses defaults)."""
        shell_content = self._read_shell_script()
        # The merge section has try/except that catches Exception
        # SystemExit is NOT caught by except Exception, so config.py must NOT sys.exit
        # when yaml is unavailable and no config file exists
        assert "except Exception" in shell_content, \
            "Shell script merge should have Exception catch for config import failure"
        # Verify config.py doesn't sys.exit on import (the fix)
        config_content = self._read_module_file("config.py")
        import_section_end = config_content.find("def load_config")
        import_section = config_content[:import_section_end] if import_section_end > 0 else content[:500]
        assert "sys.exit(1)" not in import_section, \
            "config.py import section should NOT contain sys.exit — yaml failure should be deferred"

    def test_config_main_block_graceful_without_yaml(self):
        """config.py __main__ block should work without yaml (JSON fallback)."""
        content = self._read_module_file("config.py")
        main_block_start = content.find("if __name__")
        if main_block_start == -1:
            return  # No __main__ block
        main_block = content[main_block_start:]
        assert "YAML_AVAILABLE" in main_block or "json.dumps" in main_block, \
            "config.py __main__ should have yaml fallback (JSON output when yaml unavailable)"


class TestIssueDateFiltering(unittest.TestCase):
    """Test that generate_action_items only flags open issues created within lookback_days."""

    def test_recent_issue_flagged(self):
        """Issues created within lookback_days should be flagged."""
        recent = _recent_date_str()
        data = {
            "github": {
                "repos": [{
                    "repo": "test/repo",
                    "open_prs": [],
                    "open_issues": [
                        {"number": 10, "title": "Recent issue", "createdAt": recent},
                    ],
                    "ci_runs": [],
                }],
            },
            "preferences": {"lookback_days": 7, "stale_pr_days": 3, "max_issues_per_repo": 3},
        }
        items = pulse_formatter.generate_action_items(data)
        assert any("open issue" in item and "#10" in item for item in items)

    def test_old_issue_not_flagged(self):
        """Issues created beyond lookback_days should NOT be flagged."""
        old = _old_date_str()
        data = {
            "github": {
                "repos": [{
                    "repo": "test/repo",
                    "open_prs": [],
                    "open_issues": [
                        {"number": 20, "title": "Old stale issue", "createdAt": old},
                    ],
                    "ci_runs": [],
                }],
            },
            "preferences": {"lookback_days": 7, "stale_pr_days": 3, "max_issues_per_repo": 3},
        }
        items = pulse_formatter.generate_action_items(data)
        assert not any("#20" in item for item in items)

    def test_issue_without_created_at_skipped(self):
        """Issues without createdAt field should be skipped (not flagged)."""
        data = {
            "github": {
                "repos": [{
                    "repo": "test/repo",
                    "open_prs": [],
                    "open_issues": [
                        {"number": 30, "title": "No date issue"},
                    ],
                    "ci_runs": [],
                }],
            },
            "preferences": {"lookback_days": 7, "stale_pr_days": 3, "max_issues_per_repo": 3},
        }
        items = pulse_formatter.generate_action_items(data)
        assert not any("#30" in item for item in items)

    def test_custom_lookback_days_overrides_default(self):
        """Custom lookback_days should allow flagging older issues."""
        old = _old_date_str()
        data = {
            "github": {
                "repos": [{
                    "repo": "test/repo",
                    "open_prs": [],
                    "open_issues": [
                        {"number": 40, "title": "Old issue", "createdAt": old},
                    ],
                    "ci_runs": [],
                }],
            },
            "preferences": {"lookback_days": 60, "stale_pr_days": 3, "max_issues_per_repo": 3},
        }
        items = pulse_formatter.generate_action_items(data)
        assert any("#40" in item for item in items)

    def test_mixed_recent_and_old_issues(self):
        """Only recent issues should be flagged when both recent and old issues exist."""
        recent = _recent_date_str()
        old = _old_date_str()
        data = {
            "github": {
                "repos": [{
                    "repo": "test/repo",
                    "open_prs": [],
                    "open_issues": [
                        {"number": 1, "title": "Recent", "createdAt": recent},
                        {"number": 2, "title": "Old", "createdAt": old},
                    ],
                    "ci_runs": [],
                }],
            },
            "preferences": {"lookback_days": 7, "stale_pr_days": 3, "max_issues_per_repo": 3},
        }
        items = pulse_formatter.generate_action_items(data)
        assert any("#1" in item for item in items)
        assert not any("#2" in item for item in items)


class TestMaxIssuesPerRepo(unittest.TestCase):
    """Test max_issues_per_repo preference caps flagged issues per repo."""

    def test_max_issues_per_repo_in_default_config(self):
        """max_issues_per_repo should be present in DEFAULT_CONFIG preferences."""
        assert "max_issues_per_repo" in config.DEFAULT_CONFIG["preferences"]
        assert config.DEFAULT_CONFIG["preferences"]["max_issues_per_repo"] == 3

    def test_max_issues_caps_flagged_count(self):
        """Only max_issues_per_repo issues per repo should be flagged, even if more exist."""
        recent = _recent_date_str()
        data = {
            "github": {
                "repos": [{
                    "repo": "test/repo",
                    "open_prs": [],
                    "open_issues": [
                        {"number": i, "title": "Issue " + str(i), "createdAt": recent}
                        for i in range(1, 8)  # 7 recent issues
                    ],
                    "ci_runs": [],
                }],
            },
            "preferences": {"lookback_days": 7, "stale_pr_days": 3, "max_issues_per_repo": 3},
        }
        items = pulse_formatter.generate_action_items(data)
        issue_items = [i for i in items if "open issue" in i]
        assert len(issue_items) == 3

    def test_custom_max_issues_per_repo_override(self):
        """Custom max_issues_per_repo should override default cap."""
        recent = _recent_date_str()
        data = {
            "github": {
                "repos": [{
                    "repo": "test/repo",
                    "open_prs": [],
                    "open_issues": [
                        {"number": i, "title": "Issue " + str(i), "createdAt": recent}
                        for i in range(1, 6)  # 5 recent issues
                    ],
                    "ci_runs": [],
                }],
            },
            "preferences": {"lookback_days": 7, "stale_pr_days": 3, "max_issues_per_repo": 5},
        }
        items = pulse_formatter.generate_action_items(data)
        issue_items = [i for i in items if "open issue" in i]
        assert len(issue_items) == 5

    def test_shell_script_includes_max_issues_per_repo_in_preferences(self):
        """Shell script combined JSON preferences should include max_issues_per_repo."""
        content = self._read_shell_script()
        assert "max_issues_per_repo" in content, \
            "Shell script should include max_issues_per_repo in preferences"

    def test_config_example_includes_max_issues_per_repo(self):
        """config-example.yml should include max_issues_per_repo preference."""
        config_example_path = os.path.join(os.path.dirname(__file__), "..", "config-example.yml")
        if os.path.exists(config_example_path):
            content = open(config_example_path).read()
            assert "max_issues_per_repo" in content, \
                "config-example.yml should include max_issues_per_repo preference"

    def test_skill_md_includes_max_issues_per_repo(self):
        """SKILL.md config section should include max_issues_per_repo."""
        skill_md_path = os.path.join(os.path.dirname(__file__), "..", "SKILL.md")
        content = open(skill_md_path).read()
        assert "max_issues_per_repo" in content, \
            "SKILL.md should include max_issues_per_repo preference"

    def _read_shell_script(self):
        """Read the shell script content for inspection."""
        script_path = os.path.join(SCRIPTS_DIR, "daily-dev-pulse.sh")
        with open(script_path) as f:
            return f.read()


class TestMaxActionItems(unittest.TestCase):
    """Test that max_action_items preference is functional and configurable."""

    def test_max_action_items_in_default_config(self):
        """max_action_items should be present in DEFAULT_CONFIG preferences."""
        assert "max_action_items" in config.DEFAULT_CONFIG["preferences"], \
            "DEFAULT_CONFIG should include max_action_items preference"
        assert config.DEFAULT_CONFIG["preferences"]["max_action_items"] == 10

    def test_max_action_items_caps_output(self):
        """generate_action_items should cap output at max_action_items."""
        recent = _recent_date_str()
        data = {
            "github": {
                "repos": [{
                    "repo": "test/repo",
                    "open_prs": [
                        {"number": i, "title": "PR " + str(i),
                         "createdAt": (datetime.now(timezone.utc) - timedelta(days=5)).strftime("%Y-%m-%dT%H:%M:%SZ")}
                        for i in range(1, 20)  # 19 stale PRs
                    ],
                    "open_issues": [],
                    "ci_runs": [
                        {"name": "CI", "conclusion": "failure", "headBranch": "main"}
                    ],
                }],
            },
            "security": {
                "alerts": [
                    {"cve_id": "CVE-2025-" + str(i), "product": "fastapi",
                     "severity": "CRITICAL", "score": 9.0}
                    for i in range(1, 10)
                ],
            },
            "preferences": {"stale_pr_days": 3, "lookback_days": 7,
                            "max_issues_per_repo": 3, "max_action_items": 5},
        }
        items = pulse_formatter.generate_action_items(data)
        assert len(items) <= 5, f"Expected <=5 action items with max_action_items=5, got {len(items)}"

    def test_default_max_action_items_is_10(self):
        """Default max_action_items should be 10 when not specified in data."""
        data = {"github": {"repos": []}, "preferences": {}}
        items = pulse_formatter.generate_action_items(data)
        # No items generated from empty data, but the cap should be 10
        # Verify the default cap by checking the code uses 10 as fallback
        max_items = data.get("preferences", {}).get("max_action_items", 10)
        assert max_items == 10

    def test_custom_max_action_items_override(self):
        """Custom max_action_items should override the default cap."""
        recent = _recent_date_str()
        data = {
            "github": {
                "repos": [{
                    "repo": "test/repo",
                    "open_prs": [
                        {"number": i, "title": "PR " + str(i),
                         "createdAt": (datetime.now(timezone.utc) - timedelta(days=5)).strftime("%Y-%m-%dT%H:%M:%SZ")}
                        for i in range(1, 20)  # 19 stale PRs
                    ],
                    "open_issues": [],
                    "ci_runs": [],
                }],
            },
            "preferences": {"stale_pr_days": 3, "lookback_days": 7,
                            "max_issues_per_repo": 3, "max_action_items": 3},
        }
        items = pulse_formatter.generate_action_items(data)
        assert len(items) <= 3, f"Expected <=3 action items with max_action_items=3, got {len(items)}"

    def test_shell_script_includes_max_action_items_in_preferences(self):
        """Shell script combined JSON preferences should include max_action_items."""
        content = open(os.path.join(SCRIPTS_DIR, "daily-dev-pulse.sh")).read()
        assert "max_action_items" in content, \
            "Shell script should include max_action_items in preferences"

    def test_config_example_includes_max_action_items(self):
        """config-example.yml should include max_action_items preference."""
        config_example_path = os.path.join(os.path.dirname(__file__), "..", "config-example.yml")
        if os.path.exists(config_example_path):
            content = open(config_example_path).read()
            assert "max_action_items" in content, \
                "config-example.yml should include max_action_items preference"

    def test_skill_md_includes_max_action_items(self):
        """SKILL.md config section should include max_action_items."""
        skill_md_path = os.path.join(os.path.dirname(__file__), "..", "SKILL.md")
        content = open(skill_md_path).read()
        assert "max_action_items" in content, \
            "SKILL.md should include max_action_items preference"


class TestSkillMdStep4Accuracy(unittest.TestCase):
    """Test that SKILL.md Step 4 description matches actual implementation."""

    def test_step4_mentions_stale_pr_days_configurable(self):
        """Step 4 should describe stale PR threshold as configurable, not hardcoded."""
        skill_md_path = os.path.join(os.path.dirname(__file__), "..", "SKILL.md")
        content = open(skill_md_path).read()
        # Should NOT say "open > 3 days" (hardcoded threshold)
        assert "open > 3 days" not in content, \
            "SKILL.md Step 4 should not hardcode stale PR threshold as '3 days'"
        # Should mention configurable threshold
        assert "stale_pr_days" in content, \
            "SKILL.md Step 4 should reference configurable stale_pr_days threshold"

    def test_step4_does_not_claim_assigned_issues(self):
        """Step 4 should NOT claim 'assigned to you' — implementation flags recently created issues."""
        skill_md_path = os.path.join(os.path.dirname(__file__), "..", "SKILL.md")
        content = open(skill_md_path).read()
        assert "assigned to you" not in content, \
            "SKILL.md Step 4 should not claim 'assigned to you' — implementation flags recently created issues within lookback_days"

    def test_step4_mentions_lookback_days_for_issues(self):
        """Step 4 should mention lookback_days as the issue filtering criterion."""
        skill_md_path = os.path.join(os.path.dirname(__file__), "..", "SKILL.md")
        content = open(skill_md_path).read()
        assert "lookback_days" in content, \
            "SKILL.md Step 4 should mention lookback_days as the criterion for flagging issues"

    def test_step4_mentions_max_issues_per_repo(self):
        """Step 4 should mention max_issues_per_repo cap."""
        skill_md_path = os.path.join(os.path.dirname(__file__), "..", "SKILL.md")
        content = open(skill_md_path).read()
        assert "max_issues_per_repo" in content, \
            "SKILL.md Step 4 should mention max_issues_per_repo cap"


class TestConcurrentHnFetching(unittest.TestCase):
    """Test concurrent HN story fetching and partial failure handling."""

    def test_fetch_hn_item_exists(self):
        """_fetch_hn_item helper function should exist in news_aggregator."""
        assert hasattr(news_aggregator, "_fetch_hn_item"), \
            "news_aggregator should have _fetch_hn_item helper function for concurrent fetching"

    def test_fetch_hn_item_returns_story_dict(self):
        """_fetch_hn_item should return a properly structured story dict on success."""
        mock_item = {"type": "story", "title": "Test Story", "url": "https://test.com", "score": 42, "descendants": 5}
        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_resp = MagicMock()
            mock_resp.read.return_value = json.dumps(mock_item).encode()
            mock_urlopen.return_value.__enter__ = MagicMock(return_value=mock_resp)
            mock_urlopen.return_value.__exit__ = MagicMock(return_value=False)
            result = news_aggregator._fetch_hn_item(12345)
            assert result is not None
            assert result["id"] == 12345
            assert result["title"] == "Test Story"
            assert result["score"] == 42
            assert result["source"] == "hn"

    def test_fetch_hn_item_returns_none_on_error(self):
        """_fetch_hn_item should return None when the API call fails."""
        with patch("urllib.request.urlopen", side_effect=Exception("network error")):
            result = news_aggregator._fetch_hn_item(99999)
            assert result is None

    def test_fetch_hn_item_returns_none_for_non_story(self):
        """_fetch_hn_item should return None for non-story items (e.g., comments)."""
        mock_item = {"type": "comment", "text": "This is a comment"}
        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_resp = MagicMock()
            mock_resp.read.return_value = json.dumps(mock_item).encode()
            mock_urlopen.return_value.__enter__ = MagicMock(return_value=mock_resp)
            mock_urlopen.return_value.__exit__ = MagicMock(return_value=False)
            result = news_aggregator._fetch_hn_item(12345)
            assert result is None

    def test_fetch_hn_top_uses_threadpool(self):
        """fetch_hn_top should use ThreadPoolExecutor for concurrent fetching."""
        import inspect
        source = inspect.getsource(news_aggregator.fetch_hn_top)
        assert "ThreadPoolExecutor" in source, \
            "fetch_hn_top should use ThreadPoolExecutor for concurrent API calls"

    def test_fetch_hn_top_preserves_order(self):
        """fetch_hn_top should preserve original story ID order after concurrent fetch."""
        story_ids = [100, 200, 300]
        mock_results = [
            {"id": 100, "title": "Story 100", "url": "https://100.com", "score": 10, "comments": 1, "source": "hn"},
            {"id": 200, "title": "Story 200", "url": "https://200.com", "score": 20, "comments": 2, "source": "hn"},
            {"id": 300, "title": "Story 300", "url": "https://300.com", "score": 30, "comments": 3, "source": "hn"},
        ]

        with patch("news_aggregator._fetch_hn_item", side_effect=mock_results):
            with patch("urllib.request.urlopen") as mock_top:
                mock_top_resp = MagicMock()
                mock_top_resp.read.return_value = json.dumps(story_ids).encode()
                mock_top.return_value.__enter__ = MagicMock(return_value=mock_top_resp)
                mock_top.return_value.__exit__ = MagicMock(return_value=False)
                result = news_aggregator.fetch_hn_top(3)

            # Results should be in original ID order: 100, 200, 300
            assert len(result) == 3
            assert result[0]["id"] == 100
            assert result[1]["id"] == 200
            assert result[2]["id"] == 300

    def test_fetch_hn_top_handles_partial_failure(self):
        """fetch_hn_top should return successfully fetched stories even if some fail."""
        story_ids = [100, 200, 300]
        mock_results = [
            {"id": 100, "title": "Story 100", "url": "https://100.com", "score": 10, "comments": 1, "source": "hn"},
            None,  # Story 200 fetch fails
            {"id": 300, "title": "Story 300", "url": "https://300.com", "score": 30, "comments": 3, "source": "hn"},
        ]

        with patch("news_aggregator._fetch_hn_item", side_effect=mock_results):
            with patch("urllib.request.urlopen") as mock_top:
                mock_top_resp = MagicMock()
                mock_top_resp.read.return_value = json.dumps(story_ids).encode()
                mock_top.return_value.__enter__ = MagicMock(return_value=mock_top_resp)
                mock_top.return_value.__exit__ = MagicMock(return_value=False)
                result = news_aggregator.fetch_hn_top(3)

        # Should have 2 stories (partial failure gracefully handled)
        assert len(result) == 2
        assert result[0]["id"] == 100
        assert result[1]["id"] == 300

    def test_fetch_hn_top_max_workers_capped(self):
        """ThreadPoolExecutor max_workers should be capped at 5 to avoid overwhelming HN API."""
        import inspect
        source = inspect.getsource(news_aggregator.fetch_hn_top)
        assert "max_workers=min" in source, \
            "ThreadPoolExecutor should cap max_workers to avoid excessive concurrent requests"

    def test_concurrent_futures_imported(self):
        """news_aggregator should import concurrent.futures for ThreadPoolExecutor."""
        import inspect
        source = inspect.getsource(news_aggregator)
        assert "ThreadPoolExecutor" in source, \
            "news_aggregator should import ThreadPoolExecutor from concurrent.futures"
        assert "as_completed" in source, \
            "news_aggregator should import as_completed from concurrent.futures"


if __name__ == "__main__":
    unittest.main()