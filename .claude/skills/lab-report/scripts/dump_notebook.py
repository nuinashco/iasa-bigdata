# /// script
# requires-python = ">=3.13"
# dependencies = ["nbformat"]
# ///
"""Print an executed notebook as plain text: every cell's index, source and outputs.

    uv run .claude/skills/lab-report/scripts/dump_notebook.py labs/<lab>/draft.ipynb [--max-lines N] > /tmp/nb.txt

Use it to read results (numbers, tables, logs) and copy SQL verbatim without opening the
notebook UI. Cell indices match nb_screenshots.py. Long outputs are cut to --max-lines
(default 60) per output; pass 0 for everything.
"""

import argparse

import nbformat


def clip(text: str, max_lines: int) -> str:
    lines = text.rstrip("\n").splitlines()
    if max_lines and len(lines) > max_lines:
        return "\n".join(lines[:max_lines] + [f"... [{len(lines) - max_lines} more lines]"])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("notebook")
    parser.add_argument("--max-lines", type=int, default=60)
    args = parser.parse_args()

    nb = nbformat.read(args.notebook, as_version=4)
    executed = sum(1 for c in nb.cells if c.cell_type == "code" and c.execution_count)
    code = sum(1 for c in nb.cells if c.cell_type == "code")
    errors = 0
    print(f"# {args.notebook}: {len(nb.cells)} cells, {executed}/{code} code cells executed\n")
    for i, cell in enumerate(nb.cells):
        print(f"======== [{i}] {cell.cell_type}")
        print(cell.source)
        for out in cell.get("outputs", []):
            kind = out.output_type
            if kind == "stream":
                print(f"---- {out.name}\n{clip(out.text, args.max_lines)}")
            elif kind in ("execute_result", "display_data"):
                print(f"---- result\n{clip(out.data.get('text/plain', ''), args.max_lines)}")
            elif kind == "error":
                errors += 1
                print(f"---- ERROR {out.ename}: {out.evalue}")
        print()
    print(f"# errors: {errors}")


if __name__ == "__main__":
    main()
