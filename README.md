# nb2tex

Convert Jupyter notebooks to LaTeX with figures, tables, equations, and code blocks.

The LaTeX template is bundled inside the package, so conversion works from any working directory after install.

## Install

```bash
pip install .
```

## Usage

```bash
nb2tex path/to/notebook.ipynb -o path/to/output.tex
```

Custom figure directory name (relative to notebook location):

```bash
nb2tex path/to/notebook.ipynb --figures-dir plots -o path/to/output.tex
```

Custom figure directory absolute path:

```bash
nb2tex path/to/notebook.ipynb --figures-dir /absolute/path/to/my-images -o path/to/output.tex
```

If `-o/--output` is omitted, the output is written next to the notebook as `<notebook_name>.tex`.

## Figures directory requirement

`nb2tex` checks that the selected figures directory exists (default is `figures` next to the notebook).
If it does not exist, conversion fails with an error.

## Reliability normalization rules

`nb2tex` applies deterministic normalization passes so generic notebooks compile under `pdflatex` without manual TeX edits:

- Heading compatibility: the bundled template always loads `hyperref`, so heading-related macros generated from markdown are defined.
- Math delimiter sanitizer: malformed or unbalanced `$...$` / `$$...$$` delimiters are sanitized by escaping unmatched delimiters instead of emitting broken math environments.
- Unicode in markdown: selected scientific symbols are normalized to TeX-safe forms in markdown-derived LaTeX:
	- `°` -> `\ensuremath{^\circ}`
	- `Ω` -> `\ensuremath{\Omega}`
	- `ω` -> `\ensuremath{\omega}`
	- `μ` -> `\ensuremath{\mu}`
	- `φ` -> `\ensuremath{\phi}`
	- `π` -> `\ensuremath{\pi}`
	- `±` -> `\ensuremath{\pm}`
- Unicode in code listings: code cell content is made ASCII-safe for `listings`.
	- Common symbols use readable mappings (for example `±` -> `+/-`, `μ` -> `mu`).
	- Any remaining non-ASCII codepoint is emitted as `\uXXXX`.

## Regression demo and tests

- Synthetic notebook: `examples/regression_demo.ipynb`
- Regression test: `tests/test_regression_pdflatex.py`

The regression test converts the synthetic notebook with `nb2tex`, compiles the generated TeX with `pdflatex`, and asserts that these log signatures are absent:

- `Undefined control sequence`
- `Bad math environment delimiter`
- `Missing $ inserted`
- `Invalid UTF-8 byte sequence`
