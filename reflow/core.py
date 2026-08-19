"""Paragraph-aware text reflowing.

The core idea: once text has been hard-wrapped (by an editor, an email
client, a PDF export, whatever), the newlines inside a paragraph carry no
meaning any more. Only the paragraph breaks (blank lines) do. So we throw
away every newline that isn't a paragraph boundary and let textwrap decide
where the new ones go.
"""
import re
import textwrap

_PARAGRAPH_SPLIT = re.compile(r"\n[ \t]*\n+")


def normalize_paragraphs(text):
    """Split text into a list of paragraphs with internal whitespace collapsed."""
    text = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    if not text:
        return []
    paragraphs = []
    for raw in _PARAGRAPH_SPLIT.split(text):
        collapsed = " ".join(raw.split())
        if collapsed:
            paragraphs.append(collapsed)
    return paragraphs


def wrap_text(text, width=72):
    """Normalize and rewrap text to `width` columns, one blank line between paragraphs."""
    paragraphs = normalize_paragraphs(text)
    wrapped = [
        textwrap.fill(p, width=width, break_long_words=False, break_on_hyphens=False)
        for p in paragraphs
    ]
    return "\n\n".join(wrapped)
