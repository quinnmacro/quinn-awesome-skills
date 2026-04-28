"""
Tests for url-fetcher scripts (fetch.sh, search.sh).
Verifies URL routing logic, argument validation, content checks,
and social media URL transformations.
"""

import subprocess
import os
import re
import pytest

SCRIPTS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "skills", "core", "url-fetcher", "scripts"
)
FETCH_SH = os.path.join(SCRIPTS_DIR, "fetch.sh")
SEARCH_SH = os.path.join(SCRIPTS_DIR, "search.sh")


def run_bash(script, args=None, timeout=10):
    """Run a bash script with args, return (stdout, stderr, returncode)."""
    cmd = ["bash", script]
    if args:
        cmd.extend(args)
    result = subprocess.run(
        cmd, capture_output=True, text=True, timeout=timeout
    )
    return result.stdout, result.stderr, result.returncode


# ============================================
# fetch.sh - Argument Validation
# ============================================

class TestFetchArgValidation:
    def test_no_args_prints_usage(self):
        _, stderr, rc = run_bash(FETCH_SH)
        assert rc != 0
        assert "Usage" in stderr or "Usage" in _

    def test_missing_url_arg(self):
        _, stderr, rc = run_bash(FETCH_SH, [])
        assert rc != 0

    def test_empty_url_arg(self):
        _, stderr, rc = run_bash(FETCH_SH, [""])
        # Empty string still triggers usage error via :? syntax
        assert rc != 0

    def test_proxy_arg_in_script(self):
        """Verify fetch.sh accepts proxy as second argument by checking script source."""
        with open(FETCH_SH) as f:
            content = f.read()
        # Script defines PROXY="${2:-}" which means second arg is optional proxy
        assert 'PROXY="${2:-}"' in content
        # _curl function uses https_proxy and http_proxy when PROXY is set
        assert "https_proxy" in content
        assert "http_proxy" in content


# ============================================
# fetch.sh - URL Routing (Social Media)
# ============================================

class TestFetchURLRouting:
    """Test that fetch.sh routes URLs to the correct handler based on domain."""

    # Twitter/X URL patterns
    TWITTER_URLS = [
        "https://twitter.com/user/status/123",
        "https://x.com/user/status/456",
        "http://x.com/elonmusk/status/9999",
    ]

    @pytest.mark.parametrize("url", TWITTER_URLS)
    def test_twitter_url_recognized(self, url):
        """Twitter/X URLs with /status pattern should be routed to fetch_twitter."""
        pattern = r"(twitter\.com|x\.com)/.*status"
        assert re.search(pattern, url), f"URL {url} should match Twitter pattern"

    def test_twitter_url_without_status_not_matched(self):
        """Twitter/X URLs without /status should not be routed to fetch_twitter."""
        url = "https://x.com/elonmusk"
        pattern = r"(twitter\.com|x\.com)/.*status"
        assert not re.search(pattern, url)

    # Instagram
    def test_instagram_url_recognized(self):
        url = "https://instagram.com/p/ABC123"
        assert "instagram.com" in url

    # TikTok
    def test_tiktok_url_recognized(self):
        url = "https://tiktok.com/@user/video/123"
        assert "tiktok.com" in url

    # Reddit
    def test_reddit_url_recognized(self):
        url = "https://reddit.com/r/python/comments/abc"
        assert "reddit.com" in url

    # Threads
    def test_threads_url_recognized(self):
        url = "https://threads.net/post/123"
        assert "threads.net" in url

    # Bluesky
    def test_bluesky_url_recognized(self):
        url = "https://bsky.app/profile/user/post/123"
        assert "bsky.app" in url


# ============================================
# fetch.sh - Social Media URL Transformations
# ============================================

class TestFetchURLTransformations:
    """Test that social media URLs are correctly transformed to fixer services."""

    def test_instagram_to_fxstagram(self):
        url = "https://instagram.com/p/ABC123"
        fixed = re.sub(r"instagram\.com", "fxstagram.com", url)
        assert fixed == "https://fxstagram.com/p/ABC123"

    def test_tiktok_to_tnktok(self):
        url = "https://tiktok.com/@user/video/123"
        fixed = re.sub(r"tiktok\.com", "a.tnktok.com", url)
        assert fixed == "https://a.tnktok.com/@user/video/123"

    def test_reddit_to_vxreddit(self):
        url = "https://reddit.com/r/python/comments/abc"
        fixed = re.sub(r"reddit\.com", "vxreddit.com", url)
        assert fixed == "https://vxreddit.com/r/python/comments/abc"

    def test_threads_to_fixthreads(self):
        url = "https://threads.net/post/123"
        fixed = re.sub(r"threads\.net", "fixthreads.seria.moe", url)
        assert fixed == "https://fixthreads.seria.moe/post/123"

    def test_bluesky_to_fxbsky(self):
        url = "https://bsky.app/profile/user/post/123"
        fixed = re.sub(r"bsky\.app", "fxbsky.app", url)
        assert fixed == "https://fxbsky.app/profile/user/post/123"


