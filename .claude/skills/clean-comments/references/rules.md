# Comment and docstring rules

Compiled from PEP 8, PEP 257, the Google Python Style Guide (§3.8, §3.12), Google's code review guide, John Ousterhout (CS190 lecture notes, the APOSD/Clean Code debate), Robert C. Martin's *Clean Code* ch. 4, Ellen Spertus's "Best practices for writing code comments" (Stack Overflow blog) and Jeff Atwood. Rules marked [summary] come from secondary summaries of the books rather than the books themselves.

## Contents
1. Principles
2. Per-comment decisions: DELETE / REWRITE / KEEP / ADD
3. Never touch (machine-read and legal comments)
4. Docstrings
5. TODO, FIXME, commented-out code
6. Per-language notes
7. Before/after examples
8. Sources

## 1. Principles

1. **A comment says what the code can't**: why, intent, constraints, the design behind it. "Comments are for information that the code itself can't possibly contain, like the reasoning behind a decision" (Google review guide). "Code tells you how, comments tell you why" (Atwood).
2. **Never describe the code.** "Assume the person reading the code knows Python (though not what you're trying to do) better than you do" (Google §3.8.5).
3. **A wrong comment is worse than none.** "Comments that contradict the code are worse than no comments" (PEP 8).
4. **Fix the code before commenting it.** A good comment doesn't excuse unclear code; a better name often replaces a comment (Spertus #2–3, Atwood).
5. **Comments work at a different level from the code**: lower-level ones add *precision* (units, bounds, ownership, invariants), higher-level ones add *intuition* (rationale, the abstract model) (Ousterhout).
6. **Interfaces need documentation.** A signature can't state formats, ordering, side effects or errors; "without comments there is no way to have abstraction or modularity" (Ousterhout).

## 2. Per-comment decisions

### DELETE when the comment

