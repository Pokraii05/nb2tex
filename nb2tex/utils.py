import pypandoc


def markdown_to_latex(md_text):
    return pypandoc.convert_text(md_text, "latex", format="md")


def extract_caption(md_text, default="Generated"):
    if not md_text:
        return default

    for line in md_text.splitlines():
        if line.lower().startswith("figure:"):
            return line.split(":", 1)[1].strip()
        if line.lower().startswith("table:"):
            return line.split(":", 1)[1].strip()

    return default
