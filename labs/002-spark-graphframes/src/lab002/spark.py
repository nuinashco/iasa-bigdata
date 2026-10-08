import os
from pathlib import Path

from pyspark.sql import SparkSession

MASTER_URL = "spark://127.0.0.1:7077"
# GraphFrames' JVM side; the version must match the graphframes-py package.
GRAPHFRAMES_PACKAGE = "io.graphframes:graphframes-spark4_2.13:0.12.3"
# See infra/Dockerfile.
WORKER_PYTHON = "/usr/local/bin/python3.13"


def spark_session(data_dir: str | Path, app_name: str = "lab002", driver_memory: str = "4g") -> SparkSession:
    """The driver runs in this process; executors run in the worker containers and, sharing the
    host network, connect back to it at 127.0.0.1. The checkpoint dir lives in data/, which is
    mounted at the same path in every container (connected components need checkpoints).
    """
    data_dir = Path(data_dir).resolve()
    # PySpark tells executors which Python to start from this variable of the driver process
    # (the spark.pyspark.python setting is only read by spark-submit).
    os.environ["PYSPARK_PYTHON"] = WORKER_PYTHON
    spark = (
        SparkSession.builder.master(MASTER_URL)
        .appName(app_name)
        .config("spark.driver.host", "127.0.0.1")
        .config("spark.driver.bindAddress", "127.0.0.1")
        .config("spark.driver.memory", driver_memory)
        .config("spark.jars.packages", GRAPHFRAMES_PACKAGE)
        .config("spark.sql.shuffle.partitions", "16")
        # All executors report host 127.0.0.1 (host networking), so Spark would take them for one
        # machine and read each other's shuffle files from disk; those live in another container.
        .config("spark.shuffle.readHostLocalDisk", "false")
        # Progress bars would end up in notebook outputs (as would INFO/WARN logs: setLogLevel below).
        .config("spark.ui.showConsoleProgress", "false")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("ERROR")
    checkpoints = data_dir / "checkpoints"
    checkpoints.mkdir(parents=True, exist_ok=True)
    spark.sparkContext.setCheckpointDir(str(checkpoints))
    return spark
