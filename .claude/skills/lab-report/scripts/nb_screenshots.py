# /// script
# requires-python = ">=3.13"
# dependencies = ["nbconvert", "playwright", "pillow"]
# ///
"""Screenshot output areas of an executed Jupyter notebook, e.g. as figures for a lab report.

    uv run .claude/skills/lab-report/scripts/nb_screenshots.py \
        labs/<lab>/draft.ipynb labs/<lab>/report/screenshots.toml labs/<lab>/report/assets

The spec (TOML) maps each output PNG to notebook cells:

    width = 820                       # default viewport width, CSS px

    [shots.hdfs-ls]                   # -> assets/hdfs-ls.png
    cells = ['hdfs("dfs", "-ls"']     # source snippets (or indices) of one or more code cells
    width = 1000                      # optional: wider page for wide tables
    max_height = 400                  # optional: crop long outputs (cut at a blank row)

A snippet must occur in exactly one cell, so the spec survives cells being added or moved.
Only outputs are captured; code and In/Out prompts are hidden.

Needs a Chromium: the system one (`chromium`, `google-chrome`) is used if present, otherwise
Playwright's own (`uv run --with playwright playwright install chromium`).
"""

import shutil
import sys
import tempfile
import tomllib
from pathlib import Path

import nbformat
from nbconvert import HTMLExporter
from PIL import Image, ImageChops
from playwright.sync_api import sync_playwright

DEFAULT_WIDTH = 820  # ~110 monospace characters per line before wrapping
SCALE = 2  # device pixel ratio: crisp text when the PNG is scaled down in the PDF

CSS = """
.jp-InputArea, .jp-InputPrompt, .jp-OutputPrompt, .jp-Collapser { display: none !important; }
.jp-Cell { padding: 0 !important; }
body { margin: 0 !important; padding: 8px !important; background: white !important; }
.jp-RenderedText pre { white-space: pre-wrap !important; overflow-wrap: anywhere; }
"""


def resolve(cells: list, nb: nbformat.NotebookNode) -> list[int]:
    indices = []
    for ref in cells:
        if isinstance(ref, int):
            indices.append(ref)
            continue
        hits = [i for i, c in enumerate(nb.cells) if c.cell_type == "code" and ref in c.source]
        if len(hits) != 1:
            sys.exit(f"error: snippet {ref!r} matches {len(hits)} code cells, expected exactly 1")
        indices.append(hits[0])
    return indices


def tidy(path: Path, cut_at_blank: bool) -> None:
    """Trim white margins; for a height-limited shot also drop the partly cut last line."""
    img = Image.open(path).convert("RGB")
    if cut_at_blank:
        gray = img.convert("L")
        for y in range(gray.height - 1, 0, -1):
            if min(gray.crop((0, y, gray.width, y + 1)).getdata()) > 245:
                img = img.crop((0, 0, img.width, y))
                break
    bbox = ImageChops.difference(img, Image.new("RGB", img.size, "white")).getbbox()
    if bbox is None:
        sys.exit(f"error: {path.name} is blank; the cell has no visible output")
    pad = 12
    img.crop((max(bbox[0] - pad, 0), max(bbox[1] - pad, 0),
              min(bbox[2] + pad, img.width), min(bbox[3] + pad, img.height))).save(path)


def browser_path() -> str | None:
    for name in ("chromium", "chromium-browser", "google-chrome"):
        if path := shutil.which(name):
            return path
    return None


def main() -> None:
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    notebook, spec_file, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    spec = tomllib.loads(spec_file.read_text(encoding="utf-8"))
    default_width = spec.get("width", DEFAULT_WIDTH)
    nb = nbformat.read(notebook, as_version=4)
    out.mkdir(parents=True, exist_ok=True)

    # The lab template renders every notebook cell as one .jp-Cell, in order.
    html, _ = HTMLExporter(template_name="lab").from_notebook_node(nb)
    with tempfile.TemporaryDirectory() as tmp:
        page_file = Path(tmp) / "notebook.html"
        page_file.write_text(html, encoding="utf-8")

        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=browser_path())
            for name, shot in spec["shots"].items():
                cells = resolve(shot["cells"], nb)
                max_height = shot.get("max_height")
                page = browser.new_page(viewport={"width": shot.get("width", default_width), "height": 800},
                                        device_scale_factor=SCALE)
                page.goto(page_file.as_uri())
                page.add_style_tag(content=CSS)
                boxes = []
                for i in cells:
                    box = page.locator(".jp-Cell").nth(i).locator(".jp-Cell-outputWrapper").bounding_box()
                    if box is None:
                        sys.exit(f"error: shot {name!r}: cell {i} has no output")
                    boxes.append(box)
                x = min(b["x"] for b in boxes)
                y = min(b["y"] for b in boxes)
                right = max(b["x"] + b["width"] for b in boxes)
                bottom = max(b["y"] + b["height"] for b in boxes)
                # Wide DataFrames overflow the cell box; include their full width.
                scroll = page.evaluate(
                    "(idx) => Math.max(...idx.map(i => document.querySelectorAll('.jp-Cell')[i]"
                    ".querySelector('.jp-Cell-outputWrapper').scrollWidth))",
                    cells,
                )
                right = max(right, x + scroll)
                height = bottom - y if max_height is None else min(bottom - y, max_height)
                target = out / f"{name}.png"
                # full_page + clip captures below the viewport without resizing it (resizing reflows).
                page.screenshot(path=target, full_page=True,
                                clip={"x": x, "y": y, "width": right - x, "height": height})
                page.close()
                tidy(target, cut_at_blank=max_height is not None)
                print(f"{target}  (cells {cells})")
            browser.close()


if __name__ == "__main__":
    main()
