"""Download the OpenFlights datasets used in lab 2 into data/openflights/.

Files come from the OpenFlights GitHub repository, pinned to one commit so every run gets the
same data. Does nothing for files that already exist, unless --force is given.

Usage:
    python labs/002-spark-graphframes/scripts/download_data.py [--data-dir DIR] [--force]
"""

import argparse
import urllib.request
from pathlib import Path

COMMIT = "7d1a611e070295dba776d6afb86e57d0d1aa1cef"
BASE_URL = f"https://raw.githubusercontent.com/jpatokal/openflights/{COMMIT}/data"
FILES = ["airports-extended.dat", "airlines.dat", "routes.dat"]

DEFAULT_DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument("--force", action="store_true", help="re-download even if files exist")
    args = parser.parse_args()

    target = args.data_dir / "openflights"
    target.mkdir(parents=True, exist_ok=True)
    for name in FILES:
        path = target / name
        if path.exists() and not args.force:
            print(f"[skip] {path.name} already present")
            continue
        partial = path.with_suffix(".part")
        urllib.request.urlretrieve(f"{BASE_URL}/{name}", partial)
        partial.rename(path)
        lines = sum(1 for _ in path.open(encoding="utf-8"))
        print(f"[download] {path.name}: {lines:,} lines, {path.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
