% Lab report for "Обробка надвеликих масивів даних" (KPI, IASA), compiled with XeLaTeX.
% Formatting follows the KPI requirements used in the department's thesis template:
% 14pt Times New Roman, 1.5 spacing, 1.25cm indent, margins 3/1.5/2/2 cm, page number top right.
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{iasa-lab}[2026/10/07 KPI IASA lab report]

\LoadClass[14pt,a4paper,oneside]{extarticle}

% ------------------------------------------------------------------ fonts & language
\RequirePackage{fontspec}
\defaultfontfeatures{Ligatures=TeX}
\setmainfont{Times New Roman}
\setsansfont{Arial}
% TeXOff: keep `--`, quotes etc. literal in code (SQL comments would otherwise become dashes).
\setmonofont{Courier New}[Ligatures=TeXOff]
% polyglossia looks up these families for Cyrillic text instead of the main ones.
\newfontfamily\cyrillicfont{Times New Roman}
\newfontfamily\cyrillicfontsf{Arial}
\newfontfamily\cyrillicfonttt{Courier New}[Ligatures=TeXOff]

% Times-compatible math, so formulas match the text instead of falling back to Computer Modern.
% amsmath must precede unicode-math, which also supplies the amssymb symbols.
\RequirePackage{amsmath}
\RequirePackage{unicode-math}
\setmathfont{TeX Gyre Termes Math}

\RequirePackage{polyglossia}
\setdefaultlanguage{ukrainian}
\setotherlanguage{english}

% ------------------------------------------------------------------ page layout
\RequirePackage[left=3cm,right=1.5cm,top=2cm,bottom=2cm]{geometry}
\renewcommand{\baselinestretch}{1.5}
\setlength{\parindent}{1.25cm}
\RequirePackage{indentfirst}
\sloppy
\hyphenpenalty=1000
\clubpenalty=10000
\widowpenalty=10000
\raggedbottom

\RequirePackage{fancyhdr}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[R]{\thepage}
\setlength{\headheight}{17pt}
\renewcommand{\headrulewidth}{0pt}
\fancypagestyle{plain}{\fancyhf{}\fancyhead[R]{\thepage}}

