
def render_markdown(block):
    return markdown_to_latex(block.text)


def render_code(block):
    return f"""
\\begin{{minted}}[fontsize=\\small, breaklines]{{python}}
{block.code}
\\end{{minted}}
"""


def render_figure(block):
    return f"""
\\begin{{figure}}[htbp]
\\centering
\\includegraphics[width=0.8\\textwidth]{{{block.path}}}
\\caption{{{block.caption}}}
\\label{{{block.label}}}
\\end{{figure}}
"""


def render_table(block):
    return f"""
\\begin{{table}}[htbp]
\\centering
{block.latex}
\\caption{{{block.caption}}}
\\label{{{block.label}}}
\\end{{table}}
"""


def render_equation(block):
    return f"""
\\begin{{equation}}
{block.latex}
\\label{{{block.label}}}
\\end{{equation}}
"""


def render_document(ir):
    body = []

    for block in ir:
        if isinstance(block, MarkdownBlock):
            body.append(render_markdown(block))
        elif isinstance(block, CodeBlock):
            body.append(render_code(block))
        elif isinstance(block, FigureBlock):
            body.append(render_figure(block))
        elif isinstance(block, TableBlock):
            body.append(render_table(block))
        elif isinstance(block, EquationBlock):
            body.append(render_equation(block))

    content = "\n".join(body)

    with open("templates/article.tex") as f:
        template = f.read()

    return template % content