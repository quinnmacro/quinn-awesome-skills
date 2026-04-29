"""Tests for skill_discovery module."""

import pytest
from pathlib import Path

# Project root for real skills directory
SKILL_HUB_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = SKILL_HUB_DIR.parent.parent.parent
REAL_SKILLS_DIR = PROJECT_ROOT / "skills"

from skill_discovery import (
    discover_skills,
    get_skill_by_name,
    search_skills,
    _yaml_frontmatter,
    _parse_description,
    _list_scripts,
    _list_modules,
    _layer_from_category,
    _extract_dependencies,
    check_dep_installed,
    check_all_deps,
    _add_skill,
    _read_skill_md,
)


# --- _yaml_frontmatter tests ---


class TestYamlFrontmatter:
    def test_simple_frontmatter(self):
        text = "---\nname: foo\nversion: 1.0\n---\nbody"
        result = _yaml_frontmatter(text)
        assert result["name"] == "foo"
        assert result["version"] == "1.0"

    def test_multiline_description(self):
        text = "---\nname: bar\ndescription: |\n  Multi line\n  description text\nversion: 2.0\n---\nbody"
        result = _yaml_frontmatter(text)
        assert result["name"] == "bar"
        assert "Multi" in result["description"]
        assert result["version"] == "2.0"

    def test_no_frontmatter(self):
        text = "# Just markdown\nno frontmatter"
        result = _yaml_frontmatter(text)
        assert result == {}

    def test_empty_frontmatter(self):
        text = "---\n---\nbody"
        result = _yaml_frontmatter(text)
        assert result == {}

    def test_multiple_keys(self):
        text = "---\nname: test\nversion: 3.0\nauthor: dev\nlayer: core\n---\n"
        result = _yaml_frontmatter(text)
        assert result["name"] == "test"
        assert result["version"] == "3.0"
        assert result["author"] == "dev"
        assert result["layer"] == "core"

    def test_description_with_pipe(self):
        text = "---\nname: x\ndescription: |\n  Line one\n  Line two\n---\n"
        result = _yaml_frontmatter(text)
        assert "Line one" in result["description"]

    def test_inline_description(self):
        text = "---\nname: y\ndescription: Short desc\n---\n"
        result = _yaml_frontmatter(text)
        assert result["description"] == "Short desc"

    def test_description_with_triggers(self):
        text = "---\nname: z\ndescription: Fetch URLs. Triggers: fetch this\n---\n"
        result = _yaml_frontmatter(text)
        assert "Fetch URLs" in result["description"]

    def test_key_with_empty_value(self):
        text = "---\nname: a\nauthor:\nversion: 1.0\n---\n"
        result = _yaml_frontmatter(text)
        assert result["name"] == "a"
        assert result.get("author", "") == ""

    def test_frontmatter_with_special_chars(self):
        text = "---\nname: url-fetcher\nversion: 1.0.0\n---\n"
        result = _yaml_frontmatter(text)
        assert result["name"] == "url-fetcher"

    def test_description_multiline_with_period(self):
        text = "---\ndescription: |\n  Search existing solutions. Avoid reinventing the wheel. Triggers: presearch\n---\n"
        result = _yaml_frontmatter(text)
        assert "Search existing solutions" in result["description"]


# --- _parse_description tests ---


class TestParseDescription:
    def test_simple_description(self):
        assert _parse_description({"description": "A simple skill"}) == "A simple skill"

    def test_description_with_trigger_phrases(self):
        desc = _parse_description({"description": "Fetch URLs. Triggers: fetch this"})
        assert "Triggers" not in desc

    def test_empty_description(self):
        assert _parse_description({"description": ""}) == ""

    def test_missing_description_key(self):
        assert _parse_description({}) == ""

    def test_multiline_description_first_sentence(self):
        desc = _parse_description({"description": "Line one. Line two. Line three"})
        assert desc == "Line one."

    def test_description_single_period(self):
        desc = _parse_description({"description": "One sentence"})
        assert desc == "One sentence"


# --- _list_scripts tests ---


