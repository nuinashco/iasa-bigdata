# Hadoop 3 + Hive 3 Docker stack

Local multi-container cluster for `labs/001-hadoop-and-hive`: a real HDFS
filesystem and a real YARN resource manager, with Hive 3 wired to run its
queries as actual MapReduce jobs on that cluster (not in an embedded/local
mode). This satisfies the lab's "Hadoop 3+ / Hive 3+" requirement and lets
HDFS CLI commands, Hive DDL/DML, and the WordCount MapReduce job (tasks 1-5
in `task.pdf`) all execute against one coherent cluster.

## Why not the obvious single-image options

- `apache/hive` alone starts HiveServer2 with an embedded Derby metastore and
  a bundled Hadoop *client* only — there is no NameNode/DataNode/
  ResourceManager behind it. `hive.execution.engine` defaults to Tez running
  in **local mode** (in-process, not on YARN), and the warehouse lives on the
  container's local disk, not HDFS. Fine for a Hive-only smoke test, useless
  for tasks that need `hdfs dfs` or a visible YARN job.
- `big-data-europe/docker-hive` (the compose file most tutorials link to)
  bundles Hadoop **2.7.4**, which fails the task's explicit "3+" requirement
  outright, version mismatch aside.

So this setup composes a real Hadoop 3.1.3 cluster (HDFS + YARN) out of the
`bde2020/hadoop-*` images, and points a separate `apache/hive:3.1.3`
container at that cluster instead of running it standalone.

## Services and where each image comes from

| Service | Image | Role |
|---|---|---|
| `namenode` | `bde2020/hadoop-namenode:2.0.0-hadoop3.1.3-java8` | HDFS NameNode: filesystem namespace, block-to-DataNode mapping |
| `datanode` | `bde2020/hadoop-datanode:2.0.0-hadoop3.1.3-java8` | HDFS DataNode: stores the actual block data |
| `resourcemanager` | `bde2020/hadoop-resourcemanager:2.0.0-hadoop3.1.3-java8` | YARN ResourceManager: schedules jobs, allocates containers |
| `nodemanager` | `bde2020/hadoop-nodemanager:2.0.0-hadoop3.1.3-java8` | YARN NodeManager: actually runs Map/Reduce task containers |
| `historyserver` | `bde2020/hadoop-historyserver:2.0.0-hadoop3.1.3-java8` | MapReduce JobHistory server (finished-job UI, needed for report screenshots) |
| `hive-server` | `apache/hive:3.1.3` | HiveServer2, compiles HiveQL into MapReduce jobs submitted to the cluster above |

All `bde2020/hadoop-*` images are official-Hadoop-tarball wrappers from the
[big-data-europe/docker-hadoop](https://github.com/big-data-europe/docker-hadoop)
project (not affiliated with the ASF, but a widely used, straightforward
packaging of real `hadoop-3.1.3` binaries — one JVM role per container). The
`3.1.3` tag was picked specifically to match `apache/hive:3.1.3`'s own
bundled Hadoop client, minimizing wire-protocol/version mismatch risk between
Hive's client and the cluster's NameNode/ResourceManager.

Single DataNode + single NodeManager = a "pseudo-cluster": enough to
demonstrate every mechanism the lab asks about (replication, partitioning,
bucketing, MapReduce stages), not a production topology.

## Files in this directory and what reads them

### `docker-compose.yml`
Defines the 6 services above, their ports, volumes and startup order. All
`bde2020` services share one `env_file: ./hadoop.env`; `hive-server` gets its
own `environment:` block plus a mounted config directory (see below).

Two non-obvious bits baked into it:

1. **`hive-server` custom entrypoint.** The `bde2020` images have a built-in
   `SERVICE_PRECONDITION` mechanism (their base entrypoint polls
   `host:port` with `nc` before starting). The official `apache/hive` image
   has no such wait logic, and HiveServer2 touches HDFS (creates its scratch
   dir) right at startup. If HDFS/YARN aren't up yet, HiveServer2 fails
   immediately. The `entrypoint:` override is a plain `bash -c` loop using
   bash's own `/dev/tcp/<host>/<port>` pseudo-device (no `nc`/`curl` needed —
   the image's Debian base doesn't ship them) that blocks until
   `namenode:9000` and `resourcemanager:8088` accept connections, then
   `exec /entrypoint.sh` to hand off to the image's normal startup.
