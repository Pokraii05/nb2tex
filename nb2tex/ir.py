# =========================
# nb2tex/ir.py
# =========================

class Counters:
    def __init__(self):
        self.fig = 0
        self.tbl = 0
        self.eq = 0

    def next_fig(self):
        self.fig += 1
        return f"nb2tex:fig:{self.fig}"

    def next_tbl(self):
        self.tbl += 1
        return f"nb2tex:tbl:{self.tbl}"

    def next_eq(self):
        self.eq += 1
        return f"nb2tex:eq:{self.eq}"


class MarkdownBlock:
    def __init__(self, text):
        self.text = text


class CodeBlock:
    def __init__(self, code):
        self.code = code


class FigureBlock:
    def __init__(self, path, caption, label):
        self.path = path
        self.caption = caption
        self.label = label


class TableBlock:
    def __init__(self, latex, caption, label):
        self.latex = latex
        self.caption = caption
        self.label = label


class EquationBlock:
    def __init__(self, latex, label):
        self.latex = latex
        self.label = label


class DocumentMeta:
    def __init__(self, title="", authors="", date=""):
        self.title = title
        self.authors = authors
        self.date = date

    def has_title_info(self):
        return any([self.title, self.authors, self.date])
