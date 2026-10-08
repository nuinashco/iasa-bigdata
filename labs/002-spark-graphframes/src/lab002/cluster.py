import os
import shlex
import subprocess
from pathlib import Path


def run(cmd: list[str], check: bool = True, echo: bool = True, env: dict[str, str] | None = None) -> str:
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                          env={**os.environ, **(env or {})})
    if echo:
        print(f"$ {shlex.join(cmd)}")
        if proc.stdout:
            print(proc.stdout, end="" if proc.stdout.endswith("\n") else "\n")
    if check and proc.returncode != 0:
        raise RuntimeError(f"command failed with exit code {proc.returncode}:\n{proc.stdout[-2000:]}")
    return proc.stdout


def cluster_env(data_dir: str | Path) -> dict[str, str]:
    """Variables infra/docker-compose.yml requires: the data dir (mounted at the same path in
    every container) and the host user the containers run as."""
    return {"LAB_DATA": str(Path(data_dir).resolve()), "LAB_UID": str(os.getuid()), "LAB_GID": str(os.getgid())}


def compose(compose_file: str | Path, data_dir: str | Path, *args: str, echo: bool = True) -> str:
    cmd = ["docker", "compose", "--progress", "quiet", "-f", str(compose_file), *args]
    return run(cmd, env=cluster_env(data_dir), echo=echo)


def compose_up(compose_file: str | Path, data_dir: str | Path, timeout: int = 300) -> None:
    # --wait (healthchecks) instead of probing ports from here: a port can accept connections
    # before the service behind it is ready.
    compose(compose_file, data_dir, "up", "-d", "--build", "--wait", "--wait-timeout", str(timeout))
