# /// script
# requires-python = ">=3.13"
# dependencies = ["playwright"]
# ///
"""Render Mermaid diagrams (.mmd) to SVG and PDF next to each source file.

    uv run scripts/render_mermaid.py labs/<lab>/assets/*.mmd

The .mmd file is the single source: the SVG is for notebooks and Markdown (shown as an image,
so no Mermaid support is needed), the PDF is for LaTeX reports (XeLaTeX can't include SVG;
PDF stays vector). Uses the system Chromium if installed, otherwise Playwright's.
"""

import shutil
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

# Pinned so re-rendering an unchanged source gives the same picture.
MERMAID_URL = "https://cdn.jsdelivr.net/npm/mermaid@11.17.2/dist/mermaid.min.js"

# htmlLabels=false: labels become plain SVG text. HTML labels are embedded via <foreignObject>,
# which renders blank when the SVG is displayed as an image (<img>, notebooks, GitHub).
RENDER_JS = """async (src) => {
    mermaid.initialize({startOnLoad: false, htmlLabels: false, markdownAutoWrap: false,
                        flowchart: {htmlLabels: false, wrappingWidth: 1000}});
    const {svg} = await mermaid.render("diagram", src);
    document.body.innerHTML = svg;
    const el = document.querySelector("svg");
    const box = el.getBoundingClientRect();
    return {svg: el.outerHTML, width: Math.ceil(box.width), height: Math.ceil(box.height)};
}"""


def browser_path() -> str | None:
    for name in ("chromium", "chromium-browser", "google-chrome"):
        if path := shutil.which(name):
            return path
    return None


def main() -> None:
    sources = [Path(arg) for arg in sys.argv[1:]]
    if not sources:
        sys.exit(__doc__)
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=browser_path())
        for source in sources:
            page = browser.new_page()
            page.set_content(f'<html><body style="margin:0"><script src="{MERMAID_URL}"></script></body></html>')
            page.wait_for_function("window.mermaid !== undefined")
            try:
                result = page.evaluate(RENDER_JS, source.read_text(encoding="utf-8"))
            except Exception as error:
                sys.exit(f"error: {source}: {error}")
            source.with_suffix(".svg").write_text(result["svg"], encoding="utf-8")
            page.pdf(path=source.with_suffix(".pdf"), width=f"{result['width']}px",
                     height=f"{result['height'] + 1}px", print_background=True)
            page.close()
            print(f"{source} -> .svg, .pdf ({result['width']}x{result['height']})")
        browser.close()


if __name__ == "__main__":
    main()
