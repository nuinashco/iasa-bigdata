import re
import statistics
import time

import pandas as pd

_STATEMENT_END = re.compile(r";\s*$", flags=re.MULTILINE)
_LINE_COMMENT = re.compile(r"^\s*--.*$\n?", flags=re.MULTILINE)


def split_statements(script: str) -> list[str]:
    """Splits only on `;` at end of line, so `;` inside a one-line string literal is safe.
    Full-line comments are dropped: Hive recognises commands like SET by their first word."""
    script = _LINE_COMMENT.sub("", script)
    return [stmt for s in _STATEMENT_END.split(script) if (stmt := s.strip())]


def _summary(stmt: str, width: int = 100) -> str:
    text = " ".join(_LINE_COMMENT.sub("", stmt).split())
    return text if len(text) <= width else text[: width - 3] + "..."


class SqlClient:
    """Subclasses open `self._conn` and `self._cursor`. `last_elapsed` covers the whole script
    passed to the last `sql()` call, not just its last statement."""

    def __init__(self, verbose: bool = True) -> None:
        self.verbose = verbose
        self.last_elapsed: float | None = None
        self._conn = None
        self._cursor = None

    def sql(self, script: str) -> pd.DataFrame | None:
        """Returns the result set of the last statement that produced one."""
        result = None
        total = 0.0
        self._start_script()
        for stmt in split_statements(script):
            started = time.monotonic()
            self._cursor.execute(stmt)
            if self._cursor.description:
                columns = [c[0] for c in self._cursor.description]
                result = pd.DataFrame(self._cursor.fetchall(), columns=columns)
            elapsed = time.monotonic() - started
            total += elapsed
            details = self._statement_details()
            if self.verbose:
                print(f"[{elapsed:.2f}s{details}] {_summary(stmt)}")
        self.last_elapsed = total
        return result

    def _start_script(self) -> None:
        pass

    def _statement_details(self) -> str:
        return ""

    def _script_details(self) -> str:
        return ""

    def benchmark(self, script: str, repeat: int = 3) -> list[float]:
        verbose, self.verbose = self.verbose, False
        try:
            times = []
            for _ in range(repeat):
                self.sql(script)
                times.append(self.last_elapsed)
        finally:
            self.verbose = verbose
        if self.verbose:
            runs = ", ".join(f"{t:.2f}" for t in times)
            print(f"median {statistics.median(times):.2f}s (runs: {runs}){self._script_details()} | {_summary(script)}")
        return times

    def close(self) -> None:
        self._cursor.close()
        self._conn.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc) -> None:
        self.close()
