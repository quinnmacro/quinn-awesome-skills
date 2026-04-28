"""Pulse formatter for Daily Dev Pulse.

Takes combined JSON data and produces formatted output in terminal, markdown, or JSON mode.
"""

import argparse
import copy
import json
import sys
from datetime import datetime, timezone


# ANSI color codes for terminal output
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    DIM = "\033[2m"
    BOX_TL = "╔"
    BOX_TR = "╗"
    BOX_BL = "╚"
    BOX_BR = "╝"
    BOX_SIDE = "║"
    BOX_HORIZ = "═"
    BAR_CHAR = "█"
    BAR_EMPTY = "▒"


SEVERITY_EMOJI = {
    "CRITICAL": "🔴",
    "HIGH": "⚠️",
    "MEDIUM": "📋",
    "LOW": "💡",
    "unknown": "❓",
}

CI_EMOJI = {
    "success": "✅",
    "failure": "❌",
    "in_progress": "🔄",
    "queued": "⏳",
    "cancelled": "🚫",
    "unknown": "❓",
}


def ascii_bar(count, max_count, width=30):
    """Generate ASCII bar chart for commit counts."""
    if max_count == 0:
        return Colors.BAR_EMPTY * width
    filled = int(count / max_count * width)
    return Colors.BAR_CHAR * filled + Colors.BAR_EMPTY * (width - filled)


