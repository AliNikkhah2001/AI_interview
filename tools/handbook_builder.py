"""Generate the modular, compilable LaTeX handbook."""

from __future__ import annotations

from pathlib import Path
import re


def visual_latex(visual, latex_escape):
    """Render one canonical visual as native vector LaTeX/TikZ."""
    lines = [
        r"\subsection{" + latex_escape(visual["title"]) + "}",
        r"\badge{" + latex_escape(visual["kicker"]) + r"} \quad " + latex_escape(visual["intuition"]),
    ]
    if visual["kind"] == "plot":
        labels = visual["x_labels"]
        series = visual["series"]
        max_x = max(1, len(labels) - 1)
        lines += [
            r"\begin{center}\begin{tikzpicture}[x=1.32cm,y=0.047cm]",
            rf"\draw[->,draw=navy] (0,0)--({max_x + .45},0) node[right]{{\scriptsize {latex_escape(visual['x_label'])}}};",
            rf"\draw[->,draw=navy] (0,0)--(0,108) node[above]{{\scriptsize {latex_escape(visual['y_label'])}}};",
        ]
        for y in [25, 50, 75, 100]:
            lines.append(rf"\draw[draw=gray!25,dashed] (0,{y})--({max_x},{y}) node[left]{{\scriptsize {y}}};")
        colors = ["cyan", "amber"]
        for series_index, item in enumerate(series):
            coordinates = " ".join(f"({i},{value})" for i, value in enumerate(item["values"]))
            color = colors[series_index % len(colors)]
            lines.append(rf"\draw[very thick,draw={color}] plot coordinates {{{coordinates}}};")
            for i, value in enumerate(item["values"]):
                lines.append(rf"\fill[{color}] ({i},{value}) circle (1.5pt);")
        for i, label in enumerate(labels):
            lines.append(rf"\node[below,font=\scriptsize] at ({i},0) {{{latex_escape(label)}}};")
        legend = r"\quad ".join(rf"\textcolor{{{colors[i % len(colors)]}}}{{\rule{{5mm}}{{1.2pt}}}} {latex_escape(item['label'])}" for i, item in enumerate(series))
        lines += [r"\end{tikzpicture}\par\smallskip " + legend + r"\end{center}"]
    else:
        lines.append(r"\begin{center}\begin{tikzpicture}[visual/.style={draw=cyan,fill=paper,rounded corners,align=center,text width=25mm,minimum height=12mm,font=\small},arr/.style={-{Stealth},thick,draw=blue},node distance=7mm]")
        for i, step in enumerate(visual["steps"]):
            anchor = "" if i == 0 else f",right=of v{i-1}"
            lines.append(
                r"\node[visual" + anchor + f"] (v{i}) "
                + r"{\textbf{" + latex_escape(step["label"]) + r"}\\{\scriptsize "
                + latex_escape(step["detail"]) + r"}};"
            )
        for i in range(len(visual["steps"]) - 1):
            lines.append(rf"\draw[arr] (v{i})--(v{i+1});")
        if visual.get("loop"):
            last = len(visual["steps"]) - 1
            lines.append(rf"\draw[arr] (v{last}.south) to[bend left=32] node[below,font=\scriptsize]{{feedback}} (v0.south);")
        lines.append(r"\end{tikzpicture}\end{center}")
    lines.append(r"\colorbox{paper}{\parbox{0.96\linewidth}{\textbf{Remember.} " + latex_escape(visual["takeaway"]) + "}}")
    return lines


