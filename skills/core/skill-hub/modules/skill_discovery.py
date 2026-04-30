"""Auto-discover skills by scanning SKILL.md files in core/ and external/ directories."""

import importlib
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional


def _yaml_frontmatter(text: str) -> dict:
    """Parse YAML frontmatter from SKILL.md content."""
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not match:
        return {}
    raw = match.group(1)
    result: dict = {}
    current_key: Optional[str] = None
    current_val: str = ""
    in_multiline = False

    for line in raw.split("\n"):
        stripped = line.rstrip()
        if in_multiline:
            if stripped and not stripped[0].isspace() and ":" in stripped:
                result[current_key] = current_val.strip()
                current_key = None
                current_val = ""
                in_multiline = False
            else:
                current_val += " " + stripped.strip()
                continue

        key_match = re.match(r"^(\w+):\s*(.*)", stripped)
        if key_match:
            key = key_match.group(1)
            val = key_match.group(2).strip()
            current_key = key
            if val == "|" or val == "":
                in_multiline = True
                current_val = ""
            else:
                result[key] = val
                current_key = None

    if current_key:
        result[current_key] = current_val.strip()

    return result


def _parse_description(fm: dict) -> str:
    """Extract a clean description string from frontmatter."""
    desc = fm.get("description", "")
    if not desc:
        return ""
    # Take first meaningful sentence (up to first period followed by space or end)
    # Avoids truncating on abbreviations like "e.g.", "i.e.", "etc."
    abbrevs = {"e.g.", "i.e.", "etc.", "vs.", "cf.", "approx.", "viz.", "ca.", "al.", "a.s."}
    text = desc.strip()
    # Walk through the text, looking for period+space boundaries that aren't abbreviations
    for i in range(len(text)):
        if text[i] in '.!?':
            # Extract the word preceding this punctuation
            preceding_word_start = i
            while preceding_word_start > 0 and text[preceding_word_start - 1] not in ' \t\n':
                preceding_word_start -= 1
            preceding_word = text[preceding_word_start:i + 1].lower()
            # If preceding word is an abbreviation, skip this punctuation as a sentence end
            if preceding_word in abbrevs:
                continue
            # Check if this is followed by a space/end (sentence boundary)
            next_char = text[i + 1] if i + 1 < len(text) else ''
            if next_char in (' ', '\t', '\n', '') or i == len(text) - 1:
                return text[:i + 1].strip()
    # No sentence-ending punctuation found — return first line
    return text.split('\n')[0].strip()


def _list_scripts(skill_dir: Path) -> list[str]:
    """List script filenames in the skill's scripts/ directory."""
    scripts_dir = skill_dir / "scripts"
    if not scripts_dir.is_dir():
        return []
    return sorted(
        f.name for f in scripts_dir.iterdir()
        if f.is_file() and not f.name.startswith(".") and f.suffix in {".sh", ".py"}
    )


def _list_modules(skill_dir: Path) -> list[str]:
    """List module filenames in the skill's modules/ directory."""
    modules_dir = skill_dir / "modules"
    if not modules_dir.is_dir():
        return []
    return sorted(
        f.name for f in modules_dir.iterdir()
        if f.is_file() and not f.name.startswith(".") and f.suffix == ".py"
    )


def _read_skill_md(skill_dir: Path) -> str:
    """Read full SKILL.md content."""
    md_path = skill_dir / "SKILL.md"
    if md_path.is_file():
        return md_path.read_text(encoding="utf-8", errors="replace")
    return ""


def _layer_from_category(category: str) -> str:
    """Map directory category to skill layer."""
    # For nested categories like "external/bloomberg/company", just use the top-level
    mapping = {"core": "core", "external": "external", "presearch": "core"}
    top = category.split("/")[0]
    return mapping.get(top, top)


