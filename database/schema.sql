CREATE TABLE IF NOT EXISTS analyses (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    filename TEXT NOT NULL,

    timestamp TEXT NOT NULL,

    duration REAL,

    fps REAL,

    width INTEGER,

    height INTEGER,

    motion_score REAL,

    scene_changes INTEGER,

    hook_intensity REAL,

    face_count INTEGER,

    face_presence_ratio REAL,

    brightness REAL,

    contrast REAL,

    pacing_score REAL,

    virality_score REAL,

    prediction_label TEXT
);