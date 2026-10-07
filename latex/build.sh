#!/usr/bin/env bash
# Build a report with the Dockerised TeX toolchain; only Docker is needed on the host.
#   latex/build.sh labs/001-hadoop-and-hive/report/report.tex [extra latexmk args, e.g. -pvc]
# The PDF lands next to the .tex file; auxiliary files go to build/ beside it.
set -euo pipefail

repo="$(cd "$(dirname "$0")/.." && pwd)"
tex="$(realpath "${1:?usage: latex/build.sh path/to/report.tex [latexmk args]}")"
shift
[[ "$tex" == "$repo"/* ]] || { echo "error: $tex is outside $repo (only the repo is mounted)" >&2; exit 1; }

# Cheap when nothing changed: every layer comes from the cache.
docker build --quiet --tag iasa-latex "$repo/latex" >/dev/null

rel="${tex#"$repo"/}"
# Host uid/gid so outputs aren't root-owned; HOME=/tmp because that uid has no home in the image.
docker run --rm \
    --user "$(id -u):$(id -g)" \
    --env HOME=/tmp \
    --env TEXINPUTS="/work/latex//:" \
    --volume "$repo":/work \
    --workdir "/work/$(dirname "$rel")" \
    iasa-latex \
    latexmk -r /work/latex/latexmkrc "$@" "$(basename "$rel")"
