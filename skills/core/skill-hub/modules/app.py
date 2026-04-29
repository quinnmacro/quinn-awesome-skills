"""Skill Hub FastAPI application with Jinja2 templates and REST API."""

import asyncio
import json
import os
import re
import subprocess
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

# Ensure modules directory is on sys.path for imports
MODULES_DIR = str(Path(__file__).resolve().parent)
if MODULES_DIR not in sys.path:
    sys.path.insert(0, MODULES_DIR)

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from fastapi.exceptions import RequestValidationError

from skill_discovery import discover_skills, get_skill_by_name, search_skills, check_dep_installed, check_all_deps, _yaml_frontmatter
from database import (
    DEFAULT_DB_PATH,
    init_db,
    upsert_skill,
    get_all_skills,
    get_skill,
    search_skills_db,
    record_test_run,
    get_test_runs,
    get_health_stats,
    sync_skills,
    sync_dependencies,
    upsert_dependency,
    get_dependencies,
    record_version,
    get_versions,
)

# Resolve paths: app.py is in skill-hub/modules/
SKILL_HUB_DIR = Path(__file__).resolve().parent.parent  # skills/core/skill-hub/
PROJECT_ROOT = SKILL_HUB_DIR.parent.parent.parent  # quinn-awesome-skills/
DEFAULT_SKILLS_DIR = PROJECT_ROOT / "skills"
DEFAULT_PORT = int(os.environ.get("SKILL_HUB_PORT", "8765"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize DB and sync discovered skills
    global _db
    db_path = os.environ.get("SKILL_HUB_DB", DEFAULT_DB_PATH)
    _db = await init_db(db_path)
    skills_dir = Path(os.environ.get("SKILL_HUB_SKILLS_DIR", str(DEFAULT_SKILLS_DIR)))
    discovered = discover_skills(skills_dir)
    await sync_skills(_db, discovered)
    await sync_dependencies(_db, discovered)
    yield
    # Shutdown: close DB connection
    if _db is not None:
        await _db.close()
        _db = None


app = FastAPI(title="Skill Hub", version="1.0.0", lifespan=lifespan)

# Global db connection
_db = None


async def _render_error_page(status_code: int, message: str, skill_name: str = "") -> str:
    """Render a styled error page using the error template."""
    return _render_template("error.html", {
        "status_code": status_code,
        "message": message,
        "skill_name": skill_name,
        "nav_active": "",
    })


@app.exception_handler(404)
async def custom_404_handler(request: Request, exc):
    """Handle 404 errors with a styled error page."""
    # Check if this is an API request (path starts with /api/)
    if request.url.path.startswith("/api/"):
        return JSONResponse({"error": "Not found", "path": str(request.url.path)}, status_code=404)
    html = await _render_error_page(404, "Page not found")
    return HTMLResponse(html, status_code=404)


@app.exception_handler(500)
async def custom_500_handler(request: Request, exc):
    """Handle 500 errors with a styled error page."""
    if request.url.path.startswith("/api/"):
        return JSONResponse({"error": "Internal server error"}, status_code=500)
    html = await _render_error_page(500, "Internal server error")
    return HTMLResponse(html, status_code=500)


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors."""
    if request.url.path.startswith("/api/"):
        return JSONResponse({"error": "Validation error", "details": str(exc)}, status_code=422)
    html = await _render_error_page(422, "Invalid request parameters")
    return HTMLResponse(html, status_code=422)


async def get_db():
    global _db
    if _db is None:
        db_path = os.environ.get("SKILL_HUB_DB", DEFAULT_DB_PATH)
        _db = await init_db(db_path)
        skills_dir = Path(os.environ.get("SKILL_HUB_SKILLS_DIR", str(DEFAULT_SKILLS_DIR)))
        discovered = discover_skills(skills_dir)
        await sync_skills(_db, discovered)
    return _db


# --- Jinja2 Environment (initialized once) ---
from jinja2 import Environment, FileSystemLoader

_jinja_env = Environment(
    loader=FileSystemLoader(str(SKILL_HUB_DIR / "templates")),
    autoescape=True,
)

def _render_template(template_name: str, context: dict) -> str:
    """Render a Jinja2 template from the templates/ directory."""
    template = _jinja_env.get_template(template_name)
    return template.render(**context)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request, q: Optional[str] = None, layer: Optional[str] = None, health: Optional[str] = None, sort: Optional[str] = None):
    db = await get_db()
    skills_dir = Path(os.environ.get("SKILL_HUB_SKILLS_DIR", str(DEFAULT_SKILLS_DIR)))
    discovered = discover_skills(skills_dir)
    if q:
        # Search discovered skills directly (not DB) to avoid enrichment re-adding all skills
        skills = search_skills(skills_dir, q)
        enriched = await _enrich_with_discovered_from_db(skills, db)
    else:
        skills = await get_all_skills(db)
        enriched = _enrich_with_discovered(skills, discovered)
    # Add test count per skill from latest test run
    enriched = await _add_test_counts(enriched, db)
    # Apply layer and health filters
    if layer:
        enriched = [s for s in enriched if s.get("layer") == layer]
    if health:
        enriched = [s for s in enriched if s.get("health") == health]
    # Apply sort
    enriched = _sort_skills(enriched, sort)
    # Collect unique layers and health values for filter dropdowns
    all_layers = sorted(set(s.get("layer", "") for s in enriched if s.get("layer")))
    all_healths = sorted(set(s.get("health", "") for s in enriched if s.get("health")))
    # If no filters applied, use full discovered set for dropdowns
    if not layer and not health:
        unfiltered = _enrich_with_discovered(await get_all_skills(db), discovered)
        unfiltered = await _add_test_counts(unfiltered, db)
        all_layers = sorted(set(s.get("layer", "") for s in unfiltered if s.get("layer")))
        all_healths = sorted(set(s.get("health", "") for s in unfiltered if s.get("health")))
    return _render_template("home.html", {
        "skills": enriched, "query": q or "", "total": len(enriched),
        "nav_active": "skills", "layer": layer or "", "health": health or "",
        "sort": sort or "", "all_layers": all_layers, "all_healths": all_healths,
    })


@app.get("/skill/{name}", response_class=HTMLResponse)
async def skill_detail(request: Request, name: str):
    db = await get_db()
    skill = await get_skill(db, name)
    if skill is None:
        skills_dir = Path(os.environ.get("SKILL_HUB_SKILLS_DIR", str(DEFAULT_SKILLS_DIR)))
        skill = get_skill_by_name(skills_dir, name)
        if skill is None:
            html = await _render_error_page(404, f"Skill '{name}' not found", skill_name=name)
            return HTMLResponse(html, status_code=404)
    else:
        # Enrich DB skill with discovery data (scripts, modules, skill_md)
        skills_dir = Path(os.environ.get("SKILL_HUB_SKILLS_DIR", str(DEFAULT_SKILLS_DIR)))
        discovered = get_skill_by_name(skills_dir, name)
        if discovered:
            skill["scripts"] = discovered.get("scripts", skill.get("scripts", []))
            skill["modules"] = discovered.get("modules", skill.get("modules", []))
            skill["skill_md"] = discovered.get("skill_md", "")
            skill["path"] = discovered.get("path", skill.get("path", ""))
    test_runs = await get_test_runs(db, name)
    deps = await get_dependencies(db, name)
    versions = await get_versions(db, name)
    skill_md_rendered = _render_markdown(skill.get("skill_md", ""))
    config = _build_skill_config(skill)
    return _render_template("detail.html", {"skill": skill, "test_runs": test_runs, "deps": deps, "versions": versions, "config": config, "skill_md_rendered": skill_md_rendered, "nav_active": "skills"})


@app.get("/health", response_class=HTMLResponse)
async def health_page(request: Request):
    db = await get_db()
    stats = await get_health_stats(db)
    skills_dir = Path(os.environ.get("SKILL_HUB_SKILLS_DIR", str(DEFAULT_SKILLS_DIR)))
    discovered = discover_skills(skills_dir)
    skills = await get_all_skills(db)
    enriched = _enrich_with_discovered(skills, discovered)
    enriched = await _add_test_counts(enriched, db)
    return _render_template("health.html", {"stats": stats, "skills": enriched, "nav_active": "health"})


@app.get("/install", response_class=HTMLResponse)
async def install_page(request: Request):
    db = await get_db()
    skills = await get_all_skills(db)
    skills_dir = Path(os.environ.get("SKILL_HUB_SKILLS_DIR", str(DEFAULT_SKILLS_DIR)))
    discovered = discover_skills(skills_dir)
    enriched = _enrich_with_discovered(skills, discovered)
    # Collect all dependencies across skills
    all_deps = {}
    for s in enriched:
        deps = await get_dependencies(db, s["name"])
        if deps:
            all_deps[s["name"]] = deps
    return _render_template("install.html", {
        "skills_dir": str(DEFAULT_SKILLS_DIR),
        "skills": enriched,
        "all_deps": all_deps,
        "nav_active": "install",
    })


@app.get("/test/{name}", response_class=HTMLResponse)
async def test_page(request: Request, name: str):
    db = await get_db()
    skill = await get_skill(db, name)
    if skill is None:
        html = await _render_error_page(404, f"Skill '{name}' not found", skill_name=name)
        return HTMLResponse(html, status_code=404)
    test_runs = await get_test_runs(db, name)
    return _render_template("test.html", {"skill": skill, "test_runs": test_runs, "nav_active": "skills"})


# --- REST API ---

@app.get("/api/skills")
async def api_skills(q: Optional[str] = None, layer: Optional[str] = None, health: Optional[str] = None, sort: Optional[str] = None):
    db = await get_db()
    skills_dir = Path(os.environ.get("SKILL_HUB_SKILLS_DIR", str(DEFAULT_SKILLS_DIR)))
    discovered = discover_skills(skills_dir)
    if q:
        skills = search_skills(skills_dir, q)
        enriched = await _enrich_with_discovered_from_db(skills, db)
    else:
        skills = await get_all_skills(db)
        enriched = _enrich_with_discovered(skills, discovered)
    enriched = await _add_test_counts(enriched, db)
    if layer:
        enriched = [s for s in enriched if s.get("layer") == layer]
    if health:
        enriched = [s for s in enriched if s.get("health") == health]
    enriched = _sort_skills(enriched, sort)
    return enriched


@app.get("/api/skills/export.csv", response_class=PlainTextResponse)
async def api_export_csv():
    """Export all skills as CSV."""
    db = await get_db()
    skills = await get_all_skills(db)
    lines = ["name,version,layer,health,author,description,category,path"]
    for s in skills:
        desc = s.get("description", "").replace(",", ";")
        lines.append(f"{s['name']},{s.get('version','')},{s.get('layer','')},{s.get('health','')},{s.get('author','')},{desc},{s.get('category','')},{s.get('path','')}")
    return "\n".join(lines)


@app.get("/api/skills/{name}")
async def api_skill_detail(name: str):
    db = await get_db()
    skill = await get_skill(db, name)
    if skill is None:
        skills_dir = Path(os.environ.get("SKILL_HUB_SKILLS_DIR", str(DEFAULT_SKILLS_DIR)))
        skill = get_skill_by_name(skills_dir, name)
        if skill is None:
            return JSONResponse({"error": f"Skill '{name}' not found"}, status_code=404)
    test_runs = await get_test_runs(db, name)
    skill["test_runs"] = test_runs
    return skill


@app.post("/api/skills/{name}/test")
async def api_run_test(name: str):
    db = await get_db()
    skill = await get_skill(db, name)
    if skill is None:
        return JSONResponse({"error": f"Skill '{name}' not found"}, status_code=404)

    result = await _run_skill_tests(name, skill.get("path", ""))
    run_id = await record_test_run(db, result)
    result["run_id"] = run_id
    # Update skill health based on test result
    health = "passing" if result["failed"] == 0 and result["errors"] == 0 and result["passed"] > 0 else "failing"
    skill["health"] = health
    await upsert_skill(db, skill)
    return result


@app.get("/api/health")
async def api_health():
    db = await get_db()
    return await get_health_stats(db)


@app.get("/api/skills/{name}/versions")
async def api_skill_versions(name: str):
    """Get version history for a skill."""
    db = await get_db()
    skill = await get_skill(db, name)
    if skill is None:
        return JSONResponse({"error": f"Skill '{name}' not found"}, status_code=404)
    versions = await get_versions(db, name)
    return {"skill_name": name, "current_version": skill.get("version", "0.0.0"), "versions": versions}


@app.post("/api/skills/resync")
async def api_resync_skills():
    """Re-discover skills from filesystem and sync to database."""
    db = await get_db()
    skills_dir = Path(os.environ.get("SKILL_HUB_SKILLS_DIR", str(DEFAULT_SKILLS_DIR)))
    discovered = discover_skills(skills_dir)
    await sync_skills(db, discovered)
    await sync_dependencies(db, discovered)
    enriched = _enrich_with_discovered(await get_all_skills(db), discovered)
    enriched = await _add_test_counts(enriched, db)
    return {"resynced": len(enriched), "skills": enriched}


@app.post("/api/skills/{name}/check-deps")
async def api_check_deps(name: str):
    """Check whether a skill's dependencies are actually installed."""
    db = await get_db()
    skill = await get_skill(db, name)
    if skill is None:
        skills_dir = Path(os.environ.get("SKILL_HUB_SKILLS_DIR", str(DEFAULT_SKILLS_DIR)))
        skill = get_skill_by_name(skills_dir, name)
        if skill is None:
            return JSONResponse({"error": f"Skill '{name}' not found"}, status_code=404)
    deps_from_db = await get_dependencies(db, name)
    if not deps_from_db:
        # Try discovered dependencies
        skills_dir = Path(os.environ.get("SKILL_HUB_SKILLS_DIR", str(DEFAULT_SKILLS_DIR)))
        discovered = get_skill_by_name(skills_dir, name)
        if discovered and discovered.get("dependencies"):
            deps_from_db = discovered["dependencies"]
    checked = check_all_deps(deps_from_db)
    # Update DB with actual installed status
    for d in checked:
        await upsert_dependency(db, name, d["dep_name"], d["dep_type"], 1 if d["installed"] else 0)
    return {"skill_name": name, "dependencies": checked}


@app.post("/api/skills/test-all")
async def api_test_all():
    """Run tests for all skills and return aggregated results."""
    db = await get_db()
    skills = await get_all_skills(db)
    results = []
    for skill in skills:
        name = skill["name"]
        skill_path = skill.get("path", "")
        test_result = await _run_skill_tests(name, skill_path)
        await record_test_run(db, test_result)
        # Update skill health based on test result
        if test_result.get("status") == "completed" and test_result.get("failed", 0) == 0 and test_result.get("errors", 0) == 0:
            skill["health"] = "passing"
        elif test_result.get("status") == "completed":
            skill["health"] = "failing"
        else:
            skill["health"] = "unknown"
        await upsert_skill(db, skill)
        results.append(test_result)
    total_passed = sum(r.get("passed", 0) for r in results)
    total_failed = sum(r.get("failed", 0) for r in results)
    total_errors = sum(r.get("errors", 0) for r in results)
    total_skills = len(results)
    skills_completed = sum(1 for r in results if r.get("status") == "completed")
    return {
        "total_skills": total_skills,
        "skills_completed": skills_completed,
        "total_passed": total_passed,
        "total_failed": total_failed,
        "total_errors": total_errors,
        "results": results,
    }


# --- WebSocket for live test streaming ---

@app.websocket("/ws/test/{name}")
async def ws_test_stream(websocket: WebSocket, name: str):
    await websocket.accept()
    db = await get_db()
    skill = await get_skill(db, name)
    if skill is None:
        await websocket.send_json({"error": f"Skill '{name}' not found"})
        await websocket.close()
        return

    skill_path = skill.get("path", "")
    # Find test directory
    test_dir = _find_test_dir(name, skill_path)

    try:
        proc = await asyncio.create_subprocess_exec(
            sys.executable, "-m", "pytest",
            str(test_dir), "-v", "--tb=short",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )

        total = 0
        passed = 0
        failed = 0
        errors = 0
        skipped = 0

        while True:
            line = await proc.stdout.readline()
            if not line:
                break
            text = line.decode("utf-8", errors="replace").rstrip()
            await websocket.send_json({"line": text})

            # Parse pytest output for counts
            if text.startswith("PASSED"):
                passed += 1; total += 1
            elif text.startswith("FAILED"):
                failed += 1; total += 1
            elif text.startswith("ERROR"):
                errors += 1; total += 1
            elif text.startswith("SKIPPED"):
                skipped += 1; total += 1

        await proc.wait()

        result = {
            "skill_name": name,
            "status": "completed",
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "skipped": skipped,
            "duration_seconds": 0.0,
            "output": "",
        }
        # Parse summary line for accurate counts
        result = _parse_pytest_summary(result, text if text else "")
        run_id = await record_test_run(db, result)
        health = "passing" if result["failed"] == 0 and result["errors"] == 0 and result["passed"] > 0 else "failing"
        skill["health"] = health
        await upsert_skill(db, skill)

        await websocket.send_json({"result": result, "run_id": run_id})
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json({"error": str(e)})
    finally:
        await websocket.close()


# --- Helpers ---


def _sort_skills(skills: list[dict], sort: Optional[str] = None) -> list[dict]:
    """Sort skills by a specified field. Options: name, name-desc, version, test_count, health."""
    if not sort:
        return skills
    sort_key, reverse = _sort_key_and_reverse(sort)
    if sort_key == "test_count":
        skills.sort(key=lambda s: s.get("test_count", 0) or 0, reverse=reverse)
    elif sort_key == "health":
        health_order = {"passing": 0, "unknown": 1, "failing": 2}
        skills.sort(key=lambda s: health_order.get(s.get("health", "unknown"), 1), reverse=reverse)
    elif sort_key == "version":
        skills.sort(key=lambda s: s.get("version", "0.0.0"), reverse=reverse)
    elif sort_key == "name":
        skills.sort(key=lambda s: s.get("name", "").lower(), reverse=reverse)
    return skills


def _sort_key_and_reverse(sort: str) -> tuple[str, bool]:
    """Parse sort parameter into (key, reverse). Supports 'name', 'name-desc', etc."""
    desc_suffix = "-desc"
    if sort.endswith(desc_suffix):
        return sort[:-len(desc_suffix)], True
    return sort, False


def _build_skill_config(skill: dict) -> dict:
    """Build a config dict from SKILL.md frontmatter, excluding internal fields."""
    skill_md = skill.get("skill_md", "")
    if not skill_md:
        return {}
    fm = _yaml_frontmatter(skill_md)
    # Exclude fields that are displayed in other sections
    internal_keys = {"name", "description", "version", "author", "layer"}
    config = {k: v for k, v in fm.items() if k not in internal_keys}
    return config


def _enrich_with_discovered(db_skills: list[dict], discovered: list[dict]) -> list[dict]:
    """Merge DB data with real-time discovery for scripts/modules/skill_md."""
    disc_map = {s["name"]: s for s in discovered}
    enriched = []
    for s in db_skills:
        name = s["name"]
        if name in disc_map:
            d = disc_map[name]
            s["scripts"] = d.get("scripts", s.get("scripts", []))
            s["modules"] = d.get("modules", s.get("modules", []))
            s["skill_md"] = d.get("skill_md", "")
            s["path"] = d.get("path", s.get("path", ""))
        enriched.append(s)
    # Add any discovered skills not in DB
    for d in discovered:
        if d["name"] not in {s["name"] for s in db_skills}:
            enriched.append(d)
    return enriched


async def _enrich_with_discovered_from_db(skills: list[dict], db) -> list[dict]:
    """Enrich search-filtered discovered skills with DB data (health, timestamps)."""
    enriched = []
    for s in skills:
        db_skill = await get_skill(db, s["name"])
        if db_skill:
            s["health"] = db_skill.get("health", s.get("health", "unknown"))
            s["discovered_at"] = db_skill.get("discovered_at", "")
            s["updated_at"] = db_skill.get("updated_at", "")
        enriched.append(s)
    return enriched


async def _add_test_counts(skills: list[dict], db) -> list[dict]:
    """Add test count, last_tested_at, and pass_rate from latest test run for each skill."""
    for s in skills:
        runs = await get_test_runs(db, s["name"], limit=1)
        if runs:
            run = runs[0]
            s["test_count"] = run.get("total_tests", 0)
            s["last_tested_at"] = run.get("started_at", "")
            total = run.get("total_tests", 0)
            passed = run.get("passed", 0)
            s["pass_rate"] = (passed / total) if total > 0 else 0.0
        else:
            test_dir = Path(s.get("path", "")) / "tests"
            if test_dir.is_dir():
                s["test_count"] = _count_tests_in_dir(test_dir)
            else:
                s["test_count"] = 0
            s["last_tested_at"] = ""
            s["pass_rate"] = 0.0
    return skills


def _count_tests_in_dir(test_dir: Path) -> int:
    """Count test functions in a test directory by scanning for 'def test_' patterns."""
    count = 0
    for f in test_dir.glob("test_*.py"):
        try:
            content = f.read_text(encoding="utf-8", errors="replace")
            # Count both top-level and class method test definitions
            count += len(re.findall(r"def test_\w+", content))
        except Exception:
            pass
    return count


async def _run_skill_tests(name: str, skill_path: str) -> dict:
    """Run pytest for a skill and return structured results."""
    test_dir = _find_test_dir(name, skill_path)
    from datetime import datetime, timezone
    started = datetime.now(timezone.utc).isoformat()

    try:
        proc = await asyncio.create_subprocess_exec(
            sys.executable, "-m", "pytest",
            str(test_dir), "-v", "--tb=short", "-q",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        output = stdout.decode("utf-8", errors="replace")
        duration = 0.0

        result = {
            "skill_name": name,
            "status": "completed" if proc.returncode == 0 else "failed",
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "skipped": 0,
            "duration_seconds": duration,
            "output": output,
            "started_at": started,
            "finished_at": datetime.now(timezone.utc).isoformat(),
        }
        result = _parse_pytest_summary(result, output)
        return result
    except Exception as e:
        return {
            "skill_name": name,
            "status": "error",
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": 1,
            "skipped": 0,
            "duration_seconds": 0.0,
            "output": str(e),
            "started_at": started,
            "finished_at": datetime.now(timezone.utc).isoformat(),
        }


def _find_test_dir(name: str, skill_path: str) -> Path:
    """Find the test directory for a skill."""
    # Check skill's own tests/ dir first
    if skill_path:
        skill_test = Path(skill_path) / "tests"
        if skill_test.is_dir():
            return skill_test
    # Check project-level tests/
    project_test = PROJECT_ROOT / "tests"
    if project_test.is_dir():
        return project_test
    # Fallback
    return Path(skill_path) / "tests" if skill_path else PROJECT_ROOT / "tests"


def _render_markdown(text: str) -> str:
    """Convert basic Markdown to HTML (headers, bold, italic, code, links, lists, tables, blockquotes, hr)."""
    if not text:
        return ""
    # Code blocks first (preserve content inside)
    code_blocks = []
    def _save_code(m):
        code_blocks.append(m.group(2).rstrip())
        return f'<CODE_BLOCK_{len(code_blocks) - 1}>'
    text = re.sub(r'```(\w*)\n(.*?)```', _save_code, text, flags=re.DOTALL)

    # Inline code
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)

    # Horizontal rules (---, ***, ___ on their own line)
    text = re.sub(r'^\s*[-*_]{3,}\s*$', '<hr>', text, flags=re.MULTILINE)

    # Headers
    text = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', text, flags=re.MULTILINE)
    text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^# (.+)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)

    # Bold and italic
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)

    # Links
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)

    # Blockquotes (lines starting with >)
    lines = text.split('\n')
    result_lines = []
    in_quote = False
    in_ul = False
    in_ol = False
    ol_start = 1

    # Markdown tables: detect consecutive lines starting with | and parse them
    table_lines = []
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        # Check if this line starts a markdown table
        if stripped.startswith('|') and '|' in stripped[1:]:
            # Collect all table lines
            table_lines = [stripped]
            j = i + 1
            while j < len(lines) and lines[j].strip().startswith('|') and '|' in lines[j].strip()[1:]:
                table_lines.append(lines[j].strip())
                j += 1
            # Parse and render table
            if len(table_lines) >= 2:
                table_html = _parse_md_table(table_lines)
                # Close any open list before inserting table
                if in_ul:
                    result_lines.append('</ul>')
                    in_ul = False
                if in_ol:
                    result_lines.append('</ol>')
                    in_ol = False
                if in_quote:
                    result_lines.append('</blockquote>')
                    in_quote = False
                result_lines.append(table_html)
                i = j
                continue
            else:
                # Single | line, not a valid table — treat as regular text
                table_lines = []

        # Blockquotes
        if stripped.startswith('> '):
            content = stripped[2:]
            if not in_quote:
                # Close any open list before blockquote
                if in_ul:
                    result_lines.append('</ul>')
                    in_ul = False
                if in_ol:
                    result_lines.append('</ol>')
                    in_ol = False
                result_lines.append('<blockquote>')
                in_quote = True
            result_lines.append(content)
        elif stripped.startswith('>') and not stripped.startswith('> ') and len(stripped) > 1:
            # > without space — still blockquote content
            if not in_quote:
                if in_ul:
                    result_lines.append('</ul>')
                    in_ul = False
                if in_ol:
                    result_lines.append('</ol>')
                    in_ol = False
                result_lines.append('<blockquote>')
                in_quote = True
            result_lines.append(stripped[1:])
        else:
            if in_quote:
                result_lines.append('</blockquote>')
                in_quote = False

            # Ordered lists (1. item, 2. item, etc.)
            ol_match = re.match(r'^\s*(\d+)\.\s+(.+)$', stripped)
            ul_match = stripped.startswith('- ') or stripped.startswith('* ')

            if ol_match:
                num = int(ol_match.group(1))
                content = ol_match.group(2)
                if not in_ol:
                    # Close unordered list if open
                    if in_ul:
                        result_lines.append('</ul>')
                        in_ul = False
                    result_lines.append(f'<ol start="{num}">')
                    in_ol = True
                    ol_start = num
                result_lines.append(f'<li>{content}</li>')
            elif ul_match:
                if not in_ul:
                    # Close ordered list if open
                    if in_ol:
                        result_lines.append('</ol>')
                        in_ol = False
                    result_lines.append('<ul>')
                    in_ul = True
                result_lines.append(f'<li>{stripped[2:]}</li>')
            else:
                if in_ul:
                    result_lines.append('</ul>')
                    in_ul = False
                if in_ol:
                    result_lines.append('</ol>')
                    in_ol = False
                result_lines.append(lines[i])
        i += 1

    # Close any open elements at end
    if in_quote:
        result_lines.append('</blockquote>')
    if in_ul:
        result_lines.append('</ul>')
    if in_ol:
        result_lines.append('</ol>')
    text = '\n'.join(result_lines)

    # Paragraphs (double newline = paragraph break)
    text = re.sub(r'\n\n+', '\n</p>\n<p>\n', text)
    text = f'<p>{text}</p>'
    # Clean up empty paragraphs
    text = re.sub(r'<p>\s*</p>', '', text)
    # Don't wrap block elements in <p>
    text = re.sub(r'<p>(<h[1-6]>.*?</h[1-6]>)</p>', r'\1', text, flags=re.DOTALL)
    text = re.sub(r'<p>(<ul>.*?</ul>)</p>', r'\1', text, flags=re.DOTALL)
    text = re.sub(r'<p>(<ol[^>]*>.*?</ol>)</p>', r'\1', text, flags=re.DOTALL)
    text = re.sub(r'<p>(<blockquote>.*?</blockquote>)</p>', r'\1', text, flags=re.DOTALL)
    text = re.sub(r'<p>(<table.*?</table>)</p>', r'\1', text, flags=re.DOTALL)
    text = re.sub(r'<p>(<hr>)</p>', r'\1', text)
    text = re.sub(r'<p>(<CODE_BLOCK_\d+>)</p>', r'\1', text)

    # Restore code blocks as <pre>
    for i, code in enumerate(code_blocks):
        # Escape HTML entities in code
        escaped = code.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        text = text.replace(f'<CODE_BLOCK_{i}>', f'<pre><code>{escaped}</code></pre>')

    return text


