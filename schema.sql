CREATE TABLE IF NOT EXISTS RawDisruptions (
    LineID TEXT NOT NULL,
    LineName TEXT,
    ServiceQuality INTEGER NOT NULL,
    ServiceQualityDescription TEXT,
    Reason TEXT,
    FromDate TEXT,
    ToDate TEXT,
    FetchedAtUTC TEXT NOT NULL,
    UNIQUE (LineID, FetchedAtUTC)
);