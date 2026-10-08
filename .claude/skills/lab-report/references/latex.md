# LaTeX reference for lab reports

Read this when writing or fixing `report.tex`. The class is `latex/iasa-lab.cls`; open it if
something here seems out of date.

## Contents
- Class interface
- Figures, tables, listings
- Text conventions
- Pitfalls (each one cost a debugging round in lab 1)
- Build and verification

## Class interface

```latex
\documentclass{iasa-lab}
\addbibresource{references.bib}

\labnumber{2}
\topic{<тема з task.pdf>}
\student{Гавлицький Іван}
\studentgroup{КІ-61мп}
\variant{3: Німеччина -- Велика Британія}   % if the lab has variants; printed under the topic
% optional: \department{Кафедра ...}  \reportyear{2026}
% subject-wide defaults already set: \discipline, \teacher

\begin{document}
\maketitle        % KPI title page; the next page is numbered 2
\tableofcontents
\clearpage
...
\end{document}
```

- `\section` / `\subsection` / `\subsubsection`: numbered; section titles are capitalised automatically in the text and TOC, so write them in normal case.
- `\anonsection{Мета роботи}`: unnumbered section that still appears in the TOC (Мета роботи, Висновки, Додаток А. ...).
- Bibliography: `\printbibliography[heading=bibintoc, title={Список використаних джерел}]`, IEEE style, `\cite{key}`.

## Figures, tables, listings

**Screenshots**: `\addshot{file}{caption}{label}`. Files live in `report/assets/` (on the graphics path). The macro uses a fixed scale, so text in every screenshot comes out the same size (≈ 7 pt); oversized images shrink to fit the page width or 70 % of its height. Don't pick widths per figure.

**Other images** (diagrams): `\addimg{file}{fraction of \linewidth}{caption}{label}`. Diagrams rendered from Mermaid (`../assets/*.pdf`, see SKILL.md step 3b) are vector, but a wide left-to-right diagram scaled to the page width gets tiny text: zoom into its page and check the node labels are readable.

**Tables**: `table[H]` + `tabularx` with full borders (for tall tables see the float pitfall below). Use the `Y` column type (left-aligned `X`) for any text column: justified narrow cells leave large gaps between words. Numbers right-aligned (`r`).

```latex
\begin{table}[H]
  \caption{Час виконання COUNT(*), медіана трьох запусків}\label{tab:count}
  \begin{tabularx}{\textwidth}{|Y|r|r|}
    \hline
    Таблиця & Hive, с & PostgreSQL, с \\
    \hline
    UO & 28,18 & 0,15 \\
    \hline
  \end{tabularx}
\end{table}
```

Merged cells: `\multirow{3}{=}{text}` in a `Y`/`X` column, `\multirow{2}{*}{text}` in `l`.

**Listings**: `\begin{lstlisting}[language=HiveQL, caption={...}, label={lst:...}]`. Languages: `HiveQL` (Hive; handles backslash escapes like `"\""`), `SQL` (PostgreSQL), `bash`, `Python`. Whole files: `\lstinputlisting[language=Python, caption={...}]{../scripts/x.py}` (paths are relative to `report/`; only the repo is mounted in the build container).

Listings break across pages freely, so a short one can leave its caption and a line or two at the bottom of a page. Keep a listing that fits on one page in one piece with a minipage:

```latex
\noindent\begin{minipage}{\linewidth}
\begin{lstlisting}[language=SQL, caption={...}, label={lst:...}]
...
\end{lstlisting}
\end{minipage}
\medskip
```

Don't use `float=H` on a listing instead: with this class it fails at `\end{lstlisting}` (`Missing } inserted`, then cascading `Misplaced \noalign`). A `\lstnewenvironment` wrapper fails in this TeX Live too. Longer listings stay plain `lstlisting` and may break.

Captions read «Рисунок 2.3 – ...», «Таблиця 2.1 – ...», «Лістинг 2.4 – ...», numbered within sections. In appendices, renumber listings before the first one:

```latex
\setcounter{lstlisting}{0}
\renewcommand{\thelstlisting}{Б.\arabic{lstlisting}}
```

## Text conventions

- Cross-references in KPI style: `рис.~\ref{fig:x}`, `табл.~\ref{tab:x}`, `лістинг~\ref{lst:x}`, `(рис.~\ref{a},~\ref{b})`. Every figure, table and listing is referenced in the text before it appears.
- Numbers: thin-space thousands `1\,853\,363`, decimal comma `28,18`, unit after a tie: `28,18~с`, `1,1 ГБ`. Ranges with `--`: `28--37~с`. Dash in prose: ` -- `.
- Quotes: «...».
- Identifiers, paths, commands in running text: `\texttt{uo\_table}` (escape `_`, `#`, `%`, `&`). For backslashes or quotes use `\verb|"\""|`.
- Math symbols in math mode: `$\approx 20$~с`, `$25\,\% \pm 0{,}2\,\%$`, `$\bigl(\operatorname{hash}(\mathit{key}) \mathbin{\&} \texttt{Integer.MAX\_VALUE}\bigr) \bmod R$`. Math uses TeX Gyre Termes Math, so it matches Times New Roman; don't replace math with Unicode characters.

## Pitfalls (each one cost a debugging round in lab 1)

- **No `cleveref`.** Its Ukrainian names use 8-bit encoding commands that crash under XeLaTeX. Use the `рис.~\ref{}` style above.
- **No `amssymb`.** `unicode-math` already provides the symbols and the two conflict; `amsmath` is loaded by the class.
- **Listing strings break** with language `SQL` on HiveQL backslash escapes (spaces render as `␣`, keywords inside strings turn bold). Use `language=HiveQL` for Hive code.
- **`\contentsline` / TOC hooks** must come after `hyperref`; already handled in the class. Don't redefine TOC macros in the report.
- **Wide tables**: put them in `tabularx` with `Y` columns or shorten headers; never let them overflow (check the log for `Overfull \hbox`).
- **Floats**: use `[H]` (figures/tables right where they're described); the class's `\addshot` already does. Exception: a table taller than about a third of a page with `[H]` leaves a half-empty page before it, or overflows (`Overfull \vbox`). Give such tables `[!htb]`, and put `\FloatBarrier` (the class loads `placeins`) before `\anonsection{Висновки}` so a floated table can't drift into the conclusions.
- **Bibliography URLs** used to render spread out (`https : / / github . com`); the class now breaks URLs anywhere instead. If you see it again, check the `\biburl...` settings in the class.

## Build and verification

```bash
latex/build.sh labs/<lab>/report/report.tex      # -> report.pdf next to report.tex, aux in build/
grep -E "^\S+\.(tex|sty|cls):[0-9]+:|Warning|Overfull" labs/<lab>/report/build/report.log
uv run .claude/skills/lab-report/scripts/render_pages.py labs/<lab>/report/report.pdf <scratch>/pages
```

- The first build creates the `iasa-latex` Docker image (~3 min); later builds take seconds.
- A failing build exits non-zero; the real error is in `build/report.log` (search for `.tex:<line>:`).
- Expected fonts in the PDF: `TimesNewRoman*`, `CourierNew*`, `TeXGyreTermesMath`, plus `LiberationSans`/`DejaVuSans` if a Mermaid diagram PDF is included (they're embedded in the diagram, not used by the text). `CM*` fonts mean something left math mode setup (e.g. a package forced Computer Modern).
- Look at the contact sheets: title page, ЗМІСТ, every figure readable, no empty half-pages before big figures, tables inside margins. Use `--zoom N` (repeatable) to render just those pages readably, e.g. for small text; it skips the contact sheets, so it's quick.