def format_terminal(data):
    """Format data as rich terminal output with ASCII charts and colors."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    width = 48

    lines = []
    # Compute padding dynamically based on visible content width
    # ANSI escape sequences have 0 visible width, so only count actual chars
    header_prefix = "   🌅 DAILY DEV PULSE — "
    header_suffix_len = 1  # BOX_SIDE
    # 🌅 emoji renders as 2 columns in most terminals
    visible_prefix_len = len("   ") + 2 + len(" DAILY DEV PULSE — ")  # 3+2+18=23
    padding = width - visible_prefix_len - len(today) - header_suffix_len

    lines.append(f"{Colors.BOX_TL}{Colors.BOX_HORIZ * width}{Colors.BOX_TR}")
    lines.append(f"{Colors.BOX_SIDE}{Colors.BOLD}{Colors.CYAN}{header_prefix}{today}{Colors.RESET}{' ' * padding}{Colors.BOX_SIDE}")
    lines.append(f"{Colors.BOX_BL}{Colors.BOX_HORIZ * width}{Colors.BOX_BR}")
    lines.append("")

    # GitHub Activity
    github = data.get("github", {})
    if github and not github.get("error"):
        repos = github.get("repos", [])
        if isinstance(repos, list) and repos:
            lines.append(f"{Colors.BOLD}{Colors.BLUE}📊 GitHub Activity (Last {data.get('preferences', {}).get('lookback_days', data.get('github', {}).get('lookback_days', 7))} Days){Colors.RESET}")
            max_commits = max(r.get("commit_count", 0) for r in repos) if repos else 1
            for repo in repos:
                name = (repo.get("repo") or "").split("/")[-1]
                count = repo.get("commit_count", 0)
                bar = ascii_bar(count, max(max_commits, 1), 20)
                lines.append(f"  {Colors.GREEN}{name:20s}{Colors.RESET} {bar} {Colors.BOLD}{count}{Colors.RESET} commits")

            # CI Status (only show heading if at least one repo has CI runs)
            has_ci = any(isinstance(repo.get("ci_runs"), list) and len(repo.get("ci_runs", [])) > 0 for repo in repos)
            if has_ci:
                lines.append("")
                lines.append(f"{Colors.BOLD}{Colors.BLUE}🔄 CI Status{Colors.RESET}")
                for repo in repos:
                    name = (repo.get("repo") or "").split("/")[-1]
                    ci_runs = repo.get("ci_runs", [])
                    if isinstance(ci_runs, list) and ci_runs:
                        latest = ci_runs[0]
                        status = (latest.get("status") or "unknown")
                        conclusion = (latest.get("conclusion") or "unknown")
                        emoji = CI_EMOJI.get(conclusion, CI_EMOJI.get(status, CI_EMOJI["unknown"]))
                        lines.append(f"  {emoji} {name}: {conclusion} ({latest.get('name') or 'unknown'})")
                lines.append("")

    # GitHub error
    if github.get("error"):
        lines.append(f"{Colors.YELLOW}⚠️ GitHub: {github.get('error')}{Colors.RESET}")
        lines.append("")

    # Open PRs & Issues
    if github and not github.get("error"):
        repos = github.get("repos", [])
        if isinstance(repos, list):
            has_prs = any(isinstance(r.get("open_prs"), list) and len(r.get("open_prs", [])) > 0 for r in repos)
            has_issues = any(isinstance(r.get("open_issues"), list) and len(r.get("open_issues", [])) > 0 for r in repos)

            if has_prs or has_issues:
                lines.append(f"{Colors.BOLD}{Colors.BLUE}🔍 Open PRs & Issues{Colors.RESET}")
                lines.append(f"  ┌{'─' * 30}┬{'─' * 8}┬{'─' * 30}┐")
                lines.append(f"  │{'Repo':^30}│{'Type':^8}│{'Title':^30}│")
                lines.append(f"  ├{'─' * 30}┼{'─' * 8}┼{'─' * 30}┤")
                for repo in repos:
                    name = (repo.get("repo") or "").split("/")[-1][:30]
                    open_prs = repo.get("open_prs", [])
                    if isinstance(open_prs, list):
                        for pr in open_prs[:5]:
                            title = (pr.get("title") or "")[:30]
                            lines.append(f"  │{name:^30}│{'PR':^8}│{title:^30}│")
                    open_issues = repo.get("open_issues", [])
                    if isinstance(open_issues, list):
                        for issue in open_issues[:5]:
                            title = (issue.get("title") or "")[:30]
                            lines.append(f"  │{name:^30}│{'Issue':^8}│{title:^30}│")
                lines.append(f"  └{'─' * 30}┴{'─' * 8}┴{'─' * 30}┘")
                lines.append("")

    # Security Alerts
    security = data.get("security", {})
    if security and not security.get("error"):
        alerts = security.get("alerts", [])
        if isinstance(alerts, list) and alerts:
            sec_lookback = data.get('preferences', {}).get('security_lookback_days', 30)
            lines.append(f"{Colors.BOLD}{Colors.RED}🛡️ Security Alerts (Last {sec_lookback} Days){Colors.RESET}")
            for alert in alerts[:8]:
                sev = alert.get("severity") or "unknown"
                emoji = SEVERITY_EMOJI.get(sev, SEVERITY_EMOJI["unknown"])
                cve_id = alert.get("cve_id") or ""
                product = alert.get("product") or ""
                desc = (alert.get("description") or "")[:60]
                lines.append(f"  {emoji} {cve_id} — {product} ({sev}): {desc}")
            lines.append("")

    # Package Updates
    packages = data.get("packages", {})
    if packages and not packages.get("error"):
        updates = packages.get("updates", [])
        if isinstance(updates, list) and updates:
            lines.append(f"{Colors.BOLD}{Colors.BLUE}📦 Package Updates{Colors.RESET}")
            for pkg in updates:
                name = pkg.get("package") or ""
                reg = pkg.get("registry") or ""
                ver = pkg.get("latest_version") or "unknown"
                lines.append(f"  {reg:4s} {Colors.GREEN}{name}{Colors.RESET} → {ver}")
            lines.append("")

    # News
    news = data.get("news", {})
    if news and not news.get("error"):
        headlines = news.get("headlines", [])
        if isinstance(headlines, list) and headlines:
            lines.append(f"{Colors.BOLD}{Colors.BLUE}📰 Trending Dev News{Colors.RESET}")
            for i, hl in enumerate(headlines[:10], 1):
                source = hl.get("source") or ""
                title = (hl.get("title") or "")[:60]
                score = hl.get("score", 0)
                lines.append(f"  {i:2d}. [{source:4s}] {title} ({score} pts)")
            lines.append("")

    # Action Items
    lines.append(f"{Colors.BOLD}{Colors.GREEN}✅ Action Items{Colors.RESET}")
    action_items = generate_action_items(data)
    for item in action_items:
        lines.append(f"  → {item}")
    if not action_items:
        lines.append(f"  {Colors.DIM}No urgent items — have a productive day!{Colors.RESET}")

    return "\n".join(lines)


def format_markdown(data):
    """Format data as structured markdown for Claude consumption."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines = [f"# 🌅 Daily Dev Pulse — {today}", ""]

    # GitHub
    github = data.get("github", {})
    if github and not github.get("error"):
        repos = github.get("repos", [])
        if isinstance(repos, list) and repos:
            lookback = data.get("preferences", {}).get("lookback_days", 7)
            lines.append(f"## GitHub Activity (Last {lookback} Days)")
            lines.append("")
            lines.append("| Repo | Commits | Latest CI |")
            lines.append("|------|---------|-----------|")
            for repo in repos:
                name = (repo.get("repo") or "").split("/")[-1]
                count = repo.get("commit_count", 0)
                ci_runs = repo.get("ci_runs", [])
                ci_status = ci_runs[0].get("conclusion") or "N/A" if isinstance(ci_runs, list) and ci_runs else "N/A"
                emoji = CI_EMOJI.get(ci_status, "❓")
                lines.append(f"| {name} | {count} | {emoji} {ci_status} |")
            lines.append("")

        # PRs
        all_prs = []
        repos_for_iteration = github.get("repos", [])
        if isinstance(repos_for_iteration, list):
            for repo in repos_for_iteration:
                open_prs = repo.get("open_prs", [])
                if isinstance(open_prs, list):
                    for pr in open_prs:
                        all_prs.append((repo.get("repo") or "", pr))
        if all_prs:
            lines.append("### Open PRs")
            lines.append("")
            for full_repo, pr in all_prs[:10]:
                lines.append(f"- **{full_repo}** #{pr.get('number') or ''}: {pr.get('title') or ''}")
            lines.append("")

        # Issues
        all_issues = []
        repos_for_iteration = github.get("repos", [])
        if isinstance(repos_for_iteration, list):
            for repo in repos_for_iteration:
                open_issues = repo.get("open_issues", [])
                if isinstance(open_issues, list):
                    for issue in open_issues:
                        all_issues.append((repo.get("repo") or "", issue))
        if all_issues:
            lines.append("### Open Issues")
            lines.append("")
            for full_repo, issue in all_issues[:10]:
                lines.append(f"- **{full_repo}** #{issue.get('number') or ''}: {issue.get('title') or ''}")
            lines.append("")

    # Security
    security = data.get("security", {})
    if security and not security.get("error"):
        alerts = security.get("alerts", [])
        if isinstance(alerts, list) and alerts:
            sec_lookback = data.get("preferences", {}).get("security_lookback_days", 30)
            lines.append(f"## Security Alerts (Last {sec_lookback} Days)")
            lines.append("")
            lines.append("| CVE ID | Product | Severity | Description |")
            lines.append("|--------|---------|----------|-------------|")
            for alert in alerts[:10]:
                lines.append(f"| {alert.get('cve_id') or ''} | {alert.get('product') or ''} | {alert.get('severity') or ''} | {(alert.get('description') or '')[:50]} |")
            lines.append("")

    # Packages
    packages = data.get("packages", {})
    if packages and not packages.get("error"):
        updates = packages.get("updates", [])
        if isinstance(updates, list) and updates:
            lines.append("## Package Updates Available")
            lines.append("")
            lines.append("| Registry | Package | Latest Version |")
            lines.append("|----------|---------|----------------|")
            for pkg in updates:
                lines.append(f"| {pkg.get('registry') or ''} | {pkg.get('package') or ''} | {pkg.get('latest_version') or ''} |")
            lines.append("")

    # News
    news = data.get("news", {})
    if news and not news.get("error"):
        headlines = news.get("headlines", [])
        if isinstance(headlines, list) and headlines:
            lines.append("## Trending Dev News")
            lines.append("")
            for i, hl in enumerate(headlines[:15], 1):
                source = hl.get("source") or ""
                title = hl.get("title") or ""
                url = hl.get("url") or ""
                score = hl.get("score", 0)
                lines.append(f"{i}. **[{source}]** [{title}]({url}) ({score} pts)")
            lines.append("")

    # Action Items
    lines.append("## Action Items")
    lines.append("")
    action_items = generate_action_items(data)
    for item in action_items:
        lines.append(f"- [ ] {item}")
    if not action_items:
        lines.append("- No urgent items today")

    return "\n".join(lines)


