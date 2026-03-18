from nb2tex.ir import *
from nb2tex.extractors import (
    extract_figure_from_output,
    extract_table_from_output,
    extract_equation_from_output,
)
from nb2tex.utils import extract_caption, split_markdown_display_equations
import re


_PIPE_TABLE_SEPARATOR_RE = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$")


def _escape_latex_cell(text):
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def _pipe_row_to_cells(line):
    stripped = line.strip()
    if "|" not in stripped:
        return []

    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|"):
        stripped = stripped[:-1]

    return [cell.strip() for cell in stripped.split("|")]


def _pipe_table_to_latex(header, body):
    col_count = len(header)
    escaped_header = [_escape_latex_cell(cell) for cell in header]
    escaped_body = [[_escape_latex_cell(cell) for cell in row] for row in body]

    lines = [
        "\\begin{tabular}{" + "l" * col_count + "}",
        "\\toprule",
        " & ".join(escaped_header) + r" \\",
        "\\midrule",
    ]

    for row in escaped_body:
        lines.append(" & ".join(row) + r" \\")

    lines.extend(["\\bottomrule", "\\end{tabular}"])
    return "\n".join(lines)


def _split_markdown_pipe_tables(md_text):
    lines = md_text.splitlines()
    if not lines:
        return [("markdown", md_text)]

    parts = []
    markdown_lines = []
    i = 0

    def flush_markdown():
        if not markdown_lines:
            return
        chunk = "\n".join(markdown_lines)
        if chunk.strip():
            parts.append(("markdown", chunk))
        markdown_lines.clear()

    while i < len(lines):
        if i + 1 < len(lines) and _PIPE_TABLE_SEPARATOR_RE.match(lines[i + 1]):
            header = _pipe_row_to_cells(lines[i])
            separator = _pipe_row_to_cells(lines[i + 1])

            if len(header) >= 2 and len(separator) == len(header):
                j = i + 2
                body = []

                while j < len(lines):
                    line = lines[j]
                    if not line.strip() or "|" not in line:
                        break
                    row = _pipe_row_to_cells(line)
                    if len(row) != len(header):
                        break
                    body.append(row)
                    j += 1

                if body:
                    flush_markdown()
                    parts.append(("table", _pipe_table_to_latex(header, body)))
                    i = j
                    continue

        markdown_lines.append(lines[i])
        i += 1

    flush_markdown()

    if not parts:
        return [("markdown", md_text)]

    return parts


def _parse_document_meta(md_text):
    title = ""
    authors = ""
    date = ""

    for line in md_text.splitlines():
        match = re.match(r"^\s*(title|authors?|date)\s*:\s*(.*?)\s*$", line, re.IGNORECASE)
        if not match:
            continue

        key = match.group(1).lower()
        value = match.group(2).strip()

        if key == "title":
            title = value
        elif key in {"author", "authors"}:
            authors = value
        elif key == "date":
            date = value

    return DocumentMeta(title=title, authors=authors, date=date)


def build_ir(nb, figure_dir="figures", figure_ref_dir=None):
    ir = []
    metadata = DocumentMeta()
    counters = Counters()
    last_md = ""
    figure_file_index = 0
    first_markdown_processed = False

    for cell in nb["cells"]:
        if cell["cell_type"] == "markdown":
            text = "".join(cell["source"])

            if not first_markdown_processed:
                first_markdown_processed = True
                parsed_meta = _parse_document_meta(text)

                if parsed_meta.has_title_info():
                    metadata = parsed_meta
                    continue

            for kind, chunk in split_markdown_display_equations(text):
                if kind == "markdown":
                    for md_kind, md_chunk in _split_markdown_pipe_tables(chunk):
                        if md_kind == "markdown":
                            ir.append(MarkdownBlock(md_chunk))
                        else:
                            ir.append(TableBlock(md_chunk, "", ""))
                else:
                    label = counters.next_eq()
                    ir.append(EquationBlock(chunk, label))

            last_md = text

        elif cell["cell_type"] == "code":
            code = "".join(cell["source"])
            ir.append(CodeBlock(code))

            outputs = cell.get("outputs", [])

            # Preserve output order exactly as they appear in the notebook.
            for out in outputs:
                path = extract_figure_from_output(
                    out,
                    fig_dir=figure_dir,
                    figure_ref_dir=figure_ref_dir,
                    figure_index=figure_file_index,
                )
                if path:
                    figure_file_index += 1
                    label = counters.next_fig()
                    caption = extract_caption(last_md, "Generated figure")
                    ir.append(FigureBlock(path, caption, label))
                    continue

                tbl = extract_table_from_output(out)
                if tbl:
                    label = counters.next_tbl()
                    caption = extract_caption(last_md, "Generated table")
                    ir.append(TableBlock(tbl, caption, label))
                    continue

                eq = extract_equation_from_output(out)
                if eq:
                    label = counters.next_eq()
                    ir.append(EquationBlock(eq, label))

    return ir, metadata