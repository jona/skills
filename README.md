# Claude Code Skills

A collection of skills that extend Claude Code with specialized knowledge and workflows.

## Skills

| Skill   | Description                                                  |
| ------- | ------------------------------------------------------------ |
| `seshi` | Export Claude Code sessions as readable markdown transcripts |

## Structure

Each skill lives in its own directory and contains a `SKILL.md` file that defines:

- **name** — identifier used to invoke the skill
- **description** — trigger conditions and use cases
- **instructions** — the workflow Claude follows when the skill is activated

Some skills also include scripts or additional reference files.

## Usage

Skills are loaded automatically by Claude Code when a user's request matches the skill's trigger description. You can also invoke them directly with `/<skill-name>`.

## Installation

Place skill directories in `~/.claude/skills/` and they'll be picked up automatically.
