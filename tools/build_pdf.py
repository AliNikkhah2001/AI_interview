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
from reportlab.pdfbase.ttfonts import TTFont
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
questions = load("questions.json")
core = load("core_questions.json")
designs = load("designs.json")
refs = load("references.json")


for regular, bold in [
    ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    ("/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf", "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"),
]:
    if Path(regular).exists() and Path(bold).exists():
        pdfmetrics.registerFont(TTFont("Atlas", regular))
        pdfmetrics.registerFont(TTFont("AtlasBold", bold))
        break
else:
    raise RuntimeError("No supported TrueType font found")


def safe(text):
    return (str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="AtlasBody", fontName="Atlas", fontSize=8.3, leading=11.4, textColor=colors.HexColor("#172334"), spaceAfter=4))
styles.add(ParagraphStyle(name="AtlasSmall", parent=styles["AtlasBody"], fontSize=7.1, leading=9.3, textColor=MUTED))
styles.add(ParagraphStyle(name="AtlasH1", fontName="AtlasBold", fontSize=22, leading=25, textColor=NAVY, spaceBefore=5, spaceAfter=10))
styles.add(ParagraphStyle(name="AtlasH2", fontName="AtlasBold", fontSize=12.5, leading=15, textColor=BLUE, spaceBefore=8, spaceAfter=5))
styles.add(ParagraphStyle(name="AtlasH3", fontName="AtlasBold", fontSize=9.5, leading=12, textColor=NAVY, spaceBefore=4, spaceAfter=3))
styles.add(ParagraphStyle(name="AtlasQuestion", fontName="AtlasBold", fontSize=8.4, leading=11.2, textColor=NAVY, spaceAfter=3))
styles.add(ParagraphStyle(name="AtlasOption", fontName="Atlas", fontSize=7.4, leading=9.6, leftIndent=8, firstLineIndent=-8, textColor=colors.HexColor("#263445"), spaceAfter=1.5))
styles.add(ParagraphStyle(name="AtlasAnswer", fontName="Atlas", fontSize=7.35, leading=9.7, textColor=GREEN, leftIndent=8, borderColor=CYAN, borderWidth=0, borderPadding=0, spaceBefore=2))
styles.add(ParagraphStyle(name="AtlasCenter", parent=styles["AtlasBody"], alignment=TA_CENTER))


class AtlasDoc(BaseDocTemplate):
    def __init__(self, filename):
        super().__init__(filename, pagesize=A4, leftMargin=16*mm, rightMargin=16*mm, topMargin=18*mm, bottomMargin=16*mm, title="AI Engineering Interview Atlas", author="Ali Nikkhah")
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
        canvas.setFont("AtlasBold", 7.2); canvas.setFillColor(NAVY)
        canvas.drawString(doc.leftMargin, A4[1]-9*mm, "AI ENGINEERING INTERVIEW ATLAS")
        canvas.setFont("Atlas", 6.7); canvas.setFillColor(MUTED)
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
        c.setFont("AtlasBold", 30); c.setFillColor(colors.white)
        c.drawString(0, h-82*mm, "AI Engineering")
        c.drawString(0, h-96*mm, "Interview Atlas")
        c.setFont("Atlas", 13); c.setFillColor(colors.HexColor("#BFD2E6"))
        c.drawString(0, h-116*mm, "Systems, theory, and 1,000+ questions")
        stats=[("192","topics"),("1,970","questions"),("12","design drills"),("42","primary sources")]
        x=0
        for number,label in stats:
            c.setFillColor(colors.HexColor("#173D64")); c.roundRect(x, h-165*mm, 38*mm, 25*mm, 3*mm, stroke=0, fill=1)
            c.setFont("AtlasBold",15); c.setFillColor(colors.white); c.drawString(x+4*mm,h-151*mm,number)
            c.setFont("Atlas",6.5); c.setFillColor(colors.HexColor("#BFD2E6")); c.drawString(x+4*mm,h-158*mm,label.upper())
            x+=41*mm
        c.setFont("Atlas",8); c.setFillColor(colors.HexColor("#BFD2E6"))
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
            c.setFont("AtlasBold",6.8); c.setFillColor(NAVY); c.drawCentredString(x+bw/2,y+6.5*mm,label)
            if i < len(labels)-1:
                c.setStrokeColor(BLUE); c.setLineWidth(1.4); c.line(x+bw,y+7.5*mm,x+bw+gap-1.5*mm,y+7.5*mm)
                c.setFillColor(BLUE); c.circle(x+bw+gap-1.2*mm,y+7.5*mm,1.2*mm,stroke=0,fill=1)
        c.setFont("Atlas",7); c.setFillColor(MUTED); c.drawString(0,5*mm,"Production readiness comes from the connections: evidence, control, telemetry, policy, and rollback.")


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
            c.setFont("AtlasBold",6.8); c.setFillColor(NAVY); c.drawCentredString(x+bw/2,yy+3.1*mm,label[:55])
            if i+2 < len(self.labels):
                c.setStrokeColor(BLUE); c.line(x+bw/2,yy,x+bw/2,yy-3.5*mm)


