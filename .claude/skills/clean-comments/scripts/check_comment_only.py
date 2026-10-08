# /// script
# requires-python = ">=3.10"
# ///
"""Verify that changes touch only comments and docstrings, never behaviour.

    uv run check_comment_only.py                 # working tree (staged + unstaged) vs HEAD
    uv run check_comment_only.py --ref main      # working tree vs another revision
    uv run check_comment_only.py --only a.py b/  # limit the git check to these paths
    uv run check_comment_only.py OLD NEW         # two files

Python files and notebook code cells are compared by AST with docstrings removed, so any
change to code fails even if it looks like a comment. Other files are compared line by line:
every added or removed line must be blank or a comment, and a line whose code part changed
fails. Exits 1 and lists the offending files if anything other than comments changed.
"""

import argparse
import ast
import difflib
import json
import re
import subprocess
import sys
from pathlib import Path

LINE_COMMENT = {
    "#": {".py", ".sh", ".bash", ".zsh", ".yml", ".yaml", ".toml", ".cfg", ".ini", ".conf", ".env",
          ".r", ".rb", ".pl", ".mk", ".tf", ".dockerfile", ""},
    "--": {".sql", ".lua", ".hs"},
    "//": {".js", ".jsx", ".ts", ".tsx", ".java", ".kt", ".c", ".h", ".cc", ".cpp", ".hpp", ".cs", ".go",
           ".rs", ".swift", ".scala", ".dart", ".php"},
    "%": {".tex", ".sty", ".cls", ".m"},
}
NAMED = {"Dockerfile": "#", "Makefile": "#", "Containerfile": "#", "latexmkrc": "#"}


def marker_for(path: str) -> str | None:
    name = Path(path).name
    if name in NAMED or name.startswith("Dockerfile"):
        return NAMED.get(name, "#")
    suffix = Path(path).suffix.lower()
    return next((m for m, exts in LINE_COMMENT.items() if suffix in exts), None)


def strip_docstrings(tree: ast.AST) -> ast.AST:
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            body = node.body
            if body and isinstance(body[0], ast.Expr) and isinstance(getattr(body[0], "value", None), ast.Constant) \
                    and isinstance(body[0].value.value, str):
                node.body = body[1:] or [ast.Pass()]
    return tree


def python_equal(old: str, new: str) -> bool:
    try:
        dump = lambda src: ast.dump(strip_docstrings(ast.parse(src)), include_attributes=False)
        return dump(old) == dump(new)
    except SyntaxError:
        return False


def notebook_cell_source(src: str) -> str:
    # IPython magics and shell escapes aren't Python; neutralise them so the cell still parses.
    return "\n".join("pass" if line.lstrip().startswith(("%", "!")) else line for line in src.splitlines())


def notebook_equal(old: str, new: str) -> str | None:
    """None if only code-cell comments/docstrings differ, otherwise the reason."""
    a, b = json.loads(old)["cells"], json.loads(new)["cells"]
    if len(a) != len(b):
        return "cell count changed"
    for i, (x, y) in enumerate(zip(a, b)):
        sx, sy = "".join(x["source"]), "".join(y["source"])
        if x["cell_type"] != y["cell_type"]:
            return f"cell {i}: type changed"
        if x["cell_type"] == "code":
            if not python_equal(notebook_cell_source(sx), notebook_cell_source(sy)):
                return f"cell {i}: code changed"
        elif sx != sy:
            return f"cell {i}: {x['cell_type']} cell changed (only code-cell comments may change)"
    return None


def code_part(line: str, marker: str) -> str:
    """The line with any trailing comment removed; quote-aware for '#' and '--' markers."""
    quote = None
    i = 0
    while i < len(line):
        ch = line[i]
        if quote:
            if ch == "\\":
                i += 2
                continue
            if ch == quote:
                quote = None
        elif ch in "\"'`":
            quote = ch
        elif line.startswith(marker, i):
            return line[:i].rstrip()
        i += 1
    return line.rstrip()


def text_equal(old: str, new: str, marker: str) -> str | None:
    strip = lambda text: [code_part(l, marker) for l in text.splitlines() if code_part(l, marker).strip()]
    a, b = strip(old), strip(new)
    if a == b:
        return None
    diff = next(l for l in difflib.unified_diff(a, b, lineterm="", n=0) if l[:1] in "+-" and l[:3] not in ("+++", "---"))
    return f"code changed: {diff.strip()[:100]}"


def compare(path: str, old: str, new: str) -> str | None:
    if path.endswith(".py"):
        return None if python_equal(old, new) else "Python code changed (AST differs beyond docstrings)"
    if path.endswith(".ipynb"):
        return notebook_equal(old, new)
    marker = marker_for(path)
    if marker is None:
        return None if old == new else "unknown file type: can't tell comments from code"
    return text_equal(old, new, marker)


def git(*args: str) -> str:
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout


def git_pairs(ref: str, only: list[str]):
    changed = [line for line in git("diff", "--name-status", ref, "--", *only).splitlines() if line]
    for entry in changed:
        status, *paths = entry.split("\t")
        path = paths[-1]
        if status.startswith(("A", "D", "R", "C")):
            yield path, None, f"file {'added' if status[0] == 'A' else 'deleted' if status[0] == 'D' else 'renamed'}"
            continue
        yield path, (git("show", f"{ref}:{path}"), Path(path).read_text(encoding="utf-8")), None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("files", nargs="*", help="OLD NEW file pair (default: git working tree vs --ref)")
    parser.add_argument("--ref", default="HEAD")
    parser.add_argument("--only", nargs="+", default=[], metavar="PATH", help="limit the git check to these paths")
    args = parser.parse_args()

    if args.files:
        if len(args.files) != 2:
            parser.error("give exactly two files: OLD NEW")
        old, new = (Path(f).read_text(encoding="utf-8") for f in args.files)
        results = [(args.files[1], compare(args.files[1], old, new))]
    else:
        results = []
        for path, pair, problem in git_pairs(args.ref, args.only):
            results.append((path, problem or compare(path, *pair)))

    failed = [(p, why) for p, why in results if why]
    for path, why in results:
        print(f"{'FAIL' if why else 'ok  '}  {path}" + (f"  — {why}" if why else ""))
    if not results:
        print("no changed files")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