| # | Condition | Why |
|---|---|---|
| D1 | Restates the code (`i += 1  # increment i`) | No information, extra upkeep (Spertus #1, Google §3.8.5) |
| D2 | Repeats the name it's attached to | Adds nothing beyond the name (Ousterhout [summary]) |
| D3 | Is commented-out code | Version control keeps history; dead code rots (Clean Code [summary]) |
| D4 | Is a journal/changelog entry ("2019-03-02 JS: fixed X") | Belongs in VCS (Clean Code [summary]) |
| D5 | Is a byline ("Added by Bob") that isn't a legal notice | `git blame` records it (Clean Code [summary]) |
| D6 | Marks a closing brace (`} // end if`) | Editors match braces (Clean Code [summary]) |
| D7 | Is a banner/position marker, unless the project uses them for navigation in long files | Noise (Clean Code [summary]) |
| D8 | Is cryptic or an in-joke | Confuses rather than clarifies (Spertus #4) |
| D9 | Is a TODO the code already resolves | Misleads (Google review guide) |
| D10 | Is a docstring that only repeats the name and signature, on private or trivial code | Google allows omitting it when "name and signature are informative enough" (§3.8.3) |
| D11 | Is vague mumbling ("weird stuff here") | If the quirk is real, rewrite it instead (R2) (Clean Code [summary]) |

### REWRITE when the comment

| # | Condition | Action |
|---|---|---|
| R1 | Contradicts the code | Fix it to match the code. If it's unclear which one is wrong, **flag it, don't guess** (PEP 8) |
| R2 | Says *what* when a *why* exists | Replace it with the reason or constraint (Atwood, Google) |
| R3 | Is too long, historical or off-topic | Cut to what a maintainer needs |
| R4 | Describes code that lives elsewhere | Move it next to that code, or turn it into a pointer (Ousterhout) |
| R5 | Has an unclear connection to the line it's on | Say what it refers to |
| R6 | Is a TODO without context | `TODO: <issue link> - <what>`; no personal names (Google §3.12) |
| R7 | Is a docstring in the wrong form (signature-like, unterminated summary, inconsistent mood) | Fix to PEP 257 / the file's convention (§4) |
| R8 | Is ungrammatical or an unclear fragment | Complete sentence, capitalised, in the project's comment language (PEP 8, Google §3.8.6) |

Part of a comment can be worth keeping while the rest restates the code: trim it to the useful part rather than deleting it whole.

### KEEP when the comment

| # | Condition |
|---|---|
| K1 | Is a legal, copyright or licence notice |
| K2 | Explains intent or a decision ("X over Y because …") |
| K3 | Warns about consequences ("not thread-safe", "takes minutes") |
| K4 | Explains unidiomatic code someone might "fix" (Spertus #5) |
| K5 | Explains a workaround or bug fix, ideally with an issue link (Spertus #8) |
| K6 | Credits copied code or points to a spec/RFC (Spertus #6–7) |
| K7 | Clarifies a regex, algorithm, units, ranges or invariants |
| K8 | Amplifies something that looks unimportant but matters |
| K9 | Notes a cross-file dependency ("if you change this, also update …") (Ousterhout) |
| K10 | Is a valid, actionable TODO |

### ADD a comment when

| # | Condition |
|---|---|
| A1 | A public, non-trivial module, class or function has no docstring (PEP 257, Google §3.8.3) |
| A2 | You'd have to explain it in code review: tricky logic, a magic number, a non-obvious reason (Google §3.8.5) |
| A3 | A variable's units, bounds or ownership aren't in its name (Ousterhout) |
| A4 | A long block needs a one-line summary of what it achieves |
| A5 | There's a hidden coupling to another file, service or config |
| A6 | A workaround or non-standard choice was made |

Be conservative with ADD in an automated pass: add only what can be established from the code, the commit history or an issue. **Never invent a rationale**; if the reason isn't knowable, list the spot for the user instead.

## 3. Never touch

Machine-read or legally required. Leave them byte-for-byte, including their position:

- **Interpreter and encoding:** shebang on line 1; `# -*- coding: … -*-` / `# vim: set fileencoding=…` on line 1–2; Emacs/Vim modelines.
- **Legal:** copyright/licence headers, `SPDX-License-Identifier:`, `SPDX-FileCopyrightText:`, attributions a licence requires.
- **Python tools:** `# noqa`, `# type: ignore[…]`, `# type:` comments, `# pyright:`, `# mypy:`, `# pragma: no cover`, `# fmt: off/on/skip`, `# isort: …`, `# ruff: noqa`, `# pylint: disable=…`, `# nosec`, `# nosemgrep`, `# pyre-ignore`, `# codespell:ignore`, `# doctest: +SKIP`. Doctest `>>>` blocks inside docstrings are executable tests.
- **PEP 723 inline metadata:** the `# /// script` … `# ///` block (TOML in comments).
- **JS/TS:** `eslint-disable…`, `@ts-ignore`, `@ts-expect-error`, `@ts-nocheck`, `/// <reference …/>`, `prettier-ignore`, `istanbul ignore`, `c8 ignore`, `biome-ignore`, `/*#__PURE__*/`, `webpackChunkName`, `@flow`, `//# sourceMappingURL=`, JSDoc type annotations in JSDoc-typed projects, `/*! … */` licence banners.
- **Shell:** `# shellcheck disable=…`, `# shellcheck shell=…`, `# shellcheck source=…`.
- **Dockerfile:** parser directives `# syntax=`, `# escape=`, `# check=`; they only work at the very top, before any comment or blank line, so never insert anything above them. A `#` inside an instruction is an argument; lines in a `RUN` heredoc are script.
- **YAML/compose:** `# yaml-language-server: $schema=…`, `# yamllint …`, `# renovate: …`, `# checkov:skip=…`, `# kics-scan …`.
- **SQL:** optimizer hints `/*+ … */`, MySQL versioned comments `/*!50003 … */`, `-- noqa`, `-- name:` (sqlc/yesql), migration markers (`-- migrate:up`, `-- +goose Up`, `-- changeset`, `-- liquibase formatted sql`).
- **Notebooks and generated code:** `# %%` / `# In[ ]:` cell markers, jupytext headers, cell magics on line 1, `# Code generated … DO NOT EDIT.`, `@generated`, `# region` / `# endregion` if the project uses them.
- **Default:** anything shaped like `tool: …`, `pragma`, an `@`-annotation or `key=value` is treated as a directive and kept.

## 4. Docstrings

**When required.** Modules, exported classes and functions, public methods (PEP 257). Google: public API, non-trivial size, or non-obvious logic; may be omitted when "name and signature are informative enough". Test classes/methods and `@override` methods are exempt unless they refine the contract.

**Content.** Enough to call the function "without reading its code" (Google): what it does, arguments, return value, side effects, exceptions, restrictions (PEP 257). Summary line ≤ 80 characters ending in a period, then a blank line, then details. Google sections `Args:` / `Returns:` / `Yields:` / `Raises:`; types only where there are no annotations. Classes say what an instance represents (not that it's a class); `@property` docstrings read like attributes ("The X."). A script's module docstring is its usage message.

**Mood.** PEP 257: imperative ("Return the path."); Google allows descriptive too, consistently per file. Follow the file's existing convention. Never repeat the signature.

**Interface vs implementation.** Docstrings describe what and why for callers, with no implementation detail; implementation comments say what a block achieves and why (Ousterhout [summary]).

**Drop or shrink a docstring** when it paraphrases the name, the function is private or trivial, and it adds no constraint, unit, side effect or error. If the project's linter requires docstrings (pydocstyle, ruff `D` rules), improve it instead of deleting it.

**Formatting.** `"""` triple double quotes; a one-liner closes on its line; a multi-line docstring's closing `"""` is on its own line. Inline comments: at least two spaces before `#`, one after; block comments indented with the code, paragraphs separated by a bare `#` (PEP 8).

## 5. TODO, FIXME, commented-out code

- Format: `# TODO: <link to issue> - <description>`; avoid personal names (Google §3.12).
- TODOs are legitimate for known gaps (Spertus #9). An automated pass normalises their format but **doesn't delete unresolved ones**; it removes only those the code visibly resolves.
- Commented-out code: delete, unless it's labelled as an alternative with a reason ("Uncomment to …") or is example usage inside a docstring. When unsure, ask.

## 6. Per-language notes

- **Python:** PEP 8/257 and Google rules. Keep the project's docstring style (Google, NumPy or Sphinx); don't convert between them.
- **Shell:** the header comment (usage, required env vars, side effects) is the script's docstring. Comment non-obvious flags (`set -euo pipefail`, `IFS=`), quoting tricks, exit-code assumptions.
- **Dockerfile:** directives first (§3); comments on their own lines. Explain pinned versions, layer ordering or cache-busting, non-obvious `--platform` or user choices. Don't narrate `COPY . .`.
- **YAML / docker-compose:** comments are the only documentation of config: explain non-default ports, healthcheck timings, memory limits, why one service depends on another. Delete comments that restate the key (`# image` above `image:`).
- **SQL:** `--` for short notes, `/* */` for headers. Explain business rules behind filters, join-cardinality assumptions, magic constants.
- **JS/TS:** JSDoc/TSDoc `/** */` on exported APIs; in TS don't repeat types in `@param {T}`. Linter directives should carry a reason (`// eslint-disable-next-line no-await-in-loop -- sequential by design`).
- **Jupyter code cells:** prose belongs in markdown cells, not long `#` blocks. Keep magics and their position. Edit cell sources only, never outputs or metadata.

## 7. Before/after examples

**Restating the code → delete**
```python
count += 1  # increment count        →   count += 1
```

**What → why**
```python
# Sleep for 2 seconds.                         # The metastore accepts connections ~2 s
time.sleep(2)                          →       # after the container reports healthy.
                                               time.sleep(2)
```

**Workaround → keep and sharpen**
```python
df = df.repartition(1)  # fix          →   # Spark writes one part-file per partition; the grader expects one CSV.
                                           df = df.repartition(1)
```

**Magic number → name it, comment only what the name can't say**
```python
if retries > 7:  # 7                   →   MAX_RETRIES = 7  # ~2 min in total with exponential backoff from 1 s.
                                           if retries > MAX_RETRIES:
```
(Renaming is a code change: suggest it, don't make it, in a comment-only pass.)

**Docstring paraphrasing the name**
```python
def load_edges(path):                  →   def load_edges(path: str) -> DataFrame:
    """Loads edges."""                          """Read the edge list as a (src, dst) DataFrame.

                                                Self-loops are dropped; duplicate edges are kept.
                                                """
```
If the function is private and obvious, delete the docstring instead.

**Misleading → match the code**
```python
# Returns None if the user is missing.          def get_user(uid):
def get_user(uid): ...  # raises KeyError  →        """Return the user with `uid`; raise KeyError if absent."""
```

**TODO → issue format**
```python
# TODO(ivan): fix later                →   # TODO: github.com/org/repo/issues/42 - Stream rows instead of collect().
```

**Commented-out code and journal → delete**
```python
# 2024-03-01 changed by Bob
# old_df = spark.read.csv(path)        →   df = spark.read.parquet(path)
df = spark.read.parquet(path)
```

**Docstring as signature → imperative summary**
```python
"""mean(xs) -> float"""                →   """Return the arithmetic mean of a non-empty sequence."""
```

**Dockerfile directive order**
```dockerfile
# Base image for lab 2                 →   # syntax=docker/dockerfile:1
# syntax=docker/dockerfile:1               # Base image for lab 2
```
(A directive below a comment is silently ignored.)

## 8. Sources

- Ellen Spertus, Best practices for writing code comments — https://stackoverflow.blog/2021/12/23/best-practices-for-writing-code-comments/
- PEP 8 — https://peps.python.org/pep-0008/ ; PEP 257 — https://peps.python.org/pep-0257/ ; PEP 723 — https://peps.python.org/pep-0723/
- Google Python Style Guide §3.8, §3.12 — https://google.github.io/styleguide/pyguide.html
- Google engineering practices, What to look for in a code review — https://google.github.io/eng-practices/review/reviewer/looking-for.html
- Linux kernel coding style §8 — https://www.kernel.org/doc/html/latest/process/coding-style.html
- Jeff Atwood, Code Tells You How, Comments Tell You Why — https://blog.codinghorror.com/code-tells-you-how-comments-tell-you-why/
- John Ousterhout, CS190 lecture notes on comments — https://web.stanford.edu/~ouster/cgi-bin/cs190-winter18/lecture.php?topic=comments
- Ousterhout & Martin, APOSD vs Clean Code — https://github.com/johnousterhout/aposd-vs-clean-code/blob/main/README.md
- Dockerfile reference, parser directives — https://docs.docker.com/reference/dockerfile/
- Summaries of *A Philosophy of Software Design* and *Clean Code* ch. 4 (Dan Lebrero; dev.to) for rules marked [summary]
