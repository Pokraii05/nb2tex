from nb2tex.ir import *
from nb2tex.extractors import extract_figures, extract_equations, extract_tables
from nb2tex.utils import extract_caption


def build_ir(nb):
    ir = []
    counters = Counters()
    last_md = ""

    for cell in nb["cells"]:
        if cell["cell_type"] == "markdown":
            text = "".join(cell["source"])
            ir.append(MarkdownBlock(text))
            last_md = text

        elif cell["cell_type"] == "code":
            code = "".join(cell["source"])
            ir.append(CodeBlock(code))

            outputs = cell.get("outputs", [])

            # Figures
            for path in extract_figures(outputs):
                label = counters.next_fig()
                caption = extract_caption(last_md, "Generated figure")
                ir.append(FigureBlock(path, caption, label))

            # Tables
            for tbl in extract_tables(outputs):
                label = counters.next_tbl()
                caption = extract_caption(last_md, "Generated table")
                ir.append(TableBlock(tbl, caption, label))

            # Equations
            for eq in extract_equations(outputs):
                label = counters.next_eq()
                ir.append(EquationBlock(eq, label))

    return ir