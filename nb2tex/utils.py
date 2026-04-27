import pypandoc
import re


_ESCAPED_INLINE_MATH_RE = re.compile(r"\\\$(.+?)\\\$", re.DOTALL)
_SPACED_INLINE_MATH_RE = re.compile(r"(?<!\\)\$\s+(.+?)\s+\$", re.DOTALL)
_PANDOC_BOUNDED_IMAGE_RE = re.compile(
    r"\\pandocbounded\{\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}\}"
)
_INLINE_MATH_LATEX_RE = re.compile(r"\\\((.+?)\\\)", re.DOTALL)


def _normalize_problematic_unicode_in_latex(latex_text):
    # Keep pdflatex-safe output for common scientific Unicode symbols in markdown.
    replacements = {
        "°": r"\ensuremath{^\circ}",
        "Ω": r"\ensuremath{\Omega}",
        "ω": r"\ensuremath{\omega}",
        "μ": r"\ensuremath{\mu}",
        "φ": r"\ensuremath{\phi}",
        "π": r"\ensuremath{\pi}",
        "±": r"\ensuremath{\pm}",
    }
    for old, new in replacements.items():
        latex_text = latex_text.replace(old, new)
    return latex_text


def _balance_dollar_math_delimiters(latex_text):
    # Validate and sanitize $ / $$ delimiters so malformed pairs become literals.
    out = []
    stack = []
    i = 0

    while i < len(latex_text):
        ch = latex_text[i]

        if ch == "\\" and i + 1 < len(latex_text):
            out.append(latex_text[i : i + 2])
            i += 2
            continue

        if ch != "$":
            out.append(ch)
            i += 1
            continue

        is_display = i + 1 < len(latex_text) and latex_text[i + 1] == "$"
        delim = "$$" if is_display else "$"

        if not stack:
            out.append(delim)
            stack.append((delim, len(out) - 1))
            i += 2 if is_display else 1
            continue

        current_delim, _ = stack[-1]
        if current_delim == delim:
            out.append(delim)
            stack.pop()
            i += 2 if is_display else 1
            continue

        # Mismatched nesting: treat as literal dollars rather than opening math.
        out.append(r"\$\$" if is_display else r"\$")
        i += 2 if is_display else 1

    while stack:
        delim, idx = stack.pop()
        out[idx] = r"\$\$" if delim == "$$" else r"\$"

    return "".join(out)


def _normalize_inline_math_delimiters(md_text):
    # Accept author-written \$...\$ as inline math and convert to $...$.
    md_text = _ESCAPED_INLINE_MATH_RE.sub(lambda m: f"${m.group(1)}$", md_text)
    # Also normalize spaced delimiters like "$ e^{...} $" to "$e^{...}$".
    return _SPACED_INLINE_MATH_RE.sub(lambda m: f"${m.group(1).strip()}$", md_text)


def _normalize_pandoc_bounded_images(latex_text):
    # Force all Pandoc-bounded images to stay within page bounds.
    def repl(match):
        path = match.group(1)
        return "\\pandocbounded{\\includegraphics{" + path + "}}"

    return _PANDOC_BOUNDED_IMAGE_RE.sub(repl, latex_text)


def _normalize_inline_math_spacing_in_latex(latex_text):
    # Keep natural word spacing around inline math when Pandoc collapses it,
    # e.g. "current\(I_k\)by" -> "current \(I_k\) by".
    def repl(match):
        segment = match.group(0)

        before = ""
        if match.start() > 0 and latex_text[match.start() - 1].isalnum():
            before = " "

        after = ""
        if match.end() < len(latex_text) and latex_text[match.end()].isalnum():
            after = " "

        return f"{before}{segment}{after}"

    return _INLINE_MATH_LATEX_RE.sub(repl, latex_text)


def markdown_to_latex(md_text, id_prefix=""):
    md_text = _normalize_inline_math_delimiters(md_text)
    extra_args = []
    if id_prefix:
        extra_args.append(f"--id-prefix={id_prefix}")

    latex = pypandoc.convert_text(
        md_text,
        "latex",
        format="markdown+tex_math_dollars-auto_identifiers",
        extra_args=extra_args,
    )
    latex = _normalize_pandoc_bounded_images(latex)
    # Avoid heuristic conversion of escaped dollars to math wrappers,
    # which can introduce partial delimiters in plain-text fragments.
    latex = _normalize_inline_math_spacing_in_latex(latex)
    latex = _normalize_problematic_unicode_in_latex(latex)
    latex = _balance_dollar_math_delimiters(latex)
    # Pandoc may return CRLF line endings; normalize to LF to keep spacing stable.
    return latex.replace("\r\n", "\n").replace("\r", "\n")


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
