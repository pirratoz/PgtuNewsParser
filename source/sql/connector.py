import sqlite3

from source.sql.query import (
    CREATE_TABEL_NEWS,
    INSERT_NEWS,
)


class DatabaseConnector:
    def __init__(self, path: str) -> None:
        self.connection = sqlite3.connect(path)

    def create_tabel_news(self) -> None:
        self.connection.execute(CREATE_TABEL_NEWS)

    def insert_news(self, data: list[tuple[str, str]]) -> None:
        self.connection.executemany(INSERT_NEWS, data)

    def close_connection(self) -> None:
        self.connection.close()
