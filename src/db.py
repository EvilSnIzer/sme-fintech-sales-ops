"""Small SQLite helper used by the pipeline."""
import os
import sqlite3

import pandas as pd


class SalesDB:
    """Wraps SQLite so the rest of the pipeline can stay focused on data."""

    def __init__(self, db_path: str):
        os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("PRAGMA foreign_keys = ON")

    def load_dataframe(self, table_name: str, df: pd.DataFrame) -> None:
        df.to_sql(table_name, self.conn, if_exists="replace", index=False)

    def query(self, sql: str) -> pd.DataFrame:
        return pd.read_sql_query(sql, self.conn)

    def run_script(self, sql: str) -> None:
        self.conn.executescript(sql)
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()