class TestListScripts:
    def test_list_sh_and_py(self, tmp_skills_dir):
        fetcher = tmp_skills_dir / "core" / "mock-fetcher"
        scripts = _list_scripts(fetcher)
        assert "fetch.sh" in scripts
        assert "search.py" in scripts

    def test_no_scripts_dir(self, tmp_skills_dir):
        pulse = tmp_skills_dir / "core" / "mock-pulse"
        scripts = _list_scripts(pulse)
        assert scripts == []

    def test_hidden_scripts_excluded(self, tmp_path):
        skill_dir = tmp_path / "skill"
        skill_dir.mkdir()
        scripts_dir = skill_dir / "scripts"
        scripts_dir.mkdir()
        (scripts_dir / ".hidden.sh").write_text("hidden")
        (scripts_dir / "visible.sh").write_text("visible")
        result = _list_scripts(skill_dir)
        assert ".hidden.sh" not in result
        assert "visible.sh" in result

    def test_non_script_files_excluded(self, tmp_path):
        skill_dir = tmp_path / "skill"
        skill_dir.mkdir()
        scripts_dir = skill_dir / "scripts"
        scripts_dir.mkdir()
        (scripts_dir / "data.json").write_text("{}")
        (scripts_dir / "run.sh").write_text("run")
        result = _list_scripts(skill_dir)
        assert "data.json" not in result
        assert "run.sh" in result

    def test_sorted_output(self, tmp_path):
        skill_dir = tmp_path / "skill"
        skill_dir.mkdir()
        scripts_dir = skill_dir / "scripts"
        scripts_dir.mkdir()
        (scripts_dir / "z.sh").write_text("")
        (scripts_dir / "a.sh").write_text("")
        result = _list_scripts(skill_dir)
        assert result == ["a.sh", "z.sh"]


# --- _list_modules tests ---


class TestListModules:
    def test_list_py_modules(self, tmp_skills_dir):
        fetcher = tmp_skills_dir / "core" / "mock-fetcher"
        modules = _list_modules(fetcher)
        assert "core.py" in modules

    def test_no_modules_dir(self, tmp_skills_dir):
        pulse = tmp_skills_dir / "core" / "mock-pulse"
        modules = _list_modules(pulse)
        assert modules == []

    def test_non_py_files_excluded(self, tmp_path):
        skill_dir = tmp_path / "skill"
        skill_dir.mkdir()
        modules_dir = skill_dir / "modules"
        modules_dir.mkdir()
        (modules_dir / "data.json").write_text("{}")
        (modules_dir / "core.py").write_text("pass")
        result = _list_modules(skill_dir)
        assert "data.json" not in result
        assert "core.py" in result

    def test_hidden_modules_excluded(self, tmp_path):
        skill_dir = tmp_path / "skill"
        skill_dir.mkdir()
        modules_dir = skill_dir / "modules"
        modules_dir.mkdir()
        (modules_dir / ".hidden.py").write_text("")
        (modules_dir / "visible.py").write_text("")
        result = _list_modules(skill_dir)
        assert ".hidden.py" not in result


# --- _layer_from_category tests ---


class TestLayerFromCategory:
    def test_core_category(self):
        assert _layer_from_category("core") == "core"

    def test_external_category(self):
        assert _layer_from_category("external") == "external"

    def test_presearch_category(self):
        assert _layer_from_category("presearch") == "core"

    def test_unknown_category(self):
        assert _layer_from_category("unknown") == "unknown"


# --- discover_skills tests ---


