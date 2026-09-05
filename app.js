const READ_PARTS = ["principles", "math", "decision", "production", "blueprint"];
const PASS_SCORE = 80;
const safeStored = (key, fallback) => {
  try { return JSON.parse(localStorage.getItem(key) || JSON.stringify(fallback)); }
  catch { return fallback; }
};

const state = {
  topics: [], questions: [], core: [], designs: [], refs: [], tutorials: [], formulas: [], roadmap: [], visuals: [],
  technologies: [], technologyCategories: [], technologyQuestions: [],
  courseOrder: [], pool: [], index: 0, activeTutorial: null, activeExam: null, readingObserver: null,
  seen: new Set(safeStored("atlas-seen", [])),
  mastered: new Set(safeStored("atlas-mastered", [])),
  phases: new Set(safeStored("atlas-roadmap-progress", [])),
  reading: safeStored("atlas-reading-v2", {}),
  examScores: safeStored("atlas-exam-scores-v2", {}),
  examAttempts: safeStored("atlas-exam-attempts-v2", {}),
  lastTopic: localStorage.getItem("atlas-last-topic-v2") || null,
};

const $ = selector => document.querySelector(selector);
const $$ = selector => [...document.querySelectorAll(selector)];
const esc = value => String(value ?? "").replace(/[&<>"']/g, char => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[char]));
const questionFiles = ["data/questions_1.json", "data/questions_2.json", "data/questions_3.json", "data/questions_4.json"];
const dataFiles = [
  "data/topics.json", "data/core_questions.json", "data/designs.json", "data/references.json",
  "data/tutorials.json", "data/formulas.json", "data/roadmap.json", "data/visuals.json",
  "data/technology_categories.json", "data/technologies.json", "data/technology_questions.json",
  ...questionFiles,
];

Promise.all(dataFiles.map(url => fetch(url).then(response => {
  if (!response.ok) throw new Error(`${url}: ${response.status}`);
  return response.json();
}))).then(([topics, core, designs, refs, tutorials, formulas, roadmap, visuals, technologyCategories, technologies, technologyQuestions, ...shards]) => {
  Object.assign(state, {
    topics, core, designs, refs, tutorials, formulas, roadmap, visuals,
    technologyCategories, technologies, technologyQuestions,
    questions: shards.flat().concat(technologyQuestions),
  });
  state.courseOrder = orderedTutorials();
  state.activeTutorial = resumeTutorial()?.topic_id || state.lastTopic || tutorials[0]?.topic_id || null;
  syncPhaseProgress();
  renderAll();
  applyQuestionFilters();
  restoreRoute();
}).catch(error => {
  $("#main").insertAdjacentHTML("afterbegin", `<p class="error-panel"><strong>Content failed to load.</strong> ${esc(error.message)}</p>`);
});

function persistSet(key, values) { localStorage.setItem(key, JSON.stringify([...values])); }
function typeset(node = document.body) {
  if (window.MathJax?.typesetPromise) window.MathJax.typesetPromise([node]).catch(() => {});
}
function orderedTutorials() {
  const ordered = [];
  const included = new Set();
  state.roadmap.forEach(phase => phase.categories.forEach(category => {
    state.tutorials.filter(tutorial => tutorial.category === category).forEach(tutorial => {
      if (!included.has(tutorial.topic_id)) { included.add(tutorial.topic_id); ordered.push(tutorial); }
    });
  }));
  state.tutorials.forEach(tutorial => {
    if (!included.has(tutorial.topic_id)) { included.add(tutorial.topic_id); ordered.push(tutorial); }
  });
  return ordered;
}
function phaseTutorials(phase) {
  return state.courseOrder.filter(tutorial => phase.categories.includes(tutorial.category));
}
function phaseForTutorial(tutorial) {
  return state.roadmap.find(phase => phase.categories.includes(tutorial?.category));
}
function nextTutorial(topicId) {
  const start = Math.max(0, state.courseOrder.findIndex(tutorial => tutorial.topic_id === topicId));
  return state.courseOrder.slice(start + 1).find(tutorial => !state.mastered.has(tutorial.topic_id))
    || state.courseOrder.slice(0, start + 1).find(tutorial => !state.mastered.has(tutorial.topic_id))
    || null;
}
function resumeTutorial() {
  if (!state.courseOrder.length) return null;
  const lastIndex = state.courseOrder.findIndex(tutorial => tutorial.topic_id === state.lastTopic);
  if (lastIndex >= 0 && !state.mastered.has(state.lastTopic)) return state.courseOrder[lastIndex];
  if (lastIndex >= 0) {
    const later = state.courseOrder.slice(lastIndex + 1).find(tutorial => !state.mastered.has(tutorial.topic_id));
    if (later) return later;
  }
  return state.courseOrder.find(tutorial => !state.mastered.has(tutorial.topic_id)) || null;
}
function readSet(topicId) {
  if (state.mastered.has(topicId)) return new Set(READ_PARTS);
  return new Set(state.reading[topicId] || []);
}
function syncPhaseProgress() {
  state.roadmap.forEach(phase => {
    const lessons = phaseTutorials(phase);
    if (!lessons.length) return;
    if (lessons.every(tutorial => state.mastered.has(tutorial.topic_id))) state.phases.add(phase.id);
    else state.phases.delete(phase.id);
  });
  persistSet("atlas-roadmap-progress", state.phases);
}

function showView(id, topicId = null) {
  $$(".view").forEach(view => view.classList.toggle("active", view.id === id));
  $$("nav button").forEach(button => button.classList.toggle("active", button.dataset.view === id));
  if (id === "tutorial" && topicId) selectTutorial(topicId, false);
  if (id === "toolbox" && topicId) selectTechnology(topicId, false);
  history.replaceState(null, "", `#${id}${topicId ? `/${topicId}` : ""}`);
  typeset($(`#${id}`) || document.body);
  window.scrollTo({top: $(".command").offsetHeight, behavior: "smooth"});
}
function resumeLesson(topicId) {
  if (!topicId) return;
  showView("tutorial", topicId);
  const firstUnread = READ_PARTS.find(part => !readSet(topicId).has(part));
  const selector = firstUnread ? `[data-read-section="${firstUnread}"]` : "#chapterExam";
  window.setTimeout(() => $(selector)?.scrollIntoView({behavior: "smooth", block: "start"}), 180);
}
function restoreRoute() {
  const [view, topicId] = location.hash.replace(/^#/, "").split("/");
  if (view && $(`#${view}`)) showView(view, topicId || null);
  else showView("learn");
}
$$("nav button").forEach(button => { button.onclick = () => showView(button.dataset.view); });

function renderAll() {
  renderLearn(); renderMap(); renderRoadmap(); renderTutorialControls(); renderTechnologies(); renderTopics(); renderCore(); renderDesigns(); renderSources();
  $("#qTechnology").innerHTML = `<option value="">All technologies</option>${state.technologies.map(technology => `<option value="${esc(technology.id)}">${esc(technology.name)}</option>`).join("")}`;
}

function renderLearn() {
  const next = resumeTutorial();
  const complete = state.courseOrder.filter(tutorial => state.mastered.has(tutorial.topic_id)).length;
  const percent = state.courseOrder.length ? Math.round(complete / state.courseOrder.length * 100) : 0;
  const phase = phaseForTutorial(next);
  const read = next ? readSet(next.topic_id).size : 0;
  $("#learningDashboard").innerHTML = next ? `
    <article class="resume-card">
      <p class="eyebrow">${complete ? "CONTINUE WHERE YOU STOPPED" : "START THE GUIDED PATH"}</p>
      <h3>${esc(next.name)}</h3>
      <p>${esc(next.objective)}</p>
      <div class="resume-meta"><span>${esc(phase?.title || next.category)}</span><span>${complete + 1} of ${state.courseOrder.length}</span><span>${read}/5 parts read</span><span>${state.examScores[next.topic_id] ? `best exam ${state.examScores[next.topic_id]}%` : "exam not passed"}</span></div>
      <button id="resumeLearning">${read ? "Resume lesson" : "Start lesson"} →</button>
    </article>
    <article class="course-overview"><p class="eyebrow">COURSE PROGRESS</p><div class="course-number">${percent}%</div><h3>${complete.toLocaleString()} chapters passed</h3><div class="roadmap-bar"><i style="width:${percent}%"></i></div><dl><dt>Reading checkpoints</dt><dd>${Object.values(state.reading).reduce((sum, parts) => sum + new Set(parts).size, 0).toLocaleString()}</dd><dt>Passed exams</dt><dd>${state.mastered.size.toLocaleString()}</dd><dt>Next phase</dt><dd>${esc(phase ? String(phase.order).padStart(2, "0") : "Done")}</dd></dl></article>` : `<article class="resume-card"><h3>Course complete</h3><p>Maintain recall with mixed questions and system-design rehearsals.</p><button id="resumeLearning">Review the last chapter →</button></article>`;
  $("#resumeLearning").onclick = () => resumeLesson(next?.topic_id || state.courseOrder.at(-1)?.topic_id);

  const guidedPhases = state.roadmap.filter(phaseItem => phaseTutorials(phaseItem).length);
  const current = guidedPhases.find(phaseItem => phaseTutorials(phaseItem).some(tutorial => !state.mastered.has(tutorial.topic_id)));
  $("#coursePath").innerHTML = guidedPhases.map(phaseItem => {
    const lessons = phaseTutorials(phaseItem);
    const done = lessons.filter(tutorial => state.mastered.has(tutorial.topic_id)).length;
    const phasePercent = Math.round(done / lessons.length * 100);
    const first = lessons.find(tutorial => !state.mastered.has(tutorial.topic_id)) || lessons.at(-1);
    return `<article class="course-phase ${done === lessons.length ? "done" : ""} ${current?.id === phaseItem.id ? "current" : ""}" data-start-topic="${esc(first.topic_id)}"><span class="badge">PHASE ${String(phaseItem.order).padStart(2, "0")}</span><h3>${esc(phaseItem.title)}</h3><div class="mini-progress"><i style="width:${phasePercent}%"></i></div><p>${done}/${lessons.length} chapters passed · ${phasePercent}%</p><button class="course-action">${done === lessons.length ? "Review phase" : current?.id === phaseItem.id ? "Continue phase" : "Open phase"}</button></article>`;
  }).join("");
  $$("#coursePath [data-start-topic]").forEach(card => { card.querySelector("button").onclick = () => resumeLesson(card.dataset.startTopic); });
}

function renderMap() {
  const groups = state.topics.reduce((result, topic) => ((result[topic.category] ??= []).push(topic), result), {});
  $("#mindmap").innerHTML = Object.entries(groups).map(([category, topics]) => `<details class="branch" open><summary>${esc(category)}<span>${topics.length} topics</span></summary><ul>${topics.map(topic => `<li data-search="${esc((topic.name + " " + topic.summary).toLowerCase())}"><button class="map-topic-link" data-topic="${esc(topic.id)}">${esc(topic.name)}</button></li>`).join("")}</ul></details>`).join("");
  $$("#mindmap [data-topic]").forEach(button => { button.onclick = () => showView("tutorial", button.dataset.topic); });
  $("#visualGallery").innerHTML = state.visuals.map(visual => renderVisual(visual, true)).join("");
  $$("#visualGallery [data-visual-topic]").forEach(button => { button.onclick = () => showView("tutorial", button.dataset.visualTopic); });
}

function renderVisual(visual, includeLink = false) {
  const openTopic = visual.topic_ids.find(topicId => state.tutorials.some(tutorial => tutorial.topic_id === topicId))
    || state.tutorials.find(tutorial => tutorial.category === visual.category)?.topic_id;
  let canvas;
  if (visual.kind === "plot") canvas = renderPlot(visual);
  else canvas = `<div class="visual-canvas"><div class="visual-flow ${visual.loop ? "loop" : ""} ${esc(visual.kind)}">${visual.steps.map(step => `<div class="visual-step"><strong>${esc(step.label)}</strong><small>${esc(step.detail)}</small></div>`).join("")}</div></div>`;
  return `<figure class="intuition-figure"><figcaption><span class="visual-kicker">${esc(visual.kicker)}</span><h4>${esc(visual.title)}</h4><p>${esc(visual.intuition)}</p>${includeLink ? `<button class="course-action visual-open" data-visual-topic="${esc(openTopic)}">Study this mechanism →</button>` : ""}</figcaption>${canvas}<p class="visual-takeaway"><strong>Remember:</strong> ${esc(visual.takeaway)}</p></figure>`;
}
function renderPlot(visual) {
  const width = 620, height = 255, left = 58, right = 20, top = 18, bottom = 205;
  const plotWidth = width - left - right, plotHeight = bottom - top;
  const count = visual.x_labels.length;
  const point = (value, index) => `${left + (count === 1 ? 0 : index / (count - 1) * plotWidth)},${bottom - value / 100 * plotHeight}`;
  const paths = visual.series.map((series, seriesIndex) => `<polyline class="series-${seriesIndex ? "b" : "a"}" points="${series.values.map(point).join(" ")}"/>${series.values.map((value, index) => { const [x, y] = point(value, index).split(","); return `<circle cx="${x}" cy="${y}" r="4" fill="${seriesIndex ? "#ffb547" : "#1db6c7"}"/>`; }).join("")}`).join("");
  const grid = [0, 25, 50, 75, 100].map(value => { const y = bottom - value / 100 * plotHeight; return `<line class="grid" x1="${left}" y1="${y}" x2="${width-right}" y2="${y}"/><text x="8" y="${y+4}">${value}</text>`; }).join("");
  const labels = visual.x_labels.map((label, index) => `<text text-anchor="middle" x="${left + (count === 1 ? 0 : index / (count - 1) * plotWidth)}" y="229">${esc(label)}</text>`).join("");
  return `<div class="visual-canvas"><div class="visual-legend">${visual.series.map(series => `<span><i></i>${esc(series.label)}</span>`).join("")}</div><svg class="visual-plot" viewBox="0 0 ${width} ${height}" role="img" aria-label="${esc(visual.title)}"><line class="axis" x1="${left}" y1="${bottom}" x2="${width-right}" y2="${bottom}"/><line class="axis" x1="${left}" y1="${top}" x2="${left}" y2="${bottom}"/>${grid}${paths}${labels}<text text-anchor="middle" x="${left+plotWidth/2}" y="251">${esc(visual.x_label)}</text></svg></div>`;
}

function renderRoadmap() {
  syncPhaseProgress();
  const courseComplete = state.courseOrder.filter(tutorial => state.mastered.has(tutorial.topic_id)).length;
  const percent = state.courseOrder.length ? Math.round(courseComplete / state.courseOrder.length * 100) : 0;
  const current = state.roadmap.find(phase => phaseTutorials(phase).some(tutorial => !state.mastered.has(tutorial.topic_id)));
  $("#roadmapPercent").textContent = `${percent}%`;
  $("#roadmapBar").style.width = `${percent}%`;
  $("#currentPhase").innerHTML = current ? `<strong>Study now:</strong> ${esc(current.title)} · ${courseComplete}/${state.courseOrder.length} chapters passed` : "<strong>Guided chapters complete.</strong> Continue with the integrated system-design and mock-interview milestones.";
  $("#roadmapFlow").innerHTML = state.roadmap.map(phase => {
    const lessons = phaseTutorials(phase), doneCount = lessons.filter(tutorial => state.mastered.has(tutorial.topic_id)).length;
    const done = lessons.length ? doneCount === lessons.length : state.phases.has(phase.id);
    const isCurrent = current?.id === phase.id;
    const locked = phase.prerequisites.some(id => {
      const prerequisite = state.roadmap.find(item => item.id === id);
      return prerequisite && phaseTutorials(prerequisite).length && !state.phases.has(id);
    });
    return `<div class="roadmap-node ${done ? "done" : ""} ${isCurrent ? "current" : ""} ${locked ? "locked" : ""}"><small>${String(phase.order).padStart(2, "0")} · ${phase.hours}H</small><strong>${esc(phase.title)}</strong>${lessons.length ? `<small>${doneCount}/${lessons.length} chapters</small>` : ""}</div>`;
  }).join("");
  $("#roadmapList").innerHTML = state.roadmap.map(phase => {
    const lessons = phaseTutorials(phase), doneCount = lessons.filter(tutorial => state.mastered.has(tutorial.topic_id)).length;
    const done = lessons.length ? doneCount === lessons.length : state.phases.has(phase.id);
    const isCurrent = current?.id === phase.id;
    const missing = phase.prerequisites.filter(id => {
      const prerequisite = state.roadmap.find(item => item.id === id);
      return prerequisite && phaseTutorials(prerequisite).length && !state.phases.has(id);
    });
    const status = lessons.length ? (done ? "Completed automatically" : `${doneCount}/${lessons.length} chapter exams passed`) : "Hands-on checkpoint";
    return `<article class="phase-card ${done ? "done" : ""} ${isCurrent ? "current" : ""}"><div class="phase-number">${String(phase.order).padStart(2, "0")}</div><div><h3>${esc(phase.title)}</h3><div class="phase-meta"><span class="badge">${phase.hours} hours</span><span class="badge">${lessons.length || "integrated"} chapters</span>${missing.length ? `<span class="badge">after ${missing.map(esc).join(", ")}</span>` : ""}</div><p><strong>Milestone.</strong> ${esc(phase.milestone)}</p><ul>${phase.outcomes.map(outcome => `<li>${esc(outcome)}</li>`).join("")}</ul><p><strong>Practice.</strong> ${esc(phase.practice)}</p></div><div class="phase-actions"><span class="auto-state">${esc(status)}</span>${lessons.length ? `<button data-phase-topic="${esc((lessons.find(tutorial => !state.mastered.has(tutorial.topic_id)) || lessons.at(-1)).topic_id)}">${done ? "Review" : "Continue"}</button>` : ""}</div></article>`;
  }).join("");
  $$("#roadmapList [data-phase-topic]").forEach(button => { button.onclick = () => resumeLesson(button.dataset.phaseTopic); });
}

function filteredTutorials() {
  const category = $("#tutorialCategory").value;
  const query = $("#globalSearch").value.trim().toLowerCase();
  return state.courseOrder.filter(tutorial => (!category || tutorial.category === category) && (!query || (tutorial.name + " " + tutorial.first_principles + " " + tutorial.decision_reasoning + " " + tutorial.failure_reasoning).toLowerCase().includes(query)));
}
function renderTutorialControls() {
  const tutorials = filteredTutorials();
  if (!tutorials.some(tutorial => tutorial.topic_id === state.activeTutorial)) state.activeTutorial = tutorials[0]?.topic_id || null;
  $("#tutorialTopic").innerHTML = tutorials.map(tutorial => `<option value="${esc(tutorial.topic_id)}" ${tutorial.topic_id === state.activeTutorial ? "selected" : ""}>${esc(tutorial.name)}</option>`).join("");
  $("#tutorialIndex").innerHTML = tutorials.map(tutorial => {
    const icon = state.mastered.has(tutorial.topic_id) ? "✓ " : readSet(tutorial.topic_id).size ? "◔ " : "";
    return `<button class="lesson-link ${tutorial.topic_id === state.activeTutorial ? "active" : ""}" data-topic="${esc(tutorial.topic_id)}">${icon}${esc(tutorial.name)}</button>`;
  }).join("") || "<p class=\"empty\">No lesson matches.</p>";
  $$("#tutorialIndex [data-topic]").forEach(button => { button.onclick = () => selectTutorial(button.dataset.topic); });
  renderTutorial();
}
$("#tutorialCategory").onchange = renderTutorialControls;
$("#tutorialTopic").onchange = event => selectTutorial(event.target.value);
function selectTutorial(id, updateRoute = true) {
  if (!state.tutorials.some(tutorial => tutorial.topic_id === id)) return;
  state.activeTutorial = id;
  state.lastTopic = id;
  state.activeExam = null;
  localStorage.setItem("atlas-last-topic-v2", id);
  syncPhaseProgress();
  $$("#tutorialIndex .lesson-link").forEach(button => button.classList.toggle("active", button.dataset.topic === id));
  if ($("#tutorialTopic")) $("#tutorialTopic").value = id;
  renderTutorial();
  renderLearn();
  if (updateRoute) history.replaceState(null, "", `#tutorial/${id}`);
}
function lessonSection(id, title, bodyHtml) {
  const read = readSet(state.activeTutorial).has(id);
  return `<section class="lesson-section" data-read-section="${id}"><h4>${esc(title)}</h4>${bodyHtml}<div class="read-sentinel ${read ? "read" : ""}" data-read-sentinel="${id}">${read ? "Part learned" : "Reading checkpoint"}</div></section>`;
}
function renderTutorial() {
  const tutorial = state.tutorials.find(item => item.topic_id === state.activeTutorial);
  if (!tutorial) { $("#tutorialLesson").innerHTML = "<p class=\"empty\">Choose a lesson.</p>"; return; }
  if (state.readingObserver) state.readingObserver.disconnect();
  const formulas = tutorial.formula_ids.map(id => state.formulas.find(formula => formula.id === id)).filter(Boolean);
  const formulaHtml = formulas.length ? formulas.map(formula => `<section class="formula-card"><h5>${esc(formula.title)}</h5><div class="formula-display">\\[${formula.latex}\\]</div><p><strong>Variables.</strong> ${formula.variables.map(esc).join(" · ")}</p>${formula.derivation.map((step, index) => `<div class="derivation-step"><b>${index + 1}</b><div><p>${esc(step.text)}</p><div>\\[${step.latex}\\]</div></div></div>`).join("")}<p><strong>Worked interpretation.</strong> ${esc(formula.example)}</p></section>`).join("") : "<p class=\"coverage-note\">This topic is evaluated with an explicit workload and SLO model rather than a single canonical equation. Quantify arrival rate, volume, service time, quality, cost, and error budget.</p>";
  const visual = state.visuals.find(item => item.topic_ids.includes(tutorial.topic_id)) || state.visuals.find(item => item.category === tutorial.category);
  const read = readSet(tutorial.topic_id);
  const percent = Math.round(read.size / READ_PARTS.length * 100);
  const number = state.courseOrder.findIndex(item => item.topic_id === tutorial.topic_id) + 1;
  const phase = phaseForTutorial(tutorial);
  $("#tutorialLesson").innerHTML = `<header class="lesson-hero"><div><span class="cat">${esc(tutorial.category)}</span><h3>${esc(tutorial.name)}</h3><p>${esc(tutorial.objective)}</p></div><div class="lesson-status"><strong>${state.mastered.has(tutorial.topic_id) ? "Chapter passed ✓" : `${read.size}/5 parts read`}</strong><small>Chapter ${number} of ${state.courseOrder.length} · Phase ${String(phase?.order ?? "-").padStart(2, "0")}</small><div class="reading-meter"><i style="width:${state.mastered.has(tutorial.topic_id) ? 100 : percent}%"></i></div></div></header>
    ${visual ? renderVisual(visual) : ""}
    ${lessonSection("principles", "First principles", `<p>${esc(tutorial.first_principles)}</p><p>${esc(tutorial.mental_model)}</p>`)}
    ${lessonSection("math", "Mathematics and quantitative reasoning", `<p>${esc(tutorial.quantitative_reasoning)}</p>${formulaHtml}`)}
    ${lessonSection("decision", "Decision and failure reasoning", `<p>${esc(tutorial.decision_reasoning)}</p><p>${esc(tutorial.failure_reasoning)}</p>`)}
    ${lessonSection("production", "Worked production method", `<ol>${tutorial.worked_reasoning.map(item => `<li>${esc(item)}</li>`).join("")}</ol><div class="answer-grid"><div><strong>Evaluate</strong><ul>${tutorial.evaluation.map(item => `<li>${esc(item)}</li>`).join("")}</ul></div><div><strong>Operate</strong><ul>${tutorial.operations.map(item => `<li>${esc(item)}</li>`).join("")}</ul></div></div>`)}
    ${lessonSection("blueprint", "Interview answer blueprint", `<div class="answer-grid">${Object.entries(tutorial.answer_blueprint).map(([key, value]) => `<div><strong>${esc(key.replace("_", " "))}</strong><span>${esc(value)}</span></div>`).join("")}</div><p class="coverage-note">${esc(tutorial.question_coverage)}</p>`)}
    <section id="chapterExam" class="chapter-exam"></section>`;
  observeReading(tutorial);
  renderExam(tutorial);
  typeset($("#tutorialLesson"));
}
function observeReading(tutorial) {
  state.readingObserver = new IntersectionObserver(entries => {
    entries.filter(entry => entry.isIntersecting).forEach(entry => markSectionRead(tutorial.topic_id, entry.target.dataset.readSentinel));
  }, {threshold: 0.65, rootMargin: "0px 0px -8% 0px"});
  $$("#tutorialLesson [data-read-sentinel]").forEach(sentinel => state.readingObserver.observe(sentinel));
}
function markSectionRead(topicId, part) {
  if (!READ_PARTS.includes(part)) return;
  const parts = readSet(topicId);
  if (parts.has(part)) return;
  parts.add(part);
  state.reading[topicId] = [...parts];
  localStorage.setItem("atlas-reading-v2", JSON.stringify(state.reading));
  const sentinel = $(`[data-read-sentinel="${part}"]`);
  if (sentinel) { sentinel.classList.add("read"); sentinel.textContent = "Part learned"; }
  const tutorial = state.tutorials.find(item => item.topic_id === topicId);
  updateLessonStatus(tutorial);
  renderExam(tutorial);
  renderLearn();
}
function updateLessonStatus(tutorial) {
  if (!tutorial || tutorial.topic_id !== state.activeTutorial) return;
  const count = readSet(tutorial.topic_id).size;
  const status = $(".lesson-status strong"), meter = $(".lesson-status i");
  if (status) status.textContent = state.mastered.has(tutorial.topic_id) ? "Chapter passed ✓" : `${count}/5 parts read`;
  if (meter) meter.style.width = `${state.mastered.has(tutorial.topic_id) ? 100 : count / READ_PARTS.length * 100}%`;
}
function topicExamPool(topicId) {
  return state.questions.filter(question => question.tutorial_id === topicId && question.type === "mcq" && question.options?.length === 4);
}
function startChapterExam(tutorial) {
  const pool = topicExamPool(tutorial.topic_id);
  const attempt = (state.examAttempts[tutorial.topic_id] || 0) + 1;
  state.examAttempts[tutorial.topic_id] = attempt;
  localStorage.setItem("atlas-exam-attempts-v2", JSON.stringify(state.examAttempts));
  const offset = ((attempt - 1) * 2) % pool.length;
  const questions = Array.from({length: Math.min(5, pool.length)}, (_, index) => pool[(offset + index) % pool.length]);
  state.activeExam = {topicId: tutorial.topic_id, questions, submitted: false, answers: [], score: 0};
  renderExam(tutorial);
  $("#chapterExam").scrollIntoView({behavior: "smooth", block: "start"});
}
function renderExam(tutorial) {
  const container = $("#chapterExam");
  if (!container || tutorial.topic_id !== state.activeTutorial) return;
  const ready = readSet(tutorial.topic_id).size === READ_PARTS.length;
  const best = state.examScores[tutorial.topic_id] || 0;
  const exam = state.activeExam?.topicId === tutorial.topic_id ? state.activeExam : null;
  if (state.mastered.has(tutorial.topic_id) && !exam) {
    const next = nextTutorial(tutorial.topic_id);
    container.innerHTML = `<div class="exam-head"><div><p class="eyebrow">CHAPTER COMPLETE</p><h4>${best ? `Exam passed · best score ${best}%` : "Previously completed"}</h4><p>Reading and exam evidence are saved on this device. The roadmap phase updates automatically.</p></div>${next ? `<button id="nextLesson">Continue to ${esc(next.name)} →</button>` : ""}</div>`;
    if (next) $("#nextLesson").onclick = () => selectTutorial(next.topic_id);
    return;
  }
  if (!exam) {
    container.innerHTML = `<div class="exam-head"><div><p class="eyebrow">CHAPTER EXAM</p><h4>${ready ? "Ready for active recall" : "Finish the five reading parts to unlock"}</h4><p>Five four-option questions · pass at ${PASS_SCORE}% · explanations appear after submission.</p></div><button id="startExam" ${ready ? "" : "disabled"}>${best ? `Retry · best ${best}%` : "Start exam"}</button></div>`;
    $("#startExam").onclick = () => startChapterExam(tutorial);
    return;
  }
  const questionHtml = exam.questions.map((question, qIndex) => `<fieldset class="exam-question"><legend><h5>${qIndex + 1}. ${esc(question.prompt)}</h5></legend>${question.options.map((option, optionIndex) => {
    const chosen = exam.answers[qIndex] === optionIndex;
    const correct = exam.submitted && option === question.answer;
    const wrong = exam.submitted && chosen && option !== question.answer;
    return `<label class="exam-choice ${correct ? "correct" : ""} ${wrong ? "wrong" : ""}"><input type="radio" name="exam-q-${qIndex}" value="${optionIndex}" ${chosen ? "checked" : ""} ${exam.submitted ? "disabled" : ""}><span>${String.fromCharCode(65 + optionIndex)}. ${esc(option)}</span></label>`;
  }).join("")}${exam.submitted ? `<p class="${exam.answers[qIndex] !== question.options.indexOf(question.answer) ? "exam-correction" : ""}"><strong>Answer:</strong> ${esc(question.answer)}<br>${esc(question.explanation || "")}</p>` : ""}</fieldset>`).join("");
  const result = exam.submitted ? `<div class="exam-result ${exam.score >= PASS_SCORE ? "pass" : "fail"}"><h4>${exam.score >= PASS_SCORE ? "Passed - chapter learned" : "Not passed yet"} · ${exam.score}%</h4><p>${exam.score >= PASS_SCORE ? "The chapter and its roadmap progress were updated automatically." : "Review the highlighted corrections, then retry with a rotated question set."}</p></div>` : "";
  container.innerHTML = `<div class="exam-head"><div><p class="eyebrow">CHAPTER EXAM</p><h4>${esc(tutorial.name)}</h4><p>Answer all five questions before submitting.</p></div><span class="badge">Attempt ${state.examAttempts[tutorial.topic_id]}</span></div><div class="exam-body">${questionHtml}<p id="examMessage" role="status"></p>${result}<div class="exam-actions">${exam.submitted ? (exam.score >= PASS_SCORE ? `<button class="next-lesson" id="continueAfterPass">Continue to next lesson →</button>` : `<button class="exam-submit" id="retryExam">Review lesson and retry</button>`) : `<button class="exam-submit" id="submitExam">Submit exam</button>`}</div></div>`;
  if (!exam.submitted) $("#submitExam").onclick = () => submitChapterExam(tutorial);
  else if (exam.score >= PASS_SCORE) $("#continueAfterPass").onclick = () => { const next = nextTutorial(tutorial.topic_id); if (next) selectTutorial(next.topic_id); else showView("learn"); };
  else $("#retryExam").onclick = () => { state.activeExam = null; renderExam(tutorial); $("#chapterExam").scrollIntoView({behavior: "smooth"}); };
}
function submitChapterExam(tutorial) {
  const exam = state.activeExam;
  exam.answers = exam.questions.map((_, index) => {
    const checked = $(`input[name="exam-q-${index}"]:checked`);
    return checked ? Number(checked.value) : null;
  });
  if (exam.answers.some(answer => answer === null)) { $("#examMessage").textContent = "Answer every question before submitting."; return; }
  const correct = exam.questions.filter((question, index) => question.options[exam.answers[index]] === question.answer).length;
  exam.score = Math.round(correct / exam.questions.length * 100);
  exam.submitted = true;
  state.examScores[tutorial.topic_id] = Math.max(state.examScores[tutorial.topic_id] || 0, exam.score);
  localStorage.setItem("atlas-exam-scores-v2", JSON.stringify(state.examScores));
  if (exam.score >= PASS_SCORE) {
    state.mastered.add(tutorial.topic_id);
    persistSet("atlas-mastered", state.mastered);
    syncPhaseProgress();
  }
  renderExam(tutorial);
  updateLessonStatus(tutorial);
  renderLearn();
  renderRoadmap();
  renderTutorialIndexState();
}
function renderTutorialIndexState() {
  $$("#tutorialIndex [data-topic]").forEach(button => {
    const tutorial = state.tutorials.find(item => item.topic_id === button.dataset.topic);
    if (!tutorial) return;
    const prefix = state.mastered.has(tutorial.topic_id) ? "✓ " : readSet(tutorial.topic_id).size ? "◔ " : "";
    button.textContent = prefix + tutorial.name;
  });
}

function technologySearchText(technology) {
  return [technology.name, technology.category, technology.kind, technology.languages.join(" "), technology.deployment,
    technology.summary, technology.choose_when, technology.avoid_when, technology.failure_mode,
    technology.alternatives.join(" "), technology.flow.join(" ")].join(" ").toLowerCase();
}
function technologyFlow(technology, compact = false) {
  return `<div class="tech-flow ${compact ? "compact" : ""}" role="img" aria-label="${esc(technology.name)}: ${esc(technology.flow.join(" to "))}">${technology.flow.map((step, index) => `${index ? '<span class="tech-arrow" aria-hidden="true">→</span>' : ""}<span class="tech-node">${esc(step)}</span>`).join("")}</div>`;
}
function technologyDesign(technology) {
  const candidates = new Set([technology.id.toLowerCase(), technology.name.toLowerCase()]);
  if (technology.id === "mcp") candidates.add("mcp");
  if (technology.id === "triton-inference-server") candidates.add("nvidia triton inference server");
  return state.designs.find(design => (design.tool_choices || []).some(choice => {
    const normalized = choice.toLowerCase();
    return candidates.has(normalized) || technology.name.toLowerCase().includes(normalized) || normalized.includes(technology.name.toLowerCase());
  }));
}
function bindTechnologyLogos() {
  $$(".tech-logo img").forEach(image => {
    const showFallback = () => {
      image.hidden = true;
      const fallback = image.nextElementSibling;
      if (fallback) fallback.hidden = false;
    };
    image.addEventListener("error", showFallback, {once: true});
    if (image.complete && !image.naturalWidth) showFallback();
  });
}
function renderTechnologyComparison() {
  const categoryId = $("#comparisonCategory").value || state.technologyCategories[0]?.id;
  if (!categoryId) return;
  $("#comparisonCategory").value = categoryId;
  const category = state.technologyCategories.find(item => item.id === categoryId);
  const technologies = state.technologies.filter(technology => technology.category_id === categoryId);
  $("#technologyComparison").innerHTML = `<p class="comparison-question"><strong>Decision question:</strong> ${esc(category.question)}</p><div class="table-scroll"><table><caption>${esc(category.title)} comparison</caption><thead><tr><th>Technology</th><th>Kind</th><th>Languages</th><th>Deployment boundary</th><th>Choose when</th><th>Reject when</th></tr></thead><tbody>${technologies.map(technology => `<tr><th scope="row"><button class="table-tech-link" data-compare-tech="${esc(technology.id)}">${esc(technology.name)}</button></th><td>${esc(technology.kind)}</td><td>${esc(technology.languages.join(", "))}</td><td>${esc(technology.deployment)}</td><td>${esc(technology.choose_when)}</td><td>${esc(technology.avoid_when)}</td></tr>`).join("")}</tbody></table></div>`;
  $$("[data-compare-tech]").forEach(button => { button.onclick = () => selectTechnology(button.dataset.compareTech); });
}
function renderTechnologies() {
  const categoryId = $("#technologyCategory").value;
  const kind = $("#technologyKind").value;
  const query = $("#globalSearch").value.trim().toLowerCase();
  const technologies = state.technologies.filter(technology => (!categoryId || technology.category_id === categoryId)
    && (!kind || technology.kind === kind) && (!query || technologySearchText(technology).includes(query)));
  const categoryCounts = state.technologyCategories.map(category => ({...category, count: state.technologies.filter(technology => technology.category_id === category.id).length}));
  $("#technologyStats").innerHTML = `<article><strong>${state.technologies.length}</strong><span>technology profiles</span></article><article><strong>${state.technologyCategories.length}</strong><span>stack layers</span></article><article><strong>${state.technologyQuestions.length}</strong><span>tiered questions</span></article><article><strong>${state.designs.filter(design => design.tool_choices?.length).length}</strong><span>tool-centered designs</span></article>`;
  $("#technologyLandscape").innerHTML = categoryCounts.map(category => `<article class="technology-layer" data-layer="${esc(category.id)}"><header><span>${String(category.order).padStart(2, "0")}</span><div><h3>${esc(category.title)}</h3><p>${category.count} profiles · ${esc(category.question)}</p></div></header><div class="layer-flow"><span>${esc(category.need)}</span><b>→</b><span>${esc(category.mechanism)}</span><b>→</b><span>${esc(category.result)}</span></div></article>`).join("");
  $$("[data-layer]").forEach(card => { card.onclick = () => { $("#technologyCategory").value = card.dataset.layer; $("#comparisonCategory").value = card.dataset.layer; renderTechnologies(); }; });
  $("#technologyCount").textContent = `${technologies.length} of ${state.technologies.length} profiles`;
  $("#technologyGrid").innerHTML = technologies.length ? technologies.map(technology => {
    const design = technologyDesign(technology);
    return `<details class="technology-card" id="technology-${esc(technology.id)}" data-technology-card="${esc(technology.id)}"><summary><span class="tech-logo"><img src="${esc(technology.logo_url)}" alt="${esc(technology.name)} logo" loading="lazy"><span hidden aria-hidden="true">${esc(technology.logo_fallback)}</span></span><span class="tech-title"><span class="cat">${esc(technology.category)}</span><strong>${esc(technology.name)}</strong><small>${esc(technology.kind)}</small></span><span class="card-chevron" aria-hidden="true">＋</span></summary><div class="technology-body"><p class="tech-summary">${esc(technology.summary)}</p><div class="tech-badges"><span>${esc(technology.languages.join(" · "))}</span><span>${esc(technology.deployment)}</span></div><h4>Abstract execution path</h4>${technologyFlow(technology)}<div class="selection-grid"><div><strong>Choose when</strong><p>${esc(technology.choose_when)}</p></div><div><strong>Reject when</strong><p>${esc(technology.avoid_when)}</p></div><div><strong>Primary failure</strong><p>${esc(technology.failure_mode)}</p></div><div><strong>Compare with</strong><p>${esc(technology.alternatives.join(" · "))}</p></div></div><details class="tech-quickstart"><summary>Language and minimal use</summary><pre><code>${esc(technology.quickstart)}</code></pre><p>Start with the linked official documentation; APIs and version support change faster than this conceptual guide.</p></details><div class="tech-actions"><a href="${esc(technology.source_url)}" target="_blank" rel="noreferrer">Official documentation ↗</a><button data-tech-practice="${esc(technology.id)}">Practice medium → very hard</button>${design ? `<button data-tech-design="${esc(design.id)}">Open ${esc(design.title)}</button>` : ""}</div></div></details>`;
  }).join("") : '<p class="empty">No technology matches this layer, kind, and search query.</p>';
  bindTechnologyLogos();
  $$("[data-technology-card]").forEach(card => { card.addEventListener("toggle", () => { if (card.open) history.replaceState(null, "", `#toolbox/${card.dataset.technologyCard}`); }); });
  $$("[data-tech-practice]").forEach(button => { button.onclick = event => {
    event.preventDefault(); event.stopPropagation();
    $("#qCategory").value = "Libraries and Technologies"; $("#qTechnology").value = button.dataset.techPractice; $("#qDifficulty").value = ""; $("#qType").value = "";
    showView("practice"); applyQuestionFilters();
  }; });
  $$("[data-tech-design]").forEach(button => { button.onclick = event => {
    event.preventDefault(); event.stopPropagation();
    const design = state.designs.find(item => item.id === button.dataset.techDesign);
    $("#globalSearch").value = design?.title || ""; renderDesigns(); showView("design");
  }; });
  renderTechnologyComparison();
}
function selectTechnology(id, updateRoute = true) {
  const technology = state.technologies.find(item => item.id === id);
  if (!technology) return;
  $("#technologyCategory").value = technology.category_id;
  $("#technologyKind").value = "";
  $("#globalSearch").value = "";
  renderTechnologies();
  const card = $(`#technology-${id}`);
  if (card) {
    card.open = true;
    window.setTimeout(() => card.scrollIntoView({behavior: "smooth", block: "start"}), 160);
  }
  if (updateRoute) history.replaceState(null, "", `#toolbox/${id}`);
}
$("#technologyCategory").onchange = event => {
  if (event.target.value) $("#comparisonCategory").value = event.target.value;
  renderTechnologies();
};
$("#technologyKind").onchange = renderTechnologies;
$("#comparisonCategory").onchange = renderTechnologyComparison;

function renderTopics() {
  const category = $("#topicCategory").value, query = $("#globalSearch").value.trim().toLowerCase();
  const topics = state.topics.filter(topic => (!category || topic.category === category) && (!query || (topic.name + " " + topic.summary + " " + topic.tradeoff + " " + topic.pitfall).toLowerCase().includes(query)));
  $("#topicGrid").innerHTML = topics.length ? topics.map(topic => `<article class="topic-card"><span class="cat">${esc(topic.category)}</span><h3>${esc(topic.name)}</h3><p>${esc(topic.summary)}</p><dl><dt>Tradeoff</dt><dd>${esc(topic.tradeoff)}</dd><dt>Production failure</dt><dd>${esc(topic.pitfall)}</dd></dl><div class="topic-actions"><button data-topic="${esc(topic.id)}">Open deep tutorial →</button></div></article>`).join("") : "<p class=\"empty\">No topics match this filter.</p>";
  $$("#topicGrid [data-topic]").forEach(button => { button.onclick = () => showView("tutorial", button.dataset.topic); });
}
$("#topicCategory").onchange = renderTopics;

function applyQuestionFilters() {
  const type = $("#qType").value, difficulty = $("#qDifficulty").value, category = $("#qCategory").value, technologyId = $("#qTechnology").value, query = $("#globalSearch").value.trim().toLowerCase();
  state.pool = state.questions.filter(question => (!type || question.type === type) && (!difficulty || question.difficulty === difficulty)
    && (!category || question.category === category) && (!technologyId || question.technology_id === technologyId)
    && (!query || (question.prompt + " " + question.topic + " " + question.category + " " + (question.technology_category || "")).toLowerCase().includes(query)));
  state.index = 0; renderQuestion();
}
["#qType", "#qDifficulty"].forEach(selector => { $(selector).onchange = applyQuestionFilters; });
$("#qCategory").onchange = event => {
  if (event.target.value !== "Libraries and Technologies") $("#qTechnology").value = "";
  applyQuestionFilters();
};
$("#qTechnology").onchange = event => {
  if (event.target.value) $("#qCategory").value = "Libraries and Technologies";
  applyQuestionFilters();
};
function renderQuestion() {
  const element = $("#questionCard"); $("#seenCount").textContent = state.seen.size; $("#poolCount").textContent = `${state.pool.length.toLocaleString()} questions in this pool`;
  if (!state.pool.length) { element.innerHTML = "<p class=\"empty\">No questions match this filter.</p>"; return; }
  const question = state.pool[state.index % state.pool.length];
  const options = question.options ? `<div class="options">${question.options.map((option, index) => `<button class="option" data-value="${esc(option)}"><b>${String.fromCharCode(65 + index)}</b><span>${esc(option)}</span></button>`).join("")}</div>` : "";
  element.innerHTML = `<div class="badges"><span class="badge">${esc(question.id)}</span><span class="badge">${esc(question.type)}</span><span class="badge">${esc(question.difficulty)}</span></div><span class="cat">${esc(question.category)} · ${esc(question.topic)}</span><h3>${esc(question.prompt)}</h3>${options}<div id="answerBox"></div><div class="question-actions"><button id="reveal">Reveal answer</button><button id="next" class="secondary">Next question →</button></div>`;
  $$(".option").forEach(button => { button.onclick = () => grade(button, question); });
  $("#reveal").onclick = () => reveal(question);
  $("#next").onclick = () => { markSeen(question); state.index = (state.index + 1) % state.pool.length; renderQuestion(); };
}
function grade(button, question) { $$(".option").forEach(option => { option.disabled = true; option.classList.toggle("correct", option.dataset.value === question.answer); }); if (button.dataset.value !== question.answer) button.classList.add("wrong"); reveal(question); }
function reveal(question) {
  const target = question.technology_id ? `#toolbox/${question.technology_id}` : `#tutorial/${question.tutorial_id}`;
  const label = question.technology_id ? "Open the technology profile and comparison" : "Study the full lesson and derivation";
  $("#answerBox").innerHTML = `<div class="answer"><strong>Answer</strong><p>${esc(question.answer)}</p><small>${esc(question.explanation || "")}</small><a class="deep-link" href="${esc(target)}">${label} →</a></div>`;
  $("#answerBox .deep-link").onclick = event => { event.preventDefault(); showView(question.technology_id ? "toolbox" : "tutorial", question.technology_id || question.tutorial_id); };
  markSeen(question);
}
function markSeen(question) { state.seen.add(question.id); persistSet("atlas-seen", state.seen); $("#seenCount").textContent = state.seen.size; }
$("#shuffleBtn").onclick = () => { state.pool.sort(() => Math.random() - .5); state.index = 0; renderQuestion(); };
$("#resetBtn").onclick = () => { state.seen.clear(); localStorage.removeItem("atlas-seen"); renderQuestion(); };

function renderCore() {
  const query = $("#globalSearch").value.trim().toLowerCase();
  const items = state.core.filter(item => !query || (item.prompt + " " + item.answer + " " + item.category).toLowerCase().includes(query));
  $("#coreList").innerHTML = items.map(item => `<details class="qa"><summary><span class="badge">${esc(item.id)} · ${esc(item.difficulty)}</span><strong>${esc(item.prompt)}</strong><span class="badge">${esc(item.origin)}</span></summary><div class="qa-answer"><p>${esc(item.answer)}</p><small>${esc(item.category)}</small></div></details>`).join("");
}
function wrapSvgLabel(label, limit = 22) {
  const words = label.split(/\s+/), lines = [];
  words.forEach(word => {
    const current = lines.at(-1) || "";
    if (!current || `${current} ${word}`.length > limit) lines.push(word);
    else lines[lines.length - 1] = `${current} ${word}`;
  });
  return lines.slice(0, 3);
}
function renderDesignDiagram(design) {
  const labels = new Map();
  for (const match of design.diagram.matchAll(/([A-Za-z0-9_]+)\[([^\]]+)\]/g)) if (!labels.has(match[1])) labels.set(match[1], match[2]);
  for (const match of design.diagram.matchAll(/([A-Za-z0-9_]+)\{([^}]+)\}/g)) if (!labels.has(match[1])) labels.set(match[1], match[2]);
  const edges = [...design.diagram.matchAll(/([A-Za-z0-9_]+)(?:\[[^\]]+\]|\{[^}]+\})?\s*-->(?:\|[^|]*\|)?\s*([A-Za-z0-9_]+)/g)]
    .map(match => [match[1], match[2]]).filter(([left, right]) => labels.has(left) && labels.has(right));
  if (!labels.size) return '<div class="case-diagram"><div class="node">Architecture sketch unavailable</div></div>';
  const incoming = new Map([...labels.keys()].map(id => [id, 0]));
  const children = new Map([...labels.keys()].map(id => [id, []]));
  edges.forEach(([left, right]) => { incoming.set(right, incoming.get(right) + 1); children.get(left).push(right); });
  const depth = new Map([...labels.keys()].map(id => [id, 0]));
  const queue = [...labels.keys()].filter(id => incoming.get(id) === 0), visited = new Set();
  while (queue.length) {
    const id = queue.shift(); visited.add(id);
    children.get(id).forEach(child => {
      depth.set(child, Math.max(depth.get(child), depth.get(id) + 1));
      incoming.set(child, incoming.get(child) - 1);
      if (incoming.get(child) === 0) queue.push(child);
    });
  }
  [...labels.keys()].filter(id => !visited.has(id)).forEach(id => depth.set(id, Math.max(...depth.values()) + 1));
  const layers = new Map();
  [...labels.keys()].forEach(id => { const layer = depth.get(id); if (!layers.has(layer)) layers.set(layer, []); layers.get(layer).push(id); });
  const width = 760, top = 36, layerHeight = 112, boxHeight = 58;
  const height = top * 2 + (Math.max(...layers.keys()) + 1) * layerHeight;
  const positions = new Map();
  [...layers.entries()].forEach(([layer, ids]) => ids.forEach((id, index) => positions.set(id, {x: (index + 1) * width / (ids.length + 1), y: top + layer * layerHeight})));
  const maxInLayer = Math.max(...[...layers.values()].map(ids => ids.length));
  const boxWidth = Math.min(190, Math.max(105, width / (maxInLayer + 1) - 18));
  const markerId = `arrow-${design.id.replace(/[^a-z0-9]/gi, "")}`;
  const edgeSvg = edges.map(([left, right]) => {
    const from = positions.get(left), to = positions.get(right);
    return `<path d="M ${from.x} ${from.y + boxHeight / 2} C ${from.x} ${from.y + 78}, ${to.x} ${to.y - 48}, ${to.x} ${to.y - boxHeight / 2}" marker-end="url(#${markerId})"/>`;
  }).join("");
  const nodeSvg = [...labels.entries()].map(([id, label]) => {
    const point = positions.get(id), lines = wrapSvgLabel(label);
    const firstY = point.y - (lines.length - 1) * 8;
    return `<g><rect x="${point.x - boxWidth / 2}" y="${point.y - boxHeight / 2}" width="${boxWidth}" height="${boxHeight}" rx="9"/>` +
      `<text x="${point.x}" y="${firstY}" text-anchor="middle">${lines.map((line, index) => `<tspan x="${point.x}" dy="${index ? 17 : 0}">${esc(line)}</tspan>`).join("")}</text></g>`;
  }).join("");
  return `<div class="case-diagram-svg"><svg viewBox="0 0 ${width} ${height}" role="img" aria-label="Architecture for ${esc(design.title)}"><defs><marker id="${markerId}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z"/></marker></defs>${edgeSvg}${nodeSvg}</svg></div>`;
}
function renderDesigns() {
  const query = $("#globalSearch").value.trim().toLowerCase();
  const items = state.designs.filter(item => !query || (item.title + " " + item.brief + " " + JSON.stringify(item.stages) + " " + (item.tool_choices || []).join(" ")).toLowerCase().includes(query));
  $("#designList").innerHTML = items.map((design, index) => {
    const toolChoices = design.tool_choices?.length ? `<div class="tool-choice-strip"><strong>Explicit tool choices</strong>${design.tool_choices.map(tool => `<span>${esc(tool)}</span>`).join("")}</div>` : "";
    return `<article class="design-case"><header><div><span class="badge">DESIGN ${String(index + 1).padStart(2, "0")}</span><h3>${esc(design.title)}</h3><p>${esc(design.brief)}</p>${toolChoices}</div><span class="badge">4-stage interview</span></header><div class="case-body">${renderDesignDiagram(design)}<div class="stages">${design.stages.map((stage, stageIndex) => `<div class="stage"><h4>${stageIndex + 1}. ${esc(stage.q)}</h4><p>${esc(stage.a)}</p></div>`).join("")}</div></div></article>`;
  }).join("");
}
function renderSources() {
  const query = $("#globalSearch").value.trim().toLowerCase();
  const items = state.refs.filter(item => !query || (item.title + " " + item.kind).toLowerCase().includes(query));
  $("#sourceGrid").innerHTML = items.map(item => `<a class="source-card" href="${esc(item.url)}" target="_blank" rel="noreferrer"><small>${esc(item.kind)}</small><span>${esc(item.title)}</span></a>`).join("");
}
let searchTimer;
$("#globalSearch").oninput = () => {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => {
    renderTechnologies(); renderTopics(); renderTutorialControls(); renderCore(); renderDesigns(); renderSources(); applyQuestionFilters();
    const query = $("#globalSearch").value.trim().toLowerCase();
    $$("#mindmap li").forEach(item => { item.hidden = Boolean(query && !item.dataset.search.includes(query)); });
  }, 120);
};
document.addEventListener("keydown", event => {
  if (event.key === "/" && document.activeElement.tagName !== "INPUT") { event.preventDefault(); $("#globalSearch").focus(); }
});
