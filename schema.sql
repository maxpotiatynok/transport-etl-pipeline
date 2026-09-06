CREATE TABLE IF NOT EXISTS Disruptions (
        Line TEXT NOT NULL,
        Category TEXT,
        DType TEXT,
        CategoryDescription TEXT,
        Description TEXT,
        Summary TEXT,
        AdditionalInfo TEXT,
        Created DATETIME,
        APILastUpdated TEXT,
        ClientLastUpdated TEXT,
        PRIMARY KEY(Line, Category, ClientLastUpdated)
    );