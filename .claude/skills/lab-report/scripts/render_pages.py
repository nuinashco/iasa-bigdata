# /// script
# requires-python = ">=3.13"
# dependencies = ["pymupdf", "pillow"]
# ///
"""Render a PDF into contact sheets (8 pages each) and run quick text checks.

    uv run .claude/skills/lab-report/scripts/render_pages.py labs/<lab>/report/report.pdf OUT_DIR [--zoom PAGE]

Prints page count, embedded fonts and leftovers (TODO, unresolved "??" references); writes
OUT_DIR/sheet1.png, sheet2.png, ... for viewing. --zoom PAGE (1-based) also writes a readable
OUT_DIR/page-PAGE.png, for checking screenshot text size or a formula.
"""

import argparse
import io
import re
from pathlib import Path

import pymupdf
from PIL import Image


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf")
    parser.add_argument("out_dir", type=Path)
    parser.add_argument("--zoom", type=int, action="append", default=[])
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    doc = pymupdf.open(args.pdf)
    text = "\n".join(page.get_text() for page in doc)
    fonts = sorted({f[3].split("+")[-1] for page in doc for f in page.get_fonts()})
    print(f"pages: {doc.page_count}")
    print(f"fonts: {fonts}")
    print(f"TODO: {text.count('TODO')}, unresolved refs '??': {text.count('??')}")
    for kind in ("Рисунок", "Таблиця", "Лістинг"):
        print(f"{kind}: {len(re.findall(kind + r' [\dА-ЯЄІЇ]+\.\d+ –', text))}")

    pages = [Image.open(io.BytesIO(page.get_pixmap(dpi=45).tobytes("png"))) for page in doc]
    width, height = pages[0].size
    for start in range(0, len(pages), 8):
        sheet = Image.new("RGB", (width * 4, height * 2), "white")
        for k, img in enumerate(pages[start:start + 8]):
            sheet.paste(img, ((k % 4) * width, (k // 4) * height))
        sheet.save(args.out_dir / f"sheet{start // 8 + 1}.png")
    for number in args.zoom:
        doc[number - 1].get_pixmap(dpi=110).save(args.out_dir / f"page-{number}.png")
    print(f"sheets: {args.out_dir}/sheet*.png")


if __name__ == "__main__":
    main()
