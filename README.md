# IASA Master's — Big Data Processing

Labs for «Обробка надвеликих масивів даних» (KPI, IASA): Jupyter notebooks running on local Docker clusters, with LaTeX reports.

| Lab | Topic |
|---|---|
| [001](labs/001-hadoop-and-hive) | Distributed data processing in Apache Hadoop and Apache Hive |
| [002](labs/002-spark-graphframes) | Graph structures with Spark GraphFrames (OpenFlights) |

## Installation and Usage

### 1. Install uv and necessary tools

Install `uv`:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

For alternatives, see [Installing uv](https://docs.astral.sh/uv/getting-started/installation/).

Install [Docker Engine](https://docs.docker.com/engine/install/) with the Compose plugin: labs run their clusters in Docker, and reports are built in a Docker image.

### 2. Create and activate the virtual environment

```bash
uv sync
source .venv/bin/activate
```

### 3. Run a lab

Open `labs/<lab>/draft.ipynb` with the `.venv` kernel and run all cells. The notebook starts the lab's cluster (`labs/<lab>/infra/`), downloads the data and runs every task.

### 4. Build a report

```bash
latex/build.sh labs/001-hadoop-and-hive/report/report.tex
```

The PDF is written next to `report.tex`. The first build creates the `iasa-latex` Docker image (~3 min).

See [CONTRIBUTING.md](CONTRIBUTING.md) for the repository layout, adding a lab and report conventions.