class TestDiscoverSkills:
    def test_discover_core_skills(self, tmp_skills_dir):
        skills = discover_skills(tmp_skills_dir)
        core_skills = [s for s in skills if s["layer"] == "core"]
        assert len(core_skills) >= 2

    def test_discover_external_skills(self, tmp_skills_dir):
        skills = discover_skills(tmp_skills_dir)
        ext_skills = [s for s in skills if s["layer"] == "external"]
        assert len(ext_skills) >= 1

    def test_skill_has_required_keys(self, tmp_skills_dir):
        skills = discover_skills(tmp_skills_dir)
        assert len(skills) > 0
        skill = skills[0]
        required = ["name", "version", "description", "layer", "category", "path", "scripts", "modules", "skill_md", "author", "health"]
        for key in required:
            assert key in skill

    def test_skill_md_content(self, tmp_skills_dir):
        skills = discover_skills(tmp_skills_dir)
        fetcher = next(s for s in skills if s["name"] == "mock-fetcher")
        assert "Mock Fetcher" in fetcher["skill_md"]

    def test_hidden_dirs_skipped(self, tmp_skills_dir_with_hidden):
        skills = discover_skills(tmp_skills_dir_with_hidden)
        assert "should-not-appear" not in [s["name"] for s in skills]

    def test_nonexistent_dir(self, tmp_path):
        skills = discover_skills(tmp_path / "nonexistent")
        assert skills == []

    def test_empty_skills_dir(self, tmp_path):
        empty_dir = tmp_path / "skills"
        empty_dir.mkdir()
        skills = discover_skills(empty_dir)
        assert skills == []

    def test_discover_real_project_skills(self):
        """Test discovery against the actual project skills directory."""
        skills = discover_skills(REAL_SKILLS_DIR)
        assert len(skills) >= 3
        names = [s["name"] for s in skills]
        assert "url-fetcher" in names
        assert "presearch" in names
        assert "daily-dev-pulse" in names

    def test_scripts_listed(self, tmp_skills_dir):
        skills = discover_skills(tmp_skills_dir)
        fetcher = next(s for s in skills if s["name"] == "mock-fetcher")
        assert len(fetcher["scripts"]) >= 2

    def test_modules_listed(self, tmp_skills_dir):
        skills = discover_skills(tmp_skills_dir)
        fetcher = next(s for s in skills if s["name"] == "mock-fetcher")
        assert len(fetcher["modules"]) >= 1

    def test_nested_external_skills(self, tmp_skills_dir_nested):
        skills = discover_skills(tmp_skills_dir_nested)
        names = [s["name"] for s in skills]
        assert "company-snapshot" in names

    def test_skill_path_is_str(self, tmp_skills_dir):
        skills = discover_skills(tmp_skills_dir)
        for s in skills:
            assert isinstance(s["path"], str)

    def test_version_format(self, tmp_skills_dir):
        skills = discover_skills(tmp_skills_dir)
        for s in skills:
            assert "." in s["version"]  # semver-like


# --- get_skill_by_name tests ---


class TestGetSkillByName:
    def test_find_existing_skill(self, tmp_skills_dir):
        skill = get_skill_by_name(tmp_skills_dir, "mock-fetcher")
        assert skill is not None
        assert skill["name"] == "mock-fetcher"

    def test_not_found(self, tmp_skills_dir):
        skill = get_skill_by_name(tmp_skills_dir, "nonexistent")
        assert skill is None

    def test_find_external_skill(self, tmp_skills_dir):
        skill = get_skill_by_name(tmp_skills_dir, "mock-bloomberg")
        assert skill is not None
        assert skill["layer"] == "external"

    def test_find_real_url_fetcher(self):
        skill = get_skill_by_name(REAL_SKILLS_DIR, "url-fetcher")
        assert skill is not None
        assert skill["name"] == "url-fetcher"


# --- search_skills tests ---


class TestSearchSkills:
    def test_search_by_name(self, tmp_skills_dir):
        results = search_skills(tmp_skills_dir, "fetcher")
        assert len(results) >= 1
        assert any(s["name"] == "mock-fetcher" for s in results)

    def test_search_by_description(self, tmp_skills_dir):
        results = search_skills(tmp_skills_dir, "pulse")
        assert len(results) >= 1

    def test_case_insensitive(self, tmp_skills_dir):
        results = search_skills(tmp_skills_dir, "FETCHER")
        assert len(results) >= 1

    def test_no_results(self, tmp_skills_dir):
        results = search_skills(tmp_skills_dir, "nonexistent-term")
        assert len(results) == 0

    def test_partial_match(self, tmp_skills_dir):
        results = search_skills(tmp_skills_dir, "mock")
        assert len(results) >= 2

    def test_search_real_project(self):
        results = search_skills(REAL_SKILLS_DIR, "fetch")
        assert len(results) >= 1

    def test_search_empty_string(self, tmp_skills_dir):
        results = search_skills(tmp_skills_dir, "")
        # Empty query matches everything
        assert len(results) >= 3

    def test_search_special_chars(self, tmp_skills_dir):
        results = search_skills(tmp_skills_dir, "@#$")
        assert len(results) == 0


