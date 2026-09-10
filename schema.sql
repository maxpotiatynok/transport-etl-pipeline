CREATE TABLE IF NOT EXISTS RawDisruptions (
        Line TEXT NOT NULL,
        LineName TEXT,
        StatusSeverity INT NOT NULL,
        SeverityDescription TEXT,
        Reason TEXT,
        FromDate TEXT,
        IsPlanned INT,
        ToDate TEXT,
        DisruptionClosureText TEXT,
        FetchedAt TEXT,
        UNIQUE (Line, FromDate, DisruptionClosureText)
    );