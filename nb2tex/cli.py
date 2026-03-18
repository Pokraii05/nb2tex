import argparse
import json
import os
from nb2tex.parser import build_ir
from nb2tex.renderer import render_document


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("-o", "--output")

    args = parser.parse_args()

    input_path = os.path.abspath(args.input)
    if args.output:
        output_path = os.path.abspath(args.output)
    else:
        input_dir = os.path.dirname(input_path)
        input_stem = os.path.splitext(os.path.basename(input_path))[0]
        output_path = os.path.join(input_dir, f"{input_stem}.tex")

    output_dir = os.path.dirname(output_path)
    os.makedirs(output_dir, exist_ok=True)
    figure_dir = os.path.join(output_dir, "figures")

    with open(input_path, "r", encoding="utf-8-sig") as f:
        nb = json.load(f)

    ir = build_ir(nb, figure_dir=figure_dir, figure_ref_dir="figures")
    tex = render_document(ir)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(tex)


if __name__ == "__main__":
    main()