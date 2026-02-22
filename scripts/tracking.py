#!/usr/bin/env python3
"""Weekly tracking updater for skills.sh metrics.

Writes only to a dedicated GitHub issue:
- one weekly comment with nested raw-output details
- one aggregated summary block in issue body
"""

from __future__ import annotations

import datetime as dt
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

SKILL_SOURCE = "erikhuizinga/concurrency-lock-vs-lockfree"
QUERIES = [
    "lock-free",
    "lockfree",
    "lock free",
    "lockless",
    "atomic",
    "mutex",
    "concurrency",
    "synchronization",
    "ABA",
    "memory ordering",
    "compare-and-swap",
    "CAS",
    "mutex vs lock-free",
    "ABA problem",
    "linearizability",
    "hazard pointers",
    "concurrency-lock-vs-lockfree",
    "erikhuizinga/concurrency-lock-vs-lockfree",
]
DEFAULT_SEARCH_LIMIT = 10
RAW_CHARS_LIMIT = 12000

SUMMARY_START = "<!-- tracking-summary:start -->"
SUMMARY_END = "<!-- tracking-summary:end -->"
JSON_START = "<!-- tracking-json:start -->"
JSON_END = "<!-- tracking-json:end -->"


def now_utc() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def week_key(instant: dt.datetime) -> str:
    year, week, _ = instant.isocalendar()
    return f"{year}-W{week:02d}"


def require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def gh_api(
    method: str,
    path: str,
    token: str,
    payload: dict[str, Any] | None = None,
    query: dict[str, Any] | None = None,
    allow_not_found: bool = False,
) -> Any:
    url = f"https://api.github.com{path}"
    if query:
        url += "?" + urllib.parse.urlencode(query, doseq=True)
    body = None
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "tracking-entity-updater",
    }
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        if allow_not_found and exc.code == 404:
            return None
        raise RuntimeError(f"GitHub API {method} {path} failed ({exc.code}): {raw[:800]}") from exc


def skills_search(query: str, limit: int) -> dict[str, Any]:
    params = urllib.parse.urlencode({"q": query, "limit": str(limit)})
    url = f"https://skills.sh/api/search?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": "tracking-entity-updater"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        text = resp.read().decode("utf-8")
        return json.loads(text)


def find_target_skill(search_payload: dict[str, Any]) -> tuple[int | None, dict[str, Any] | None]:
    skills = search_payload.get("skills", [])
    if not isinstance(skills, list):
        return None, None
    for idx, item in enumerate(skills, start=1):
        if not isinstance(item, dict):
            continue
        source = str(item.get("source", ""))
        skill_id = str(item.get("id", ""))
        if source == SKILL_SOURCE or skill_id.startswith(SKILL_SOURCE + "/"):
            return idx, item
    return None, None


def trim_raw(value: Any) -> str:
    text = json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True)
    if len(text) <= RAW_CHARS_LIMIT:
        return text
    return (
        text[: RAW_CHARS_LIMIT - 200]
        + "\n\n... [truncated]\n"
        + f"original_length={len(text)} chars, limit={RAW_CHARS_LIMIT}"
    )


def list_issue_comments(repo: str, issue_number: int, token: str) -> list[dict[str, Any]]:
    comments: list[dict[str, Any]] = []
    page = 1
    while True:
        batch = gh_api(
            "GET",
            f"/repos/{repo}/issues/{issue_number}/comments",
            token,
            query={"per_page": 100, "page": page},
        )
        if not isinstance(batch, list):
            raise RuntimeError("Unexpected issue comments payload")
        comments.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return comments


def extract_json_block(body: str) -> dict[str, Any] | None:
    pattern = re.compile(
        re.escape(JSON_START) + r"\s*(\{.*?\})\s*" + re.escape(JSON_END),
        re.DOTALL,
    )
    match = pattern.search(body)
    if not match:
        return None
    try:
        return json.loads(match.group(1))
    except json.JSONDecodeError:
        return None


