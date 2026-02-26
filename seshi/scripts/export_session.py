#!/usr/bin/env python3
"""Export a Claude Code session JSONL file to a readable markdown transcript.

Usage:
  export_session.py <input.jsonl> <output.md>
  export_session.py --list [search_term]       # List sessions, optionally filtered
  export_session.py --list-projects             # List all projects with session counts
"""

import json
import sys
import os
import re
from datetime import datetime
from pathlib import Path

SESSIONS_DIR = Path.home() / ".claude" / "projects"
DEFAULT_OUTPUT_DIR = Path.home() / ".claude" / "session-exports"


# ─── Listing helpers ───────────────────────────────────────────────────────────

def get_project_display_name(dirname):
    """Convert project directory name to readable name."""
    name = dirname
    home_user = os.path.basename(os.path.expanduser("~"))
    name = re.sub(rf"^-Users-{re.escape(home_user)}-Code-", "", name)
    name = re.sub(rf"^-Users-{re.escape(home_user)}-", "~/", name)
    name = re.sub(rf"^-Users-{re.escape(home_user)}$", "~", name)
    return name


def get_first_human_message(jsonl_path):
    """Extract the first human message text from a session."""
    try:
        with open(jsonl_path) as f:
            for line in f:
                try:
                    d = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if d.get("type") != "user":
                    continue
                msg = d.get("message", {})
                content = msg.get("content", [])
                if not isinstance(content, list):
                    continue
                # Skip tool_result messages
                if any(isinstance(c, dict) and c.get("type") == "tool_result" for c in content):
                    continue
                for c in content:
                    if isinstance(c, dict) and c.get("type") == "text":
                        text = c.get("text", "")
                        if text.startswith("<") or text.startswith("[Request"):
                            continue
                        return text.strip()
    except Exception:
        pass
    return ""


def count_human_turns(jsonl_path):
    """Count the number of human turns in a session."""
    count = 0
    try:
        with open(jsonl_path) as f:
            for line in f:
                try:
                    d = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if d.get("type") != "user":
                    continue
                content = d.get("message", {}).get("content", [])
                if isinstance(content, list) and any(
                    isinstance(c, dict) and c.get("type") == "tool_result" for c in content
                ):
                    continue
                # Check for actual text content
                if isinstance(content, list):
                    for c in content:
                        if isinstance(c, dict) and c.get("type") == "text":
                            text = c.get("text", "")
                            if not text.startswith("<") and not text.startswith("[Request"):
                                count += 1
                                break
    except Exception:
        pass
    return count


def list_projects():
    """List all projects with session counts."""
    if not SESSIONS_DIR.exists():
        print("No sessions directory found.")
        return

    projects = []
    for d in sorted(SESSIONS_DIR.iterdir()):
        if not d.is_dir():
            continue
        sessions = list(d.glob("*.jsonl"))
        if sessions:
            total_size = sum(s.stat().st_size for s in sessions)
            projects.append((get_project_display_name(d.name), len(sessions), total_size, d.name))

    if not projects:
        print("No sessions found.")
        return

    print(f"{'Project':<40} {'Sessions':>8} {'Total Size':>12}")
    print("-" * 62)
    for name, count, size, _ in sorted(projects, key=lambda x: -x[2]):
        size_str = f"{size / (1024*1024):.1f}MB" if size > 1024*1024 else f"{size / 1024:.0f}KB"
        print(f"{name:<40} {count:>8} {size_str:>12}")


