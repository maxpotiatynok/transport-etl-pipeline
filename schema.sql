CREATE TABLE IF NOT EXISTS Disruptions (
        Line TEXT NOT NULL,
        LineName TEXT,
        StatusSeverity TEXT NOT NULL,
        SeverityDescription TEXT,
        Reason TEXT,
        FromDate TEXT,
        ToDate TEXT,
        DisruptionCategory TEXT,
        DisruptionClosureText TEXT,
        FetchDate TEXT,
        UNIQUE (Line,StatusSeverity, FromDate, DisruptionCategory)
    );