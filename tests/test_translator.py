"""Tests for translator module."""

import pytest
from translator import TechTranslator


class TestTechTranslatorInit:
    def test_default_init(self):
        translator = TechTranslator(enable_api=False)
        assert translator.enable_api is False

    def test_api_disabled_init(self):
        translator = TechTranslator(enable_api=False)
        assert translator.enable_api is False


class TestIsChinese:
    def test_chinese_text(self):
        translator = TechTranslator(enable_api=False)
        assert translator.is_chinese("机器学习") is True

    def test_mixed_text(self):
        translator = TechTranslator(enable_api=False)
        assert translator.is_chinese("Python机器学习") is True

    def test_english_text(self):
        translator = TechTranslator(enable_api=False)
        assert translator.is_chinese("machine learning") is False

    def test_empty_text(self):
        translator = TechTranslator(enable_api=False)
        assert translator.is_chinese("") is False


class TestTranslateLocal:
    def test_direct_match(self):
        translator = TechTranslator(enable_api=False)
        result = translator.translate_local("机器学习")
        assert result == "machine learning"

    def test_direct_match_database(self):
        translator = TechTranslator(enable_api=False)
        result = translator.translate_local("数据库")
        assert result == "database"

    def test_no_match(self):
        translator = TechTranslator(enable_api=False)
        result = translator.translate_local("企鹅")
        assert result is None

    def test_partial_match(self):
        translator = TechTranslator(enable_api=False)
        result = translator.translate_local("数据库连接池")
        # Should find longest match "数据库"
        assert result is not None
        assert "database" in result


class TestTranslate:
    def test_chinese_with_local_dict(self):
        translator = TechTranslator(enable_api=False)
        result = translator.translate("机器学习")
        assert result == "machine learning"

    def test_english_text_unchanged(self):
        translator = TechTranslator(enable_api=False)
        result = translator.translate("machine learning")
        assert result == "machine learning"

    def test_unknown_chinese_returns_original(self):
        translator = TechTranslator(enable_api=False)
        result = translator.translate("企鹅")
        # No local match, no API, should return original
        assert result == "企鹅"

    def test_api_disabled(self):
        translator = TechTranslator(enable_api=False)
        # translate_api should return None when API is disabled
        result = translator.translate_api("企鹅")
        assert result is None


class TestTranslateKeywords:
    def test_list_of_keywords(self):
        translator = TechTranslator(enable_api=False)
        result = translator.translate_keywords(["机器学习", "python"])
        assert len(result) == 2
        assert result[0] == ("机器学习", "machine learning")
        assert result[1] == ("python", "python")

    def test_all_english(self):
        translator = TechTranslator(enable_api=False)
        result = translator.translate_keywords(["python", "web"])
        assert result == [("python", "python"), ("web", "web")]


class TestBuildEnglishQuery:
    def test_mixed_keywords(self):
        translator = TechTranslator(enable_api=False)
        result = translator.build_english_query(["python", "机器学习"])
        assert "python" in result
        assert "machine learning" in result

    def test_all_english(self):
        translator = TechTranslator(enable_api=False)
        result = translator.build_english_query(["python", "web"])
        assert result == "python web"

    def test_all_chinese(self):
        translator = TechTranslator(enable_api=False)
        result = translator.build_english_query(["数据库", "缓存"])
        assert "database" in result
        assert "cache" in result


class TestTechDictionary:
    def test_dictionary_has_entries(self):
        assert len(TechTranslator.TECH_DICTIONARY) > 50

    def test_common_entries(self):
        assert TechTranslator.TECH_DICTIONARY["编程语言"] == "programming language"
        assert TechTranslator.TECH_DICTIONARY["数据库"] == "database"
        assert TechTranslator.TECH_DICTIONARY["缓存"] == "cache"
        assert TechTranslator.TECH_DICTIONARY["微服务"] == "microservice"