def technology_latex(technology, latex_escape):
    """Render a workload-oriented technology profile with a native vector diagram."""
    flow = technology["flow"]
    lines = [
        r"\subsubsection{" + latex_escape(technology["name"]) + "}",
        r"\noindent\colorbox{navy}{\parbox[c][10mm][c]{10mm}{\centering\textcolor{white}{\Large\bfseries "
        + latex_escape(technology["logo_fallback"]) + r"}}}\quad "
        + r"\badge{" + latex_escape(technology["kind"]) + r"} \quad "
        + r"\textbf{Languages:} " + latex_escape(" / ".join(technology["languages"])),
        r"\par\smallskip " + latex_escape(technology["summary"]),
        r"\par\smallskip\colorbox{paper}{\parbox{0.96\linewidth}{\textbf{Mental model.} "
        + latex_escape(technology["mental_model"]) + r"}}",
        r"\begin{center}\begin{tikzpicture}[node distance=8mm,tech/.style={draw=cyan,fill=paper,rounded corners,align=center,text width=42mm,minimum height=12mm,font=\small},arr/.style={-{Stealth},thick,draw=blue}]",
        r"\node[tech](t0){" + latex_escape(flow[0]) + r"};",
        r"\node[tech,right=of t0](t1){" + latex_escape(flow[1]) + r"};",
        r"\node[tech,right=of t1](t2){" + latex_escape(flow[2]) + r"};",
        r"\draw[arr](t0)--(t1);\draw[arr](t1)--(t2);",
        r"\end{tikzpicture}\end{center}",
        r"\paragraph{Framework structure and design.}",
        r"\begin{tabularx}{\linewidth}{>{\bfseries\color{blue}}p{34mm}X}",
        r"Data plane & " + latex_escape(" -> ".join(technology["flow"])) + r"\\",
        r"Control plane & " + latex_escape(technology["architecture"][3]["detail"]) + r"\\",
        r"State and trust boundary & " + latex_escape(technology["architecture"][4]["detail"]) + r"\\",
        r"\end{tabularx}",
        r"\paragraph{Five-part tutorial.}",
        r"\begin{description}[leftmargin=38mm,style=nextline]",
        *[
            r"\item[" + latex_escape(lesson["title"]) + r"] " + latex_escape(lesson["body"])
            for lesson in technology["tutorial"]
        ],
        r"\end{description}",
        r"\begin{tabularx}{\linewidth}{>{\bfseries\color{blue}}p{27mm}X}",
        r"Deployment & " + latex_escape(technology["deployment"]) + r"\\",
        r"Choose when & " + latex_escape(technology["choose_when"]) + r"\\",
        r"Reject when & " + latex_escape(technology["avoid_when"]) + r"\\",
        r"Primary failure & " + latex_escape(technology["failure_mode"]) + r"\\",
        r"Compare with & " + latex_escape("; ".join(technology["alternatives"])) + r"\\",
        r"\end{tabularx}",
        r"\paragraph{Minimal use in " + latex_escape(" / ".join(technology["languages"])) + r".}",
        r"\begin{Verbatim}[fontsize=\scriptsize]",
        technology["quickstart"],
        r"\end{Verbatim}",
        r"\textbf{Primary sources.} " + r" \quad ".join(
            r"\href{" + source["url"] + "}{" + latex_escape(source["label"]) + "}"
            for source in technology["sources"]
        ) + ".",
    ]
    return lines


def design_diagram_latex(design, latex_escape):
    """Convert the small Mermaid architecture graphs into positioned TikZ DAGs."""
    source = design.get("diagram", "")
    node_matches = re.findall(r"([A-Za-z0-9_]+)\[([^\]]+)\]", source)
    node_matches += re.findall(r"([A-Za-z0-9_]+)\{([^}]+)\}", source)
    labels = {}
    for node_id, label in node_matches:
        labels.setdefault(node_id, label)
    edges = re.findall(r"([A-Za-z0-9_]+)(?:\[[^\]]+\]|\{[^}]+\})?\s*-->(?:\|[^|]*\|)?\s*([A-Za-z0-9_]+)", source)
    edges = [(left, right) for left, right in edges if left in labels and right in labels]
    if not labels:
        return []

    incoming = {node_id: 0 for node_id in labels}
    children = {node_id: [] for node_id in labels}
    for left, right in edges:
        incoming[right] += 1
        children[left].append(right)
    depth = {node_id: 0 for node_id in labels}
    queue = [node_id for node_id in labels if incoming[node_id] == 0]
    visited = set()
    while queue:
        node_id = queue.pop(0)
        visited.add(node_id)
        for child in children[node_id]:
            depth[child] = max(depth[child], depth[node_id] + 1)
            incoming[child] -= 1
            if incoming[child] == 0:
                queue.append(child)
    for node_id in labels:
        if node_id not in visited:
            depth[node_id] = max(depth.values(), default=0) + 1

    layers = {}
    for node_id in labels:
        layers.setdefault(depth[node_id], []).append(node_id)
    positions = {}
    for layer, node_ids in sorted(layers.items()):
        spacing = min(48, 150 / max(1, len(node_ids) - 1)) if len(node_ids) > 1 else 0
        for index, node_id in enumerate(node_ids):
            positions[node_id] = ((index - (len(node_ids) - 1) / 2) * spacing, -layer * 20)

    aliases = {node_id: f"d{index}" for index, node_id in enumerate(labels)}
    lines = [
        r"\begin{center}\begin{adjustbox}{max width=\linewidth}\begin{tikzpicture}[design/.style={draw=cyan,fill=paper,rounded corners,align=center,text width=37mm,minimum height=11mm,font=\scriptsize},arr/.style={-{Stealth},thick,draw=blue}]"
    ]
    for node_id, label in labels.items():
        x, y = positions[node_id]
        lines.append(rf"\node[design]({aliases[node_id]}) at ({x:.2f}mm,{y:.2f}mm){{{latex_escape(label)}}};")
    for left, right in edges:
        lines.append(rf"\draw[arr]({aliases[left]})--({aliases[right]});")
    lines.append(r"\end{tikzpicture}\end{adjustbox}\end{center}")
    return lines


