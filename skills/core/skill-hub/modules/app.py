"""Skill Hub FastAPI application with Jinja2 templates and REST API."""

import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

# Ensure modules directory is on sys.path for imports
MODULES_DIR = str(Path(__file__).resolve().parent)
if MODULES_DIR not in sys.path:
    sys.path.insert(0, MODULES_DIR)

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from skill_discovery import discover_skills, get_skill_by_name, search_skills
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
    upsert_dependency,
    get_dependencies,
)

# Resolve paths: app.py is in skill-hub/modules/
SKILL_HUB_DIR = Path(__file__).resolve().parent.parent  # skills/core/skill-hub/
PROJECT_ROOT = SKILL_HUB_DIR.parent.parent.parent  # quinn-awesome-skills/
DEFAULT_SKILLS_DIR = PROJECT_ROOT / "skills"
DEFAULT_PORT = int(os.environ.get("SKILL_HUB_PORT", "8765"))

app = FastAPI(title="Skill Hub", version="1.0.0")

# Global db connection
_db = None


async def get_db():
    global _db
    if _db is None:
        db_path = os.environ.get("SKILL_HUB_DB", DEFAULT_DB_PATH)
        _db = await init_db(db_path)
        # Sync discovered skills on startup
        skills_dir = Path(os.environ.get("SKILL_HUB_SKILLS_DIR", str(DEFAULT_SKILLS_DIR)))
        discovered = discover_skills(skills_dir)
        await sync_skills(_db, discovered)
    return _db


@app.on_event("startup")
async def startup():
    await get_db()


@app.on_event("shutdown")
async def shutdown():
    global _db
    if _db is not None:
        await _db.close()
        _db = None


# --- HTML Pages (Jinja2) ---

def _render_template(template_name: str, context: dict) -> str:
    """Render a Jinja2 template from the templates/ directory."""
    from jinja2 import Environment, FileSystemLoader
    env = Environment(
        loader=FileSystemLoader(str(SKILL_HUB_DIR / "templates")),
        autoescape=True,
    )
    template = env.get_template(template_name)
    return template.render(**context)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request, q: Optional[str] = None):
    db = await get_db()
    if q:
        skills = await search_skills_db(db, q)
    else:
        skills = await get_all_skills(db)
    # Also enrich with real-time discovery data for scripts/modules
    skills_dir = Path(os.environ.get("SKILL_HUB_SKILLS_DIR", str(DEFAULT_SKILLS_DIR)))
    discovered = discover_skills(skills_dir)
    enriched = _enrich_with_discovered(skills, discovered)
    return _render_template("home.html", {"skills": enriched, "query": q or "", "total": len(enriched)})


@app.get("/skill/{name}", response_class=HTMLResponse)
async def skill_detail(request: Request, name: str):
    db = await get_db()
    skill = await get_skill(db, name)
    if skill is None:
        skills_dir = Path(os.environ.get("SKILL_HUB_SKILLS_DIR", str(DEFAULT_SKILLS_DIR)))
        skill = get_skill_by_name(skills_dir, name)
        if skill is None:
            return HTMLResponse(f"<h1>Skill '{name}' not found</h1>", status_code=404)
    test_runs = await get_test_runs(db, name)
    deps = await get_dependencies(db, name)
    return _render_template("detail.html", {"skill": skill, "test_runs": test_runs, "deps": deps})


@app.get("/health", response_class=HTMLResponse)
async def health_page(request: Request):
    db = await get_db()
    stats = await get_health_stats(db)
    return _render_template("health.html", {"stats": stats})


@app.get("/install", response_class=HTMLResponse)
async def install_page(request: Request):
    return _render_template("install.html", {"skills_dir": str(DEFAULT_SKILLS_DIR)})


@app.get("/test/{name}", response_class=HTMLResponse)
async def test_page(request: Request, name: str):
    db = await get_db()
    skill = await get_skill(db, name)
    if skill is None:
        return HTMLResponse(f"<h1>Skill '{name}' not found</h1>", status_code=404)
    return _render_template("test.html", {"skill": skill})


# --- REST API ---

@app.get("/api/skills")
async def api_skills(q: Optional[str] = None):
    db = await get_db()
    if q:
        skills = await search_skills_db(db, q)
    else:
        skills = await get_all_skills(db)
    skills_dir = Path(os.environ.get("SKILL_HUB_SKILLS_DIR", str(DEFAULT_SKILLS_DIR)))
    discovered = discover_skills(skills_dir)
    return _enrich_with_discovered(skills, discovered)


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


def _parse_pytest_summary(result: dict, output: str) -> dict:
    """Parse pytest summary line for accurate counts."""
    import re
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
    uvicorn.run(app, host="0.0.0.0", port=DEFAULT_PORT)