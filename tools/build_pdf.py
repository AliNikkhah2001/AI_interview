#!/usr/bin/env python3
"""Render the interview atlas as a polished PDF from canonical JSON data."""

from __future__ import annotations

import json
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import (
    BaseDocTemplate, Flowable, Frame, KeepTogether, PageBreak, PageTemplate,
    Paragraph, Spacer, Table, TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "pdf" / "ai_engineering_interview_handbook.pdf"
NAVY = colors.HexColor("#0C2744")
BLUE = colors.HexColor("#1E63E9")
CYAN = colors.HexColor("#1DB6C7")
PAPER = colors.HexColor("#F4F7FB")
LINE = colors.HexColor("#D7E1EC")
MUTED = colors.HexColor("#5F6B7A")
GREEN = colors.HexColor("#167A5B")


def load(name):
    return json.loads((ROOT / "data" / name).read_text(encoding="utf-8"))


topics = load("topics.json")
questions = sum((load(f"questions_{i}.json") for i in range(1, 5)), [])
core = load("core_questions.json")
designs = load("designs.json")
refs = load("references.json")
tutorials = load("tutorials.json")
formulas = load("formulas.json")
roadmap = load("roadmap.json")


def safe(text):
    return (str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="AtlasBody", fontName="Helvetica", fontSize=8.3, leading=11.4, textColor=colors.HexColor("#172334"), spaceAfter=4))
styles.add(ParagraphStyle(name="AtlasSmall", parent=styles["AtlasBody"], fontSize=7.1, leading=9.3, textColor=MUTED))
styles.add(ParagraphStyle(name="AtlasH1", fontName="Helvetica-Bold", fontSize=22, leading=25, textColor=NAVY, spaceBefore=5, spaceAfter=10))
styles.add(ParagraphStyle(name="AtlasH2", fontName="Helvetica-Bold", fontSize=12.5, leading=15, textColor=BLUE, spaceBefore=8, spaceAfter=5))
styles.add(ParagraphStyle(name="AtlasH3", fontName="Helvetica-Bold", fontSize=9.5, leading=12, textColor=NAVY, spaceBefore=4, spaceAfter=3))
styles.add(ParagraphStyle(name="AtlasQuestion", fontName="Helvetica-Bold", fontSize=8.4, leading=11.2, textColor=NAVY, spaceAfter=3))
styles.add(ParagraphStyle(name="AtlasOption", fontName="Helvetica", fontSize=7.4, leading=9.6, leftIndent=8, firstLineIndent=-8, textColor=colors.HexColor("#263445"), spaceAfter=1.5))
styles.add(ParagraphStyle(name="AtlasAnswer", fontName="Helvetica", fontSize=7.35, leading=9.7, textColor=GREEN, leftIndent=8, borderColor=CYAN, borderWidth=0, borderPadding=0, spaceBefore=2))
styles.add(ParagraphStyle(name="AtlasCenter", parent=styles["AtlasBody"], alignment=TA_CENTER))
styles.add(ParagraphStyle(name="AtlasFormula", fontName="Courier", fontSize=6.35, leading=8.5, textColor=NAVY, backColor=colors.HexColor("#EFF9FA"), borderColor=CYAN, borderWidth=.5, borderPadding=6, spaceBefore=3, spaceAfter=5))