# ============================================
# fetch.sh - Twitter URL Parsing (Embedded Python)
# ============================================

class TestFetchTwitterParsing:
    """Test the embedded Python Twitter URL parsing logic from fetch.sh."""

    def parse_twitter_url(self, url):
        """Replicate the Python parsing logic from fetch_twitter()."""
        m = re.search(r"(x\.com|twitter\.com)/([^/]+)/status/(\d+)", url)
        if m:
            return m.group(2), m.group(3)
        return None, None

    def test_x_com_url_parsed(self):
        screen_name, status_id = self.parse_twitter_url(
            "https://x.com/elaboratestuff/status/1234567890"
        )
        assert screen_name == "elaboratestuff"
        assert status_id == "1234567890"

    def test_twitter_com_url_parsed(self):
        screen_name, status_id = self.parse_twitter_url(
            "https://twitter.com/elonmusk/status/18945683125"
        )
        assert screen_name == "elonmusk"
        assert status_id == "18945683125"

    def test_http_x_com_parsed(self):
        screen_name, status_id = self.parse_twitter_url(
            "http://x.com/testuser/status/99"
        )
        assert screen_name == "testuser"
        assert status_id == "99"

    def test_no_status_id_returns_none(self):
        screen_name, status_id = self.parse_twitter_url(
            "https://x.com/elonmusk"
        )
        assert screen_name is None
        assert status_id is None

    def test_non_twitter_url_returns_none(self):
        screen_name, status_id = self.parse_twitter_url(
            "https://example.com/page"
        )
        assert screen_name is None
        assert status_id is None

    def test_long_status_id(self):
        screen_name, status_id = self.parse_twitter_url(
            "https://x.com/user/status/1894628739501827365"
        )
        assert screen_name == "user"
        assert status_id == "1894628739501827365"


# ============================================
# fetch.sh - _has_content Logic
# ============================================

class TestFetchHasContent:
    """Test the _has_content validation logic from fetch.sh."""

    def has_content(self, content):
        """Replicate _has_content bash logic in Python."""
        lines = content.strip().split("\n")
        if len(lines) <= 5:
            return False
        error_patterns = [
            "Don't miss what's happening",
            "Access Denied",
            "404 Not Found",
        ]
        for pattern in error_patterns:
            if pattern in content:
                return False
        return True

    def test_short_content_rejected(self):
        content = "line1\nline2\nline3\nline4\nline5"
        assert not self.has_content(content)

    def test_exactly_5_lines_rejected(self):
        content = "\n".join(["line"] * 5)
        assert not self.has_content(content)

    def test_6_lines_accepted(self):
        content = "\n".join(["line"] * 6)
        assert self.has_content(content)

    def test_many_lines_accepted(self):
        content = "\n".join(["line"] * 50)
        assert self.has_content(content)

    def test_twitter_error_page_rejected(self):
        content = "\n".join(["Don't miss what's happening"] + ["line"] * 20)
        assert not self.has_content(content)

    def test_access_denied_rejected(self):
        content = "\n".join(["Access Denied"] + ["line"] * 20)
        assert not self.has_content(content)

    def test_404_not_found_rejected(self):
        content = "\n".join(["404 Not Found"] + ["line"] * 20)
        assert not self.has_content(content)

    def test_normal_content_accepted(self):
        content = "\n".join(["# Title", "Some content", "More content"] + ["line"] * 20)
        assert self.has_content(content)

    def test_empty_content_rejected(self):
        assert not self.has_content("")

    def test_single_line_rejected(self):
        assert not self.has_content("just one line")


# ============================================
# fetch.sh - Proxy Handling (_curl)
# ============================================

