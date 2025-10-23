-- UK Crime Analytics Database Schema
-- Based on ACTUAL police.uk API structure

-- Police forces reference table
CREATE TABLE IF NOT EXISTS police_forces (
    force_id TEXT PRIMARY KEY,
    force_name TEXT NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Crime categories reference table (from actual 'category' field)
CREATE TABLE IF NOT EXISTS crime_categories (
    category_id TEXT PRIMARY KEY,
    category_name TEXT NOT NULL,
    severity_level INTEGER DEFAULT 1
);

-- Main crime incidents table (MAPPED FROM ACTUAL API COLUMNS)
CREATE TABLE IF NOT EXISTS crime_incidents (
    -- Core identifiers
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    crime_api_id INTEGER UNIQUE,              -- API's 'id' field
    persistent_id TEXT,                       -- API's 'persistent_id'
    
    -- Crime details (from actual API columns)
    category TEXT NOT NULL,                   -- Crime type
    location_type TEXT,                       -- Force/BNG
    location_subtype TEXT,                    -- Additional location info
    context TEXT,                             -- Additional context
    
    -- Location information (flattened from nested structure)
    latitude REAL,                            -- location.latitude
    longitude REAL,                           -- location.longitude
    street_id INTEGER,                        -- location.street.id
    street_name TEXT,                         -- location.street.name
    
    -- Outcome information (from outcome_status nested object)
    outcome_status_category TEXT,             -- outcome_status.category
    outcome_status_date TEXT,                 -- outcome_status.date
    
    -- Temporal information
    month TEXT NOT NULL,                      -- Reporting month (YYYY-MM)
    date_loaded TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign keys
    FOREIGN KEY (category) REFERENCES crime_categories(category_id)
);

-- Crime statistics summary table (optimized for Power BI)
CREATE TABLE IF NOT EXISTS crime_summary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    month TEXT,
    police_force TEXT,
    crime_category TEXT,
    incident_count INTEGER,
    high_severity_count INTEGER,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Performance indexes (based on actual query patterns)
CREATE INDEX IF NOT EXISTS idx_crime_month ON crime_incidents(month);
CREATE INDEX IF NOT EXISTS idx_crime_category ON crime_incidents(category);
CREATE INDEX IF NOT EXISTS idx_crime_location ON crime_incidents(latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_crime_outcome ON crime_incidents(outcome_status_category);

-- Street reference table (for location analysis)
CREATE TABLE IF NOT EXISTS street_reference (
    street_id INTEGER PRIMARY KEY,
    street_name TEXT NOT NULL,
    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);