"""Generate the modular, compilable LaTeX handbook."""

from __future__ import annotations

from pathlib import Path


def build_handbook(root: Path, topics, questions, core, designs, refs, tutorials, formulas, roadmap, latex_escape):
    formula_by_id = {f["id"]: f for f in formulas}
    lines = [
        r"\documentclass[10pt]{article}",
        r"\usepackage[margin=0.68in]{geometry}",
        r"\usepackage[T1]{fontenc}", r"\usepackage[utf8]{inputenc}", r"\usepackage{lmodern}",
        r"\usepackage{amsmath,amssymb,mathtools}", r"\usepackage{xcolor}", r"\usepackage{hyperref}",
        r"\usepackage{fancyhdr}", r"\usepackage{titlesec}", r"\usepackage{enumitem}",
        r"\usepackage{longtable}", r"\usepackage{tabularx}", r"\usepackage{booktabs}", r"\usepackage{adjustbox}",
        r"\usepackage{tikz}", r"\usetikzlibrary{arrows.meta,positioning,shapes.geometric,calc}",
        r"\definecolor{navy}{HTML}{0C2744}", r"\definecolor{blue}{HTML}{1E63E9}",
        r"\definecolor{cyan}{HTML}{1DB6C7}", r"\definecolor{paper}{HTML}{F4F7FB}",
        r"\definecolor{green}{HTML}{167A5B}", r"\definecolor{amber}{HTML}{B77700}",
        r"\hypersetup{colorlinks=true,linkcolor=blue,urlcolor=blue,pdftitle={AI Engineering Interview Atlas}}",
        r"\pagestyle{fancy}\fancyhf{}\fancyhead[L]{\textcolor{navy}{AI Engineering Interview Atlas}}\fancyhead[R]{\textcolor{gray}{\leftmark}}\fancyfoot[C]{\thepage}",
        r"\titleformat{\section}{\Large\bfseries\color{navy}}{\thesection}{.7em}{}",
        r"\titleformat{\subsection}{\large\bfseries\color{blue}}{\thesubsection}{.7em}{}",
        r"\titleformat{\subsubsection}{\normalsize\bfseries\color{navy}}{\thesubsubsection}{.7em}{}",
        r"\setlist{nosep,leftmargin=*}", r"\setlength{\parindent}{0pt}", r"\setlength{\parskip}{3pt}",
        r"\newcommand{\tradeoff}[1]{\par\smallskip\noindent\textbf{Tradeoff.} #1}",
        r"\newcommand{\pitfall}[1]{\par\smallskip\noindent\textbf{Production failure.} #1}",
        r"\newcommand{\badge}[1]{\colorbox{paper}{\textcolor{blue}{\textbf{#1}}}}",
        r"\newcommand{\mathblock}[1]{\begin{center}\begin{adjustbox}{max width=\linewidth}$\displaystyle #1$\end{adjustbox}\end{center}}",
        r"\newenvironment{derivation}{\begin{quote}\small\color{navy}}{\end{quote}}",
        r"\begin{document}",
        r"\begin{titlepage}\pagecolor{navy}\color{white}\vspace*{1.1in}{\Huge\bfseries AI Engineering\\Interview Atlas\par}\vspace{.35in}{\Large Mathematical tutorials, systems, and 1,000+ questions\par}\vspace{.35in}{\large " + str(len(formulas)) + r" derivations \textbullet\ " + str(len(tutorials)) + r" deep lessons \textbullet\ " + str(len(roadmap)) + r" roadmap phases\par}\vfill{\large Research snapshot: 2 September 2026\par}\vspace{.15in}{\normalsize Primary papers, official documentation, specifications, and standards\par}\vspace{.7in}{\color{cyan}\rule{\textwidth}{3pt}}\end{titlepage}\nopagecolor\color{black}",
        r"\tableofcontents\newpage",
        r"\section{How to use this handbook}",
        "This handbook contains " + str(len(topics)) + " complete topic tutorials, " + str(len(questions)) + " generated practice questions, 50 core interview questions, " + str(len(designs)) + " progressive system-design challenges, and " + str(len(formulas)) + " mathematical modules. The tutorials are deliberately written to cover the definition, tradeoff, failure, scenario, design, and production reasoning tested by the question bank.",
        r"\subsection{The interview answer loop}",
        r"Answer in seven moves: \textbf{mechanism $\rightarrow$ assumptions $\rightarrow$ quantitative model $\rightarrow$ alternative $\rightarrow$ experiment $\rightarrow$ operation $\rightarrow$ recovery}. For a short answer, compress the same structure rather than replacing it with product slogans.",
        r"\subsection{How to study a derivation}",
        r"For every equation: (1) define the tensor or random-variable shapes; (2) state assumptions; (3) derive rather than memorize; (4) check units or limiting cases; (5) connect each parameter to quality, latency, memory, or cost; and (6) identify where the approximation stops being valid.",
    ]

    # Roadmap and compact dependency diagram.
    lines += [r"\clearpage\section{Ordered study roadmap and progress model}",
              r"The online atlas stores completed phases, mastered lessons, and reviewed questions in browser storage. The first incomplete phase is highlighted as the current phase. In print, mark the boxes and write a date beside each milestone.",
              r"\begin{center}\begin{tikzpicture}[node distance=6mm and 18mm,phase/.style={draw=cyan,fill=paper,rounded corners,align=left,text width=66mm,minimum height=10mm,font=\small},arr/.style={-{Stealth},thick,draw=blue}]" ]
    # Two-column U-shaped ordered path: 00..05 down, then 06..11 up.
    for i, phase in enumerate(roadmap[:6]):
        anchor = "" if i == 0 else f",below=of p{i-1}"
        lines.append(r"\node[phase%s](p%d){\textbf{%02d. %s}\hfill %dh};" % (anchor, i, phase["order"], latex_escape(phase["title"]), phase["hours"]))
    for j, phase in enumerate(roadmap[6:]):
        idx = j + 6
        if j == 0:
            anchor = ",right=of p5"
        else:
            anchor = f",above=of p{idx-1}"
        lines.append(r"\node[phase%s](p%d){\textbf{%02d. %s}\hfill %dh};" % (anchor, idx, phase["order"], latex_escape(phase["title"]), phase["hours"]))
    for i in range(len(roadmap)-1):
        lines.append(rf"\draw[arr](p{i})--(p{i+1});")
    lines += [r"\end{tikzpicture}\end{center}"]
    for phase in roadmap:
        prereq = ", ".join(phase["prerequisites"]) or "none"
        lines += [
            r"\subsection{" + f"{phase['order']:02d}. " + latex_escape(phase["title"]) + "}",
            r"\badge{" + str(phase["hours"]) + r" focused hours} \quad \textbf{Prerequisites:} " + latex_escape(prereq),
            r"\begin{itemize}",
            *[r"\item " + latex_escape(x) for x in phase["outcomes"]],
            r"\end{itemize}",
            r"\textbf{Milestone.} " + latex_escape(phase["milestone"]),
            r"\textbf{Practice.} " + latex_escape(phase["practice"]),
        ]

    # Formula reference chapter with explicit derivations.
    lines += [r"\clearpage\section{Mathematical formula and derivation reference}",
              r"These equations are not decorative. Each derivation states the engineering interpretation and a limiting case or worked estimate. Symbols are redefined locally so modules can be studied independently."]
    for formula in formulas:
        lines += [
            r"\subsection{" + latex_escape(formula["title"]) + "}",
            r"\mathblock{\boxed{" + formula["latex"] + r"}}",
            r"\textbf{Variables.}\begin{itemize}",
            *[r"\item " + latex_escape(v) for v in formula["variables"]],
            r"\end{itemize}",
            r"\textbf{Derivation.}\begin{derivation}\begin{enumerate}",
        ]
        for step in formula["derivation"]:
            lines += [r"\item " + latex_escape(step["text"]), r"\mathblock{" + step["latex"] + r"}"]
        lines += [r"\end{enumerate}\end{derivation}", r"\textbf{Worked interpretation.} " + latex_escape(formula["example"])]

    # Deep tutorials: exact source for answering every generated question.
    current = None
    for tutorial in tutorials:
        if tutorial["category"] != current:
            current = tutorial["category"]
            lines += [r"\clearpage\section{" + latex_escape(current) + "}"]
        lines += [
            r"\subsection{" + latex_escape(tutorial["name"]) + "}",
            r"\textbf{Learning objective.} " + latex_escape(tutorial["objective"]),
            r"\subsubsection*{First principles and mental model}",
            latex_escape(tutorial["first_principles"]),
            latex_escape(tutorial["mental_model"]),
            r"\subsubsection*{Mathematics and quantitative reasoning}",
            latex_escape(tutorial["quantitative_reasoning"]),
        ]
        for formula_id in tutorial["formula_ids"]:
            formula = formula_by_id[formula_id]
            lines += [r"\paragraph{" + latex_escape(formula["title"]) + "}", r"\mathblock{" + formula["latex"] + r"}"]
        lines += [
            r"\subsubsection*{Decision and failure reasoning}",
            latex_escape(tutorial["decision_reasoning"]),
            latex_escape(tutorial["failure_reasoning"]),
            r"\subsubsection*{Worked production method}", r"\begin{enumerate}",
            *[r"\item " + latex_escape(x) for x in tutorial["worked_reasoning"]], r"\end{enumerate}",
            r"\textbf{Evaluate.}\begin{itemize}", *[r"\item " + latex_escape(x) for x in tutorial["evaluation"]], r"\end{itemize}",
            r"\textbf{Operate.}\begin{itemize}", *[r"\item " + latex_escape(x) for x in tutorial["operations"]], r"\end{itemize}",
            r"\subsubsection*{Interview answer blueprint}", r"\begin{description}",
            *[r"\item[" + latex_escape(k.replace("_", " ").title()) + "] " + latex_escape(v) for k, v in tutorial["answer_blueprint"].items()],
            r"\end{description}",
            r"\colorbox{paper}{\parbox{0.96\linewidth}{\textbf{Question coverage.} " + latex_escape(tutorial["question_coverage"]) + r"}}",
        ]

    lines += [r"\clearpage\section{Core 50 interview questions}"]
    for q in core:
        lines += [r"\subsection*{" + latex_escape(q["id"] + " - " + q["prompt"]) + "}", r"\badge{" + latex_escape(q["difficulty"].upper()) + r"} \quad " + latex_escape(q["category"]), r"\par\smallskip\textbf{Answer rubric.} " + latex_escape(q["answer"])]

    lines += [r"\clearpage\section{Progressive system-design challenges}",
              r"For each design, clarify workload and SLOs first. Draw the initial architecture, then incorporate each stage without erasing the earlier reasoning. Explicitly discuss data flow, control flow, failure isolation, observability, cost, migration, and rollback."]
    for design in designs:
        lines += [r"\subsection{" + latex_escape(design["title"]) + "}", latex_escape(design["brief"]), r"\begin{enumerate}"]
        for stage in design["stages"]:
            lines.append(r"\item \textbf{" + latex_escape(stage["q"]) + "} " + latex_escape(stage["a"]))
        lines.append(r"\end{enumerate}")

    lines += [r"\clearpage\section{Complete practice bank}",
              r"Every prompt is paired with an answer. When an explanation is brief, return to the topic tutorial: it contains the complete definition, tradeoff, failure, experiment, operations, and recovery reasoning used to construct all ten prompts for that topic."]
    current = None
    for q in questions:
        if q["category"] != current:
            current = q["category"]
            lines.append(r"\subsection{" + latex_escape(current) + "}")
        lines += [r"\paragraph{" + latex_escape(q["id"] + " [" + q["difficulty"] + "]") + "} " + latex_escape(q["prompt"])]
        if q.get("options"):
            lines += [r"\begin{enumerate}[label=\Alph*.]", *[r"\item " + latex_escape(o) for o in q["options"]], r"\end{enumerate}"]
        lines += [r"\noindent\textbf{Answer.} " + latex_escape(q["answer"]), r"\par\textit{" + latex_escape(q.get("explanation", "")) + "}"]

    lines += [r"\clearpage\section{Primary sources}", r"\begin{enumerate}"]
    for ref in refs:
        lines.append(r"\item \href{" + ref["url"] + "}{" + latex_escape(ref["title"]) + "} (" + latex_escape(ref["kind"]) + ")")
    lines += [r"\end{enumerate}", r"\end{document}"]

    begin = lines.index(r"\begin{document}")
    preamble, body_lines = lines[:begin + 1], lines[begin + 1:-1]
    part_dir = root / "handbook" / "parts"
    part_dir.mkdir(parents=True, exist_ok=True)
    for old in part_dir.glob("part_*.tex"):
        old.unlink()
    chunks, chunk, size = [], [], 0
    for line in body_lines:
        line_size = len(line.encode("utf-8")) + 1
        if chunk and size + line_size > 320_000:
            chunks.append(chunk); chunk=[]; size=0
        chunk.append(line); size += line_size
    if chunk:
        chunks.append(chunk)
    for i, part in enumerate(chunks, 1):
        (part_dir / f"part_{i:02d}.tex").write_text("\n".join(part) + "\n", encoding="utf-8")
    main = preamble + [rf"\input{{handbook/parts/part_{i:02d}.tex}}" for i in range(1, len(chunks)+1)] + [r"\end{document}"]
    (root / "handbook" / "ai_engineering_interview_handbook.tex").write_text("\n".join(main) + "\n", encoding="utf-8")
