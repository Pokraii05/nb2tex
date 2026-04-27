import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from nb2tex.utils import markdown_to_latex


ERROR_SIGNATURES = [
    "Undefined control sequence",
    "Bad math environment delimiter",
    "Missing $ inserted",
    "Invalid UTF-8 byte sequence",
]


def _read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


class Nb2TexRegressionTests(unittest.TestCase):
    def test_exact_inline_math_sentence_is_stable(self):
        sentence = (
            r"We arrive at values of $R_R = 109.5\Omega$, $R_L = 5.9\Omega $ "
            r"and $C = 2.165 \mu F$."
        )

        latex = markdown_to_latex(sentence)

        self.assertIn(r"\(R_R = 109.5\Omega\)", latex)
        self.assertIn(r"\(R_L = 5.9\Omega\)", latex)
        self.assertIn(r"\(C = 2.165 \mu F\)", latex)
        self.assertNotIn(r"\$R\_L", latex)
        self.assertNotIn(r"\degree", latex)

    def test_regression_demo_compiles_without_known_failures(self):
        repo_root = Path(__file__).resolve().parents[1]
        source_nb = repo_root / "examples" / "regression_demo.ipynb"
        self.assertTrue(source_nb.exists(), f"Missing demo notebook: {source_nb}")

        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            nb_path = tmp_dir / "regression_demo.ipynb"
            tex_path = tmp_dir / "regression_demo.tex"
            figures_dir = tmp_dir / "figures"

            shutil.copy2(source_nb, nb_path)
            figures_dir.mkdir(parents=True, exist_ok=True)

            convert_cmd = [
                sys.executable,
                "-m",
                "nb2tex.cli",
                str(nb_path),
                "--figures-dir",
                "figures",
                "-o",
                str(tex_path),
            ]
            convert_result = subprocess.run(
                convert_cmd,
                cwd=repo_root,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
            self.assertEqual(
                0,
                convert_result.returncode,
                msg=f"nb2tex conversion failed:\n{convert_result.stdout}\n{convert_result.stderr}",
            )
            self.assertTrue(tex_path.exists(), "Expected .tex output was not generated")

            pdflatex_cmd = [
                "pdflatex",
                "-interaction=nonstopmode",
                "-halt-on-error",
                tex_path.name,
            ]
            try:
                pdflatex_result = subprocess.run(
                    pdflatex_cmd,
                    cwd=tmp_dir,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    check=False,
                )
            except FileNotFoundError:
                self.skipTest("pdflatex is not available in PATH")

            combined_log = "\n".join(
                [
                    pdflatex_result.stdout,
                    pdflatex_result.stderr,
                    _read_text(tmp_dir / "regression_demo.log"),
                ]
            )

            self.assertEqual(
                0,
                pdflatex_result.returncode,
                msg=f"pdflatex failed:\n{combined_log}",
            )

            for signature in ERROR_SIGNATURES:
                self.assertNotIn(
                    signature,
                    combined_log,
                    msg=f"Unexpected LaTeX error signature found: {signature}",
                )

            tex_output = _read_text(tex_path)
            self.assertIn("Lissajous curve collapses", tex_output)
            self.assertIn("phase shift", tex_output)


if __name__ == "__main__":
    unittest.main()