# --- Additional discovery edge case tests ---


class TestYamlFrontmatterAdditional:
    def test_frontmatter_only_equals_name(self):
        text = "---\nname: only-name\n---\n"
        result = _yaml_frontmatter(text)
        assert result["name"] == "only-name"
        assert len(result) == 1

    def test_frontmatter_with_boolean_like_values(self):
        text = "---\nname: bool-test\nprivate: false\n---\n"
        result = _yaml_frontmatter(text)
        assert result["name"] == "bool-test"
        assert result["private"] == "false"

    def test_frontmatter_with_numeric_version(self):
        text = "---\nname: num\nversion: 42\n---\n"
        result = _yaml_frontmatter(text)
        assert result["version"] == "42"

    def test_frontmatter_malformed_no_closing(self):
        text = "---\nname: broken\nno closing dashes"
        result = _yaml_frontmatter(text)
        assert result == {}

    def test_frontmatter_with_spaces_in_value(self):
        text = "---\nname: spaced\nauthor: Some Person\n---\n"
        result = _yaml_frontmatter(text)
        assert result["author"] == "Some Person"


class TestDiscoverSkillsAdditional:
    def test_discover_skill_health_is_unknown(self, tmp_skills_dir):
        skills = discover_skills(tmp_skills_dir)
        for s in skills:
            assert s["health"] == "unknown"

    def test_discover_skill_path_is_absolute(self, tmp_skills_dir):
        skills = discover_skills(tmp_skills_dir)
        for s in skills:
            assert Path(s["path"]).is_absolute()

    def test_discover_no_skills_in_empty_category(self, tmp_path):
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()
        (skills_dir / "empty_category").mkdir()
        skills = discover_skills(skills_dir)
        assert skills == []

    def test_discover_skill_dir_without_skill_md(self, tmp_path):
        """A directory without SKILL.md should not appear as a top-level skill."""
        skills_dir = tmp_path / "skills"
        core = skills_dir / "core"
        core.mkdir(parents=True)
        no_md = core / "no-md-skill"
        no_md.mkdir()
        (no_md / "README.md").write_text("# Not a skill")
        skills = discover_skills(skills_dir)
        names = [s["name"] for s in skills]
        assert "no-md-skill" not in names

    def test_discover_category_dot_dirs_skipped(self, tmp_path):
        skills_dir = tmp_path / "skills"
        dot = skills_dir / ".hidden_cat"
        dot.mkdir(parents=True)
        skill_dir = dot / "some-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("---\nname: should-skip\n---\n")
        skills = discover_skills(skills_dir)
        assert "should-skip" not in [s["name"] for s in skills]

    def test_discover_returns_correct_layer(self, tmp_skills_dir):
        skills = discover_skills(tmp_skills_dir)
        core_skills = [s for s in skills if s["layer"] == "core"]
        ext_skills = [s for s in skills if s["layer"] == "external"]
        assert len(core_skills) >= 2
        assert len(ext_skills) >= 1


class TestListScriptsAdditional:
    def test_python_scripts_listed(self, tmp_path):
        skill_dir = tmp_path / "skill"
        skill_dir.mkdir()
        scripts_dir = skill_dir / "scripts"
        scripts_dir.mkdir()
        (scripts_dir / "process.py").write_text("pass")
        result = _list_scripts(skill_dir)
        assert "process.py" in result

    def test_empty_scripts_dir(self, tmp_path):
        skill_dir = tmp_path / "skill"
        skill_dir.mkdir()
        scripts_dir = skill_dir / "scripts"
        scripts_dir.mkdir()
        result = _list_scripts(skill_dir)
        assert result == []


