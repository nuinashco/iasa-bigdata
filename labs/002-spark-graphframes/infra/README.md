# Spark 4 standalone cluster

Local Spark cluster for `labs/002-spark-graphframes`: one master and two workers in Docker. The driver is the notebook kernel on the host, so GraphFrames jobs are planned in the notebook and executed by executors in the worker containers.

| Service | Image | Role |
|---|---|---|
| `spark-master` | `lab002-spark:4.0.4` (built from `Dockerfile`) | Standalone master: registers workers, allocates executors |
| `spark-worker-1`, `spark-worker-2` | same | Workers: 4 cores, 6 GB each; run executors |

Start it from the lab directory with `lab002.cluster.compose_up` (the notebook's first step does this), which sets the required environment:

```python
compose_up("infra/docker-compose.yml", "data")
```

Web UIs: master http://localhost:8080, workers http://localhost:8081 and :8082, the running application (driver) http://localhost:4040.

## Design decisions

- **Image** (`Dockerfile`): the official `apache/spark:4.0.4-scala2.13-java21-ubuntu` plus Python 3.13 installed with uv. Executors must run the same Python minor version as the driver (the notebook's `.venv`); the official python3 image ships Ubuntu's 3.10, which PySpark rejects for UDFs and RDD code.
- **Spark 4.0.4 with Java 21**: Debian trixie (the host) only packages Java 21, which Spark 3.5 doesn't support officially. GraphFrames 0.12.3 has a Spark 4 build (`io.graphframes:graphframes-spark4_2.13`), downloaded by the driver at session start.
- **Host networking**: executors connect back to the driver; with host networking that's `127.0.0.1`, with no driver ports to publish. Linux only. Because every executor then reports host `127.0.0.1`, `spark.shuffle.readHostLocalDisk` is disabled in `lab002.spark`, otherwise Spark would read other executors' shuffle files from a disk it doesn't share.
- **Data at the same path everywhere**: Spark reads files on each worker, so the lab's `data/` is mounted at its host path in every container (`LAB_DATA`). A real cluster would use HDFS or object storage; for one machine a bind mount is the equivalent. Connected components write their checkpoints there too.
- **Containers run as the host user** (`LAB_UID`/`LAB_GID`), so checkpoints in `data/` aren't owned by root. Hadoop's login inside Spark needs a passwd entry for that uid, hence the read-only `/etc/passwd` and `/etc/group` mounts.
- **Project name `lab002`**: every lab keeps its compose file in `infra/`; with the default project name (the directory) the labs' clusters would look like each other's orphan containers.