def build_weekly_comment(run_payload: dict[str, Any], raw_map: dict[str, Any]) -> str:
    wk = run_payload["week_key"]
    run_url = ""
    server_url = os.getenv("GITHUB_SERVER_URL", "").strip()
    repository = os.getenv("GITHUB_REPOSITORY", "").strip()
    run_id = os.getenv("GITHUB_RUN_ID", "").strip()
    if server_url and repository and run_id:
        run_url = f"{server_url}/{repository}/actions/runs/{run_id}"

    lines: list[str] = []
    lines.append(f"<!-- tracking-run:start week={wk} -->")
    lines.append(f"### Weekly tracking run `{wk}`")
    lines.append(f"- Timestamp (UTC): `{run_payload['timestamp_utc']}`")
    lines.append(f"- Status: `{run_payload['status']}`")
    lines.append(f"- Target source: `{SKILL_SOURCE}`")
    if run_url:
        lines.append(f"- Workflow run: {run_url}")
    lines.append("")
    lines.append("| query | found | rank | installs |")
    lines.append("| --- | --- | --- | --- |")
    for row in run_payload["queries"]:
        rank = row["rank"] if row["rank"] is not None else "N/A"
        installs = row["installs"] if row["installs"] is not None else "N/A"
        found = "yes" if row["found"] else "no"
        lines.append(f"| `{row['query']}` | {found} | {rank} | {installs} |")
    lines.append("")
    lines.append("<details>")
    lines.append("<summary>Raw outputs (nested)</summary>")
    lines.append("")
    for query in QUERIES:
        lines.append("<details>")
        lines.append(f"<summary>{query}</summary>")
        lines.append("")
        lines.append("```json")
        lines.append(trim_raw(raw_map.get(query, {"error": "missing raw output"})))
        lines.append("```")
        lines.append("")
        lines.append("</details>")
        lines.append("")
    lines.append("</details>")
    lines.append("")
    lines.append(JSON_START)
    lines.append(json.dumps(run_payload, indent=2, sort_keys=True))
    lines.append(JSON_END)
    lines.append("<!-- tracking-run:end -->")
    return "\n".join(lines)


def build_aggregate_summary(run_entries: list[dict[str, Any]]) -> str:
    if not run_entries:
        return "No tracking runs found yet."

    run_entries.sort(key=lambda x: x["payload"].get("timestamp_utc", ""))
    latest = run_entries[-1]
    latest_payload = latest["payload"]

    latest_query_map = {row["query"]: row for row in latest_payload.get("queries", [])}
    recent = run_entries[-4:]
    earliest_recent = recent[0]["payload"] if recent else latest_payload
    earliest_query_map = {row["query"]: row for row in earliest_recent.get("queries", [])}

    lines: list[str] = []
    lines.append("### Aggregated tracking view")
    lines.append(f"- Last updated (UTC): `{now_utc().isoformat(timespec='seconds')}`")
    lines.append(f"- Latest run week: `{latest_payload.get('week_key', 'unknown')}`")
    lines.append(f"- Latest run status: `{latest_payload.get('status', 'unknown')}`")
    lines.append("")
    lines.append("#### Latest query snapshot")
    lines.append("")
    lines.append("| query | found | rank | installs | note |")
    lines.append("| --- | --- | --- | --- | --- |")
    for query in QUERIES:
        row = latest_query_map.get(query, {})
        found = "yes" if row.get("found") else "no"
        rank = row.get("rank")
        installs = row.get("installs")
        note = "error" if row.get("error") else ("not found in top N" if not row.get("found") else "ok")
        lines.append(
            f"| `{query}` | {found} | {rank if rank is not None else 'N/A'} | "
            f"{installs if installs is not None else 'N/A'} | {note} |"
        )
    lines.append("")
    lines.append("#### 4-week trend")
    lines.append("")
    lines.append("| query | rank delta | installs delta |")
    lines.append("| --- | --- | --- |")
    for query in QUERIES:
        early = earliest_query_map.get(query, {})
        late = latest_query_map.get(query, {})
        early_rank = early.get("rank")
        late_rank = late.get("rank")
        early_installs = early.get("installs")
        late_installs = late.get("installs")
        if isinstance(early_rank, int) and isinstance(late_rank, int):
            rank_delta = late_rank - early_rank
            rank_text = f"{rank_delta:+d}"
        else:
            rank_text = "n/a"
        if isinstance(early_installs, int) and isinstance(late_installs, int):
            inst_delta = late_installs - early_installs
            inst_text = f"{inst_delta:+d}"
        else:
            inst_text = "n/a"
        lines.append(f"| `{query}` | {rank_text} | {inst_text} |")
    lines.append("")
    lines.append("#### Recent runs")
    lines.append("")
    lines.append("| week | status | timestamp | comment |")
    lines.append("| --- | --- | --- | --- |")
    for entry in reversed(run_entries[-12:]):
        payload = entry["payload"]
        week = payload.get("week_key", "unknown")
        status = payload.get("status", "unknown")
        timestamp = payload.get("timestamp_utc", "unknown")
        comment_url = entry.get("comment_url", "")
        comment_md = f"[link]({comment_url})" if comment_url else "n/a"
        lines.append(f"| `{week}` | {status} | `{timestamp}` | {comment_md} |")

    latest_errors = latest_payload.get("errors", [])
    missing = [q["query"] for q in latest_payload.get("queries", []) if not q.get("found")]
    lines.append("")
    lines.append("#### Warnings")
    lines.append("")
    if latest_errors:
        lines.append(f"- Latest run had `{len(latest_errors)}` query/API error(s).")
    if missing:
        lines.append("- Not found in top-N for: " + ", ".join(f"`{q}`" for q in missing))
    if not latest_errors and not missing:
        lines.append("- None.")

    return "\n".join(lines)