def _parse_md_table(lines: list[str]) -> str:
    """Parse markdown table lines (| col | col |) into HTML <table>."""
    if len(lines) < 2:
        return ''
    # First line: header
    header_cells = [c.strip() for c in lines[0].strip().strip('|').split('|')]
    # Second line: separator (| --- | --- |) — skip it
    # Remaining lines: body rows
    body_lines = lines[2:] if len(lines) > 2 else []
    rows_html = ''
    for row_line in body_lines:
        cells = [c.strip() for c in row_line.strip().strip('|').split('|')]
        row_cells = ''.join(f'<td>{c}</td>' for c in cells)
        rows_html += f'<tr>{row_cells}</tr>'
    header_html = ''.join(f'<th>{c}</th>' for c in header_cells)
    return f'<table><thead><tr>{header_html}</tr></thead><tbody>{rows_html}</tbody></table>'


def _parse_pytest_summary(result: dict, output: str) -> dict:
    """Parse pytest summary line for accurate counts."""
    # Match: "2 passed, 1 failed, 3 errors in 1.23s"
    summary_match = re.search(
        r"(\d+) passed(?:,\s*(\d+) failed)?(?:,\s*(\d+) errors)?(?:,\s*(\d+) skipped)?(?:,\s*(\d+) warnings)?\s*in\s*([\d.]+)s",
        output,
    )
    if summary_match:
        result["passed"] = int(summary_match.group(1) or 0)
        result["failed"] = int(summary_match.group(2) or 0)
        result["errors"] = int(summary_match.group(3) or 0)
        result["skipped"] = int(summary_match.group(4) or 0)
        result["total_tests"] = result["passed"] + result["failed"] + result["errors"] + result["skipped"]
        result["duration_seconds"] = float(summary_match.group(6) or 0)
    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=DEFAULT_PORT)