def _scan_for_skills(dir_path: Path, skills: list[dict], category_prefix: str) -> None:
    """Recursively scan a directory for SKILL.md or template.md files."""
    # If this directory itself contains SKILL.md or template.md, register it as a skill
    if (dir_path / "SKILL.md").is_file():
        _add_skill(skills, dir_path, category_prefix)
        return
    if (dir_path / "template.md").is_file():
        _add_skill(skills, dir_path, category_prefix, is_template=True)
        return

    # Otherwise recurse into subdirectories
    for sub in sorted(dir_path.iterdir()):
        if not sub.is_dir() or sub.name.startswith("."):
            continue
        # Skip directories that are clearly not skill dirs (scripts, modules, tests, references, templates)
        if sub.name in {"scripts", "modules", "tests", "references", "templates", "__pycache__"}:
            continue
        extended_category = f"{category_prefix}/{sub.name}" if category_prefix else sub.name
        _scan_for_skills(sub, skills, extended_category)


def discover_skills(skills_dir: Path) -> list[dict]:
    """Scan skills directory and commands/ for SKILL.md, template.md, and command .md files.

    Recursively walks core/ and external/ directories, finding skills at
    any nesting depth. Also scans commands/ and .claude/commands/ for
    slash command definitions. Returns list of skill dicts with keys:
    name, version, description, layer, category, path, scripts, modules,
    skill_md, author, health
    """
    if not skills_dir.is_dir():
        return []

    skills: list[dict] = []
    for category_dir in sorted(skills_dir.iterdir()):
        if not category_dir.is_dir() or category_dir.name.startswith("."):
            continue
        _scan_for_skills(category_dir, skills, category_dir.name)

    # Also scan commands/ and .claude/commands/ for slash command definitions
    project_root = skills_dir.parent
    _scan_commands_dir(project_root / "commands", skills)
    _scan_commands_dir(project_root / ".claude" / "commands", skills)

    return skills


def _scan_commands_dir(commands_dir: Path, skills: list[dict]) -> None:
    """Scan a commands/ directory for slash command .md files."""
    if not commands_dir.is_dir():
        return
    for f in sorted(commands_dir.iterdir()):
        if not f.is_file() or not f.name.endswith(".md") or f.name.startswith("."):
            continue
        content = f.read_text(encoding="utf-8", errors="replace")
        fm = _yaml_frontmatter(content)
        if not fm:
            continue
        name = fm.get("name", f.stem)
        # Avoid duplicating skills already discovered from skills/ dir
        # Commands like presearch, url-fetcher, daily-dev-pulse have corresponding skill dirs
        existing_names = {s["name"] for s in skills}
        if name in existing_names:
            continue
        skills.append({
            "name": name,
            "version": fm.get("version", "0.0.0"),
            "description": fm.get("description", ""),
            "layer": "command",
            "category": "commands",
            "path": str(f.parent),
            "scripts": [],
            "modules": [],
            "skill_md": content,
            "author": fm.get("author", ""),
            "health": "unknown",
            "dependencies": [],
        })


def _extract_dependencies(skill_md_content: str) -> list[dict]:
    """Extract dependency names/types from SKILL.md content.

    Looks for 'pip install ...' and 'brew install ...' patterns in
    ## Dependencies sections or anywhere in the document.
    """
    deps: list[dict] = []
    # pip install patterns
    for match in re.finditer(r"pip install\s+([^\n&]+)", skill_md_content):
        packages = match.group(1).strip().split()
        for pkg in packages:
            if pkg.startswith("-"):
                continue
            # Strip version specifiers like >=1.0, ==2.0, >0.5
            name = re.split(r"[><=!]", pkg)[0].strip()
            if name:
                deps.append({"dep_name": name, "dep_type": "pip"})
    # brew install patterns
    for match in re.finditer(r"brew install\s+([^\n&]+)", skill_md_content):
        packages = match.group(1).strip().split()
        for pkg in packages:
            if pkg.startswith("-"):
                continue
            name = re.split(r"[><=!]", pkg)[0].strip()
            if name:
                deps.append({"dep_name": name, "dep_type": "brew"})
    # npm install patterns
    for match in re.finditer(r"npm\s+install\s+([^\n&]+)", skill_md_content):
        packages = match.group(1).strip().split()
        for pkg in packages:
            if pkg.startswith("-"):
                continue
            name = re.split(r"[><=!@]", pkg)[0].strip()
            if name and name != "install":
                deps.append({"dep_name": name, "dep_type": "npm"})
    # npx patterns (npx runs packages directly, no "install" keyword)
    for match in re.finditer(r"npx\s+([^\n&\s]+)", skill_md_content):
        pkg = match.group(1).strip()
        name = re.split(r"[><=!@]", pkg)[0].strip()
        if name:
            deps.append({"dep_name": name, "dep_type": "npm"})
    # Deduplicate by (dep_name, dep_type)
    seen = set()
    unique = []
    for d in deps:
        key = (d["dep_name"], d["dep_type"])
        if key not in seen:
            seen.add(key)
            unique.append(d)
    return unique