def list_sessions(search_term=None):
    """List sessions, optionally filtered by search term. Outputs JSON for agent consumption."""
    if not SESSIONS_DIR.exists():
        print("No sessions directory found.")
        return

    sessions = []
    for d in sorted(SESSIONS_DIR.iterdir()):
        if not d.is_dir():
            continue
        for s in d.glob("*.jsonl"):
            try:
                size = s.stat().st_size
                mtime = datetime.fromtimestamp(s.stat().st_mtime)
            except OSError:
                continue
            first_msg = get_first_human_message(str(s))
            if search_term and search_term.lower() not in first_msg.lower() and search_term.lower() not in get_project_display_name(d.name).lower():
                continue
            sessions.append({
                "path": str(s),
                "project": get_project_display_name(d.name),
                "project_dir": d.name,
                "session_id": s.stem,
                "size_bytes": size,
                "modified": mtime.isoformat(),
                "first_message": first_msg[:200],
            })

    # Sort by size descending (most substantial first)
    sessions.sort(key=lambda x: -x["size_bytes"])

    # Print as JSON for agent consumption, human-readable table to stderr
    print(json.dumps(sessions[:30], indent=2))

    # Also print human-readable summary to stderr
    print(f"\n--- Found {len(sessions)} sessions (showing top 30 by size) ---", file=sys.stderr)
    for i, s in enumerate(sessions[:30], 1):
        size_str = f"{s['size_bytes'] / (1024*1024):.1f}MB" if s['size_bytes'] > 1024*1024 else f"{s['size_bytes'] / 1024:.0f}KB"
        msg_preview = s['first_message'][:80].replace('\n', ' ')
        print(f"  {i:>2}. [{s['project']}] {size_str:>6}  {msg_preview}", file=sys.stderr)


# ─── Export logic ──────────────────────────────────────────────────────────────

def extract_text_from_content(content):
    """Extract readable text from message content."""
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""

    parts = []
    for block in content:
        if not isinstance(block, dict):
            continue

        btype = block.get("type", "")

        if btype == "text":
            text = block.get("text", "")
            if text.startswith("<ide_opened_file>") or text.startswith("<system-reminder>"):
                continue
            if text.startswith("[Request interrupted"):
                continue
            if text.strip():
                parts.append(text)

        elif btype == "tool_use":
            name = block.get("name", "unknown")
            inp = block.get("input", {})
            parts.append(format_tool_use(name, inp))

        elif btype == "tool_result":
            result_content = block.get("content", "")
            is_error = block.get("is_error", False)
            result_text = ""
            if isinstance(result_content, str):
                result_text = result_content
            elif isinstance(result_content, list):
                for rc in result_content:
                    if isinstance(rc, dict) and rc.get("type") == "text":
                        result_text += rc.get("text", "") + "\n"
            if result_text.strip():
                prefix = "**Error:**" if is_error else "**Result:**"
                truncated = truncate(result_text.strip(), 1500)
                parts.append(f"> {prefix}\n> ```\n> {indent_blockquote(truncated)}\n> ```")

        elif btype == "thinking":
            text = block.get("text", "")
            if text.strip():
                truncated = truncate(text.strip(), 800)
                parts.append(f"<details>\n<summary>Thinking...</summary>\n\n{truncated}\n\n</details>")

    return "\n\n".join(parts)


def format_tool_use(name, inp):
    """Format a tool call in a readable way."""
    if name == "Read":
        path = inp.get("file_path", "?")
        return f"**Read** `{shorten_path(path)}`"

    elif name == "Write":
        path = inp.get("file_path", "?")
        content = inp.get("content", "")
        preview = truncate(content, 600)
        return f"**Write** `{shorten_path(path)}`\n```\n{preview}\n```"

    elif name == "Edit":
        path = inp.get("file_path", "?")
        old = truncate(inp.get("old_string", ""), 200)
        new = truncate(inp.get("new_string", ""), 200)
        return f"**Edit** `{shorten_path(path)}`\n```diff\n- {old}\n+ {new}\n```"

    elif name == "Bash":
        cmd = inp.get("command", "?")
        desc = inp.get("description", "")
        label = f" — {desc}" if desc else ""
        return f"**Bash**{label}\n```bash\n{truncate(cmd, 300)}\n```"

    elif name == "Glob":
        pattern = inp.get("pattern", "?")
        return f"**Glob** `{pattern}`"

    elif name == "Grep":
        pattern = inp.get("pattern", "?")
        path = inp.get("path", ".")
        return f"**Grep** `{pattern}` in `{shorten_path(path)}`"

    elif name == "Task":
        desc = inp.get("description", "?")
        agent = inp.get("subagent_type", "?")
        prompt = truncate(inp.get("prompt", ""), 200)
        return f"**Subagent** ({agent}): {desc}\n> {prompt}"

    elif name == "ExitPlanMode":
        return "**Submitting plan for approval**"

    elif name in ("TodoWrite", "TaskCreate", "TaskUpdate", "TaskList"):
        return f"**{name}**"

    elif name == "WebFetch":
        url = inp.get("url", "?")
        return f"**WebFetch** `{url}`"

    elif name == "WebSearch":
        query = inp.get("query", "?")
        return f"**WebSearch** `{query}`"

    elif name == "AskUserQuestion":
        questions = inp.get("questions", [])
        if questions:
            q = questions[0].get("question", "?")
            return f"**Question:** {q}"
        return "**AskUserQuestion**"

    elif name == "NotebookEdit":
        path = inp.get("notebook_path", "?")
        return f"**NotebookEdit** `{shorten_path(path)}`"

    elif name == "Skill":
        skill = inp.get("skill", "?")
        return f"**Skill** /{skill}"

    else:
        return f"**{name}**"


