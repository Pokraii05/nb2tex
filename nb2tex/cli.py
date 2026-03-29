import argparse
import json
import os

from nb2tex.parser import build_ir
from nb2tex.renderer import render_document


def main():
    parser = argparse.ArgumentParser(
        description="Convert a Jupyter notebook (.ipynb) to LaTeX (.tex)."
    )
    parser.add_argument("input", help="Path to input notebook (.ipynb)")
    parser.add_argument("-o", "--output", help="Path to output .tex file")
    parser.add_argument(
        "--figures-dir",
        default="figures",
        help=(
            "Figure directory name or path. Relative paths are resolved "
            "relative to the input notebook directory."
        ),
    )

    args = parser.parse_args()

    input_path = os.path.abspath(args.input)
    if not os.path.isfile(input_path):
        parser.error(f"Input notebook does not exist: {input_path}")

    input_dir = os.path.dirname(input_path)
    if os.path.isabs(args.figures_dir):
        figure_dir = args.figures_dir
    else:
        figure_dir = os.path.join(input_dir, args.figures_dir)
    figure_dir = os.path.abspath(figure_dir)

    if not os.path.isdir(figure_dir):
        parser.error(
            "Expected figures directory was not found: "
            f"{figure_dir}"
        )

    if args.output:
        output_path = os.path.abspath(args.output)
    else:
        input_stem = os.path.splitext(os.path.basename(input_path))[0]
        output_path = os.path.join(input_dir, f"{input_stem}.tex")

    output_dir = os.path.dirname(output_path)
    os.makedirs(output_dir, exist_ok=True)

    figure_ref_dir = os.path.relpath(figure_dir, start=output_dir).replace("\\", "/")

    with open(input_path, "r", encoding="utf-8-sig") as f:
        nb = json.load(f)

    ir, metadata = build_ir(
        nb,
        figure_dir=figure_dir,
        figure_ref_dir=figure_ref_dir,
    )
    tex = render_document(ir, metadata)

    with open(output_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(tex)


if __name__ == "__main__":
    main()