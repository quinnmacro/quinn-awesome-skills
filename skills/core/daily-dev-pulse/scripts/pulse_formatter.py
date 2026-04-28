"""Pulse formatter for Daily Dev Pulse.

Takes combined JSON data and produces formatted output in terminal, markdown, or JSON mode.
"""

import argparse
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
    BOX_TOP = "╔"
    BOX_BOT = "╚"
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
    lines.append(f"{Colors.BOX_TOP}{Colors.BOX_HORIZ * width}{Colors.BOX_BOT}")
    lines.append(f"{Colors.BOX_SIDE}{Colors.BOLD}{Colors.CYAN}   🌅 DAILY DEV PULSE — {today}{Colors.RESET}{' ' * (width - 28)}{Colors.BOX_SIDE}")
    lines.append(f"{Colors.BOX_BOT}{Colors.BOX_HORIZ * width}{Colors.BOX_BOT}")
    lines.append("")

    # GitHub Activity
    github = data.get("github", {})
    if github and not github.get("error"):
        repos = github.get("repos", [])
        if repos:
            lines.append(f"{Colors.BOLD}{Colors.BLUE}📊 GitHub Activity (Last {data.get('github', {}).get('lookback_days', 7)} Days){Colors.RESET}")
            max_commits = max(r.get("commit_count", 0) for r in repos) if repos else 1
            for repo in repos:
                name = repo["repo"].split("/")[-1]
                count = repo.get("commit_count", 0)
                bar = ascii_bar(count, max(max_commits, 1), 20)
                lines.append(f"  {Colors.GREEN}{name:20s}{Colors.RESET} {bar} {Colors.BOLD}{count}{Colors.RESET} commits")

            # CI Status
            lines.append("")
            lines.append(f"{Colors.BOLD}{Colors.BLUE}🔄 CI Status{Colors.RESET}")
            for repo in repos:
                name = repo["repo"].split("/")[-1]
                ci_runs = repo.get("ci_runs", [])
                if ci_runs:
                    latest = ci_runs[0] if ci_runs else {}
                    status = latest.get("status", "unknown")
                    conclusion = latest.get("conclusion", "unknown")
                    emoji = CI_EMOJI.get(conclusion, CI_EMOJI.get(status, CI_EMOJI["unknown"]))
                    lines.append(f"  {emoji} {name}: {conclusion} ({latest.get('name', 'unknown')})")
            lines.append("")

    # GitHub error
    if github.get("error"):
        lines.append(f"{Colors.YELLOW}⚠️ GitHub: {github['error']}{Colors.RESET}")
        lines.append("")

    # Open PRs & Issues
    if github and not github.get("error"):
        repos = github.get("repos", [])
        has_prs = any(r.get("open_prs") for r in repos)
        has_issues = any(r.get("open_issues") for r in repos)

        if has_prs or has_issues:
            lines.append(f"{Colors.BOLD}{Colors.BLUE}🔍 Open PRs & Issues{Colors.RESET}")
            lines.append(f"  ┌{'─' * 30}┬{'─' * 8}┬{'─' * 30}┐")
            lines.append(f"  │{'Repo':^30}│{'Type':^8}│{'Title':^30}│")
            lines.append(f"  ├{'─' * 30}┼{'─' * 8}┼{'─' * 30}┤")
            for repo in repos:
                name = repo["repo"].split("/")[-1]
                for pr in repo.get("open_prs", [])[:5]:
                    title = (pr.get("title", "") or "")[:28]
                    lines.append(f"  │{name:^30}│{'PR':^8}│{title:^30}│")
                for issue in repo.get("open_issues", [])[:5]:
                    title = (issue.get("title", "") or "")[:28]
                    lines.append(f"  │{name:^30}│{'Issue':^8}│{title:^30}│")
            lines.append(f"  └{'─' * 30}┴{'─' * 8}┴{'─' * 30}┘")
            lines.append("")

    # Security Alerts
    security = data.get("security", {})
    if security and not security.get("error"):
        alerts = security.get("alerts", [])
        if alerts:
            lines.append(f"{Colors.BOLD}{Colors.RED}🛡️ Security Alerts{Colors.RESET}")
            for alert in alerts[:8]:
                sev = alert.get("severity", "unknown")
                emoji = SEVERITY_EMOJI.get(sev, SEVERITY_EMOJI["unknown"])
                cve_id = alert.get("cve_id", "")
                product = alert.get("product", "")
                desc = (alert.get("description", "") or "")[:60]
                lines.append(f"  {emoji} {cve_id} — {product} ({sev}): {desc}")
            lines.append("")

    # Package Updates
    packages = data.get("packages", {})
    if packages and not packages.get("error"):
        updates = packages.get("updates", [])
        if updates:
            lines.append(f"{Colors.BOLD}{Colors.BLUE}📦 Package Updates{Colors.RESET}")
            for pkg in updates:
                name = pkg.get("package", "")
                reg = pkg.get("registry", "")
                ver = pkg.get("latest_version", "unknown")
                lines.append(f"  {reg:4s} {Colors.GREEN}{name}{Colors.RESET} → {ver}")
            lines.append("")

    # News
    news = data.get("news", {})
    if news and not news.get("error"):
        headlines = news.get("headlines", [])
        if headlines:
            lines.append(f"{Colors.BOLD}{Colors.BLUE}📰 Trending Dev News{Colors.RESET}")
            for i, hl in enumerate(headlines[:10], 1):
                source = hl.get("source", "")
                title = (hl.get("title", "") or "")[:60]
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
        if repos:
            lines.append("## GitHub Activity")
            lines.append("")
            lines.append("| Repo | Commits | Latest CI |")
            lines.append("|------|---------|-----------|")
            for repo in repos:
                name = repo["repo"].split("/")[-1]
                count = repo.get("commit_count", 0)
                ci_runs = repo.get("ci_runs", [])
                ci_status = ci_runs[0].get("conclusion", "N/A") if ci_runs else "N/A"
                emoji = CI_EMOJI.get(ci_status, "❓")
                lines.append(f"| {name} | {count} | {emoji} {ci_status} |")
            lines.append("")

        # PRs
        all_prs = []
        for repo in (github.get("repos", [])):
            for pr in repo.get("open_prs", []):
                all_prs.append((repo["repo"], pr))
        if all_prs:
            lines.append("### Open PRs")
            lines.append("")
            for full_repo, pr in all_prs[:10]:
                lines.append(f"- **{full_repo}** #{pr.get('number', '')}: {pr.get('title', '')}")
            lines.append("")

        # Issues
        all_issues = []
        for repo in (github.get("repos", [])):
            for issue in repo.get("open_issues", []):
                all_issues.append((repo["repo"], issue))
        if all_issues:
            lines.append("### Open Issues")
            lines.append("")
            for full_repo, issue in all_issues[:10]:
                lines.append(f"- **{full_repo}** #{issue.get('number', '')}: {issue.get('title', '')}")
            lines.append("")

    # Security
    security = data.get("security", {})
    if security and not security.get("error"):
        alerts = security.get("alerts", [])
        if alerts:
            lines.append("## Security Alerts")
            lines.append("")
            lines.append("| CVE ID | Product | Severity | Description |")
            lines.append("|--------|---------|----------|-------------|")
            for alert in alerts[:10]:
                lines.append(f"| {alert.get('cve_id', '')} | {alert.get('product', '')} | {alert.get('severity', '')} | {(alert.get('description', '') or '')[:50]} |")
            lines.append("")

    # Packages
    packages = data.get("packages", {})
    if packages and not packages.get("error"):
        updates = packages.get("updates", [])
        if updates:
            lines.append("## Package Updates Available")
            lines.append("")
            lines.append("| Registry | Package | Latest Version |")
            lines.append("|----------|---------|----------------|")
            for pkg in updates:
                lines.append(f"| {pkg.get('registry', '')} | {pkg.get('package', '')} | {pkg.get('latest_version', '')} |")
            lines.append("")

    # News
    news = data.get("news", {})
    if news and not news.get("error"):
        headlines = news.get("headlines", [])
        if headlines:
            lines.append("## Trending Dev News")
            lines.append("")
            for i, hl in enumerate(headlines[:15], 1):
                source = hl.get("source", "")
                title = hl.get("title", "")
                url = hl.get("url", "")
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
    import copy
    result = copy.deepcopy(data)
    result["action_items"] = generate_action_items(data)
    return json.dumps(result, indent=2, ensure_ascii=False)


