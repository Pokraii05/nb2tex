import os
import base64
from bs4 import BeautifulSoup


def extract_figures(outputs, fig_dir="figures"):
    os.makedirs(fig_dir, exist_ok=True)
    figures = []

    for i, out in enumerate(outputs):
        data = out.get("data", {})
        if "image/png" in data:
            filename = os.path.join(fig_dir, f"fig_{i}.png")
            with open(filename, "wb") as f:
                f.write(base64.b64decode(data["image/png"]))
            figures.append(filename)

    return figures


def extract_equations(outputs):
    eqs = []
    for out in outputs:
        if out.get("output_type") == "display_data":
            data = out.get("data", {})
            if "text/latex" in data:
                eqs.append("".join(data["text/latex"]))
    return eqs


def html_table_to_latex(html):
    soup = BeautifulSoup(html, "html.parser")
    rows = soup.find_all("tr")

    table = []
    for row in rows:
        cols = [col.get_text(strip=True) for col in row.find_all(["td", "th"])]
        table.append(cols)

    if not table:
        return ""
