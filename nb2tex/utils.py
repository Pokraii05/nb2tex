import pypandoc
import re


def markdown_to_latex(md_text):
    return pypandoc.convert_text(md_text, "latex", format="markdown+tex_math_dollars")


def split_markdown_display_equations(md_text):
    parts = []
    last = 0
    pattern = re.compile(r"(?<!\\)\$\$(.+?)(?<!\\)\$\$", re.DOTALL)

    for match in pattern.finditer(md_text):
        markdown_chunk = md_text[last:match.start()]
        if markdown_chunk.strip():
            parts.append(("markdown", markdown_chunk))

        equation = match.group(1).strip()
        if equation:
            parts.append(("equation", equation))

        last = match.end()

    trailing = md_text[last:]
    if trailing.strip():
        parts.append(("markdown", trailing))

    if not parts:
        parts.append(("markdown", md_text))

    return parts


def extract_caption(md_text, default="Generated"):
    if not md_text:
        return default

    for line in md_text.splitlines():
        if line.lower().startswith("figure:"):
            return line.split(":", 1)[1].strip()
        if line.lower().startswith("table:"):
            return line.split(":", 1)[1].strip()

    return default
