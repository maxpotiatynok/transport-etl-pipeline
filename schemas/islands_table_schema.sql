CREATE TABLE IF NOT EXISTS StatusIslands (
    LineID TEXT NOT NULL,
    LineName TEXT NOT NULL,
    ServiceQuality INTEGER NOT NULL,
    ServiceQualityDescription TEXT NOT NULL,
    Reason TEXT,
    FirstPoll TEXT NOT NULL ,
    LastPoll TEXT NOT NULL ,
    PollCount INTEGER NOT NULL,
    UNIQUE (LineID, FirstPoll)
);