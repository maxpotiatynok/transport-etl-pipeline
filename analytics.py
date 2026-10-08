import sqlite3
import pandas as pd

def tfl_connect():
    return sqlite3.connect("tfl.db")

class AnalyticsClient:
    # Must match the cron schedule that runs tfl_extractor.sh (every 5 minutes).
    POLL_INTERVAL_SECONDS = 300

    def __init__(self, db = None):
        self._db = db if db is not None else tfl_connect()

    def list_lines(self) -> pd.DataFrame:
        """
        LineID and LineName of the lines present in the latest poll
        Returns a DataFrame containing the lineID and lineName
        """
        return pd.read_sql_query('''
            SELECT LineID, LineName FROM RawDisruptions
            WHERE FetchedAt = (SELECT MAX(FetchedAt) FROM RawDisruptions)
            ORDER BY LineName
        ''', self._db)
    
    def current_line_status(self) -> pd.DataFrame:
        """
        Returns a DataFrame of current line statuses
        """
        return pd.read_sql_query('''
            SELECT * FROM RawDisruptions
            WHERE FetchedAt = (SELECT MAX(FetchedAt) FROM RawDisruptions)
        ''', self._db)

    def line_poll_coverage(self, lineId:str) -> float:
        """
        Returns the percentage of line service covered by the pipeline polls of a given line
        Inputs:
            lineId - The line's ID
        Returns:
            The percentage of line service covered by the pipeline
        """
        if lineId in self.list_lines()['LineID'].values:
            row = self._db.execute('''
                WITH bounds AS (
                    SELECT
                        COUNT(DISTINCT unixepoch(FetchedAt) / :interval) AS covered_slots,
                        unixepoch('now') / :interval
                            - MIN(unixepoch(FetchedAt)) / :interval + 1 AS expected_slots
                    FROM RawDisruptions
                    WHERE LineId = :lineId
                )
                SELECT AVG(100.0 * covered_slots / expected_slots) FROM bounds
                ''',
                {"interval": self.POLL_INTERVAL_SECONDS, "lineID": lineId},
            ).fetchone()
            return row[0]
        else:
            raise ValueError("The given LineID does not exist")

    def total_poll_coverage(self) -> float:
        """
        Average poll coverage (%) across all lines, from each line's first poll until now (UTC)
        Returns:
            The percentage of all line services covered by the pipeline
        """
        row = self._db.execute('''
            WITH per_line AS (
                SELECT
                    COUNT(DISTINCT unixepoch(FetchedAt) / :interval) AS covered_slots,
                    unixepoch('now') / :interval
                        - MIN(unixepoch(FetchedAt)) / :interval + 1 AS expected_slots
                FROM RawDisruptions
                GROUP BY LineID
            )
            SELECT AVG(100.0 * covered_slots / expected_slots) FROM per_line
            ''',
            {"interval": self.POLL_INTERVAL_SECONDS},
        ).fetchone()
        if row[0] is None:
            raise ValueError("No polls recorded yet")
        return row[0]

