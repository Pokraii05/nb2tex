
from importlib import resources

from nb2tex.ir import (
    MarkdownBlock,
    CodeBlock,
    FigureBlock,
    TableBlock,
    EquationBlock,
    DocumentMeta,
)
from nb2tex.utils import markdown_to_latex


def _normalize_code_for_latex(code):
    replacements = {
        "\u2013": "-",  # en dash
        "\u2014": "--",  # em dash
        "\u2212": "-",  # minus sign
        "\u00a0": " ",  # non-breaking space
    }
    for old, new in replacements.items():
        code = code.replace(old, new)
    return code


def render_markdown(block, markdown_index=0):
    return markdown_to_latex(block.text, id_prefix=f"nb2tex-m{markdown_index}-")


def render_code(block):
    code = _normalize_code_for_latex(block.code).rstrip("\n")
    return f"""
\\begin{{lstlisting}}[style=nbpython]
{code}
\\end{{lstlisting}}
"""


def render_figure(block):
    tex_path = block.path.replace("\\", "/")
    return f"""
\\begin{{figure}}[H]
\\centering
\\adjustbox{{max width=0.8\\linewidth,max totalheight=0.65\\textheight}}{{%
\\includegraphics{{{tex_path}}}%
}}
\\caption{{{block.caption}}}
\\label{{{block.label}}}
\\end{{figure}}
"""


def render_table(block):
    caption_and_label = ""
    if block.caption:
        caption_and_label += f"\\caption{{{block.caption}}}\n"
    if block.label:
        caption_and_label += f"\\label{{{block.label}}}\n"
    if block.caption:
        caption_and_label += "\\vspace{6pt}\n"

    return f"""
\\begin{{table}}[H]
\\centering
{caption_and_label}
{block.latex}
\\end{{table}}
"""


def render_equation(block):
    return f"""
\\begin{{equation}}
{block.latex}
\\label{{{block.label}}}
\\end{{equation}}
"""


def _escape_latex_text(text):
    if not text:
        return ""

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


def _render_title_block(metadata):
    if not metadata or not metadata.has_title_info():
        return ""

    title = _escape_latex_text(metadata.title)
    authors = _escape_latex_text(metadata.authors)
    date = _escape_latex_text(metadata.date)

    return "\n".join(
        [
            f"\\title{{{title}}}",
            f"\\author{{{authors}}}",
            f"\\date{{{date}}}",
            "\\maketitle",
        ]
    )


def render_document(ir, metadata=None):
    if metadata is None:
        metadata = DocumentMeta()

    body = []
    markdown_index = 0

    for block in ir:
        if isinstance(block, MarkdownBlock):
            body.append(render_markdown(block, markdown_index=markdown_index))
            markdown_index += 1
        elif isinstance(block, CodeBlock):
            body.append(render_code(block))
        elif isinstance(block, FigureBlock):
            body.append(render_figure(block))
        elif isinstance(block, TableBlock):
            body.append(render_table(block))
        elif isinstance(block, EquationBlock):
            body.append(render_equation(block))

    content = "\n".join(body)
    title_block = _render_title_block(metadata)

    template = resources.files("nb2tex").joinpath("templates/template.tex").read_text(
        encoding="utf-8"
    )

    if "%(content)" in template or "%(title_block)" in template:
        return template % {"title_block": title_block, "content": content}

    return template % content