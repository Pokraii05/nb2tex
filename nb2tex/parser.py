from nb2tex.ir import *
from nb2tex.extractors import (
    extract_figure_from_output,
    extract_table_from_output,
    extract_equation_from_output,
)
from nb2tex.utils import extract_caption, split_markdown_display_equations
import re


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
                    ir.append(MarkdownBlock(chunk))
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