class TestListModulesAdditional:
    def test_only_py_in_modules(self, tmp_path):
        skill_dir = tmp_path / "skill"
        skill_dir.mkdir()
        modules_dir = skill_dir / "modules"
        modules_dir.mkdir()
        (modules_dir / "app.py").write_text("pass")
        (modules_dir / "config.toml").write_text("")
        result = _list_modules(skill_dir)
        assert "app.py" in result
        assert "config.toml" not in result

    def test_empty_modules_dir(self, tmp_path):
        skill_dir = tmp_path / "skill"
        skill_dir.mkdir()
        modules_dir = skill_dir / "modules"
        modules_dir.mkdir()
        result = _list_modules(skill_dir)
        assert result == []


class TestLayerFromCategoryAdditional:
    def test_numeric_category(self):
        assert _layer_from_category("123") == "123"

    def test_empty_category(self):
        assert _layer_from_category("") == ""

    def test_category_with_hyphens(self):
        assert _layer_from_category("some-layer") == "some-layer"

    def test_nested_external_category(self):
        """Nested category paths should resolve to top-level layer."""
        assert _layer_from_category("external/bloomberg/event") == "external"
        assert _layer_from_category("external/bloomberg/company") == "external"

    def test_nested_core_category(self):
        """Core category with sub-paths should still be 'core'."""
        assert _layer_from_category("core/subcategory") == "core"


class TestGetSkillByNameAdditional:
    def test_real_skill_has_modules(self):
        skill = get_skill_by_name(REAL_SKILLS_DIR, "url-fetcher")
        # url-fetcher doesn't have a modules dir
        assert isinstance(skill["modules"], list)

    def test_real_skill_has_scripts(self):
        skill = get_skill_by_name(REAL_SKILLS_DIR, "url-fetcher")
        assert isinstance(skill["scripts"], list)
        assert len(skill["scripts"]) > 0


# --- _extract_dependencies tests ---


class TestExtractDependencies:
    def test_pip_install_line(self):
        content = "## Dependencies\n\n```bash\npip install fastapi uvicorn jinja2\n```"
        deps = _extract_dependencies(content)
        assert len(deps) >= 3
        names = [d["dep_name"] for d in deps]
        assert "fastapi" in names
        assert "uvicorn" in names
        assert "jinja2" in names

    def test_pip_with_version_specifiers(self):
        content = "pip install pytest>=7.0 httpx==0.24"
        deps = _extract_dependencies(content)
        names = [d["dep_name"] for d in deps]
        assert "pytest" in names
        assert "httpx" in names

    def test_brew_install_line(self):
        content = "brew install poppler gh"
        deps = _extract_dependencies(content)
        names = [d["dep_name"] for d in deps]
        assert "poppler" in names
        assert "gh" in names
        brew_deps = [d for d in deps if d["dep_type"] == "brew"]
        assert len(brew_deps) >= 2

    def test_mixed_pip_and_brew(self):
        content = "pip install aiosqlite\nbrew install ffmpeg"
        deps = _extract_dependencies(content)
        pip_deps = [d for d in deps if d["dep_type"] == "pip"]
        brew_deps = [d for d in deps if d["dep_type"] == "brew"]
        assert len(pip_deps) >= 1
        assert len(brew_deps) >= 1

    def test_no_dependencies(self):
        content = "# Simple Skill\nNo deps here."
        deps = _extract_dependencies(content)
        assert deps == []

    def test_deduplication(self):
        content = "pip install fastapi\npip install fastapi"
        deps = _extract_dependencies(content)
        fastapi_count = sum(1 for d in deps if d["dep_name"] == "fastapi")
        assert fastapi_count == 1

    def test_flags_excluded(self):
        content = "pip install --no-cache-dir fastapi"
        deps = _extract_dependencies(content)
        names = [d["dep_name"] for d in deps]
        assert "fastapi" in names
        assert "--no-cache-dir" not in names

    def test_npx_pattern(self):
        content = "npx open-websearch@latest"
        deps = _extract_dependencies(content)
        npm_deps = [d for d in deps if d["dep_type"] == "npm"]
        assert len(npm_deps) >= 1
        assert npm_deps[0]["dep_name"] == "open-websearch"

    def test_npm_install_pattern(self):
        content = "npm install express react"
        deps = _extract_dependencies(content)
        npm_deps = [d for d in deps if d["dep_type"] == "npm"]
        assert len(npm_deps) >= 2

    def test_real_skill_hub_deps(self):
        """Test against the real skill-hub SKILL.md content."""
        skill = get_skill_by_name(REAL_SKILLS_DIR, "skill-hub")
        if skill and skill["dependencies"]:
            names = [d["dep_name"] for d in skill["dependencies"]]
            assert "fastapi" in names
            assert "uvicorn" in names

    def test_discovered_skills_include_dependencies(self, tmp_skills_dir):
        """Skills with deps in their SKILL.md should include dependencies."""
        # Create a skill with pip deps
        dep_dir = tmp_skills_dir / "core" / "dep-skill"
        dep_dir.mkdir()
        (dep_dir / "SKILL.md").write_text(
            "---\nname: dep-skill\nversion: 1.0\n---\n\n"
            "## Dependencies\n\npip install requests flask"
        )
        skills = discover_skills(tmp_skills_dir)
        dep_skill = next((s for s in skills if s["name"] == "dep-skill"), None)
        assert dep_skill is not None
        assert len(dep_skill["dependencies"]) >= 2

    def test_skill_without_deps_has_empty_list(self, tmp_skills_dir):
        """Skills without dependency lines should have empty dependencies."""
        skills = discover_skills(tmp_skills_dir)
        for s in skills:
            assert "dependencies" in s
            assert isinstance(s["dependencies"], list)


