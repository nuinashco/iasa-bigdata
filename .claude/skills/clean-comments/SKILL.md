---
name: clean-comments
description: Review and clean up code comments and docstrings without changing behaviour — delete comments that restate the code, rewrite vague or outdated ones into the why, keep workarounds, warnings and tool directives, and suggest missing ones — then prove with a checker that only comments changed. Use whenever the user asks to clean, refactor, review, trim or strip comments or docstrings, says comments "repeat the code" or are noisy, or asks to apply the project's comment conventions to files, a diff or a branch, even if they don't use the word "refactor".
---

# Clean comments

A comment earns its place by saying what the code can't: why it's written this way, a constraint, a workaround, a warning, units or invariants. Comments that restate the code cost reading time and drift out of date; a comment that contradicts the code is worse than none (PEP 8). This skill applies that standard to existing code, changing **only comments and docstrings**.

The full rule set with sources, the list of comments that must never be touched, per-language notes and before/after examples are in `references/rules.md`. Read it before the first edit; this file is the workflow.

## Workflow

### 1. Scope

Work on what the user names: files, directories, a diff, a branch. If they name nothing, use the uncommitted changes (`git status`) and say so. Don't sweep the whole repository without asking: a repo-wide comment diff is hard to review and mixes into unrelated commits.

If files in scope are open in an editor (notebooks especially), edits on disk can conflict with unsaved editor state; mention it before writing.

### 2. Learn the project's conventions first

Existing conventions beat general rules: a consistent codebase reads better than one following a style guide piecemeal. Check:
- `CLAUDE.md`, `CONTRIBUTING.md` and saved memories for comment rules (language of comments, what may be commented);
- linter config (`pyproject.toml`, `ruff.toml`, `.eslintrc`): pydocstyle / ruff `D` rules mean docstrings are required, so improve them instead of deleting;
- the docstring style already used (Google, NumPy, Sphinx) and the mood (imperative vs descriptive): match it, don't convert.

### 3. Decide per comment

Read each comment together with the code around it, then classify it with the tables in `references/rules.md` §2:
- **DELETE**: restates the code or the name, commented-out code, journal entries, bylines, stale TODOs, closing-brace and banner noise.
- **REWRITE**: says *what* where a *why* exists, contradicts the code, too long, unclear what it refers to, malformed docstring or TODO. Often only part of a comment is noise: trim to the useful part.
- **KEEP**: intent and decisions, warnings, workarounds, unidiomatic code someone might "fix", references and credits, units/invariants, cross-file couplings, valid TODOs.
- **ADD**: public non-trivial APIs without a docstring, magic numbers, hidden couplings, workarounds. Add only what you can establish from the code, git history or an issue; **never invent a rationale**. When the reason isn't knowable, list the spot in the report instead of guessing.

Never touch machine-read or legal comments: shebangs, encoding lines, licence/SPDX headers, linter and type-checker directives, PEP 723 `# /// script` blocks, Dockerfile parser directives, doctests, generated-file markers (full list: `references/rules.md` §3). When a comment looks like a directive (`tool: …`, `pragma`, `key=value`), treat it as one.

If a comment contradicts the code and it's unclear which is wrong, don't pick one: report it. That's a possible bug, not a comment problem.

### 4. Edit comments only

Behaviour must not change, so a comment pass never renames, reorders or reformats code, even when a rename would make a comment unnecessary. Note such refactors as suggestions in the report instead.

- Keep each file's existing comment language, unless the project's conventions say otherwise.
- Notebooks: edit code-cell sources only (with `nbformat`, preserving outputs and metadata); markdown cells are prose, not comments.
- Don't leave behind empty lines where a deleted comment used to be, unless they separate logical blocks.

### 5. Verify that only comments changed

```bash
uv run .claude/skills/clean-comments/scripts/check_comment_only.py --only <files or dirs in scope>
```

It compares the working tree with `HEAD` (or `--ref <rev>`): Python files and notebook code cells by AST with docstrings removed, other files line by line with comments stripped. Any `FAIL` means code changed: find and revert that part before reporting. For files the checker can't classify ("unknown file type"), review the diff by eye.

### 6. Report

Give the user a short summary they can review:
- counts per action (deleted, rewritten, kept as-is is implied, added) and per file;
- every **rewrite and addition** quoted before → after, since those carry judgement;
- open items you didn't change: contradictions that may be bugs, places that need a reason only the author knows, suggested renames;
- the checker's result.

Don't stage or commit unless asked.
