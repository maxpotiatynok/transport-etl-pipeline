import sqlite3
import pandas as pd

def tfl_connect():
    return sqlite3.connect("tfl.db")

class AnalyticsClient:

    def __init__(self, db = None):
        self._db = db if db is not None else tfl_connect()

    def current_line_status(self) -> pd.DataFrame:
        return pd.read_sql_query('''
        SELECT * FROM RawDisruptions
        WHERE FetchedAt = (SELECT MAX(FetchedAt) FROM RawDisruptions)
        ''', self._db)

    def poll_coverage(self, start, end):




