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

If `-o/--output` is omitted, the output is written next to the notebook as `<notebook_name>.tex`.

## Figures directory requirement

`nb2tex` expects a `figures` directory to exist in the same directory as the input notebook.
If that directory does not exist, conversion fails with an error.
