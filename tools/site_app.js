const state={
  topics:[],questions:[],core:[],designs:[],refs:[],tutorials:[],formulas:[],roadmap:[],
  pool:[],index:0,
  seen:new Set(JSON.parse(localStorage.getItem("atlas-seen")||"[]")),
  mastered:new Set(JSON.parse(localStorage.getItem("atlas-mastered")||"[]")),
  phases:new Set(JSON.parse(localStorage.getItem("atlas-roadmap-progress")||"[]")),
  activeTutorial:null
};
const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
const esc=s=>String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const questionFiles=["data/questions_1.json","data/questions_2.json","data/questions_3.json","data/questions_4.json"];
const dataFiles=["data/topics.json","data/core_questions.json","data/designs.json","data/references.json","data/tutorials.json","data/formulas.json","data/roadmap.json",...questionFiles];

Promise.all(dataFiles.map(u=>fetch(u).then(r=>{if(!r.ok)throw new Error(`${u}: ${r.status}`);return r.json()})))
  .then(([topics,core,designs,refs,tutorials,formulas,roadmap,...shards])=>{
    Object.assign(state,{topics,core,designs,refs,tutorials,formulas,roadmap,questions:shards.flat()});
    state.activeTutorial=tutorials[0]?.topic_id||null;
    renderAll(); applyQuestionFilters(); restoreRoute();
  })
  .catch(error=>{$("#main").insertAdjacentHTML("afterbegin",`<p class="error-panel"><strong>Content failed to load.</strong> ${esc(error.message)}</p>`)});