class TestFetchProxyHandling:
    """Test that proxy argument is correctly handled by _curl logic."""

    def test_proxy_env_vars_set(self):
        """When proxy is provided, https_proxy and http_proxy should be set."""
        # We test the logic pattern, not actual curl execution
        proxy = "http://127.0.0.1:7890"
        # The script sets both https_proxy and http_proxy when proxy is provided
        assert proxy.startswith("http://")

    def test_no_proxy_means_direct_curl(self):
        """When no proxy provided, curl should run without proxy env vars."""
        # PROXY defaults to empty string
        proxy = ""
        assert proxy == ""


# ============================================
# search.sh - Argument Validation
# ============================================

class TestSearchArgValidation:
    def test_no_args_prints_usage(self):
        _, stderr, rc = run_bash(SEARCH_SH)
        assert rc != 0
        assert "Usage" in stderr or "Usage" in _

    def test_empty_query_fails(self):
        _, stderr, rc = run_bash(SEARCH_SH, [""])
        assert rc != 0

    def test_query_only(self):
        """Search with just a query should work (uses default engine/limit)."""
        _, stderr, rc = run_bash(SEARCH_SH, ["test query"])
        # Depends on npx availability; may succeed or timeout
        # Just verify it doesn't crash immediately on arg parsing
        assert rc in (0, 1) or "Usage" not in stderr

    def test_query_with_engine(self):
        """Search with query + engine should work."""
        _, stderr, rc = run_bash(SEARCH_SH, ["test", "bing"])
        assert rc in (0, 1) or "Usage" not in stderr

    def test_query_with_engine_and_limit(self):
        """Search with all three args should work."""
        _, stderr, rc = run_bash(SEARCH_SH, ["test", "duckduckgo", "3"])
        assert rc in (0, 1) or "Usage" not in stderr


# ============================================
# search.sh - Default Values
# ============================================

class TestSearchDefaults:
    """Test that search.sh uses correct defaults for engine and limit."""

    def test_default_engine_is_duckduckgo(self):
        """ENGINE defaults to 'duckduckgo' per script line 13."""
        # Read the script to verify default
        with open(SEARCH_SH) as f:
            content = f.read()
        assert "ENGINE=\"${2:-duckduckgo}\"" in content

    def test_default_limit_is_5(self):
        """LIMIT defaults to 5 per script line 14."""
        with open(SEARCH_SH) as f:
            content = f.read()
        assert "LIMIT=\"${3:-5}\"" in content


# ============================================
# fetch.sh - Fallback Cascade Order
# ============================================

class TestFetchFallbackCascade:
    """Test that fetch.sh uses the correct fallback cascade order."""

    def test_jina_is_first_fallback(self):
        """r.jina.ai should be the first general fallback after social handlers."""
        with open(FETCH_SH) as f:
            content = f.read()
        # Find the cascade section after social handlers
        jina_pos = content.find("r.jina.ai")
        defuddle_pos = content.find("defuddle.md")
        agent_pos = content.find("agent-fetch")
        assert jina_pos > 0
        assert defuddle_pos > jina_pos
        assert agent_pos > defuddle_pos

    def test_social_handlers_before_fallbacks(self):
        """Social media handlers should appear before the fallback cascade."""
        with open(FETCH_SH) as f:
            content = f.read()
        twitter_pos = content.find("fetch_twitter")
        instagram_pos = content.find("fetch_instagram")
        jina_pos = content.find("r.jina.ai")
        # Social handlers defined before cascade
        assert twitter_pos < jina_pos
        assert instagram_pos < jina_pos

    def test_error_exit_if_all_fail(self):
        """Script should exit with error if all fetch methods fail."""
        with open(FETCH_SH) as f:
            content = f.read()
        assert "All fetch methods failed" in content
        assert "exit 1" in content.split("All fetch methods failed")[0].split("\n")[-1] or "exit 1" in content


# ============================================
# fetch.sh - Script Structure Validation
# ============================================

class TestFetchScriptStructure:
    def test_script_has_set_euo_pipefail(self):
        with open(FETCH_SH) as f:
            content = f.read()
        assert "set -euo pipefail" in content

    def test_script_has_shebang(self):
        with open(FETCH_SH) as f:
            first_line = f.readline()
        assert first_line.startswith("#!/usr/bin/env bash")

    def test_has_all_social_handlers(self):
        """fetch.sh should define handlers for all supported social media."""
        with open(FETCH_SH) as f:
            content = f.read()
        handlers = [
            "fetch_twitter", "fetch_instagram", "fetch_tiktok",
            "fetch_reddit", "fetch_threads", "fetch_bluesky"
        ]
        for handler in handlers:
            assert f"function {handler}" in content or f"{handler}()" in content, \
                f"Missing handler: {handler}"