import re
import time

from pyhive import hive

from lab001.sqlclient import SqlClient, split_statements

__all__ = ["HiveClient", "split_statements"]

# Logged by Hive for every MapReduce stage, e.g. "Stage-Stage-1: Map: 4 ... HDFS Read: 1170101104 ..."
_HDFS_READ = re.compile(r"HDFS Read: (\d+)")


def format_bytes(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024


class HiveClient(SqlClient):
    """Connecting retries for up to `connect_timeout` seconds: HiveServer2 needs ~30 s after the
    container starts to initialise its metastore.

    `last_hdfs_read` is 0 when Hive answered without a MapReduce job (DDL, fetch tasks).
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 10000,
        username: str = "hive",
        verbose: bool = True,
        connect_timeout: float = 300,
    ) -> None:
        super().__init__(verbose)
        self.last_hdfs_read = 0
        self._conn = self._connect(host, port, username, connect_timeout)
        self._cursor = self._conn.cursor()
        # Label columns "name" instead of "uo_table.name".
        self._cursor.execute("SET hive.resultset.use.unique.column.names=false")

    @staticmethod
    def _connect(host: str, port: int, username: str, timeout: float) -> hive.Connection:
        deadline = time.monotonic() + timeout
        while True:
            try:
                return hive.connect(host=host, port=port, username=username)
            except Exception:  # thrift transport errors while HiveServer2 is starting
                if time.monotonic() > deadline:
                    raise
                time.sleep(3)

    def _start_script(self) -> None:
        self.last_hdfs_read = 0

    def _statement_details(self) -> str:
        try:
            logs = self._cursor.fetch_logs()
        except Exception:  # statements without an operation log, e.g. SET
            return ""
        read = sum(int(n) for line in logs for n in _HDFS_READ.findall(line))
        self.last_hdfs_read += read
        return f", HDFS read {format_bytes(read)}" if read else ""

    def _script_details(self) -> str:
        return f", HDFS read {format_bytes(self.last_hdfs_read)}" if self.last_hdfs_read else ""
