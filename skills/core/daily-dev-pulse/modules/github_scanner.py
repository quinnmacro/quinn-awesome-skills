"""GitHub activity scanner for Daily Dev Pulse.

Uses gh CLI to fetch repo activity: commits, PRs, issues, CI status.
"""

import json
import subprocess
from datetime import datetime, timedelta, timezone

from config import get_repos, get_preferences, load_config


def run_gh(args, repo=None, fallback=None):
    """Run a gh CLI command and return parsed JSON, or fallback on error."""
    cmd = ["gh"] + args
    if repo:
        cmd += ["--repo", repo]
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            return fallback
        return json.loads(result.stdout) if result.stdout.strip() else fallback
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
        return fallback


def scan_commits(repo_owner, repo_name, days=7):
    """Get recent commits for a repo."""
    repo = f"{repo_owner}/{repo_name}"
    since = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    commits = run_gh(
        ["api", f"/repos/{repo}/commits?since={since}&per_page=50"],
        fallback=[]
    )
    if not commits:
        return []

    return [
        {
            "sha": (c.get("sha") or "")[:7],
            "message": (c.get("commit", {}).get("message") or "").split("\n")[0],
            "author": (c.get("commit", {}).get("author", {}).get("name") or "unknown"),
            "date": (c.get("commit", {}).get("author", {}).get("date") or "")[:10],
        }
        for c in commits[:20]
    ]


def scan_prs(repo_owner, repo_name, state="open"):
    """Get open/closed PRs for a repo."""
    repo = f"{repo_owner}/{repo_name}"
    prs = run_gh(
        ["pr", "list", "--repo", repo, "--state", state, "--limit", "20", "--json",
         "number,title,author,createdAt,updatedAt,labels"],
        fallback=[]
    )
    return prs if prs else []


def scan_issues(repo_owner, repo_name, state="open"):
    """Get open/closed issues for a repo."""
    repo = f"{repo_owner}/{repo_name}"
    issues = run_gh(
        ["issue", "list", "--repo", repo, "--state", state, "--limit", "20", "--json",
         "number,title,author,createdAt,labels"],
        fallback=[]
    )
    return issues if issues else []


def scan_ci_status(repo_owner, repo_name, branch="main"):
    """Get recent CI/GitHub Actions run status."""
    repo = f"{repo_owner}/{repo_name}"
    runs = run_gh(
        ["run", "list", "--repo", repo, "--branch", branch, "--limit", "5", "--json",
         "name,status,conclusion,createdAt,headBranch"],
        fallback=[]
    )
    return runs if runs else []


def scan_all_repos(config=None):
    """Scan all configured repos and return combined activity data."""
    cfg = config or load_config()
    repos = get_repos(cfg)
    prefs = get_preferences(cfg)
    days = prefs.get("lookback_days", 7)

    results = []
    for repo in repos:
        owner = repo.get("owner") or ""
        name = repo.get("name") or ""
        if not owner or not name:
            continue
        full_name = f"{owner}/{name}"

        commits = scan_commits(owner, name, days)
        prs = scan_prs(owner, name, "open")
        issues = scan_issues(owner, name, "open")
        ci_runs = scan_ci_status(owner, name)

        results.append({
            "repo": full_name,
            "commits": commits,
            "commit_count": len(commits),
            "open_prs": prs,
            "open_issues": issues,
            "ci_runs": ci_runs,
        })

    return {
        "source": "github",
        "repos": results,
        "scan_date": datetime.now(timezone.utc).isoformat(),
    }


if __name__ == "__main__":
    data = scan_all_repos()
    print(json.dumps(data, indent=2))