% ------------------------------------------------------------------ headings
\RequirePackage{textcase}
\RequirePackage[explicit]{titlesec}
\titleformat{\section}[block]
  {\centering\bfseries\normalsize}{\thesection}{1em}{\MakeTextUppercase{#1}}
\titleformat{\subsection}[block]
  {\bfseries\normalsize}{\hspace*{\parindent}\thesubsection}{1em}{#1}
\titleformat{\subsubsection}[block]
  {\bfseries\normalsize}{\hspace*{\parindent}\thesubsubsection}{1em}{#1}
\titlespacing*{\section}{0pt}{\baselineskip}{\baselineskip}
\titlespacing*{\subsection}{0pt}{\baselineskip}{\baselineskip}
\titlespacing*{\subsubsection}{0pt}{\baselineskip}{\baselineskip}
\setcounter{secnumdepth}{3}

% Unnumbered section that still appears in the TOC (МЕТА РОБОТИ, ВИСНОВКИ, ...).
\newcommand{\anonsection}[1]{%
  \section*{#1}%
  \addcontentsline{toc}{section}{\texorpdfstring{\MakeTextUppercase{#1}}{#1}}%
}

% ------------------------------------------------------------------ table of contents
\RequirePackage{tocloft}
\renewcommand{\cfttoctitlefont}{\hfill\bfseries}
\renewcommand{\cftaftertoctitle}{\hfill}
\renewcommand{\cftsecfont}{}
\renewcommand{\cftsecpagefont}{}
\renewcommand{\cftsecleader}{\cftdotfill{\cftdotsep}}
\setcounter{tocdepth}{2}
\RequirePackage{etoolbox}
% polyglossia (re)sets captions when the language is selected, so patch them, not \contentsname.
\gappto\captionsukrainian{\renewcommand{\contentsname}{ЗМІСТ}}

% ------------------------------------------------------------------ lists
\RequirePackage{enumitem}
\setlist[itemize]{label=--, leftmargin=\parindent, labelsep=0.5em,
  labelwidth=\dimexpr\parindent-0.5em\relax, labelindent=0pt, itemindent=0pt, align=right,
  itemsep=0pt, topsep=0pt, parsep=0pt}
\setlist[enumerate]{label=\arabic*., leftmargin=\parindent, labelsep=0.5em,
  labelwidth=\dimexpr\parindent-0.5em\relax, labelindent=0pt, itemindent=0pt, align=right,
  itemsep=0pt, topsep=0pt, parsep=0pt}

% ------------------------------------------------------------------ figures, tables, code
\RequirePackage{graphicx}
\graphicspath{{assets/}}
\RequirePackage{float}
% \FloatBarrier: floats queued so far are placed before this point (e.g. before Висновки).
\RequirePackage{placeins}
\RequirePackage{array}
\RequirePackage{tabularx}
\RequirePackage{longtable}
\RequirePackage{multirow}
\RequirePackage{makecell}
\RequirePackage{booktabs}
\RequirePackage{adjustbox}
% Text column of tabularx, left-aligned: justified narrow cells leave large gaps between words.
\newcolumntype{Y}{>{\raggedright\arraybackslash}X}

\RequirePackage{listings}
\lstset{
  basicstyle=\footnotesize\ttfamily,
  columns=fullflexible,
  keepspaces=true,
  breaklines=true,
  tabsize=4,
  frame=single,
  captionpos=t,
  showstringspaces=false,
}
\renewcommand{\lstlistingname}{Лістинг}
% Listings' SQL escapes quotes by doubling them; HiveQL uses backslashes ('it\'s', "\"").
\lstdefinelanguage{HiveQL}{
  language=SQL,
  deletestring=[d]',
  deletestring=[d]",
  morestring=[b]',
  morestring=[b]",
}

% Numbering within sections: «Рисунок 2.3», «Таблиця 4.1», «Лістинг 2.1», (3.2).
\counterwithin{figure}{section}
\counterwithin{table}{section}
\counterwithin{equation}{section}
% listings creates its counter at \begin{document}; renumber only after that.
\AddToHook{begindocument/end}{\counterwithin{lstlisting}{section}}

\RequirePackage{caption}
\DeclareCaptionLabelSeparator{dash}{ -- }
\captionsetup{labelsep=dash, format=plain}
\captionsetup[figure]{justification=centering, name=Рисунок}
\captionsetup[table]{justification=raggedright, singlelinecheck=false, name=Таблиця}
\captionsetup[lstlisting]{justification=raggedright, singlelinecheck=false}

% \addshot{file}{caption}{label}: screenshot taken at 2x of an ~820 CSS px wide page. A fixed
% scale keeps screenshot text the same size across figures; larger shots shrink to fit the page.
\newcommand{\addshot}[3]{%
  \begin{figure}[H]
    \centering
    \adjustimage{scale=0.285, max width=\linewidth, max totalheight=0.7\textheight}{#1}
    \caption{#2}\label{#3}
  \end{figure}%
}

% \addimg{file}{width as fraction of \linewidth}{caption}{label}: figure placed right here.
\newcommand{\addimg}[4]{%
  \begin{figure}[H]
    \centering
    \includegraphics[width=#2\linewidth]{#1}
    \caption{#3}\label{#4}
  \end{figure}%
}

% ------------------------------------------------------------------ bibliography
\RequirePackage{csquotes}
\RequirePackage[backend=biber,style=ieee]{biblatex}
% Latin-script sources keep English conjunctions inside the Ukrainian bibliography.
\DefineBibliographyStrings{ukrainian}{and={and}, andothers={et\addabbrvspace al\adddot}}
% biblatex stretches the space after '/', ':' and '.' in URLs to justify lines, which spreads them
% out ("https : / / github . com"). Allow breaks anywhere in a URL instead, with no stretch.
\biburlbigskip=0mu\relax
\setcounter{biburlnumpenalty}{9000}
\setcounter{biburlucpenalty}{9000}
\setcounter{biburllcpenalty}{9000}

% ------------------------------------------------------------------ links
\RequirePackage{hyperref}
\hypersetup{colorlinks, linkcolor=black, citecolor=black, urlcolor=black, filecolor=black}

% Section entries of the TOC in capitals, like the headings. Must come after hyperref, which
% redefines \contentsline; its extra arguments (page, anchor) pass through untouched.
\let\iasa@contentsline\contentsline
\renewcommand{\contentsline}[2]{%
  \ifstrequal{#1}{section}
    {\iasa@contentsline{#1}{\MakeTextUppercase{#2}}}
    {\iasa@contentsline{#1}{#2}}%
}

% ------------------------------------------------------------------ title page
% Subject-wide defaults; each report sets \labnumber, \topic, \student, \studentgroup and,
% if the lab has variants, \variant.
\newcommand{\discipline}[1]{\def\iasa@discipline{#1}}
\newcommand{\teacher}[1]{\def\iasa@teacher{#1}}
\newcommand{\department}[1]{\def\iasa@department{#1}}
\newcommand{\labnumber}[1]{\def\iasa@labnumber{#1}}
\newcommand{\topic}[1]{\def\iasa@topic{#1}}
\newcommand{\student}[1]{\def\iasa@student{#1}}
\newcommand{\studentgroup}[1]{\def\iasa@studentgroup{#1}}
\newcommand{\reportyear}[1]{\def\iasa@reportyear{#1}}
\newcommand{\variant}[1]{\def\iasa@variant{#1}}
\discipline{Обробка надвеликих масивів даних}
\teacher{Пишнограєв Іван Олександрович}
\department{}
\labnumber{?}
\topic{?}
\student{?}
\studentgroup{}
\reportyear{\the\year}
\variant{}

\AtBeginDocument{\hypersetup{pdfauthor={\iasa@student}, pdftitle={Лабораторна робота №\iasa@labnumber. \iasa@topic}}}

\renewcommand{\maketitle}{%
  \begin{titlepage}
    \renewcommand{\baselinestretch}{1.15}\selectfont
    \centering
    МІНІСТЕРСТВО ОСВІТИ І НАУКИ УКРАЇНИ\\
    НАЦІОНАЛЬНИЙ ТЕХНІЧНИЙ УНІВЕРСИТЕТ УКРАЇНИ\\
    «КИЇВСЬКИЙ ПОЛІТЕХНІЧНИЙ ІНСТИТУТ\\ імені ІГОРЯ СІКОРСЬКОГО»\\[0.5em]
    Навчально-науковий інститут прикладного системного аналізу\\
    \ifx\iasa@department\@empty\else\iasa@department\\\fi
    \vfill
    {\bfseries ЗВІТ}\\[0.5em]
    про виконання лабораторної роботи №\iasa@labnumber\\
    з дисципліни «\iasa@discipline»\\[0.5em]
    на тему: {\bfseries «\iasa@topic»}
    \ifx\iasa@variant\@empty\else\\[0.5em]Варіант \iasa@variant\fi
    \vfill
    \begin{minipage}[t]{0.48\textwidth}
      \raggedright
      Виконав:\\
      \ifx\iasa@studentgroup\@empty\else студент групи \iasa@studentgroup\\\fi
      \iasa@student
    \end{minipage}%
    \hfill
    \begin{minipage}[t]{0.48\textwidth}
      \raggedleft
      Перевірив:\\
      \iasa@teacher
    \end{minipage}
    \vfill
    Київ -- \iasa@reportyear
  \end{titlepage}%
  \setcounter{page}{2}%
}
