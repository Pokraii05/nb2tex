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
        return f"fig:{self.fig}"

    def next_tbl(self):
        self.tbl += 1
        return f"tbl:{self.tbl}"

    def next_eq(self):
        self.eq += 1
        return f"eq:{self.eq}"


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