function typeset(node=document.body){
  if(window.MathJax?.typesetPromise)window.MathJax.typesetPromise([node]).catch(()=>{});
}
function showView(id,topicId=null){
  $$('.view').forEach(v=>v.classList.toggle('active',v.id===id));
  $$('nav button').forEach(b=>b.classList.toggle('active',b.dataset.view===id));
  if(id==='tutorial'&&topicId)selectTutorial(topicId,false);
  history.replaceState(null,'',`#${id}${topicId?`/${topicId}`:''}`);
  typeset($(`#${id}`)||document.body);
  scrollTo({top:$('.command').offsetHeight,behavior:'smooth'});
}
$$('nav button').forEach(b=>b.onclick=()=>showView(b.dataset.view));
function restoreRoute(){
  const [view,topicId]=location.hash.replace(/^#/,'').split('/');
  if(view&&$(`#${view}`))showView(view,topicId||null);
}

function renderAll(){renderMap();renderRoadmap();renderTutorialControls();renderTopics();renderCore();renderDesigns();renderSources()}

function renderMap(){
  const groups=state.topics.reduce((a,t)=>((a[t.category]??=[]).push(t),a),{});
  $('#mindmap').innerHTML=Object.entries(groups).map(([category,topics])=>`<details class="branch" open><summary>${esc(category)}<span>${topics.length} topics</span></summary><ul>${topics.map(t=>`<li data-search="${esc((t.name+' '+t.summary).toLowerCase())}"><button class="map-topic-link" data-topic="${esc(t.id)}">${esc(t.name)}</button></li>`).join('')}</ul></details>`).join('');
  $$('#mindmap [data-topic]').forEach(b=>b.onclick=()=>showView('tutorial',b.dataset.topic));
}

function renderRoadmap(){
  const complete=state.roadmap.filter(p=>state.phases.has(p.id));
  const current=state.roadmap.find(p=>!state.phases.has(p.id));
  const pct=state.roadmap.length?Math.round(complete.length/state.roadmap.length*100):0;
  $('#roadmapPercent').textContent=`${pct}%`;
  $('#roadmapBar').style.width=`${pct}%`;
  $('#currentPhase').innerHTML=current?`<strong>Study now:</strong> ${esc(current.title)} · ${current.hours} focused hours`:'<strong>Roadmap complete.</strong> Use the mixed bank and mock designs to maintain recall.';
  $('#roadmapFlow').innerHTML=state.roadmap.map(p=>{
    const done=state.phases.has(p.id),isCurrent=current?.id===p.id;
    const locked=p.prerequisites.some(id=>!state.phases.has(id));
    return `<div class="roadmap-node ${done?'done':''} ${isCurrent?'current':''} ${locked?'locked':''}"><small>${String(p.order).padStart(2,'0')} · ${p.hours}H</small><strong>${esc(p.title)}</strong></div>`;
  }).join('');
  $('#roadmapList').innerHTML=state.roadmap.map(p=>{
    const done=state.phases.has(p.id),isCurrent=current?.id===p.id;
    const missing=p.prerequisites.filter(id=>!state.phases.has(id));
    const topicCount=state.topics.filter(t=>p.categories.includes(t.category)).length;
    return `<article class="phase-card ${isCurrent?'current':''}"><div class="phase-number">${String(p.order).padStart(2,'0')}</div><div><h3>${esc(p.title)}</h3><div class="phase-meta"><span class="badge">${p.hours} hours</span><span class="badge">${topicCount||'integrated'} topics</span>${missing.length?`<span class="badge">after ${missing.map(esc).join(', ')}</span>`:''}</div><p><strong>Milestone.</strong> ${esc(p.milestone)}</p><ul>${p.outcomes.map(x=>`<li>${esc(x)}</li>`).join('')}</ul><p><strong>Practice.</strong> ${esc(p.practice)}</p></div><div class="phase-actions"><button data-phase="${p.id}" class="${done?'done':''}">${done?'Completed ✓':'Mark complete'}</button></div></article>`;
  }).join('');
  $$('#roadmapList [data-phase]').forEach(b=>b.onclick=()=>togglePhase(b.dataset.phase));
}
function togglePhase(id){
  state.phases.has(id)?state.phases.delete(id):state.phases.add(id);
  localStorage.setItem('atlas-roadmap-progress',JSON.stringify([...state.phases]));
  renderRoadmap();
}

function filteredTutorials(){
  const category=$('#tutorialCategory').value;
  const query=$('#globalSearch').value.trim().toLowerCase();
  return state.tutorials.filter(t=>(!category||t.category===category)&&(!query||(t.name+' '+t.first_principles+' '+t.decision_reasoning+' '+t.failure_reasoning).toLowerCase().includes(query)));
}
function renderTutorialControls(){
  const tutorials=filteredTutorials();
  if(!tutorials.some(t=>t.topic_id===state.activeTutorial))state.activeTutorial=tutorials[0]?.topic_id||null;
  $('#tutorialTopic').innerHTML=tutorials.map(t=>`<option value="${esc(t.topic_id)}" ${t.topic_id===state.activeTutorial?'selected':''}>${esc(t.name)}</option>`).join('');
  $('#tutorialIndex').innerHTML=tutorials.map(t=>`<button class="lesson-link ${t.topic_id===state.activeTutorial?'active':''}" data-topic="${esc(t.topic_id)}">${state.mastered.has(t.topic_id)?'✓ ':''}${esc(t.name)}</button>`).join('')||'<p class="empty">No lesson matches.</p>';
  $$('#tutorialIndex [data-topic]').forEach(b=>b.onclick=()=>selectTutorial(b.dataset.topic));
  renderTutorial();
}
$('#tutorialCategory').onchange=renderTutorialControls;
$('#tutorialTopic').onchange=e=>selectTutorial(e.target.value);
function selectTutorial(id,updateRoute=true){
  state.activeTutorial=id; renderTutorialControls();
  if(updateRoute)history.replaceState(null,'',`#tutorial/${id}`);
  typeset($('#tutorialLesson'));
}
function renderTutorial(){
  const t=state.tutorials.find(x=>x.topic_id===state.activeTutorial);
  if(!t){$('#tutorialLesson').innerHTML='<p class="empty">Choose a lesson.</p>';return}
  const formulas=t.formula_ids.map(id=>state.formulas.find(f=>f.id===id)).filter(Boolean);
  const formulaHtml=formulas.length?formulas.map(f=>`<section class="formula-card"><h5>${esc(f.title)}</h5><div class="formula-display">\\[${f.latex}\\]</div><p><strong>Variables.</strong> ${f.variables.map(esc).join(' · ')}</p>${f.derivation.map((s,i)=>`<div class="derivation-step"><b>${i+1}</b><div><p>${esc(s.text)}</p><div>\\[${s.latex}\\]</div></div></div>`).join('')}<p><strong>Worked interpretation.</strong> ${esc(f.example)}</p></section>`).join(''):'<p class="coverage-note">This topic is evaluated with an explicit workload and SLO model rather than a single canonical equation. Quantify arrival rate, volume, service time, quality, cost, and error budget.</p>';
  $('#tutorialLesson').innerHTML=`<header class="lesson-hero"><div><span class="cat">${esc(t.category)}</span><h3>${esc(t.name)}</h3><p>${esc(t.objective)}</p></div><button class="master-button ${state.mastered.has(t.topic_id)?'done':''}" data-master="${esc(t.topic_id)}">${state.mastered.has(t.topic_id)?'Mastered ✓':'Mark mastered'}</button></header><section class="lesson-section"><h4>First principles</h4><p>${esc(t.first_principles)}</p><p>${esc(t.mental_model)}</p></section><section class="lesson-section"><h4>Mathematics and quantitative reasoning</h4><p>${esc(t.quantitative_reasoning)}</p>${formulaHtml}</section><section class="lesson-section"><h4>Decision and failure reasoning</h4><p>${esc(t.decision_reasoning)}</p><p>${esc(t.failure_reasoning)}</p></section><section class="lesson-section"><h4>Worked production method</h4><ol>${t.worked_reasoning.map(x=>`<li>${esc(x)}</li>`).join('')}</ol><div class="answer-grid"><div><strong>Evaluate</strong><ul>${t.evaluation.map(x=>`<li>${esc(x)}</li>`).join('')}</ul></div><div><strong>Operate</strong><ul>${t.operations.map(x=>`<li>${esc(x)}</li>`).join('')}</ul></div></div></section><section class="lesson-section"><h4>Interview answer blueprint</h4><div class="answer-grid">${Object.entries(t.answer_blueprint).map(([k,v])=>`<div><strong>${esc(k.replace('_',' '))}</strong><span>${esc(v)}</span></div>`).join('')}</div><p class="coverage-note">${esc(t.question_coverage)}</p></section>`;
  $('[data-master]').onclick=()=>toggleMastered(t.topic_id);
  typeset($('#tutorialLesson'));
}
function toggleMastered(id){
  state.mastered.has(id)?state.mastered.delete(id):state.mastered.add(id);
  localStorage.setItem('atlas-mastered',JSON.stringify([...state.mastered])); renderTutorialControls();
}

function renderTopics(){
  const category=$('#topicCategory').value,query=$('#globalSearch').value.trim().toLowerCase();
  const topics=state.topics.filter(t=>(!category||t.category===category)&&(!query||(t.name+' '+t.summary+' '+t.tradeoff+' '+t.pitfall).toLowerCase().includes(query)));
  $('#topicGrid').innerHTML=topics.length?topics.map(t=>`<article class="topic-card"><span class="cat">${esc(t.category)}</span><h3>${esc(t.name)}</h3><p>${esc(t.summary)}</p><dl><dt>Tradeoff</dt><dd>${esc(t.tradeoff)}</dd><dt>Production failure</dt><dd>${esc(t.pitfall)}</dd></dl><div class="topic-actions"><button data-topic="${esc(t.id)}">Open deep tutorial →</button></div></article>`).join(''):'<p class="empty">No topics match this filter.</p>';
  $$('#topicGrid [data-topic]').forEach(b=>b.onclick=()=>showView('tutorial',b.dataset.topic));
}
$('#topicCategory').onchange=renderTopics;

function applyQuestionFilters(){
  const type=$('#qType').value,difficulty=$('#qDifficulty').value,category=$('#qCategory').value,query=$('#globalSearch').value.trim().toLowerCase();
  state.pool=state.questions.filter(x=>(!type||x.type===type)&&(!difficulty||x.difficulty===difficulty)&&(!category||x.category===category)&&(!query||(x.prompt+' '+x.topic+' '+x.category).toLowerCase().includes(query)));
  state.index=0;renderQuestion();
}
['#qType','#qDifficulty','#qCategory'].forEach(s=>$(s).onchange=applyQuestionFilters);
function renderQuestion(){
  const el=$('#questionCard');$('#seenCount').textContent=state.seen.size;$('#poolCount').textContent=`${state.pool.length.toLocaleString()} questions in this pool`;
  if(!state.pool.length){el.innerHTML='<p class="empty">No questions match this filter.</p>';return}
  const q=state.pool[state.index%state.pool.length];
  const opts=q.options?`<div class="options">${q.options.map((o,i)=>`<button class="option" data-value="${esc(o)}"><b>${String.fromCharCode(65+i)}</b><span>${esc(o)}</span></button>`).join('')}</div>`:'';
  el.innerHTML=`<div class="badges"><span class="badge">${esc(q.id)}</span><span class="badge">${esc(q.type)}</span><span class="badge">${esc(q.difficulty)}</span></div><span class="cat">${esc(q.category)} · ${esc(q.topic)}</span><h3>${esc(q.prompt)}</h3>${opts}<div id="answerBox"></div><div class="question-actions"><button id="reveal">Reveal answer</button><button id="next" class="secondary">Next question →</button></div>`;
  $$('.option').forEach(b=>b.onclick=()=>grade(b,q));$('#reveal').onclick=()=>reveal(q);$('#next').onclick=()=>{markSeen(q);state.index=(state.index+1)%state.pool.length;renderQuestion()};
}
function grade(btn,q){$$('.option').forEach(b=>{b.disabled=true;b.classList.toggle('correct',b.dataset.value===q.answer)});if(btn.dataset.value!==q.answer)btn.classList.add('wrong');reveal(q)}
function reveal(q){$('#answerBox').innerHTML=`<div class="answer"><strong>Answer</strong><p>${esc(q.answer)}</p><small>${esc(q.explanation||'')}</small><a class="deep-link" href="#tutorial/${esc(q.tutorial_id)}">Study the full lesson and derivation →</a></div>`;$('#answerBox .deep-link').onclick=e=>{e.preventDefault();showView('tutorial',q.tutorial_id)};markSeen(q)}
function markSeen(q){state.seen.add(q.id);localStorage.setItem('atlas-seen',JSON.stringify([...state.seen]));$('#seenCount').textContent=state.seen.size}
$('#shuffleBtn').onclick=()=>{state.pool.sort(()=>Math.random()-.5);state.index=0;renderQuestion()};
$('#resetBtn').onclick=()=>{state.seen.clear();localStorage.removeItem('atlas-seen');renderQuestion()};

function renderCore(){
  const query=$('#globalSearch').value.trim().toLowerCase();const items=state.core.filter(x=>!query||(x.prompt+' '+x.answer+' '+x.category).toLowerCase().includes(query));
  $('#coreList').innerHTML=items.map(x=>`<details class="qa"><summary><span class="badge">${esc(x.id)} · ${esc(x.difficulty)}</span><strong>${esc(x.prompt)}</strong><span class="badge">${esc(x.origin)}</span></summary><div class="qa-answer"><p>${esc(x.answer)}</p><small>${esc(x.category)}</small></div></details>`).join('');
}
function renderDesigns(){
  const query=$('#globalSearch').value.trim().toLowerCase();const items=state.designs.filter(x=>!query||(x.title+' '+x.brief+' '+JSON.stringify(x.stages)).toLowerCase().includes(query));
  $('#designList').innerHTML=items.map((d,i)=>{const nodes=d.diagram.split('\n').filter(x=>x.includes('[')).map(x=>x.match(/\[([^\]]+)\]/)?.[1]).filter(Boolean);return `<article class="design-case"><header><div><span class="badge">DESIGN ${String(i+1).padStart(2,'0')}</span><h3>${esc(d.title)}</h3><p>${esc(d.brief)}</p></div><span class="badge">4-stage interview</span></header><div class="case-body"><div class="case-diagram">${nodes.map((n,j)=>`${j?'<div class="arrow">↓</div>':''}<div class="node">${esc(n)}</div>`).join('')}</div><div class="stages">${d.stages.map((s,j)=>`<div class="stage"><h4>${j+1}. ${esc(s.q)}</h4><p>${esc(s.a)}</p></div>`).join('')}</div></div></article>`}).join('');
}
function renderSources(){
  const query=$('#globalSearch').value.trim().toLowerCase();const items=state.refs.filter(x=>!query||(x.title+' '+x.kind).toLowerCase().includes(query));
  $('#sourceGrid').innerHTML=items.map(r=>`<a class="source-card" href="${esc(r.url)}" target="_blank" rel="noreferrer"><small>${esc(r.kind)}</small><span>${esc(r.title)}</span></a>`).join('');
}
let timer;$('#globalSearch').oninput=()=>{clearTimeout(timer);timer=setTimeout(()=>{renderTopics();renderTutorialControls();renderCore();renderDesigns();renderSources();applyQuestionFilters();const q=$('#globalSearch').value.trim().toLowerCase();$$('#mindmap li').forEach(li=>li.hidden=q&&!li.dataset.search.includes(q))},120)};
document.addEventListener('keydown',e=>{if(e.key==='/'&&document.activeElement.tagName!=='INPUT'){e.preventDefault();$('#globalSearch').focus()}});