def section(title): return Paragraph(safe(title), styles["AtlasH1"])
def subsection(title): return Paragraph(safe(title), styles["AtlasH2"])
def body(text): return Paragraph(safe(text), styles["AtlasBody"])


story=[Cover(),PageBreak(),section("How to use this handbook"),body(f"This handbook contains {len(topics)} topic notes, {len(questions)} generated practice questions, 50 core interview questions, and {len(designs)} progressive system-design challenges. Build answers in five moves: mechanism, workload, tradeoff, measurement, and failure recovery."),Spacer(1,3*mm),LandscapeFlow(),subsection("Study loop"),body("1. Read the mechanism and say it back without product slogans. 2. Name the cost or accuracy tradeoff. 3. Solve medium questions from memory. 4. Use hard questions to explain measurement and rollback. 5. Practice each system design aloud, accepting every twist before reading the rubric."),subsection("Curriculum index")]

counts={}
for t in topics: counts[t["category"]]=counts.get(t["category"],0)+1
toc_data=[[Paragraph("Domain",styles["AtlasQuestion"]),Paragraph("Topics",styles["AtlasQuestion"])]]+[[Paragraph(safe(k),styles["AtlasSmall"]),str(v)] for k,v in counts.items()]
toc=Table(toc_data,colWidths=[145*mm,20*mm],repeatRows=1)
toc.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),NAVY),("TEXTCOLOR",(0,0),(-1,0),colors.white),("GRID",(0,0),(-1,-1),.35,LINE),("VALIGN",(0,0),(-1,-1),"TOP"),("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,PAPER]),("FONTNAME",(1,1),(1,-1),"AtlasBold"),("FONTSIZE",(0,0),(-1,-1),7)]))
story += [toc,PageBreak()]

current=None
for t in topics:
    if t["category"] != current:
        current=t["category"]; story += [section(current)]
    story += [KeepTogether([subsection(t["name"]),body(t["summary"]),Paragraph("<b>Tradeoff.</b> "+safe(t["tradeoff"]),styles["AtlasSmall"]),Paragraph("<b>Production failure.</b> "+safe(t["pitfall"]),styles["AtlasSmall"])])]

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
    if q.get("explanation"): block.append(Paragraph(safe(q["explanation"]),styles["AtlasSmall"]))
    block.append(Spacer(1,2.2*mm)); story.append(KeepTogether(block))

story += [PageBreak(),section("Primary sources"),body("The atlas is original synthesis grounded in primary papers, official documentation, specifications, and standards. Product choices remain workload-dependent; benchmark representative data, filters, hardware, and service-level objectives.")]
for i,r in enumerate(refs,1):
    story.append(Paragraph(f"{i}. <link href='{r['url']}' color='#1E63E9'>{safe(r['title'])}</link> <font color='#5F6B7A'>({safe(r['kind'])})</font>",styles["AtlasBody"]))

OUT.parent.mkdir(parents=True,exist_ok=True)
AtlasDoc(str(OUT)).build(story)
print(OUT)
