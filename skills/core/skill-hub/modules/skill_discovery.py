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
    # Remove trigger phrases and extra whitespace
    lines = desc.split(".")
    cleaned = lines[0].strip().rstrip(".")
    return cleaned if cleaned else desc.strip().split("\n")[0].strip()


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


def discover_skills(skills_dir: Path) -> list[dict]:
    """Scan skills/core/*/SKILL.md and skills/external/*/SKILL.md.

    Returns list of skill dicts with keys:
    name, version, description, layer, category, path, scripts, modules,
    skill_md, author, health
    """
    if not skills_dir.is_dir():
        return []

    skills: list[dict] = []
    for category_dir in sorted(skills_dir.iterdir()):
        if not category_dir.is_dir() or category_dir.name.startswith("."):
            continue
        category = category_dir.name
        for skill_dir in sorted(category_dir.iterdir()):
            if not skill_dir.is_dir() or skill_dir.name.startswith("."):
                continue
            skill_md_path = skill_dir / "SKILL.md"
            # For nested external skills (e.g. bloomberg/company/company-snapshot),
            # also scan subdirectories for SKILL.md
            if skill_md_path.is_file():
                _add_skill(skills, skill_dir, category)
            else:
                # Scan one level deeper for nested skills
                for sub_dir in sorted(skill_dir.iterdir()):
                    if not sub_dir.is_dir():
                        continue
                    for nested_dir in sorted(sub_dir.iterdir()):
                        if not nested_dir.is_dir():
                            continue
                        if (nested_dir / "SKILL.md").is_file():
                            _add_skill(skills, nested_dir, f"{category}/{skill_dir.name}/{sub_dir.name}")
                        elif (nested_dir / "template.md").is_file():
                            # External skills may use template.md instead
                            _add_skill(skills, nested_dir, f"{category}/{skill_dir.name}/{sub_dir.name}", is_template=True)

    return skills


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

    skills.append({
        "name": name,
        "version": fm.get("version", "0.0.0"),
        "description": _parse_description(fm),
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