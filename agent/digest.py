# agent/digest.py
import io
import re
from typing import List
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch

def synthesize_digest(topic: str, items, model, prompt_template: str) -> str:
    import json
    items_json = json.dumps(items, ensure_ascii=False)
    prompt = prompt_template.format(topic=topic, items_json=items_json)
    md = model.complete_text(prompt, max_tokens=1200)  # returns Markdown
    return md

LINK_RE = re.compile(r"\[([^\]]+)\]\(([^()\s]+)\)")

def _md_to_paragraphs(md_text: str) -> List[Paragraph]:
    styles = getSampleStyleSheet()
    body = styles["BodyText"]
    header = ParagraphStyle("Header", parent=styles["Heading2"], spaceAfter=6)

    paras: List[Paragraph] = []
    for raw in md_text.splitlines():
        line = raw.rstrip()

        # blank line = small spacer
        if not line:
            paras.append(Spacer(1, 0.12 * inch))
            continue

        # Convert [text](url) -> text (url), but be forgiving
        try:
            line = LINK_RE.sub(r"\1 (\2)", line)
        except re.error:
            # If anything goes wrong, just keep the original
            pass

        # Minimal markdown treatment
        if line.startswith("#"):
            # Header lines: strip leading # and escape/normalize
            text = re.sub(r"^#+\s*", "", line)
            paras.append(Paragraph(_escape_for_reportlab(text), header))

        elif line.startswith(("- ", "* ")):
            # Bulleted list: use plain hyphen for max font compatibility
            text = _escape_for_reportlab(line[2:])
            paras.append(Paragraph(f"- {text}", body))

        elif re.match(r"^\d+\.\s+", line):
            # Numbered list: strip leading digits + dot
            text = re.sub(r"^\d+\.\s+", "", line)
            paras.append(Paragraph(_escape_for_reportlab(text), body))

        else:
            # Normal paragraph
            paras.append(Paragraph(_escape_for_reportlab(line), body))

    return paras

def export_markdown_to_pdf(md_text: str) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=LETTER,
        leftMargin=0.75 * inch, rightMargin=0.75 * inch,
        topMargin=0.75 * inch, bottomMargin=0.75 * inch,
        title="WebDigest"
    )
    story = _md_to_paragraphs(md_text)
    doc.build(story)
    return buf.getvalue()

UNICODE_FIXES = {
    "\u2010": "-",  # hyphen
    "\u2011": "-",  # non-breaking hyphen
    "\u2012": "-",  # figure dash
    "\u2013": "-",  # en dash
    "\u2014": "-",  # em dash
    "\u2212": "-",  # minus sign
    "\u2022": "-",  # bullet
    "\u00D7": "x",  # multiplication sign
    "\u00A0": " ",  # non-breaking space
    "\u200B": "",   # zero-width space
    "\u2018": "'",  # left single quote
    "\u2019": "'",  # right single quote
    "\u201C": '"',  # left double quote
    "\u201D": '"',  # right double quote
}

def _normalize_ascii(text: str) -> str:
    for k, v in UNICODE_FIXES.items():
        text = text.replace(k, v)
    return text

def _escape_for_reportlab(text: str) -> str:
    # normalize first, then escape XML-ish chars
    text = _normalize_ascii(text)
    return (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
    )
