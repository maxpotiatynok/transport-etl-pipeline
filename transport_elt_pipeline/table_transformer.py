import sqlite3
from pathlib import Path
from transport_elt_pipeline.analytics import AnalyticsClient


def tfl_connect():
    return sqlite3.connect("tfl.db")

class TableTransformer:
    """
    Transforms the polls from RawDisruption table(Bronze layer) into blocks of delays and good service in StatusIslands table(Silver layer).
    """
    def __init__(self, db = None):
        self._db = db if db is not None else tfl_connect()

    def create_islands_table(self):
        cursor = self._db.cursor()
        schema = Path("../schemas/islands_table_schema.sql").read_text()
        cursor.execute(schema)
        self._db.commit()

    def fill_islands_table(self):
        """
        Creates islands of consecutive polls on the same line, with the same reason text and the same service quality
        """
        cursor = self._db.cursor()
        cursor.execute("DELETE FROM StatusIslands")
        cursor.execute('''
        --Compares the FetchedAt, ServiceQuality and Reason columns with the previous poll columns on the same line--
        WITH compared AS(
            SELECT 
                LineID, LineName, ServiceQuality, ServiceQualityDescription, Reason, FetchedAt,
                LAG(FetchedAt) OVER(PARTITION BY LineID ORDER BY FetchedAt) AS PreviousPoll,                    
                LAG(ServiceQuality) OVER(PARTITION BY LineID ORDER BY FetchedAt) AS PreviousServiceQuality,
                LAG(Reason) OVER(PARTITION BY LineID ORDER BY FetchedAt) AS PreviousReason
            FROM RawDisruptions
        ),
        /*Flags a new island start poll by setting RepeatingServiceQuality as 1 when either:
            - ServiceQuality or Reason is NOT the same as the previous poll (also true for a line's first poll)
            - Good Service poll AND the time gap is ABOVE the time gap threshold
            - Any other status AND the time gap is ABOVE the time gap threshold times 2
        Otherwise, sets RepeatingServiceQuality as 0
        */
        flagged AS(
            SELECT
                LineID, LineName, ServiceQuality, ServiceQualityDescription, Reason, FetchedAt,
                CASE 
                    WHEN (ServiceQuality IS NOT PreviousServiceQuality OR Reason IS NOT PreviousReason) THEN 1
                    WHEN (ServiceQualityDescription = :good_service_desc
                        AND unixepoch(FetchedAt) - unixepoch(PreviousPoll) > :threshold) THEN 1
                    WHEN (ServiceQualityDescription != :good_service_desc
                        AND unixepoch(FetchedAt) - unixepoch(PreviousPoll) > :disruption_threshold) THEN 1
                ELSE 0 END AS NewStatus
            FROM compared
        ),
        --Calculates a running total of islands
        numbered AS(
            SELECT
                LineID, LineName, ServiceQuality, ServiceQualityDescription, Reason, FetchedAt,
                SUM(NewStatus) OVER(PARTITION BY LineID ORDER BY FetchedAt) AS IslandNumber
            FROM flagged
        )
        INSERT INTO StatusIslands(LineID, LineName, ServiceQuality, ServiceQualityDescription,
                                  Reason, FirstPoll, LastPoll, PollCount)
        SELECT LineID, MIN(LineName), MIN(ServiceQuality), MIN(ServiceQualityDescription), MIN(Reason),
               MIN(FetchedAt), MAX(FetchedAt), COUNT(*)
        FROM numbered
        GROUP BY LineID, IslandNumber
        ''', {"threshold": AnalyticsClient.GAPS_THRESHOLD, "good_service_desc" : "Good Service", "disruption_threshold" : AnalyticsClient.GAPS_THRESHOLD * 2})
        self._db.commit()


if __name__ == "__main__":
    transformer = TableTransformer()
    transformer.create_islands_table()
    transformer.fill_islands_table()
    transformer._db.close()




