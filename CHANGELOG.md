# Changelog

## Unreleased

- Fixed heading conversion reliability by loading `hyperref` in the default LaTeX template, so heading-related macros emitted by markdown conversion are always defined.
- Added a math delimiter sanitizer pass for markdown-rendered LaTeX that balances `$...$` and `$$...$$` pairs and escapes malformed unmatched delimiters.
- Added Unicode normalization for markdown-rendered LaTeX symbols (`°`, `Ω`, `ω`, `μ`, `φ`, `π`, `±`) to TeX-safe math forms.
- Added deterministic Unicode normalization for code listings: common scientific symbols are mapped to readable ASCII (`±` -> `+/-`, `μ` -> `mu`, etc.), and any remaining non-ASCII codepoint is emitted as `\uXXXX`.
- Added a synthetic regression notebook and a compile test that runs `nb2tex` and `pdflatex`, asserting absence of:
  - `Undefined control sequence`
  - `Bad math environment delimiter`
  - `Missing $ inserted`
  - `Invalid UTF-8 byte sequence`
