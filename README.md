# iasa-bigdata

Labs for «Обробка надвеликих масивів даних» (KPI, IASA). Each lab lives in `labs/<NNN-name>/`
as a uv workspace member with its notebook, infrastructure and report.

## Setup

```bash
uv sync    # shared .venv with every lab and the notebook tooling
```

## Reports

LaTeX reports are built in Docker (XeLaTeX, biber, Times New Roman), so only Docker is needed:

```bash
latex/build.sh labs/001-hadoop-and-hive/report/report.tex   # -> report.pdf next to the .tex
```

The first run builds the `iasa-latex` image (~3 min, ~1 GB). Shared formatting (KPI
requirements, title page) is in `latex/iasa-lab.cls`; a report sets only its own data:

```latex
\documentclass{iasa-lab}
\labnumber{1}
\topic{...}
\student{...}
\studentgroup{...}
```

Figures are screenshots of notebook outputs, listed per lab in `report/screenshots.toml`:

```bash
uv run .claude/skills/lab-report/scripts/nb_screenshots.py labs/001-hadoop-and-hive/draft.ipynb \
    labs/001-hadoop-and-hive/report/screenshots.toml labs/001-hadoop-and-hive/report/assets
```

It uses the system Chromium if installed (`sudo apt install chromium`), otherwise Playwright's
(`uv run --with playwright playwright install chromium`).

For Claude Code, the `lab-report` skill (`.claude/skills/lab-report/`) describes the whole
workflow: `task.pdf` + executed `draft.ipynb` → screenshots → `report.tex` → verified PDF.
