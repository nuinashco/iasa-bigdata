# Contributing

## Project layout

The repository is a [uv workspace](https://docs.astral.sh/uv/concepts/projects/workspaces/). Each lab in `labs/` is a workspace member with its own package and only the dependencies its code needs. Notebook tooling (`ipykernel`, `jupyterlab`) lives in the root `pyproject.toml`'s `dev` group.

```
.
├── pyproject.toml              # workspace root: depends on every lab, dev group
├── latex/                      # report toolchain shared by all labs
│   ├── iasa-lab.cls            # KPI formatting + title page
│   └── build.sh                # Dockerised XeLaTeX build
├── scripts/                    # repo-wide tools (render_mermaid.py)
├── .claude/skills/             # Claude Code skills: lab-report, clean-comments
└── labs/001-hadoop-and-hive/
    ├── pyproject.toml          # lab-001-hadoop-and-hive: package deps only
    ├── src/lab001/             # importable as `lab001`
    ├── infra/                  # docker-compose.yml + configs of the lab's cluster
    ├── scripts/                # data download and other one-off scripts
    ├── task.pdf                # assignment
    ├── draft.ipynb             # the lab, end to end
    ├── assets/                 # optional diagrams: *.mmd -> *.svg (notebook), *.pdf (report)
    ├── data/                   # downloaded datasets (git-ignored)
    └── report/                 # report.tex, references.bib, screenshots.toml, assets/
```

## Adding a new lab

```bash
uv init --lib --vcs none --no-readme --no-pin-python --author-from none \
    --name lab-002-<topic> labs/002-<topic>
mv labs/002-<topic>/src/lab_002_<topic> labs/002-<topic>/src/lab002
```

Set the import name in `labs/002-<topic>/pyproject.toml`:

```toml
[tool.uv.build-backend]
module-name = "lab002"
```

Then wire it up:

```bash
uv add lab-002-<topic>                       # make the root env include it
uv add --package lab-002-<topic> numpy ...   # the lab's own deps
```

`uv add lab-002-<topic>` also adds `{ workspace = true }` to `[tool.uv.sources]`. Without the root dependency, a plain `uv sync` removes the lab from `.venv`.

## Notebooks

- Name it `draft.ipynb` and keep it reproducible: "Run All" on a clean machine starts the infrastructure, downloads the data and runs every task. Steps are idempotent, so re-running is safe.
- Markdown cells are short and in Ukrainian; code and code comments are in English. Comments explain what isn't obvious from the code.
- SQL goes inline in cells, one clause per line:

  ```sql
  SELECT
      u.address,
      COUNT(*) AS pairs

  FROM
      uo_table AS u

  INNER JOIN
      fop_table AS f
      ON u.address = f.address

  WHERE 1=1
      AND u.stan = 'зареєстровано'

  GROUP BY u.address
  ```

- Reusable helpers (cluster commands, DB clients) go in the lab's `src/lab<NNN>/`, not in the notebook.
- Diagrams are Mermaid sources in `labs/<lab>/assets/*.mmd`. Render them with `uv run scripts/render_mermaid.py labs/<lab>/assets/*.mmd`, which writes an `.svg` (embed it in the notebook as an image: `![…](assets/x.svg)`) and a `.pdf` (used by the report). Commit the source and both renders together.
- The lab's `infra/docker-compose.yml` sets `name: lab<NNN>`. Every lab's compose file lives in a directory called `infra/`, so without an explicit name all labs share the project name `infra` and treat each other's containers as orphans.

## Reports

Each lab's report lives in `labs/<lab>/report/` and uses the shared class:

```latex
\documentclass{iasa-lab}
\labnumber{2}
\topic{...}
\student{...}
\studentgroup{...}
```

Figures are screenshots of notebook outputs, listed in `report/screenshots.toml` and regenerated with:

```bash
uv run .claude/skills/lab-report/scripts/nb_screenshots.py labs/<lab>/draft.ipynb \
    labs/<lab>/report/screenshots.toml labs/<lab>/report/assets
```

It uses the system Chromium if installed (`sudo apt install chromium`), otherwise Playwright's (`uv run --with playwright playwright install chromium`). Build the PDF with `latex/build.sh labs/<lab>/report/report.tex`.

With Claude Code, the `lab-report` skill (`.claude/skills/lab-report/SKILL.md`) runs the whole workflow, from `task.pdf` and the executed `draft.ipynb` to a verified PDF.

## Commits

Conventional style with an optional scope: `feat(latex): ...`, `fix(etl): ...`, `docs(lab1): ...`, `build: ...`. One lab per branch: `lab/<NNN>-<topic>`.
