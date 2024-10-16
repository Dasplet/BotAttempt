import sqlite3
from queue import Queue
from contextlib import contextmanager
from typing import Generator

class ConnectionPool:
    path: str
    pool_size: int
    connections: Queue[sqlite3.Connection]

    def __init__(self, db_path: str, pool_size: int =5):
        self.path = db_path
        self.pool_size = pool_size
        self.connections = Queue(maxsize=pool_size)

        for _ in range(pool_size):
            self.connections.put(sqlite3.connect(self.path))

    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection]:
        try:
            conn = self.connections.get()
            yield conn
        finally:
            self.connections.put(conn)

    def release_connection(self, conn: sqlite3.Connection):
        self.connections.put(conn)


    def close(self):
        while not self.connections.empty():
            conn = self.connections.get()
            conn.close()