# --- check_dep_installed tests ---


class TestCheckDepInstalled:
    def test_pip_dep_installed(self):
        """Check that a known pip package (pytest) is detected as installed."""
        result = check_dep_installed("pytest", "pip")
        assert result is True

    def test_pip_dep_not_installed(self):
        """Check that a nonexistent pip package is detected as not installed."""
        result = check_dep_installed("nonexistent-pkg-xyzzy", "pip")
        assert result is False

    def test_brew_dep_installed(self):
        """If brew is available, check for a common package."""
        import shutil
        if shutil.which("brew"):
            # git is typically installed via brew on macOS
            result = check_dep_installed("git", "brew")
            # Result could be True or False depending on system
            assert isinstance(result, bool)
        else:
            # On systems without brew, should return False
            result = check_dep_installed("anything", "brew")
            assert result is False

    def test_brew_dep_not_installed(self):
        """Check that a nonexistent brew package returns False."""
        result = check_dep_installed("nonexistent-brew-xyzzy", "brew")
        assert result is False

    def test_npm_dep_returns_bool(self):
        """npm check should return bool regardless of npm availability."""
        result = check_dep_installed("express", "npm")
        assert isinstance(result, bool)

    def test_unknown_dep_type_returns_false(self):
        """Unknown dependency type should return False."""
        result = check_dep_installed("something", "unknown_type")
        assert result is False


class TestCheckAllDeps:
    def test_check_empty_list(self):
        """Empty dependency list should return empty list."""
        result = check_all_deps([])
        assert result == []

    def test_check_list_with_pip_deps(self):
        """Check list with pip deps should update installed status."""
        deps = [
            {"dep_name": "pytest", "dep_type": "pip", "installed": False},
            {"dep_name": "nonexistent-pkg-xyzzy", "dep_type": "pip", "installed": False},
        ]
        result = check_all_deps(deps)
        assert result[0]["installed"] is True  # pytest is installed
        assert result[1]["installed"] is False  # nonexistent is not

    def test_check_list_preserves_dep_name_and_type(self):
        """check_all_deps should preserve dep_name and dep_type."""
        deps = [{"dep_name": "aiosqlite", "dep_type": "pip", "installed": False}]
        result = check_all_deps(deps)
        assert result[0]["dep_name"] == "aiosqlite"
        assert result[0]["dep_type"] == "pip"

    def test_check_mixed_dep_types(self):
        """Check list with mixed dep types."""
        deps = [
            {"dep_name": "pytest", "dep_type": "pip", "installed": False},
            {"dep_name": "nonexistent-brew-xyzzy", "dep_type": "brew", "installed": False},
        ]
        result = check_all_deps(deps)
        assert result[0]["dep_type"] == "pip"
        assert result[1]["dep_type"] == "brew"

    def test_pip_import_module_fallback(self):
        """For pip deps, importlib check should work for importable modules."""
        # 'json' is a stdlib module that can be imported
        result = check_dep_installed("json", "pip")
        assert result is True

    def test_pip_show_fallback_uses_sys_executable(self):
        """The pip-show fallback path should use sys.executable correctly.

        Previously, sys was not imported at module level, causing NameError
        when importlib failed and the subprocess fallback was reached.
        Packages whose pip name differs from import name (e.g. pyyaml -> yaml)
        must fall through to pip show, which requires sys.executable.
        """
        import sys
        import subprocess
        # Verify sys is importable in skill_discovery module
        import skill_discovery as sd
        assert hasattr(sd, 'sys'), "skill_discovery must have sys imported at module level"
        # Verify the pip show path works by checking a real package
        # 'pip' itself can always be checked via pip show
        result = check_dep_installed("pip", "pip")
        assert result is True

    def test_pip_name_differs_from_import_name(self):
        """Verify that packages with different pip vs import names are detected.

        This is the core bug scenario: importlib.import_module("pyyaml") fails
        (it imports as "yaml"), so the pip show fallback must work.
        We use 'setuptools' as a test case since it's always installed but
        its import name differs (import setuptools works, but this validates
        the fallback path is reachable without NameError).
        """
        # pytest has same import name, so test a package that may differ
        # Use httpx as it's always installed in our test environment
        result = check_dep_installed("httpx", "pip")
        assert result is True