def generate_action_items(data):
    """Generate personalized action items from collected data."""
    items = []

    github = data.get("github", {})
    if github and not github.get("error"):
        for repo in github.get("repos", []):
            # Stale PRs (open > stale_pr_days threshold)
            for pr in repo.get("open_prs", []):
                created = pr.get("createdAt", "")
                if created:
                    try:
                        # GitHub returns ISO 8601 with Z suffix (UTC)
                        # Python 3.11+ handles Z in fromisoformat
                        created_dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                        days_open = (datetime.now(timezone.utc) - created_dt).days
                        if days_open > 3:
                            items.append(f"Review stale PR #{pr.get('number', '')} on {repo['repo']} (open {days_open} days)")
                    except (ValueError, TypeError):
                        pass

            # Failing CI
            for run in repo.get("ci_runs", []):
                if run.get("conclusion") == "failure":
                    items.append(f"Fix failing CI on {repo['repo']} ({run.get('name', 'unknown')})")

    # Security-related updates
    security = data.get("security", {})
    if security and not security.get("error"):
        for alert in security.get("alerts", [])[:5]:
            sev = alert.get("severity", "")
            if sev in ("CRITICAL", "HIGH"):
                items.append(f"Update {alert.get('product', '')} — {alert.get('cve_id', '')} ({sev})")

    return items[:10]


def main():
    parser = argparse.ArgumentParser(description="Daily Dev Pulse Formatter")
    parser.add_argument("--format", choices=["terminal", "md", "json"], default="terminal",
                        help="Output format")
    args = parser.parse_args()

    data = json.load(sys.stdin)

    if args.format == "terminal":
        print(format_terminal(data))
    elif args.format == "md":
        print(format_markdown(data))
    elif args.format == "json":
        print(format_json(data))


if __name__ == "__main__":
    main()