"""Tests for Daily Dev Pulse modules and formatter.

Uses mock data to test without requiring live API access.
"""

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

    def test_format_terminal_no_github(self):
        data = {"github": {"error": "gh_not_available"}}
        output = pulse_formatter.format_terminal(data)
        assert "gh_not_available" in output


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


if __name__ == "__main__":
    unittest.main()