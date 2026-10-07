"""Download the EDR registry (legal entities + sole proprietors) and convert it to CSV.

Source: the last open-data dump of the Unified State Register (ЄДР) published by
NAIS (nais.gov.ua) on 2022-04-08, retrieved from the Internet Archive. Later dumps
(data.gov.ua, 2026+) no longer contain ADDRESS / KVED, which the lab's queries need.

Output (UTF-8, comma-separated, every field quoted, header row):
    data/UO.csv   name, edrpou, address, boss, founders, kved, stan
    data/FOP.csv  fio, address, kved, stan

Usage:
    python labs/001-hadoop-and-hive/scripts/download_data.py [--data-dir DIR] [--force]

Does nothing if both CSVs already exist, unless --force is given.
"""

import argparse
import csv
import hashlib
import shutil
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

ARCHIVE_URL = (
    "https://web.archive.org/web/20220413051017id_/"
    "https://nais.gov.ua/files/general/2022/04/08/20220408144948-25.zip"
)
ARCHIVE_SHA256 = "c622d0817e9e252a221303e47cf7b99c439305d50692655af452e34a9ca68d72"
ARCHIVE_NAME = "edr_2022-04-08.zip"

# zip member suffix -> (output csv, [(csv column, xml tag)])
TABLES = {
    "17.1-EX_XML_EDR_UO_08.04.2022.xml": (
        "UO.csv",
        [
            ("name", "NAME"),
            ("edrpou", "EDRPOU"),
            ("address", "ADDRESS"),
            ("boss", "BOSS"),
            ("founders", "FOUNDERS"),
            ("kved", "KVED"),
            ("stan", "STAN"),
        ],
    ),
    "17.2-EX_XML_EDR_FOP_08.04.2022.xml": (
        "FOP.csv",
        [
            ("fio", "FIO"),
            ("address", "ADDRESS"),
            ("kved", "KVED"),
            ("stan", "STAN"),
        ],
    ),
}

DEFAULT_DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def download(dest: Path) -> None:
    if dest.exists() and sha256(dest) == ARCHIVE_SHA256:
        print(f"[download] {dest.name} already present, checksum OK")
        return
    print(f"[download] {ARCHIVE_URL}")
    tmp = dest.with_suffix(".part")
    with urllib.request.urlopen(ARCHIVE_URL, timeout=60) as resp, tmp.open("wb") as out:
        shutil.copyfileobj(resp, out, length=1 << 20)
    if (digest := sha256(tmp)) != ARCHIVE_SHA256:
        tmp.unlink()
        sys.exit(f"[download] checksum mismatch: got {digest}")
    tmp.rename(dest)
    print(f"[download] saved {dest} ({dest.stat().st_size / 1e6:.0f} MB)")


def clean(text: str) -> str:
    # One record per line for Hive's TextInputFormat; backslash is OpenCSVSerde's escape char.
    return " ".join(text.replace("\\", "/").split())


def field_text(elem: ET.Element | None) -> str:
    if elem is None:
        return ""
    children = list(elem)
    if children:  # multi-valued, e.g. <FOUNDERS><FOUNDER>..</FOUNDER>...</FOUNDERS>
        return " | ".join(clean(c.text or "") for c in children)
    return clean(elem.text or "")


def convert(archive: Path, member: str, out_path: Path, columns: list[tuple[str, str]]) -> int:
    started = time.monotonic()
    rows = 0
    tmp = out_path.with_suffix(".part")
    with zipfile.ZipFile(archive) as zf, zf.open(member) as src, tmp.open("w", newline="", encoding="utf-8") as dst:
        writer = csv.writer(dst, quoting=csv.QUOTE_ALL, lineterminator="\n")
        writer.writerow([col for col, _ in columns])
        for _, elem in ET.iterparse(src, events=("end",)):
            if elem.tag != "RECORD":
                continue
            writer.writerow([field_text(elem.find(tag)) for _, tag in columns])
            elem.clear()
            rows += 1
    tmp.rename(out_path)
    print(f"[convert] {out_path.name}: {rows:,} rows in {time.monotonic() - started:.0f}s")
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument("--force", action="store_true", help="re-download and re-convert even if CSVs exist")
    args = parser.parse_args()

    outputs = [args.data_dir / out_name for out_name, _ in TABLES.values()]
    if not args.force and all(p.exists() for p in outputs):
        print(f"[skip] {', '.join(p.name for p in outputs)} already in {args.data_dir} (use --force to rebuild)")
        return

    raw_dir = args.data_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    archive = raw_dir / ARCHIVE_NAME
    download(archive)

    with zipfile.ZipFile(archive) as zf:
        members = {name.rsplit("/", 1)[-1]: name for name in zf.namelist()}

    with ProcessPoolExecutor(max_workers=len(TABLES)) as pool:
        jobs = [
            pool.submit(convert, archive, members[suffix], args.data_dir / out_name, columns)
            for suffix, (out_name, columns) in TABLES.items()
        ]
        for job in jobs:
            job.result()


if __name__ == "__main__":
    main()