class AtlasDoc(BaseDocTemplate):
    def __init__(self, filename):
        super().__init__(filename, pagesize=A4, leftMargin=16*mm, rightMargin=16*mm, topMargin=18*mm, bottomMargin=16*mm, title="AI Engineering Interview Atlas", author="Ali Nikkhah", pageCompression=1)
        frame = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id="normal")
        self.addPageTemplates(PageTemplate(id="atlas", frames=[frame], onPage=self.decorate))
        self.chapter = "Interview Atlas"

    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph) and flowable.style.name == "AtlasH1":
            self.chapter = flowable.getPlainText()
            key = f"h1-{self.page}-{abs(hash(self.chapter))}"
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(self.chapter, key, 0, False)

    def decorate(self, canvas, doc):
        canvas.saveState()
        if doc.page == 1:
            canvas.restoreState(); return
        canvas.setStrokeColor(LINE); canvas.setLineWidth(.5)
        canvas.line(doc.leftMargin, A4[1]-12*mm, A4[0]-doc.rightMargin, A4[1]-12*mm)
        canvas.setFont("Helvetica-Bold", 7.2); canvas.setFillColor(NAVY)
        canvas.drawString(doc.leftMargin, A4[1]-9*mm, "AI ENGINEERING INTERVIEW ATLAS")
        canvas.setFont("Helvetica", 6.7); canvas.setFillColor(MUTED)
        canvas.drawRightString(A4[0]-doc.rightMargin, A4[1]-9*mm, self.chapter[:70])
        canvas.drawCentredString(A4[0]/2, 8*mm, str(doc.page))
        canvas.restoreState()


class Cover(Flowable):
    def __init__(self):
        super().__init__(); self.width=A4[0]; self.height=A4[1]
    def wrap(self, aw, ah): return aw, ah
    def draw(self):
        c=self.canv; w,h=A4
        c.setFillColor(NAVY); c.rect(-20*mm,-20*mm,w+40*mm,h+40*mm,stroke=0,fill=1)
        c.setFillColor(CYAN); c.rect(0, h-32*mm, 26*mm, 4*mm, stroke=0, fill=1)
        c.setFont("Helvetica-Bold", 30); c.setFillColor(colors.white)
        c.drawString(0, h-82*mm, "AI Engineering")
        c.drawString(0, h-96*mm, "Interview Atlas")
        c.setFont("Helvetica", 13); c.setFillColor(colors.HexColor("#BFD2E6"))
        c.drawString(0, h-116*mm, "Mathematical tutorials, systems, and 1,000+ questions")
        stats=[(str(len(tutorials)),"deep tutorials"),(f"{len(questions)+len(core):,}","questions"),(str(len(formulas)),"derivations"),(str(len(roadmap)),"roadmap phases")]
        x=0
        for number,label in stats:
            c.setFillColor(colors.HexColor("#173D64")); c.roundRect(x, h-165*mm, 38*mm, 25*mm, 3*mm, stroke=0, fill=1)
            c.setFont("Helvetica-Bold",15); c.setFillColor(colors.white); c.drawString(x+4*mm,h-151*mm,number)
            c.setFont("Helvetica",6.5); c.setFillColor(colors.HexColor("#BFD2E6")); c.drawString(x+4*mm,h-158*mm,label.upper())
            x+=41*mm
        c.setFont("Helvetica",8); c.setFillColor(colors.HexColor("#BFD2E6"))
        c.drawString(0, 17*mm, "Research snapshot: 2 September 2026")
        c.drawString(0, 11*mm, "Primary papers · official documentation · specifications · standards")


class LandscapeFlow(Flowable):
    def __init__(self):
        super().__init__(); self.width=170*mm; self.height=42*mm
    def wrap(self, aw, ah): return min(self.width,aw), self.height
    def draw(self):
        c=self.canv; labels=["Foundations","Retrieval + RAG","Agents + control","Serving + LLMOps","Evaluation + safety"]
        bw=30*mm; gap=4*mm; y=13*mm
        for i,label in enumerate(labels):
            x=i*(bw+gap)
            c.setFillColor(PAPER); c.setStrokeColor(CYAN); c.roundRect(x,y,bw,15*mm,2*mm,stroke=1,fill=1)
            c.setFont("Helvetica-Bold",6.8); c.setFillColor(NAVY); c.drawCentredString(x+bw/2,y+6.5*mm,label)
            if i < len(labels)-1:
                c.setStrokeColor(BLUE); c.setLineWidth(1.4); c.line(x+bw,y+7.5*mm,x+bw+gap-1.5*mm,y+7.5*mm)
                c.setFillColor(BLUE); c.circle(x+bw+gap-1.2*mm,y+7.5*mm,1.2*mm,stroke=0,fill=1)
        c.setFont("Helvetica",7); c.setFillColor(MUTED); c.drawString(0,5*mm,"Production readiness comes from the connections: evidence, control, telemetry, policy, and rollback.")