2. **`TEZ_HOME=/opt/tez_disabled`.** The image's own `/entrypoint.sh`
   unconditionally does
   `export HADOOP_CLASSPATH=$TEZ_HOME/*:$TEZ_HOME/lib/*:$HADOOP_CLASSPATH`
   whenever `SERVICE_NAME=hiveserver2` — regardless of which execution engine
   Hive is actually configured to use. With `hive.execution.engine=mr` (see
   `hive-site.xml` below), the Tez-bundled Hadoop classes on the classpath
   collide with the real `hadoop-mapreduce-client-core-3.1.0.jar` and every
   query fails with
   `NoSuchFieldError: MRJobConfig.DEFAULT_MR_AM_ADMIN_USER_ENV`
   (observed and reproduced while bringing this stack up). Pointing
   `TEZ_HOME` at a path that doesn't exist makes the glob expand to nothing,
   so no Tez jars get injected, and the classpath conflict disappears. This
   is a workaround for a real bug in the `apache/hive:3.1.3` image, not a
   documented option.

### `hadoop.env`
Adapted from the [big-data-europe/docker-hadoop `hadoop.env`](https://github.com/big-data-europe/docker-hadoop/blob/master/hadoop.env)
(verified against the raw file, not a paraphrase). Every `bde2020/hadoop-*`
image runs the same entrypoint script, which reads env vars of the form
`<PREFIX>_CONF_<dotted.property.name with underscores instead of dots>` and
turns each one into a real Hadoop XML property:

```
CORE_CONF_fs_defaultFS=hdfs://namenode:9000
     -> core-site.xml: <property><name>fs.defaultFS</name><value>hdfs://namenode:9000</value></property>
```

The name-mangling rule (single underscore -> dot, double underscore ->
literal underscore, triple underscore -> dash) is why some variable names
look unusual, e.g. `YARN_CONF_yarn_nodemanager_aux___services` becomes
`yarn.nodemanager.aux-services`. Values changed from the upstream defaults
for this host:

- `HDFS_CONF_dfs_replication=1` — only one DataNode exists here, so a
  replication factor above 1 would leave every block permanently
  under-replicated.
- `YARN_CONF_yarn_nodemanager_resource_memory___mb=8192` /
  `..._cpu___vcores=4` and the `MAPRED_CONF_*` memory/heap settings were
  scaled down from upstream's 16GB/8-vcore defaults to fit comfortably
  alongside the other 5 containers on this VM (31GB RAM, 8 cores total).

### `hive-conf/*.xml`
Mounted into the `hive-server` container at `/hive_custom_conf` and pointed
to by `HIVE_CUSTOM_CONF_DIR=/hive_custom_conf`. The image's `/entrypoint.sh`
symlinks every file from that directory into `$HIVE_CONF_DIR`
(`/opt/hive/conf`) and — critically — also sets
`HADOOP_CONF_DIR=$HIVE_CONF_DIR`, so these files replace whatever Hadoop
client config ships inside the Hive image by default (which points at
nothing, i.e. local mode). Without this, Hive has no idea the `namenode`/
`resourcemanager` containers exist.

- **`core-site.xml`** — `fs.defaultFS=hdfs://namenode:9000`. This is the one
  property that turns every relative HDFS path Hive uses (warehouse dir,
  scratch dir, table locations) into a path on the real cluster instead of
  the container's local disk.
- **`hdfs-site.xml`** — `dfs.replication=1`, mirroring the cluster setting on
  the client side.
- **`yarn-site.xml`** — `yarn.resourcemanager.hostname`/`address`/
  `scheduler.address` pointing at the `resourcemanager` container, so Hive's
  MapReduce client knows where to submit jobs.
- **`mapred-site.xml`** — `mapreduce.framework.name=yarn` (submit to YARN
  instead of running an in-process `LocalJobRunner`), plus
  `mapreduce.application.classpath` and the `*.env=HADOOP_MAPRED_HOME=...`
  properties copied from `hadoop.env` so that Map/Reduce task containers
  launched by `nodemanager` can find the Hadoop jars at
  `/opt/hadoop-3.1.3/share/hadoop/...` inside themselves.
- **`hive-site.xml`** — replaces the image's default entirely (the
  entrypoint's symlink step doesn't merge, it overwrites this one file), so
  it repeats the properties still needed (`hive.server2.enable.doAs=false`)
  and changes the two that matter for this setup:
  - `hive.execution.engine=mr` — use plain MapReduce instead of the image's
    default Tez-in-local-mode, so Hive queries show up as real YARN
    applications (visible in the ResourceManager UI, matching the theory
    section's description of Hive compiling HiveQL into MapReduce jobs).
  - `metastore.warehouse.dir` / `hive.metastore.warehouse.dir` =
    `/user/hive/warehouse` — an HDFS path (resolved against `fs.defaultFS`),
    replacing the image's default local-disk warehouse.

  The metastore itself stays embedded Derby (single `hive-server` container,
  schema initialized on every fresh start by `/entrypoint.sh` via
  `schematool -initSchema`) — there was no need for a separate metastore
  service or an external Postgres/MySQL backing store for a single-user lab
  environment.

## Verified end-to-end (see chat history for full output)

- `hdfs dfsadmin -report` — 1 live DataNode, ~465GB capacity.
- `yarn node -list` — 1 RUNNING NodeManager.
- `beeline`: `CREATE TABLE` + `INSERT INTO ... VALUES` compiled to a real
  MapReduce job (`job_..._0002`), tracked at
  `http://resourcemanager:8088/proxy/application_.../`, data landed under
  `hdfs://namenode:9000/user/hive/warehouse/...`; `SELECT` read it back
  correctly.
- `hadoop jar .../hadoop-mapreduce-examples-3.1.3.jar wordcount
  -D mapreduce.job.reduces=2 ...` — ran on YARN, produced `part-r-00000` and
  `part-r-00001` with the word counts split across two reducers.

## Usage

```bash
cd labs/001-hadoop-and-hive/infra
docker compose up -d          # start the whole cluster
docker compose ps             # check container health
docker compose logs -f hive-server   # watch HiveServer2 startup

# HDFS CLI (task 1)
docker exec namenode hdfs dfs -mkdir -p /tables_data/UO
docker exec namenode hdfs dfs -put /path/inside/container/UO.csv /tables_data/UO/

# Hive (tasks 2-4)
docker exec -it hive-server beeline -u "jdbc:hive2://localhost:10000/default"

# MapReduce example (task 5)
docker exec nodemanager hadoop jar \
  /opt/hadoop-3.1.3/share/hadoop/mapreduce/hadoop-mapreduce-examples-3.1.3.jar \
  wordcount -D mapreduce.job.reduces=2 /wordcount/input /wordcount/output

docker compose down           # stop (add -v to also wipe HDFS/warehouse volumes)
```

To get a local CSV file into a container so it can be `hdfs dfs -put` into
HDFS, use `docker cp local_file.csv namenode:/tmp/` first.

## Web UIs (from the host)

| UI | URL |
|---|---|
| HDFS NameNode | http://localhost:9870 |
| YARN ResourceManager | http://localhost:8088 |
| YARN NodeManager | http://localhost:8042 |
| MapReduce JobHistory | http://localhost:8188 |
| HDFS DataNode | http://localhost:9864 |
| HiveServer2 | http://localhost:10002 |

## Resource footprint

Total configured ceiling is well inside this VM's 31GB RAM / 8 cores:
NodeManager is capped at 8GB RAM / 4 vcores for task containers, plus
headroom for the JVMs of NameNode, DataNode, ResourceManager, HistoryServer
and HiveServer2 (a few hundred MB to ~1GB heap each by default). Named
volumes (`hadoop_namenode`, `hadoop_datanode`, `hadoop_historyserver`,
`hive_warehouse`) persist HDFS/warehouse data across `docker compose
restart`; `docker compose down -v` deletes them along with all data.