def shorten_path(path):
    """Shorten absolute paths for readability."""
    home = os.path.expanduser("~")
    if path.startswith(home):
        path = "~" + path[len(home):]
    return path


def truncate(text, max_chars):
    """Truncate text with ellipsis."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n... (truncated)"


def indent_blockquote(text):
    """Add blockquote prefix to each line."""
    return "\n> ".join(text.split("\n"))


def convert_session(jsonl_path, output_path):
    """Convert a session JSONL to markdown. Returns (block_count, turn_count)."""
    messages = []

    with open(jsonl_path) as f:
        for line in f:
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue

            if d.get("type") not in ("user", "assistant"):
                continue

            msg = d.get("message", {})
            role = msg.get("role", "")
            content = msg.get("content", [])
            user_type = d.get("userType", "")
            timestamp = d.get("timestamp", "")

            messages.append({
                "role": role,
                "content": content,
                "user_type": user_type,
                "timestamp": timestamp,
            })

    # Merge consecutive same-role messages and build markdown
    merged = []
    for m in messages:
        text = extract_text_from_content(m["content"])
        if not text.strip():
            continue

        is_human = m["role"] == "user" and not any(
            isinstance(c, dict) and c.get("type") == "tool_result"
            for c in (m["content"] if isinstance(m["content"], list) else [])
        )

        is_tool_result = m["role"] == "user" and any(
            isinstance(c, dict) and c.get("type") == "tool_result"
            for c in (m["content"] if isinstance(m["content"], list) else [])
        )

        if is_human:
            merged.append(("human", text))
        elif m["role"] == "assistant":
            if merged and merged[-1][0] == "assistant":
                merged[-1] = ("assistant", merged[-1][1] + "\n\n" + text)
            else:
                merged.append(("assistant", text))
        elif is_tool_result:
            if merged and merged[-1][0] == "assistant":
                merged[-1] = ("assistant", merged[-1][1] + "\n\n" + text)
            else:
                merged.append(("assistant", text))

    # Extract project name from path
    project_dir = os.path.basename(os.path.dirname(jsonl_path))
    project_name = get_project_display_name(project_dir)
    session_id = os.path.basename(jsonl_path).replace(".jsonl", "")

    # Build markdown
    lines = []
    lines.append(f"# Session Transcript: {project_name}")
    lines.append(f"**Session ID:** `{session_id}`")
    lines.append(f"**Project:** `{project_name}`")
    lines.append("")
    lines.append("---")
    lines.append("")

    turn_num = 0
    for role, text in merged:
        if role == "human":
            turn_num += 1
            lines.append(f"## Human (Turn {turn_num})")
            lines.append("")
            lines.append(text)
            lines.append("")
            lines.append("---")
            lines.append("")
        elif role == "assistant":
            lines.append(f"### Claude")
            lines.append("")
            lines.append(text)
            lines.append("")
            lines.append("---")
            lines.append("")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write("\n".join(lines))

    return len(merged), turn_num


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage:")
        print(f"  {sys.argv[0]} <input.jsonl> <output.md>   Export a session")
        print(f"  {sys.argv[0]} --list [search]             List sessions")
        print(f"  {sys.argv[0]} --list-projects              List projects")
        sys.exit(1)

    if sys.argv[1] == "--list-projects":
        list_projects()
    elif sys.argv[1] == "--list":
        search = sys.argv[2] if len(sys.argv) > 2 else None
        list_sessions(search)
    else:
        if len(sys.argv) != 3:
            print(f"Usage: {sys.argv[0]} <input.jsonl> <output.md>")
            sys.exit(1)
        blocks, turns = convert_session(sys.argv[1], sys.argv[2])
        print(f"Exported {blocks} blocks ({turns} human turns) -> {sys.argv[2]}")