def _extract_goal_line(content: str) -> str:
    """Extract description from a template.md — tries GOAL line first, then Metadata table Output field, then first heading."""
    # Try GOAL line (most templates use this)
    for match in re.finditer(r"^GOAL\s*\n(.+)", content, re.MULTILINE):
        line = match.group(1).strip()
        line = re.sub(r"\{[^}]+\}", "", line).strip()
        line = re.sub(r"\s{2,}", " ", line).strip()
        if line:
            return line

    # Try Metadata table Output field
    for match in re.finditer(r"\|\s*Output\s*\|\s*(.+?)\s*\|", content):
        line = match.group(1).strip()
        line = re.sub(r"\{[^}]+\}", "", line).strip()
        if line:
            return line

    # Try first Markdown heading
    for match in re.finditer(r"^#\s+(.+)", content, re.MULTILINE):
        line = match.group(1).strip()
        line = re.sub(r"\{[^}]+\}", "", line).strip()
        if line and line.lower() not in {"metadata", "prompt template"}:
            return line

    return ""


def _add_skill(
    skills: list[dict],
    skill_dir: Path,
    category: str,
    is_template: bool = False,
) -> None:
    """Parse a single skill and add it to the list."""
    md_name = "template.md" if is_template else "SKILL.md"
    content = (skill_dir / md_name).read_text(encoding="utf-8", errors="replace")
    fm = _yaml_frontmatter(content)
    name = fm.get("name", skill_dir.name)
    # Handle layer from frontmatter or category
    fm_layer = fm.get("layer", "")
    if fm_layer:
        layer = fm_layer.split(".")[0].strip()  # e.g. "core. Triggers: ..." -> "core"
    else:
        layer = _layer_from_category(category)

    description = _parse_description(fm)
    if not description and is_template:
        description = _extract_goal_line(content)

    skills.append({
        "name": name,
        "version": fm.get("version", "0.0.0"),
        "description": description,
        "layer": layer,
        "category": category,
        "path": str(skill_dir),
        "scripts": _list_scripts(skill_dir),
        "modules": _list_modules(skill_dir),
        "skill_md": content,
        "author": fm.get("author", ""),
        "health": "unknown",
        "dependencies": _extract_dependencies(content),
    })


def get_skill_by_name(skills_dir: Path, name: str) -> Optional[dict]:
    """Find a specific skill by name."""
    skills = discover_skills(skills_dir)
    for skill in skills:
        if skill["name"] == name:
            return skill
    return None


def search_skills(skills_dir: Path, query: str) -> list[dict]:
    """Search skills by name or description (case-insensitive substring match)."""
    skills = discover_skills(skills_dir)
    q = query.lower()
    return [
        s for s in skills
        if q in s["name"].lower() or q in s["description"].lower()
    ]


def check_dep_installed(dep_name: str, dep_type: str) -> bool:
    """Check whether a dependency is actually installed on the system."""
    if dep_type == "pip":
        try:
            importlib.import_module(dep_name.replace("-", "_"))
            return True
        except ImportError:
            pass
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "show", dep_name],
                capture_output=True, timeout=10,
            )
            return result.returncode == 0
        except Exception:
            return False
    elif dep_type == "brew":
        try:
            result = subprocess.run(
                ["brew", "--prefix", dep_name],
                capture_output=True, timeout=10,
            )
            return result.returncode == 0
        except Exception:
            return False
    elif dep_type == "npm":
        try:
            result = subprocess.run(
                ["npm", "list", "-g", dep_name],
                capture_output=True, timeout=10,
            )
            return result.returncode == 0
        except Exception:
            return False
    return False


def check_all_deps(deps: list[dict]) -> list[dict]:
    """Check installation status for all dependencies, returning updated list."""
    for d in deps:
        d["installed"] = check_dep_installed(d["dep_name"], d["dep_type"])
    return deps