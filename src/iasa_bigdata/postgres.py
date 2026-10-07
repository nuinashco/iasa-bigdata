import psycopg

from iasa_bigdata.sqlclient import SqlClient


class PostgresClient(SqlClient):
    def __init__(
        self,
        host: str = "localhost",
        port: int = 5432,
        user: str = "postgres",
        password: str = "postgres",
        dbname: str = "postgres",
        verbose: bool = True,
    ) -> None:
        super().__init__(verbose)
        self._conn = psycopg.connect(
            host=host, port=port, user=user, password=password, dbname=dbname, autocommit=True
        )
        self._cursor = self._conn.cursor()