def format_json(data):
    """Return data as structured JSON with action_items. Does not mutate input."""
    result = copy.deepcopy(data)
    result["action_items"] = generate_action_items(data)
    return json.dumps(result, indent=2, ensure_ascii=False)


def generate_action_items(data):
    """Generate personalized action items from collected data.

    Deduplicates identical item text to avoid repetition (e.g. same CI name on same repo).
    """
    items = []
    seen = set()
    stale_threshold = data.get("preferences", {}).get("stale_pr_days", 3)
    lookback_days = data.get("preferences", {}).get("lookback_days", 7)
    max_issues_per_repo = data.get("preferences", {}).get("max_issues_per_repo", 3)
    max_action_items = data.get("preferences", {}).get("max_action_items", 10)

    github = data.get("github", {})
    repos = github.get("repos", [])
    if github and not github.get("error") and isinstance(repos, list):
        for repo in repos:
            repo_name = repo.get("repo") or "unknown"
            # Stale PRs (open > stale_pr_days threshold from config)
            open_prs = repo.get("open_prs", [])
            if isinstance(open_prs, list):
                for pr in open_prs:
                    created = pr.get("createdAt", "")
                    if created:
                        try:
                            created_dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                            days_open = (datetime.now(timezone.utc) - created_dt).days
                            if days_open > stale_threshold:
                                text = f"Review stale PR #{pr.get('number') or ''} on {repo_name} (open {days_open} days)"
                                if text not in seen:
                                    seen.add(text)
                                    items.append(text)
                        except (ValueError, TypeError):
                            pass

            # Failing CI
            ci_runs = repo.get("ci_runs", [])
            if isinstance(ci_runs, list):
                for run in ci_runs:
                    if (run.get("conclusion") or "") == "failure":
                        text = f"Fix failing CI on {repo_name} ({run.get('name') or 'unknown'})"
                        if text not in seen:
                            seen.add(text)
                            items.append(text)

            # Open issues — only flag recently created ones (within lookback_days)
            open_issues = repo.get("open_issues", [])
            if isinstance(open_issues, list):
                flagged_issues = 0
                for issue in open_issues:
                    if flagged_issues >= max_issues_per_repo:
                        break
                    created = issue.get("createdAt", "")
                    if created:
                        try:
                            created_dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                            days_since = (datetime.now(timezone.utc) - created_dt).days
                            if days_since <= lookback_days:
                                title = (issue.get("title") or "")[:40]
                                text = f"Address open issue #{issue.get('number') or ''} on {repo_name}: {title}"
                                if text not in seen:
                                    seen.add(text)
                                    items.append(text)
                                    flagged_issues += 1
                        except (ValueError, TypeError):
                            pass

    # Security-related updates
    security = data.get("security", {})
    alerts = security.get("alerts", [])
    if security and not security.get("error") and isinstance(alerts, list):
        for alert in alerts[:5]:
            sev = alert.get("severity") or ""
            if sev in ("CRITICAL", "HIGH"):
                text = f"Update {alert.get('product') or ''} — {alert.get('cve_id') or ''} ({sev})"
                if text not in seen:
                    seen.add(text)
                    items.append(text)

    return items[:max_action_items]


def main():
    parser = argparse.ArgumentParser(description="Daily Dev Pulse Formatter")
    parser.add_argument("--format", choices=["terminal", "md", "json"], default="terminal",
                        help="Output format")
    args = parser.parse_args()

    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Error: Invalid JSON input — {e}", file=sys.stderr)
        sys.exit(1)

    if args.format == "terminal":
        print(format_terminal(data))
    elif args.format == "md":
        print(format_markdown(data))
    elif args.format == "json":
        print(format_json(data))


if __name__ == "__main__":
    main()