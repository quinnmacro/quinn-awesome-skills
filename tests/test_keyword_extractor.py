"""Tests for keyword_extractor module."""

import pytest
from keyword_extractor import KeywordExtractor


class TestKeywordExtractorInit:
    def test_default_init(self):
        extractor = KeywordExtractor()
        assert extractor is not None

    def test_init_without_translation(self):
        extractor = KeywordExtractor(enable_translation=False)
        assert extractor.translator is None

    def test_init_with_api_enabled(self):
        extractor = KeywordExtractor(enable_translation=True, enable_api=True)
        assert extractor.enable_api is True


class TestExtractKeywords:
    def test_empty_text(self):
        extractor = KeywordExtractor(enable_translation=False)
        result = extractor.extract_keywords("")
        assert result == []

    def test_none_text(self):
        extractor = KeywordExtractor(enable_translation=False)
        result = extractor.extract_keywords(None)
        assert result == []

    def test_english_simple(self):
        extractor = KeywordExtractor(enable_translation=False)
        result = extractor.extract_keywords("python web framework")
        assert "python" in result
        assert "framework" in result

    def test_english_with_stopwords(self):
        extractor = KeywordExtractor(enable_translation=False)
        result = extractor.extract_keywords("I need a library for data processing")
        assert "library" in result
        assert "data" in result
        # stopwords should be filtered
        assert "i" not in result
        assert "a" not in result
        assert "for" not in result

    def test_max_keywords_limit(self):
        extractor = KeywordExtractor(enable_translation=False)
        result = extractor.extract_keywords(
            "python javascript rust golang typescript kotlin framework library tool package",
            max_keywords=3
        )
        assert len(result) <= 3

    def test_deduplication(self):
        extractor = KeywordExtractor(enable_translation=False)
        result = extractor.extract_keywords("python python python")
        assert len(result) <= 1

    def test_short_words_filtered(self):
        extractor = KeywordExtractor(enable_translation=False)
        result = extractor.extract_keywords("a an the python framework")
        # short words (< 3 chars) should be filtered
        assert "a" not in result
        assert "an" not in result
        assert "python" in result

    def test_tech_keywords_preserved(self):
        extractor = KeywordExtractor(enable_translation=False)
        result = extractor.extract_keywords("I need a cli tool for web")
        assert "cli" in result
        assert "tool" in result
        assert "web" in result


class TestBuildSearchQuery:
    def test_empty_keywords(self):
        result = KeywordExtractor.build_search_query([])
        assert result == ""

    def test_single_keyword(self):
        result = KeywordExtractor.build_search_query(["python"])
        assert result == "python"

    def test_multiple_keywords(self):
        result = KeywordExtractor.build_search_query(["python", "web", "framework"])
        assert result == "python web framework"


class TestTranslateKeywords:
    def test_no_translator(self):
        extractor = KeywordExtractor(enable_translation=False)
        result = extractor.translate_keywords(["python", "web"])
        assert result == [("python", "python"), ("web", "web")]

    def test_english_keywords_unchanged(self):
        extractor = KeywordExtractor(enable_translation=True, enable_api=False)
        result = extractor.translate_keywords(["python", "framework"])
        assert result == [("python", "python"), ("framework", "framework")]

    def test_chinese_keyword_translated(self):
        extractor = KeywordExtractor(enable_translation=True, enable_api=False)
        result = extractor.translate_keywords(["机器学习"])
        assert len(result) == 1
        original, translated = result[0]
        assert original == "机器学习"
        assert translated == "machine learning"


class TestBuildEnglishQuery:
    def test_no_translator(self):
        extractor = KeywordExtractor(enable_translation=False)
        result = extractor.build_english_query(["python", "web"])
        assert result == "python web"

    def test_empty_keywords(self):
        extractor = KeywordExtractor(enable_translation=False)
        result = extractor.build_english_query([])
        assert result == ""

    def test_mixed_keywords(self):
        extractor = KeywordExtractor(enable_translation=True, enable_api=False)
        result = extractor.build_english_query(["python", "机器学习"])
        assert "python" in result
        assert "machine learning" in result


class TestExtractAndTranslate:
    def test_no_translator(self):
        extractor = KeywordExtractor(enable_translation=False)
        original, translated = extractor.extract_and_translate("python web framework")
        assert original == translated

    def test_english_text(self):
        extractor = KeywordExtractor(enable_translation=True, enable_api=False)
        original, translated = extractor.extract_and_translate("python web framework")
        # English keywords should be unchanged
        for o, t in zip(original, translated):
            assert o == t

    def test_chinese_text(self):
        extractor = KeywordExtractor(enable_translation=True, enable_api=False)
        original, translated = extractor.extract_and_translate("机器学习框架")
        assert len(original) > 0
        assert len(translated) > 0