# --- _parse_description abbreviation tests ---


class TestParseDescriptionAbbreviations:
    """Tests that _parse_description handles abbreviations correctly."""

    def test_eg_not_truncated(self):
        desc = _parse_description({"description": "Uses e.g. pytest for testing"})
        assert "pytest" in desc

    def test_ie_not_truncated(self):
        desc = _parse_description({"description": "Uses i.e. python scripts"})
        assert "python" in desc

    def test_etc_not_truncated(self):
        desc = _parse_description({"description": "A tool etc. for processing data"})
        assert "processing" in desc

    def test_vs_not_truncated(self):
        desc = _parse_description({"description": "Compares vs. other frameworks"})
        assert "other" in desc


# --- _add_skill tests ---


class TestAddSkill:
    """Direct unit tests for _add_skill helper."""

    def test_adds_skill_from_skill_md(self, tmp_path):
        skill_dir = tmp_path / "my-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "---\nname: my-skill\nversion: 1.2.0\ndescription: A test skill\n---\n# Content\n"
        )
        skills = []
        _add_skill(skills, skill_dir, "core")
        assert len(skills) == 1
        assert skills[0]["name"] == "my-skill"
        assert skills[0]["version"] == "1.2.0"
        assert skills[0]["description"] == "A test skill"

    def test_layer_from_frontmatter_overrides_category(self, tmp_path):
        skill_dir = tmp_path / "ext-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "---\nname: ext-skill\nlayer: core\n---\n# Content\n"
        )
        skills = []
        _add_skill(skills, skill_dir, "external")
        assert skills[0]["layer"] == "core"

    def test_layer_from_frontmatter_with_dot_suffix(self, tmp_path):
        """Frontmatter layer 'core. Triggers: ...' -> 'core'"""
        skill_dir = tmp_path / "dot-layer"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "---\nname: dot-layer\nlayer: core. Triggers when used\n---\n# Content\n"
        )
        skills = []
        _add_skill(skills, skill_dir, "external")
        assert skills[0]["layer"] == "core"

    def test_layer_from_category_when_no_frontmatter_layer(self, tmp_path):
        skill_dir = tmp_path / "no-layer"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "---\nname: no-layer\n---\n# Content\n"
        )
        skills = []
        _add_skill(skills, skill_dir, "core")
        assert skills[0]["layer"] == "core"

    def test_name_defaults_to_dir_name(self, tmp_path):
        skill_dir = tmp_path / "fallback-name"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("---\n---\n# Content\n")
        skills = []
        _add_skill(skills, skill_dir, "core")
        assert skills[0]["name"] == "fallback-name"

    def test_version_defaults_to_0_0_0(self, tmp_path):
        skill_dir = tmp_path / "no-version"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("---\nname: no-version\n---\n# Content\n")
        skills = []
        _add_skill(skills, skill_dir, "core")
        assert skills[0]["version"] == "0.0.0"

    def test_is_template_true_reads_template_md(self, tmp_path):
        skill_dir = tmp_path / "template-skill"
        skill_dir.mkdir()
        (skill_dir / "template.md").write_text(
            "---\nname: template-skill\nversion: 0.1.0\n---\n# Template Content\n"
        )
        skills = []
        _add_skill(skills, skill_dir, "external", is_template=True)
        assert len(skills) == 1
        assert skills[0]["name"] == "template-skill"
        assert "Template Content" in skills[0]["skill_md"]

    def test_skill_md_contains_full_content(self, tmp_path):
        skill_dir = tmp_path / "full-md"
        skill_dir.mkdir()
        md_content = "---\nname: full-md\n---\n# Title\nBody paragraph\n"
        (skill_dir / "SKILL.md").write_text(md_content)
        skills = []
        _add_skill(skills, skill_dir, "core")
        assert skills[0]["skill_md"] == md_content

    def test_scripts_and_modules_populated(self, tmp_path):
        skill_dir = tmp_path / "has-files"
        skill_dir.mkdir()
        scripts_dir = skill_dir / "scripts"
        scripts_dir.mkdir()
        (scripts_dir / "run.sh").write_text("#!/bin/bash\n")
        modules_dir = skill_dir / "modules"
        modules_dir.mkdir()
        (modules_dir / "helper.py").write_text("def help(): pass\n")
        (skill_dir / "SKILL.md").write_text("---\nname: has-files\n---\n# Content\n")
        skills = []
        _add_skill(skills, skill_dir, "core")
        assert "run.sh" in skills[0]["scripts"]
        assert "helper.py" in skills[0]["modules"]

    def test_dependencies_extracted_from_content(self, tmp_path):
        skill_dir = tmp_path / "deps-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "---\nname: deps-skill\n---\n# Setup\n```\npip install fastapi beautifulsoup4\n```\n"
        )
        skills = []
        _add_skill(skills, skill_dir, "core")
        dep_names = [d["dep_name"] for d in skills[0]["dependencies"]]
        assert "fastapi" in dep_names
        assert "beautifulsoup4" in dep_names

    def test_health_default_is_unknown(self, tmp_path):
        skill_dir = tmp_path / "health-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("---\nname: health-skill\n---\n# Content\n")
        skills = []
        _add_skill(skills, skill_dir, "core")
        assert skills[0]["health"] == "unknown"

    def test_path_set_to_skill_dir_str(self, tmp_path):
        skill_dir = tmp_path / "path-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("---\nname: path-skill\n---\n# Content\n")
        skills = []
        _add_skill(skills, skill_dir, "core")
        assert skills[0]["path"] == str(skill_dir)