class RoadmapFlow(Flowable):
    def __init__(self, phases):
        super().__init__(); self.phases=phases; self.width=170*mm; self.height=92*mm
    def wrap(self, aw, ah): return min(self.width,aw), self.height
    def draw(self):
        c=self.canv; bw=51*mm; bh=15*mm; gx=6*mm; gy=7*mm
        for i,p in enumerate(self.phases):
            row=i//3; slot=i%3; col=slot if row%2==0 else 2-slot; x=col*(bw+gx); y=self.height-(row+1)*(bh+gy)+gy
            c.setFillColor(PAPER); c.setStrokeColor(BLUE if i==0 else CYAN); c.roundRect(x,y,bw,bh,2*mm,stroke=1,fill=1)
            c.setFont("Helvetica-Bold",6.4); c.setFillColor(BLUE); c.drawString(x+3*mm,y+10.2*mm,f"{p['order']:02d}  |  {p['hours']} HOURS")
            c.setFont("Helvetica-Bold",5.9); c.setFillColor(NAVY)
            words=p['title'].split(); title_lines=[""]
            for word in words:
                candidate=(title_lines[-1]+" "+word).strip()
                if pdfmetrics.stringWidth(candidate,"Helvetica-Bold",5.9) > bw-6*mm and len(title_lines)<2:
                    title_lines.append(word)
                else: title_lines[-1]=candidate
            for line_no,title_line in enumerate(title_lines[:2]):
                c.drawString(x+3*mm,y+(6.1-2.8*line_no)*mm,title_line)
            if i<len(self.phases)-1:
                if slot<2:
                    direction=1 if row%2==0 else -1
                    x1=x+bw if direction==1 else x; y1=y+bh/2; x2=x1+direction*(gx-1*mm); y2=y1
                else:
                    x1=x+bw/2; y1=y; x2=x1; y2=y-gy+1*mm
                c.setStrokeColor(BLUE); c.setLineWidth(1); c.line(x1,y1,x2,y2)


class DesignFlow(Flowable):
    def __init__(self, diagram):
        self.labels=[m.group(1) for m in re.finditer(r"\[([^\]]+)\]",diagram)]
        super().__init__(); self.width=170*mm; self.height=max(32*mm,len(self.labels)*12*mm+5*mm)
    def wrap(self, aw, ah): return min(self.width,aw), self.height
    def draw(self):
        c=self.canv; cols=2; bw=76*mm; bh=8.5*mm; xgap=8*mm; y=self.height-11*mm
        for i,label in enumerate(self.labels):
            col=i%cols; row=i//cols; x=col*(bw+xgap); yy=y-row*12*mm
            c.setFillColor(PAPER); c.setStrokeColor(CYAN); c.roundRect(x,yy,bw,bh,2*mm,stroke=1,fill=1)
            c.setFont("Helvetica-Bold",6.8); c.setFillColor(NAVY); c.drawCentredString(x+bw/2,yy+3.1*mm,label[:55])
            if i+2 < len(self.labels):
                c.setStrokeColor(BLUE); c.line(x+bw/2,yy,x+bw/2,yy-3.5*mm)


def section(title): return Paragraph(safe(title), styles["AtlasH1"])
def subsection(title): return Paragraph(safe(title), styles["AtlasH2"])
def body(text): return Paragraph(safe(text), styles["AtlasBody"])


