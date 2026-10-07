---
name: lab-report
description: Write, update or rebuild the LaTeX lab report (звіт) for a lab of the IASA «Обробка надвеликих масивів даних» course in this repo — labs/NNN-name/report/report.tex compiled to report.pdf in KPI formatting — from the lab's task.pdf requirements and the results of its executed draft.ipynb, with screenshots of notebook outputs as figures. Use this whenever the user asks for a lab report, звіт, the PDF to submit, to "write up" or "turn the notebook into the report", to regenerate report screenshots or rebuild the report after re-running a notebook, even if they don't mention LaTeX.
---

# Lab report

Turns a finished lab into the PDF the student submits. Each lab directory looks like this:

```
labs/<NNN-name>/
  task.pdf            # assignment: tasks + «Вимоги до звіту» (required report sections)
  draft.ipynb         # executed notebook: every command, query and result, with outputs saved
  report/
    report.tex        # the report (you write this)
    references.bib
    screenshots.toml  # which notebook outputs become figures
    assets/*.png      # screenshots, generated
    report.pdf        # built
```

Shared tooling (already in the repo, don't re-create it):
- `latex/iasa-lab.cls`: KPI formatting and the title page. Details in `references/latex.md`.
- `latex/build.sh`: builds in Docker (XeLaTeX, biber, real Times New Roman). Only Docker is needed.
- `labs/001-hadoop-and-hive/report/`: a complete worked example of everything below. Read it before writing a new report; it's the best guide to tone, depth and structure.

## Workflow

### 1. Read the requirements

Read `task.pdf` and find three parts: the tasks («Практичне завдання»), the required report sections («Вимоги до звіту»), and anything else (e.g. «Контрольні питання»).

The report's sections mirror «Вимоги до звіту» exactly. The examiner checks the report against that list, so a missing section costs marks and an extra one adds pages nobody asked for. In lab 1 the student removed an added section answering the review questions: those are asked orally at the defence, not written in the report. If a requirement can't be met with the available results, say so to the user instead of padding.

### 2. Collect the results from the notebook

```bash
uv run .claude/skills/lab-report/scripts/dump_notebook.py labs/<lab>/draft.ipynb > <scratch>/nb.txt
```

Check the header line: all code cells executed and `errors: 0`. Every number in the report comes from these outputs. If the notebook isn't fully executed, ask the user to run it rather than estimating anything: runs can take half an hour and need the Docker cluster, so it's their call.

Don't edit `draft.ipynb`. The user owns it, often has it open in VS Code (edits on disk get lost or conflict), and the report must describe exactly what they ran.

Note from the dump:
- **personal details**: the notebook's title cell usually has the student name and group;
- **SQL and commands** for listings: copy them verbatim. The user writes SQL in a specific style (clause per line, `WHERE 1=1`), and the report shows the code that actually ran. Replace notebook placeholders like `{table}` with the concrete value used in the result you show;
- **numbers**: counts, timings (prefer medians over single runs), bytes read, job counters;
- **observations worth a sentence**: anomalies in the data, surprising timings, anything the notebook's markdown explains.

### 3. Screenshots of notebook outputs

The report needs «екранні форми» of commands and results; screenshots of the notebook outputs serve that purpose and look like what the student ran. Write `report/screenshots.toml`:

```toml
width = 820                          # default; ~110 characters per line, long lines wrap

[shots.hdfs-ls]                      # -> assets/hdfs-ls.png
cells = ['hdfs("dfs", "-ls", "-h"']  # a source snippet that occurs in exactly one code cell
                                     # (several cells -> one image, stacked)

[shots.uo-preview]
cells = ["uo_table\n\nLIMIT 10"]     # multi-line snippet when no single line is unique
width = 1000                         # wide DataFrames: 1000 so text wraps instead of shrinking

[shots.wordcount-job]
cells = ['"jar", EXAMPLES_JAR']
max_height = 640                     # long logs: keep the meaningful top part
```

Snippets instead of cell indices keep the spec valid when cells are added or moved. Then run the bundled screenshot script (it uses the system Chromium, or Playwright's if none is installed):

```bash
uv run .claude/skills/lab-report/scripts/nb_screenshots.py labs/<lab>/draft.ipynb labs/<lab>/report/screenshots.toml labs/<lab>/report/assets
```

Look at a few PNGs: right content, nothing from neighbouring cells, long logs cut at a sensible place. Only outputs are captured, so put the SQL itself in listings: listings stay searchable and sharp at any zoom.

### 4. Write the report

Follow the section list from step 1. The skeleton lab 1 used for its requirements:

```
\maketitle, \tableofcontents
\anonsection{Мета роботи}            % from task.pdf
\section{Опис задачі та вхідних даних}   % tasks, environment, data source and structure
\section{Хід роботи}                 % one \subsection per task: listing -> screenshot -> what it shows
\section{Аналіз ...}                 % one per required analysis, with a summary table
\anonsection{Висновки}
\printbibliography[heading=bibintoc, title={Список використаних джерел}]
\anonsection{Додаток А. Програмний код}  % repo link and what each file does
\anonsection{Додаток Б. ...}         % e.g. a script the task asked for, via \lstinputlisting
```

Writing style:
- **Ukrainian**, academic but plain: short paragraphs, concrete numbers, no filler. Code, identifiers and comments inside listings stay in English.
- **Explain, don't just show.** For each result say what it means and why it came out that way, e.g. partitioning read 1,0 MB instead of 1,1 GB, but time barely changed because of ~20 s MapReduce overhead. The analysis sections and Висновки carry the marks.
- **Stay honest about negative results.** In lab 1 bucketing gave no speed-up on MapReduce; the report says so and explains why, rather than implying a gain.
- **Cite data sources** in `references.bib` (datasets, documentation) with `urldate`.

LaTeX specifics (class macros, tables, listings, math, numbers, cross-references, and the pitfalls that broke lab 1's build) are in `references/latex.md`. Read it before writing.

### 5. Build

```bash
latex/build.sh labs/<lab>/report/report.tex
```

Then check the log for errors, warnings and `Overfull` boxes (commands in `references/latex.md`). Fix every warning, not just errors: undefined references and overfull boxes are visible defects in the PDF.

### 6. Verify visually

```bash
uv run .claude/skills/lab-report/scripts/render_pages.py labs/<lab>/report/report.pdf <scratch>/pages
```

Look at every contact sheet, not just the first. Check: title page details, ЗМІСТ, figures readable and placed next to their text, tables within margins, numbering (`Лістинг Б.1` in appendices), no `TODO` or `??`, fonts limited to Times New Roman, Courier New and TeX Gyre Termes Math. A clean log doesn't guarantee a good-looking document.

### 7. Hand over

Tell the user what's in the report (page count, sections, figure/table/listing counts), the key numbers it reports, and anything they need to decide or fill in (group, department, what to commit). `report/build/` is git-ignored; whether to commit `report.pdf` is the user's choice.

## Updating an existing report

After the notebook is re-run, numbers change: regenerate screenshots (step 3), re-dump the notebook, and update every number in the text and tables, not just the figures. Search the `.tex` for the old values to catch them all. If the user edited `report.tex`, read it first and keep their changes.
