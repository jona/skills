---
name: seshi
description: "Export Claude Code sessions as readable markdown transcripts. Use when the user says 'seshi', 'export session', 'export transcript', 'save session', 'session to markdown', or wants to convert a past Claude Code conversation into a shareable document."
---

# Export Session

Export Claude Code session JSONL files as clean, readable markdown transcripts.

## Script Location

`~/.claude/skills/seshi/scripts/export_session.py`

## Workflow

### 1. Understand what the user wants

Options:
- **Export a specific session** — user provides a session ID, project name, or search term
- **Browse and choose** — user wants to see available sessions and pick one
- **Export multiple sessions** — user wants batch export
- **List projects** — user wants an overview of all projects

### 2. Help the user find sessions

**List all projects:**
```bash
python3 ~/.claude/skills/seshi/scripts/export_session.py --list-projects
```

**List sessions (optionally filtered by keyword):**
```bash
python3 ~/.claude/skills/seshi/scripts/export_session.py --list
python3 ~/.claude/skills/seshi/scripts/export_session.py --list "search term"
```

The `--list` command outputs JSON to stdout with session metadata (path, project, size, first message preview). Use this to help the user choose.

When helping users pick sessions, consider these quality signals:
- **Size** — larger sessions typically indicate more substantial work
- **Human turns** — more turns suggest iterative problem-solving
- **First message** — reveals the topic and complexity

### 3. Export the session

```bash
python3 ~/.claude/skills/seshi/scripts/export_session.py \
  "<path-to-session.jsonl>" \
  "<output-path.md>"
```

**Default output directory:** `~/.claude/session-exports/`

Use a descriptive filename based on the session topic, e.g.:
- `changeblog-ui-prefers-reduced-motion.md`
- `api-auth-system-design.md`

### 4. Report results

After exporting, tell the user:
- Output file path and size
- Number of conversation blocks and human turns
- A brief description of what the session covers

## Transcript Format

The exported markdown includes:
- **Header** with session ID and project name
- **Human turns** labeled with turn numbers (`## Human (Turn N)`)
- **Claude responses** with tool calls formatted readably:
  - `Read`, `Write`, `Edit` — show file paths and diffs
  - `Bash` — show commands with descriptions
  - `Grep`, `Glob` — show search patterns
  - `Task` (subagents) — show agent type, description, and prompt
  - `WebFetch`, `WebSearch` — show URLs and queries
  - Tool results shown as blockquoted code blocks
  - Thinking blocks in collapsible `<details>` tags
- Consecutive assistant messages are merged into single blocks
- System messages, IDE events, and interrupts are filtered out
