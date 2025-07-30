-- Add categories table
CREATE TABLE IF NOT EXISTS notification_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Drop existing notifications table if it exists
DROP TABLE IF EXISTS notifications_new;

-- Create new notifications table with foreign key
CREATE TABLE notifications_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message TEXT NOT NULL,
    type TEXT NOT NULL DEFAULT 'info',
    category_id INTEGER,
    metadata TEXT,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_read BOOLEAN NOT NULL DEFAULT 0,
    FOREIGN KEY (category_id) REFERENCES notification_categories(id)
);

-- Copy data from old table to new table
INSERT INTO notifications_new (id, message, type, category_id, metadata, timestamp, is_read)
SELECT id, message, type, category_id, metadata, timestamp, is_read 
FROM notifications;

-- Drop old table and rename new one
DROP TABLE IF EXISTS notifications;
ALTER TABLE notifications_new RENAME TO notifications;

-- Recreate indexes
CREATE INDEX IF NOT EXISTS idx_notifications_timestamp ON notifications(timestamp);
CREATE INDEX IF NOT EXISTS idx_notifications_is_read ON notifications(is_read);
CREATE INDEX IF NOT EXISTS idx_notifications_category ON notifications(category_id);

-- Insert default categories
INSERT OR IGNORE INTO notification_categories (name, description) VALUES
    ('system', 'System notifications'),
    ('user', 'User-related notifications'),
    ('alert', 'Important alerts'),
    ('update', 'System updates'); 