story=[Cover(),PageBreak(),section("How to use this handbook"),body(f"This handbook contains {len(tutorials)} deep topic tutorials, {len(formulas)} mathematical derivations, {len(questions)} generated practice questions, 50 core interview questions, and {len(designs)} progressive system-design challenges. Build answers in seven moves: mechanism, assumptions, quantitative model, alternatives, experiment, operations, and failure recovery."),Spacer(1,3*mm),LandscapeFlow(),subsection("Study loop"),body("1. Follow the roadmap in order. 2. Derive equations without looking and check assumptions. 3. Read the mechanism and teach it back. 4. Solve medium questions from memory. 5. Use hard questions to explain measurement and rollback. 6. Practice each system design aloud, accepting every twist before reading the rubric."),subsection("Curriculum index")]

counts={}
for t in topics: counts[t["category"]]=counts.get(t["category"],0)+1
toc_data=[[Paragraph("Domain",styles["AtlasQuestion"]),Paragraph("Topics",styles["AtlasQuestion"])]]+[[Paragraph(safe(k),styles["AtlasSmall"]),str(v)] for k,v in counts.items()]
toc=Table(toc_data,colWidths=[145*mm,20*mm],repeatRows=1)
toc.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),NAVY),("TEXTCOLOR",(0,0),(-1,0),colors.white),("GRID",(0,0),(-1,-1),.35,LINE),("VALIGN",(0,0),(-1,-1),"TOP"),("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,PAPER]),("FONTNAME",(1,1),(1,-1),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),7)]))
story += [toc,PageBreak(),section("Ordered study roadmap"),body("Mark a phase complete only after its milestone can be performed without notes. The first incomplete phase is the current study position. Dependencies are intentional: serving depends on transformer and systems foundations; safe agents depend on retrieval, orchestration, and observability."),RoadmapFlow(roadmap)]
for p in roadmap:
    prereq=", ".join(p["prerequisites"]) or "none"
    story += [subsection(f"{p['order']:02d}. {p['title']} · {p['hours']} hours"),body(f"Prerequisites: {prereq}. Milestone: {p['milestone']} Practice: {p['practice']}"),Paragraph("<b>Outcomes.</b> "+safe(" · ".join(p["outcomes"])),styles["AtlasSmall"])]

story += [PageBreak(),section("Mathematical formula and derivation reference"),body("Every module gives a compilable LaTeX equation, its variables, the derivation logic, and a worked engineering interpretation. Read each backslash expression as source notation here; the canonical LaTeX handbook renders it as mathematics during the Pages build.")]
for f in formulas:
    story += [subsection(f["title"]),Paragraph(safe(f["latex"]),styles["AtlasFormula"]),Paragraph("<b>Variables.</b> "+safe(" · ".join(f["variables"])),styles["AtlasSmall"])]
    for i,s in enumerate(f["derivation"],1):
        story += [Paragraph(f"<b>Step {i}.</b> "+safe(s["text"]),styles["AtlasBody"]),Paragraph(safe(s["latex"]),styles["AtlasFormula"])]
    story += [Paragraph("<b>Worked interpretation.</b> "+safe(f["example"]),styles["AtlasSmall"])]

story += [PageBreak(),section("Deep tutorials: first principles to production"),body("These lessons are the teaching source for the full generated bank. Each one covers the definition, tradeoff, failure association, scenario diagnosis, design explanation, and production rubric used by all seven MCQs, both flashcards, and the long-answer prompt for its topic.")]
formula_map={f["id"]:f for f in formulas}
current=None
for t in tutorials:
    if t["category"] != current:
        current=t["category"]; story += [PageBreak(),section(current)]
    story += [subsection(t["name"]),Paragraph("<b>Objective.</b> "+safe(t["objective"]),styles["AtlasBody"]),body(t["first_principles"]),body(t["mental_model"]),Paragraph("<b>Quantitative reasoning.</b> "+safe(t["quantitative_reasoning"]),styles["AtlasBody"])]
    for fid in t["formula_ids"]:
        f=formula_map[fid]; story += [Paragraph("<b>"+safe(f["title"])+".</b>",styles["AtlasSmall"]),Paragraph(safe(f["latex"]),styles["AtlasFormula"])]
    story += [Paragraph("<b>Decision.</b> "+safe(t["decision_reasoning"]),styles["AtlasBody"]),Paragraph("<b>Failure reasoning.</b> "+safe(t["failure_reasoning"]),styles["AtlasBody"]),Paragraph("<b>Worked production method.</b>",styles["AtlasQuestion"])]
    for i,x in enumerate(t["worked_reasoning"],1): story.append(Paragraph(f"{i}. "+safe(x),styles["AtlasSmall"]))
    story += [Paragraph("<b>Evaluate.</b> "+safe(" · ".join(t["evaluation"])),styles["AtlasSmall"]),Paragraph("<b>Operate.</b> "+safe(" · ".join(t["operations"])),styles["AtlasSmall"]),Paragraph("<b>Answer blueprint.</b> "+safe(" ".join(t["answer_blueprint"].values())),styles["AtlasSmall"]),Paragraph("<b>Question coverage.</b> "+safe(t["question_coverage"]),styles["AtlasAnswer"])]

story += [PageBreak(),section("Core 50 interview questions")]
for q in core:
    story += [KeepTogether([Paragraph(f"<font color='#1E63E9'>{safe(q['id'])} · {safe(q['difficulty'].upper())}</font>  {safe(q['prompt'])}",styles["AtlasQuestion"]),Paragraph("<b>Answer rubric.</b> "+safe(q["answer"]),styles["AtlasBody"]),Spacer(1,2*mm)])]

story += [PageBreak(),section("Progressive system-design challenges")]
for i,d in enumerate(designs,1):
    story += [PageBreak(),subsection(f"Design {i:02d}: {d['title']}"),body(d["brief"]),DesignFlow(d["diagram"])]
    for j,s in enumerate(d["stages"],1):
        story += [KeepTogether([Paragraph(f"{j}. {safe(s['q'])}",styles["AtlasQuestion"]),body(s["a"])])]

story += [PageBreak(),section("Complete practice bank"),body("The bank includes four-option multiple-choice questions, flashcards, and long-answer prompts. Answers are included for self-correction. Hide the answer with a sheet of paper for active recall.")]
current=None
for q in questions:
    if q["category"] != current:
        current=q["category"]; story += [PageBreak(),subsection(current)]
    block=[Paragraph(f"<font color='#1E63E9'>{safe(q['id'])} · {safe(q['difficulty'].upper())} · {safe(q['type'].upper())}</font><br/>{safe(q['prompt'])}",styles["AtlasQuestion"])]
    for idx,opt in enumerate(q.get("options",[])):
        block.append(Paragraph(f"{chr(65+idx)}. {safe(opt)}",styles["AtlasOption"]))
    block.append(Paragraph("<b>Answer.</b> "+safe(q["answer"]),styles["AtlasAnswer"]))
    if q.get("explanation") and q["type"] == "mcq":
        block.append(Paragraph(safe(q["explanation"]),styles["AtlasSmall"]))
    block.append(Spacer(1,2.2*mm)); story.append(KeepTogether(block))

story += [PageBreak(),section("Primary sources"),body("The atlas is original synthesis grounded in primary papers, official documentation, specifications, and standards. Product choices remain workload-dependent; benchmark representative data, filters, hardware, and service-level objectives.")]
for i,r in enumerate(refs,1):
    story.append(Paragraph(f"{i}. <link href='{r['url']}' color='#1E63E9'>{safe(r['title'])}</link> <font color='#5F6B7A'>({safe(r['kind'])})</font>",styles["AtlasBody"]))

OUT.parent.mkdir(parents=True,exist_ok=True)
AtlasDoc(str(OUT)).build(story)
print(OUT)