def build_handbook(root: Path, topics, questions, core, designs, refs, tutorials, formulas, roadmap, visuals,
                   technologies, technology_categories, technology_questions, latex_escape):
    formula_by_id = {f["id"]: f for f in formulas}
    lines = [
        r"\documentclass[10pt]{article}",
        r"\usepackage[margin=0.68in]{geometry}",
        r"\usepackage[T1]{fontenc}", r"\usepackage[utf8]{inputenc}", r"\usepackage{lmodern}",
        r"\usepackage{amsmath,amssymb,mathtools}", r"\usepackage{xcolor}", r"\usepackage{hyperref}",
        r"\usepackage{fancyhdr}", r"\usepackage{titlesec}", r"\usepackage{enumitem}",
        r"\usepackage{longtable}", r"\usepackage{tabularx}", r"\usepackage{booktabs}", r"\usepackage{adjustbox}", r"\usepackage{fancyvrb}",
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
        r"\begin{titlepage}\pagecolor{navy}\color{white}\vspace*{1.1in}{\Huge\bfseries AI Engineering\\Interview Atlas\par}\vspace{.35in}{\Large Mathematical tutorials, technology field guide, systems, and 2,000+ questions\par}\vspace{.35in}{\large " + str(len(formulas)) + r" derivations \textbullet\ " + str(len(visuals)) + r" visual models \textbullet\ " + str(len(technologies)) + r" technology profiles \textbullet\ " + str(len(tutorials)) + r" deep lessons\par}\vfill{\large Research snapshot: 6 September 2026\par}\vspace{.15in}{\normalsize Primary papers, official documentation, specifications, and standards\par}\vspace{.7in}{\color{cyan}\rule{\textwidth}{3pt}}\end{titlepage}\nopagecolor\color{black}",
        r"\tableofcontents\newpage",
        r"\section{How to use this handbook}",
        "This handbook contains " + str(len(topics)) + " complete topic tutorials, " + str(len(technologies)) + " workload-oriented technology profiles, " + str(len(questions)) + " generated practice questions, 50 core interview questions, " + str(len(designs)) + " progressive system-design challenges, " + str(len(visuals)) + " visual intuition models, and " + str(len(formulas)) + " mathematical modules. The browser resumes the last unfinished chapter, records five reading checkpoints, unlocks a five-question exam, and advances after a score of at least 80 percent.",
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
    lines += [r"\end{tikzpicture}\end{center}",
              r"\subsection{The guided learning loop}",
              r"\begin{center}\begin{tikzpicture}[visual/.style={draw=cyan,fill=paper,rounded corners,align=center,text width=30mm,minimum height=11mm,font=\small},arr/.style={-{Stealth},thick,draw=blue},node distance=8mm]\node[visual](resume){Resume last\\unfinished};\node[visual,right=of resume](teach){Read five\\lesson parts};\node[visual,right=of teach](exam){Pass topic exam\\at 80\%};\node[visual,below=of exam](mark){Mark chapter\\and phase};\node[visual,left=of mark](next){Open next\\chapter};\draw[arr](resume)--(teach);\draw[arr](teach)--(exam);\draw[arr](exam)--(mark);\draw[arr](mark)--(next);\draw[arr](next.west) to[bend left=26] (resume.south);\end{tikzpicture}\end{center}",
              r"The website stores the last opened chapter, reading checkpoints, exam attempts, best scores, chapter mastery, and automatically completed lesson-bearing phases in browser storage. A chapter is learned only after all five parts have been reached and its exam has been passed."]
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

    lines += [r"\clearpage\section{Visual intuition atlas}",
              r"Use each picture to predict behavior before memorizing terminology. Curves are normalized teaching models unless a unit is stated; benchmark real systems on representative workloads."]
    for visual in visuals:
        lines += visual_latex(visual, latex_escape)

    # Dedicated technology field guide: category map, comparison, and one diagram per profile.
    lines += [
        r"\clearpage\section{Libraries and technologies field guide}",
        "This section separates technology choice from general theory. Each profile starts with the workload, shows the abstract execution path, states language and deployment boundaries, gives a minimal use pattern, and makes the rejection case explicit. The online version loads a recognizable brand mark for every profile; this print edition uses a compact vector monogram so it remains reproducible without network access.",
        r"\subsection{" + str(len(technology_categories)) + r"-layer technology landscape}",
        r"\begin{center}\begin{tikzpicture}[layer/.style={draw=cyan,fill=paper,rounded corners,align=left,text width=63mm,minimum height=13mm,font=\small},arr/.style={-{Stealth},thick,draw=blue},node distance=6mm and 15mm]",
    ]
    for index, category in enumerate(technology_categories):
        if index == 0:
            anchor = ""
        elif index == 4:
            anchor = ",right=of l3"
        elif index < 4:
            anchor = f",below=of l{index-1}"
        else:
            anchor = f",above=of l{index-1}"
        count = sum(technology["category_id"] == category["id"] for technology in technologies)
        lines.append(
            r"\node[layer" + anchor + f"] (l{index}) "
            + r"{\textbf{" + f"{category['order']:02d}. " + latex_escape(category["title"]) + r"}\hfill " + str(count)
            + r" profiles\\{\scriptsize " + latex_escape(category["question"]) + r"}};"
        )
    for index in range(len(technology_categories) - 1):
        lines.append(rf"\draw[arr](l{index})--(l{index+1});")
    lines += [r"\end{tikzpicture}\end{center}"]

    for category in technology_categories:
        category_technologies = [technology for technology in technologies if technology["category_id"] == category["id"]]
        lines += [
            r"\clearpage\subsection{" + f"{category['order']:02d}. " + latex_escape(category["title"]) + "}",
            r"\textbf{Selection question.} " + latex_escape(category["question"]),
            r"\begin{center}\begin{tikzpicture}[tech/.style={draw=cyan,fill=paper,rounded corners,align=center,text width=42mm,minimum height=12mm,font=\small},arr/.style={-{Stealth},thick,draw=blue},node distance=8mm]",
            r"\node[tech](c0){" + latex_escape(category["need"]) + r"};",
            r"\node[tech,right=of c0](c1){" + latex_escape(category["mechanism"]) + r"};",
            r"\node[tech,right=of c1](c2){" + latex_escape(category["result"]) + r"};",
            r"\draw[arr](c0)--(c1);\draw[arr](c1)--(c2);",
            r"\end{tikzpicture}\end{center}",
            r"\paragraph{Comparison matrix.}",
            r"\begin{longtable}{@{}p{20mm}p{22mm}p{26mm}p{46mm}p{46mm}@{}}",
            r"\toprule\textbf{Tool} & \textbf{Kind} & \textbf{Language / boundary} & \textbf{Choose when} & \textbf{Reject when}\\\midrule\endhead",
        ]
        for technology in category_technologies:
            language_boundary = ", ".join(technology["languages"]) + "; " + technology["deployment"]
            lines.append(
                latex_escape(technology["name"]) + " & " + latex_escape(technology["kind"]) + " & "
                + latex_escape(language_boundary) + " & " + latex_escape(technology["choose_when"])
                + " & " + latex_escape(technology["avoid_when"]) + r"\\"
            )
        lines += [r"\bottomrule\end{longtable}"]
        for technology in category_technologies:
            lines += technology_latex(technology, latex_escape)

    lines += [
        r"\clearpage\section{Technology interview question bank}",
        "Every listed technology has one medium selection question, a hard architecture question, a hard comparison and measurement question, and one very-hard failure, migration, and recovery question. Product APIs evolve; defend answers with workload evidence and the linked official documentation.",
    ]
    for category in technology_categories:
        lines.append(r"\subsection{" + latex_escape(category["title"]) + "}")
        for technology in [item for item in technologies if item["category_id"] == category["id"]]:
            lines.append(r"\subsubsection*{" + latex_escape(technology["name"]) + "}")
            for question in [item for item in technology_questions if item["technology_id"] == technology["id"]]:
                lines += [
                    r"\paragraph{" + latex_escape(question["difficulty"].upper() + " - " + question["id"]) + "} " + latex_escape(question["prompt"]),
                ]
                if question.get("options"):
                    lines += [r"\begin{enumerate}[label=\Alph*.]", *[r"\item " + latex_escape(option) for option in question["options"]], r"\end{enumerate}"]
                lines += [r"\textbf{Answer.} " + latex_escape(question["answer"]), r"\textit{" + latex_escape(question.get("explanation", "")) + "}"]

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
        lines += [r"\subsection{" + latex_escape(design["title"]) + "}", latex_escape(design["brief"])]
        if design.get("tool_choices"):
            lines += [r"\textbf{Explicit technology choices.} " + latex_escape("; ".join(design["tool_choices"])) + "."]
        lines += design_diagram_latex(design, latex_escape)
        lines.append(r"\begin{enumerate}")
        for stage in design["stages"]:
            lines.append(r"\item \textbf{" + latex_escape(stage["q"]) + "} " + latex_escape(stage["a"]))
        lines.append(r"\end{enumerate}")

    lines += [r"\clearpage\section{Complete practice bank}",
              r"Every prompt is paired with an answer. When an explanation is brief, return to the topic tutorial: it contains the complete definition, tradeoff, failure, experiment, operations, and recovery reasoning used to construct all ten prompts for that topic."]
    current = None
    curriculum_questions = [question for question in questions if not question.get("technology_id")]
    for q in curriculum_questions:
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
