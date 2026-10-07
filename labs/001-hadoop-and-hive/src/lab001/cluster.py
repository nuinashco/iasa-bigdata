import shlex
import subprocess
from pathlib import Path

# Hadoop CLI inside the bde2020 images: drop the deprecated HADOOP_PREFIX (prints a warning on
# every call; HADOOP_HOME is derived from the script path).
_HADOOP_ENV = ["env", "-u", "HADOOP_PREFIX"]
# Logged once per HDFS block written; pure noise at INFO level.
_HADOOP_NOISE = ("SaslDataTransferClient",)

EXAMPLES_JAR = "/opt/hadoop-3.1.3/share/hadoop/mapreduce/hadoop-mapreduce-examples-3.1.3.jar"


def run(cmd: list[str], display: str | None = None, check: bool = True, echo: bool = True) -> str:
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if echo:
        print(f"$ {display or shlex.join(cmd)}")
        if proc.stdout:
            print(proc.stdout, end="" if proc.stdout.endswith("\n") else "\n")
    if check and proc.returncode != 0:
        raise RuntimeError(f"command failed with exit code {proc.returncode}:\n{proc.stdout[-2000:]}")
    return proc.stdout


def compose_up(compose_file: str | Path, timeout: int = 300) -> None:
    # --wait (healthchecks) instead of probing ports: docker-proxy accepts connections on a
    # published host port before the service inside the container is listening.
    run(["docker", "compose", "--progress", "quiet", "-f", str(compose_file), "up", "-d", "--wait", "--wait-timeout", str(timeout)])


def hadoop_cli(container: str, *args: str, check: bool = True, echo: bool = True, log_level: str = "WARN") -> str:
    # UTF-8 locale: otherwise Java prints non-ASCII paths (e.g. Cyrillic partition values) as "?".
    env = ["-e", "LC_ALL=C.UTF-8", "-e", f"HADOOP_ROOT_LOGGER={log_level},console"]
    cmd = ["docker", "exec", *env, container, *_HADOOP_ENV, *args]
    output = run(cmd, check=check, echo=False)
    output = "".join(line for line in output.splitlines(keepends=True) if not any(n in line for n in _HADOOP_NOISE))
    if echo:
        print(f"$ {shlex.join(args)}")
        if output:
            print(output, end="" if output.endswith("\n") else "\n")
    return output


def hdfs(*args: str, **kwargs) -> str:
    return hadoop_cli("namenode", "hdfs", *args, **kwargs)


def hadoop(*args: str, **kwargs) -> str:
    return hadoop_cli("namenode", "hadoop", *args, **kwargs)
