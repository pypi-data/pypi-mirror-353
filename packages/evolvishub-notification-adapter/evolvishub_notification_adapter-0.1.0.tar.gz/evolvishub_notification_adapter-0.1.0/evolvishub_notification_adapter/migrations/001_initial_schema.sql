-- Initial schema for notifications table
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message TEXT NOT NULL,
    type TEXT NOT NULL DEFAULT 'info',
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_read BOOLEAN NOT NULL DEFAULT 0,
    metadata TEXT,
    category_id INTEGER
);

-- Create index on timestamp for faster sorting
CREATE INDEX IF NOT EXISTS idx_notifications_timestamp ON notifications(timestamp);

-- Create index on is_read for faster filtering
CREATE INDEX IF NOT EXISTS idx_notifications_is_read ON notifications(is_read); 