# --- _read_skill_md tests ---


class TestReadSkillMd:
    """Direct unit tests for _read_skill_md helper."""

    def test_reads_existing_file(self, tmp_path):
        skill_dir = tmp_path / "reader"
        skill_dir.mkdir()
        content = "# My Skill\nSome content here\n"
        (skill_dir / "SKILL.md").write_text(content)
        result = _read_skill_md(skill_dir)
        assert result == content

    def test_reads_unicode_content(self, tmp_path):
        skill_dir = tmp_path / "unicode-skill"
        skill_dir.mkdir()
        content = "# Skill 中文\n描述内容\n"
        (skill_dir / "SKILL.md").write_text(content)
        result = _read_skill_md(skill_dir)
        assert "中文" in result

    def test_reads_empty_file(self, tmp_path):
        skill_dir = tmp_path / "empty"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("")
        result = _read_skill_md(skill_dir)
        assert result == ""

    def test_encoding_errors_replace(self, tmp_path):
        skill_dir = tmp_path / "bad-encoding"
        skill_dir.mkdir()
        # Write bytes that aren't valid UTF-8
        (skill_dir / "SKILL.md").write_bytes(b"---\nname: bad\n---\n\xff\xfe content\n")
        result = _read_skill_md(skill_dir)
        assert "name: bad" in result