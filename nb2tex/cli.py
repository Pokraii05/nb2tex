import argparse
import json
from nb2tex.parser import build_ir
from nb2tex.renderer import render_document


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("-o", "--output", default="output.tex")

    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        nb = json.load(f)

    ir = build_ir(nb)
    tex = render_document(ir)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(tex)


if __name__ == "__main__":
    main()