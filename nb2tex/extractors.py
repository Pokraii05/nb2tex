import os
import base64
import re
from bs4 import BeautifulSoup


def _coerce_text(value):
    if isinstance(value, list):
        return "".join(value)
    if value is None:
        return ""
    return str(value)


def _escape_latex(text):
    replacements = {
        "\\": r"\\textbackslash{}",
        "&": r"\\&",
        "%": r"\\%",
        "$": r"\\$",
        "#": r"\\#",
        "_": r"\\_",
        "{": r"\\{",
        "}": r"\\}",
        "~": r"\\textasciitilde{}",
        "^": r"\\textasciicircum{}",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def _normalize_latex_math(expr):
    text = expr.strip()

    if text.startswith("$$") and text.endswith("$$") and len(text) >= 4:
        return text[2:-2].strip()
    if text.startswith("$") and text.endswith("$") and len(text) >= 2:
        return text[1:-1].strip()
    if text.startswith(r"\\[") and text.endswith(r"\\]") and len(text) >= 4:
        return text[2:-2].strip()
    if text.startswith(r"\\(") and text.endswith(r"\\)") and len(text) >= 4:
        return text[2:-2].strip()

    return text


def extract_figures(outputs, fig_dir="figures"):
    os.makedirs(fig_dir, exist_ok=True)
    figures = []

    for i, out in enumerate(outputs):
        filename = extract_figure_from_output(out, fig_dir=fig_dir, figure_index=i)
        if filename:
            figures.append(filename)

    return figures


def extract_equations(outputs):
    eqs = []
    for out in outputs:
        eq = extract_equation_from_output(out)
        if eq:
            eqs.append(eq)
    return eqs


def extract_figure_from_output(out, fig_dir="figures", figure_ref_dir=None, figure_index=0):
    data = out.get("data", {})
    if "image/png" not in data:
        return None

    os.makedirs(fig_dir, exist_ok=True)
    basename = f"fig_{figure_index}.png"
    filename = os.path.join(fig_dir, basename)
    png_data = _coerce_text(data["image/png"])
    with open(filename, "wb") as f:
        f.write(base64.b64decode(png_data))

    if figure_ref_dir is None:
        return filename
    return os.path.join(figure_ref_dir, basename)


def extract_equation_from_output(out):
    if out.get("output_type") not in {"display_data", "execute_result"}:
        return None

    data = out.get("data", {})
    if "text/latex" not in data:
        return None

    return _normalize_latex_math(_coerce_text(data["text/latex"]))


def _table_matrix_to_latex(table):
    if not table:
        return ""

    col_count = max(len(row) for row in table)
    normalized = []
    for row in table:
        padded = row + [""] * (col_count - len(row))
        normalized.append([_escape_latex(col) for col in padded])

    header = normalized[0]
    body = normalized[1:]

    lines = [
        "\\begin{tabular}{" + "l" * col_count + "}",
        "\\toprule",
        " & ".join(header) + r" \\",
        "\\midrule",
    ]

    for row in body:
        lines.append(" & ".join(row) + r" \\")

    lines.extend(["\\bottomrule", "\\end{tabular}"])
    return "\n".join(lines)


def _split_plain_row(line):
    row = re.split(r"\s{2,}|\t+", line.strip())
    return [cell for cell in row if cell != ""]


def plain_text_table_to_latex(text):
    lines = [line.rstrip() for line in text.splitlines() if line.strip()]
    if len(lines) < 2:
        return ""

    rows = [_split_plain_row(line) for line in lines]
    if any(len(row) < 2 for row in rows):
        return ""

    header = rows[0]
    body = rows[1:]
    col_count = len(header)

    indexed_rows = 0
    for row in body:
        if len(row) == col_count + 1 and row[0].isdigit():
            indexed_rows += 1

    use_index_column = indexed_rows >= max(1, len(body) // 2)
    normalized_body = []

    for row in body:
        if use_index_column and len(row) == col_count + 1:
            row = row[1:]
        if len(row) != col_count:
            return ""
        normalized_body.append(row)

    return _table_matrix_to_latex([header] + normalized_body)


def html_table_to_latex(html):
    soup = BeautifulSoup(html, "html.parser")
    rows = soup.find_all("tr")

    table = []
    for row in rows:
        cols = [col.get_text(strip=True) for col in row.find_all(["td", "th"])]
        table.append(cols)
    return _table_matrix_to_latex(table)


def extract_tables(outputs):
    tables = []

    for out in outputs:
        latex_table = extract_table_from_output(out)
        if latex_table:
            tables.append(latex_table)

    return tables


def extract_table_from_output(out):
    output_type = out.get("output_type")
    data = out.get("data", {})

    html = data.get("text/html")
    if html is not None:
        latex_table = html_table_to_latex(_coerce_text(html))
        if latex_table:
            return latex_table

    plain_text = ""
    if "text/plain" in data:
        plain_text = _coerce_text(data["text/plain"])
    elif output_type == "stream":
        plain_text = _coerce_text(out.get("text"))

    return plain_text_table_to_latex(plain_text)
