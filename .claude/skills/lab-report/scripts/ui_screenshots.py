# /// script
# requires-python = ">=3.13"
# dependencies = ["playwright"]
# ///
"""Screenshot pages of live web UIs (Spark, Hadoop/YARN, ...) as figures for a lab report.

    uv run .claude/skills/lab-report/scripts/ui_screenshots.py \
        labs/<lab>/report/ui_screenshots.toml labs/<lab>/report/assets

The spec (TOML) maps each output PNG to a page:

    width = 860                         # default viewport width, CSS px

    [shots.spark-master]                # -> assets/spark-master.png
    url = "http://localhost:8080/"
    hide = ["#completed-app", ".aggregated-completedApps"]  # optional: CSS selectors to hide
    selector = ".container-fluid"       # optional: capture this element (default: whole page)
    crop = [0, 0, 860, 600]             # optional: x, y, w, h in CSS px, relative to the element
    width = 1200                        # optional: per-shot viewport width
    script = "() => { ... }"            # optional: JS run before capture, e.g. to hide table rows

Read-only: pages are only loaded, and hide/script change the local copy of the page. The UIs
must be running when this runs; a Spark driver UI (port 4040) disappears with its notebook kernel.

Same device scale as nb_screenshots.py, so with the same width text comes out the same size.
Uses the system Chromium if installed, otherwise Playwright's.
"""

import shutil
import sys
import tomllib
from pathlib import Path

from playwright.sync_api import sync_playwright

DEFAULT_WIDTH = 860
SCALE = 2
PAD = 4  # CSS px of margin around a captured element


def browser_path() -> str | None:
    for name in ("chromium", "chromium-browser", "google-chrome"):
        if path := shutil.which(name):
            return path
    return None


def main() -> None:
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    spec = tomllib.loads(Path(sys.argv[1]).read_text())
    out_dir = Path(sys.argv[2])
    out_dir.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=browser_path())
        for name, shot in spec["shots"].items():
            width = shot.get("width", spec.get("width", DEFAULT_WIDTH))
            page = browser.new_page(viewport={"width": width, "height": 900}, device_scale_factor=SCALE)
            page.goto(shot["url"], wait_until="networkidle")
            page.wait_for_timeout(500)  # let JS-drawn content (e.g. Spark's DAG) settle
            if hide := shot.get("hide"):
                page.add_style_tag(content=f"{', '.join(hide)} {{ display: none !important; }}")
            if script := shot.get("script"):
                page.evaluate(script)

            box = {"x": 0, "y": 0, "width": width, "height": page.evaluate("document.body.scrollHeight")}
            if selector := shot.get("selector"):
                element = page.locator(selector).first
                if not element.count():
                    sys.exit(f"error: {name}: selector {selector!r} matches nothing on {shot['url']}")
                box = element.bounding_box()
                box = {"x": box["x"] - PAD, "y": box["y"] - PAD,
                       "width": box["width"] + 2 * PAD, "height": box["height"] + 2 * PAD}
            if crop := shot.get("crop"):
                x, y, w, h = crop
                box = {"x": box["x"] + x, "y": box["y"] + y, "width": w, "height": h}
            box["x"] = max(box["x"], 0)
            box["y"] = max(box["y"], 0)

            path = out_dir / f"{name}.png"
            page.screenshot(path=path, full_page=True, clip=box)
            page.close()
            print(f"{path}  ({round(box['width'])}x{round(box['height'])} CSS px)")
        browser.close()


if __name__ == "__main__":
    main()