def upsert_summary_block(issue_body: str, summary: str) -> str:
    block = f"{SUMMARY_START}\n{summary}\n{SUMMARY_END}"
    pattern = re.compile(re.escape(SUMMARY_START) + r".*?" + re.escape(SUMMARY_END), re.DOTALL)
    if pattern.search(issue_body):
        return pattern.sub(block, issue_body)
    suffix = "\n\n" if issue_body and not issue_body.endswith("\n") else "\n"
    return issue_body + suffix + block + "\n"


def write_step_summary(repo: str, issue_number: int, run_payload: dict[str, Any]) -> None:
    path = os.getenv("GITHUB_STEP_SUMMARY", "").strip()
    if not path:
        return
    lines = [
        "## Tracking run",
        f"- Repository: `{repo}`",
        f"- Issue: #{issue_number}",
        f"- Week: `{run_payload['week_key']}`",
        f"- Status: `{run_payload['status']}`",
        f"- Timestamp (UTC): `{run_payload['timestamp_utc']}`",
    ]
    with open(path, "a", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def main() -> int:
    token = require_env("GITHUB_TOKEN")
    repo = require_env("GITHUB_REPOSITORY")
    issue_number = int(require_env("TRACKING_ISSUE_NUMBER"))
    limit = int(os.getenv("TRACKING_SEARCH_LIMIT", str(DEFAULT_SEARCH_LIMIT)))

    instant = now_utc()
    wk = week_key(instant)

    raw_by_query: dict[str, Any] = {}
    query_rows: list[dict[str, Any]] = []
    errors: list[str] = []

    for query in QUERIES:
        try:
            payload = skills_search(query, limit)
            raw_by_query[query] = payload
            rank, target = find_target_skill(payload)
            row = {
                "query": query,
                "found": rank is not None,
                "rank": rank,
                "installs": int(target.get("installs")) if isinstance(target, dict) and str(target.get("installs", "")).isdigit() else (target.get("installs") if isinstance(target, dict) else None),
                "skill_id": target.get("id") if isinstance(target, dict) else None,
                "source": target.get("source") if isinstance(target, dict) else None,
                "error": None,
            }
            query_rows.append(row)
        except Exception as exc:  # noqa: BLE001
            err = f"{query}: {exc}"
            errors.append(err)
            raw_by_query[query] = {"error": str(exc)}
            query_rows.append(
                {
                    "query": query,
                    "found": False,
                    "rank": None,
                    "installs": None,
                    "skill_id": None,
                    "source": None,
                    "error": str(exc),
                }
            )

    repo_data = gh_api("GET", f"/repos/{repo}", token)
    release = gh_api("GET", f"/repos/{repo}/releases/tags/v0.1.0", token, allow_not_found=True)
    repo_stats = {
        "stars": repo_data.get("stargazers_count"),
        "forks": repo_data.get("forks_count"),
        "watchers": repo_data.get("subscribers_count"),
        "release_v0_1_0": {
            "exists": release is not None,
            "url": release.get("html_url") if isinstance(release, dict) else None,
            "published_at": release.get("published_at") if isinstance(release, dict) else None,
        },
    }

    run_payload = {
        "schema_version": "tracking.v1",
        "timestamp_utc": instant.isoformat(timespec="seconds"),
        "week_key": wk,
        "status": "partial" if errors else "success",
        "skill_source": SKILL_SOURCE,
        "search_limit": limit,
        "queries": query_rows,
        "errors": errors,
        "repo_stats": repo_stats,
    }

    comments = list_issue_comments(repo, issue_number, token)
    week_marker = f"<!-- tracking-run:start week={wk} -->"
    existing_week_comment = next((c for c in comments if week_marker in str(c.get("body", ""))), None)
    weekly_body = build_weekly_comment(run_payload, raw_by_query)

    if existing_week_comment:
        gh_api(
            "PATCH",
            f"/repos/{repo}/issues/comments/{existing_week_comment['id']}",
            token,
            payload={"body": weekly_body},
        )
    else:
        gh_api(
            "POST",
            f"/repos/{repo}/issues/{issue_number}/comments",
            token,
            payload={"body": weekly_body},
        )

    comments = list_issue_comments(repo, issue_number, token)
    run_entries: list[dict[str, Any]] = []
    for comment in comments:
        body = str(comment.get("body", ""))
        payload = extract_json_block(body)
        if not payload:
            continue
        run_entries.append(
            {
                "payload": payload,
                "comment_id": comment.get("id"),
                "comment_url": comment.get("html_url"),
            }
        )

    summary = build_aggregate_summary(run_entries)
    issue = gh_api("GET", f"/repos/{repo}/issues/{issue_number}", token)
    current_body = str(issue.get("body", ""))
    next_body = upsert_summary_block(current_body, summary)
    if next_body != current_body:
        gh_api("PATCH", f"/repos/{repo}/issues/{issue_number}", token, payload={"body": next_body})

    write_step_summary(repo, issue_number, run_payload)
    print(f"tracking updated: issue #{issue_number} ({run_payload['status']})")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"fatal: {exc}", file=sys.stderr)
        raise SystemExit(1)
