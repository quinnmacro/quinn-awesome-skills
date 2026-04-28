"""Tests for formatter module."""

import pytest
from formatter import ResultFormatter


class TestFormatTimestamp:
    def test_iso_format(self):
        result = ResultFormatter.format_timestamp("2026-03-15T10:30:00Z")
        assert result == "2026-03-15"

    def test_iso_with_timezone(self):
        result = ResultFormatter.format_timestamp("2026-03-15T10:30:00+08:00")
        assert result == "2026-03-15"

    def test_empty_string(self):
        result = ResultFormatter.format_timestamp("")
        assert result == "未知"

    def test_none_value(self):
        result = ResultFormatter.format_timestamp(None)
        assert result == "未知"

    def test_invalid_format(self):
        result = ResultFormatter.format_timestamp("not-a-date")
        assert result == "not-a-date"

    def test_plain_date(self):
        result = ResultFormatter.format_timestamp("2026-01-01")
        assert result == "2026-01-01"


class TestFormatStars:
    def test_thousands(self):
        result = ResultFormatter.format_stars(1234)
        assert result == "1.2k"

    def test_exact_thousand(self):
        result = ResultFormatter.format_stars(1000)
        assert result == "1.0k"

    def test_large_number(self):
        result = ResultFormatter.format_stars(50000)
        assert result == "50.0k"

    def test_small_number(self):
        result = ResultFormatter.format_stars(42)
        assert result == "42"

    def test_zero(self):
        result = ResultFormatter.format_stars(0)
        assert result == "0"

    def test_none(self):
        result = ResultFormatter.format_stars(None)
        assert result == "0"

    def test_string_input(self):
        result = ResultFormatter.format_stars("1500")
        assert result == "1.5k"

    def test_invalid_string(self):
        result = ResultFormatter.format_stars("not-a-number")
        assert result == "not-a-number"


class TestGetHealthIndicator:
    def test_active_high_stars(self):
        from datetime import datetime, timezone
        recent = datetime.now(timezone.utc).isoformat()
        data = {'stars': 1500, 'updated_at': recent}
        result = ResultFormatter.get_health_indicator(data)
        assert result == "🟢 优秀"

    def test_active_moderate_stars(self):
        from datetime import datetime, timezone
        recent = datetime.now(timezone.utc).isoformat()
        data = {'stars': 200, 'updated_at': recent}
        result = ResultFormatter.get_health_indicator(data)
        assert result == "🟡 良好"

    def test_low_stars(self):
        data = {'stars': 15}
        result = ResultFormatter.get_health_indicator(data)
        assert result == "🟠 一般"

    def test_new_project(self):
        data = {'stars': 3}
        result = ResultFormatter.get_health_indicator(data)
        assert result == "🔴 新项目"

    def test_stargazers_count_field(self):
        from datetime import datetime, timezone
        recent = datetime.now(timezone.utc).isoformat()
        data = {'stargazers_count': 2000, 'updated_at': recent}
        result = ResultFormatter.get_health_indicator(data)
        assert result == "🟢 优秀"

    def test_no_stars(self):
        result = ResultFormatter.get_health_indicator({})
        assert result == "🔴 新项目"


class TestFormatGithubResults:
    def test_empty_results(self):
        result = ResultFormatter.format_github_results(None, "test")
        assert "未找到" in result

    def test_no_items(self):
        result = ResultFormatter.format_github_results({'items': []}, "test")
        assert "未找到" in result

    def test_with_items(self):
        items = {
            'total_count': 1,
            'items': [{
                'full_name': 'user/repo',
                'html_url': 'https://github.com/user/repo',
                'stargazers_count': 100,
                'updated_at': '2026-03-15T10:30:00Z',
                'description': 'A test project',
            }]
        }
        result = ResultFormatter.format_github_results(items, "test query")
        assert "user/repo" in result
        assert "100" in result

    def test_long_description_truncated(self):
        items = {
            'total_count': 1,
            'items': [{
                'full_name': 'user/repo',
                'html_url': 'https://github.com/user/repo',
                'stargazers_count': 100,
                'updated_at': '2026-03-15T10:30:00Z',
                'description': 'A very long description that exceeds the 60 character limit for display purposes in the table format',
            }]
        }
        result = ResultFormatter.format_github_results(items, "test")
        assert "..." in result

    def test_none_description(self):
        items = {
            'total_count': 1,
            'items': [{
                'full_name': 'user/repo',
                'html_url': 'https://github.com/user/repo',
                'stargazers_count': 100,
                'updated_at': '2026-03-15T10:30:00Z',
                'description': None,
            }]
        }
        result = ResultFormatter.format_github_results(items, "test")
        assert "无描述" in result


class TestFormatArxivResults:
    def test_empty_results(self):
        result = ResultFormatter.format_arxiv_results(None, "test")
        assert "未找到" in result

    def test_with_papers(self):
        papers = [{
            'title': 'Deep Learning for NLP',
            'authors': ['Smith J', 'Lee K'],
            'published': '2026-01-15T00:00:00Z',
            'link': 'https://arxiv.org/abs/2601.12345',
        }]
        result = ResultFormatter.format_arxiv_results(papers, "test")
        assert "Deep Learning" in result

    def test_long_title_truncated(self):
        papers = [{
            'title': 'A very long paper title about deep learning and natural language processing that exceeds 80 characters',
            'authors': 'Smith',
            'published': '2026-01-15',
            'link': '#',
        }]
        result = ResultFormatter.format_arxiv_results(papers, "test")
        assert "..." in result

    def test_author_list_truncated(self):
        papers = [{
            'title': 'Short title',
            'authors': ['Author One', 'Author Two', 'Author Three', 'Author Four', 'Author Five'],
            'published': '2026-01-15',
            'link': '#',
        }]
        result = ResultFormatter.format_arxiv_results(papers, "test")
        # Authors string should be truncated
        assert "..." in result


class TestFormatSummary:
    def test_no_results(self):
        result = ResultFormatter.format_summary(0, 0)
        assert "未找到" in result

    def test_many_github_results(self):
        result = ResultFormatter.format_summary(5, 0)
        assert "5 个GitHub项目" in result
        assert "有多个成熟项目" in result

    def test_few_github_results(self):
        result = ResultFormatter.format_summary(1, 0)
        assert "少量相关项目" in result

    def test_only_arxiv_results(self):
        result = ResultFormatter.format_summary(0, 3)
        assert "3 篇arXiv论文" in result

    def test_mixed_results(self):
        result = ResultFormatter.format_summary(4, 2)
        assert "4 个GitHub项目" in result
        assert "2 篇arXiv论文" in result