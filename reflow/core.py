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

# A list item marker: "-", "*", "+", "1.", "2)", etc, followed by whitespace.
# Leading indent is capped at 3 spaces (same cutoff markdown uses) so an
# indented code block doesn't get mistaken for a list later on.
_LIST_ITEM = re.compile(r"^[ \t]{0,3}([-*+]|\d{1,9}[.)])[ \t]+(.*)$")

# Same cutoff markdown uses for indented code: a tab, or 4+ spaces.
_CODE_LINE = re.compile(r"^(?:\t| {4,})")


def _split_block(raw_lines):
    """Split one blank-line-delimited block into prose strings, list blocks,
    and code blocks.

    A list block is a run of consecutive list items, returned as a list of
    (marker, text) tuples. Lines that follow a marker without one of their
    own are treated as a wrapped continuation of that item, not a new
    paragraph - that's the whole point, since it's what a hard-wrapped list
    item looks like.

    A code block is a run of consecutive lines indented by a tab or 4+
    spaces, returned as ("code", [raw lines...]) with the original
    whitespace intact. Only checked outside of a list item run, so a
    continuation line that happens to be indented still attaches to its
    list item instead of breaking off into code.
    """
    blocks = []
    prose_lines = []
    list_items = None
    code_lines = None

    def flush_prose():
        if prose_lines:
            collapsed = " ".join(" ".join(prose_lines).split())
            if collapsed:
                blocks.append(collapsed)
            prose_lines.clear()

    def flush_code():
        if code_lines:
            blocks.append(("code", list(code_lines)))
            code_lines.clear()

    for line in raw_lines:
        if list_items is None and _CODE_LINE.match(line):
            flush_prose()
            if code_lines is None:
                code_lines = []
            code_lines.append(line)
            continue
        flush_code()

        match = _LIST_ITEM.match(line)
        if match:
            flush_prose()
            if list_items is None:
                list_items = []
            marker = match.group(1) + " "
            list_items.append([marker, match.group(2)])
        elif list_items is not None and line.strip():
            list_items[-1][1] += " " + line.strip()
        else:
            prose_lines.append(line)

    flush_prose()
    flush_code()
    if list_items:
        blocks.append([(marker, " ".join(item.split())) for marker, item in list_items])
    return blocks


def normalize_paragraphs(text):
    """Split text into paragraphs, collapsing fake line breaks within each.

    Each element is a plain string (an ordinary paragraph), a list of
    (marker, text) tuples (a run of bullet/numbered list items, kept
    separate so they don't get merged into one line), or a ("code", lines)
    tuple (a run of indented lines, kept exactly as written).
    """
    text = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    if not text:
        return []
    paragraphs = []
    for raw in _PARAGRAPH_SPLIT.split(text):
        paragraphs.extend(_split_block(raw.split("\n")))
    return paragraphs


def _wrap_list_block(items, width):
    lines = []
    for marker, item_text in items:
        indent = " " * len(marker)
        lines.append(
            textwrap.fill(
                item_text,
                width=max(width, len(marker) + 1),
                initial_indent=marker,
                subsequent_indent=indent,
                break_long_words=False,
                break_on_hyphens=False,
            )
        )
    return "\n".join(lines)


def _render_block(block, width):
    if isinstance(block, list):
        return _wrap_list_block(block, width)
    if isinstance(block, tuple):
        return "\n".join(block[1])
    return textwrap.fill(block, width=width, break_long_words=False, break_on_hyphens=False)


def wrap_text(text, width=72):
    """Normalize and rewrap text to `width` columns, one blank line between paragraphs.

    Indented code blocks are left exactly as they were, unwrapped.
    """
    paragraphs = normalize_paragraphs(text)
    return "\n\n".join(_render_block(p, width) for p in paragraphs)
