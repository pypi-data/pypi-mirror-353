import pytest
import pytest_asyncio
import os
import tempfile
import yaml
from evolvishub_notification_adapter import NotificationDB, Config, Notification, Category

@pytest_asyncio.fixture
async def temp_config_file():
    """Create a temporary config file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump({
            'database': {
                'path': 'test.db',
                'directory': tempfile.gettempdir()
            },
            'logging': {
                'enabled': True,
                'level': 'INFO'
            }
        }, f)
    yield f.name
    os.unlink(f.name)

@pytest_asyncio.fixture
async def config(temp_config_file):
    """Create a Config instance."""
    return Config(temp_config_file)

@pytest_asyncio.fixture
async def db(config):
    """Create a NotificationDB instance and clean up before each test."""
    async with NotificationDB(config) as db:
        # Clean up database before each test
        async with db._get_connection() as cursor:
            await cursor.execute("DELETE FROM notifications")
            await cursor.execute("DELETE FROM notification_categories")
            await cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('notifications', 'notification_categories')")
        yield db

@pytest_asyncio.fixture
async def category(db):
    """Create a test category."""
    return await db.add_category("test_category_1", "Test category")

@pytest.mark.asyncio
async def test_add_notification(db):
    """Test adding a notification."""
    notif_id = await db.add_notification("Test message", "info")
    assert notif_id > 0

@pytest.mark.asyncio
async def test_add_notification_with_category(db, category):
    """Test adding a notification with category."""
    notif_id = await db.add_notification("Test message", "info", category_id=category)
    assert notif_id > 0

@pytest.mark.asyncio
async def test_add_notification_with_metadata(db):
    """Test adding a notification with metadata."""
    metadata = {"key": "value"}
    notif_id = await db.add_notification("Test message", "info", metadata=metadata)
    assert notif_id > 0

@pytest.mark.asyncio
async def test_add_notifications_bulk(db):
    """Test adding multiple notifications."""
    notifications = [
        {"message": "Test 1", "type": "info"},
        {"message": "Test 2", "type": "warning"}
    ]
    notif_ids = await db.add_notifications(notifications)
    assert len(notif_ids) == 2

@pytest.mark.asyncio
async def test_mark_as_read(db):
    """Test marking a notification as read."""
    notif_id = await db.add_notification("Test message", "info")
    affected = await db.mark_as_read(notif_id)
    assert affected == 1

@pytest.mark.asyncio
async def test_mark_many_as_read(db):
    """Test marking multiple notifications as read."""
    # Add notifications
    notif_ids = await db.add_notifications([
        {"message": "Test 1", "type": "info"},
        {"message": "Test 2", "type": "info"}
    ])

    # Mark as read
    affected = await db.mark_many_as_read(notif_ids)
    assert affected == 2

    # Verify they're marked as read
    unread = await db.get_unread_notifications()
    assert len(unread) == 0

@pytest.mark.asyncio
async def test_get_unread_notifications(db):
    """Test getting unread notifications."""
    # Add notifications
    await db.add_notification("Test 1", "info")
    await db.add_notification("Test 2", "info")
    
    # Get unread
    unread = await db.get_unread_notifications()
    assert len(unread) == 2
    assert all(not notif.is_read for notif in unread)

@pytest.mark.asyncio
async def test_get_all_notifications(db):
    """Test getting all notifications."""
    # Add notifications
    await db.add_notification("Test 1", "info")
    await db.add_notification("Test 2", "warning")
    
    # Get all
    all_notifs = await db.get_all_notifications()
    assert len(all_notifs) == 2

@pytest.mark.asyncio
async def test_get_categories(db):
    """Test getting categories."""
    # Add some categories
    await db.add_category("category1", "First category")
    await db.add_category("category2", "Second category")
    
    # Get all categories
    categories = await db.get_categories()
    assert len(categories) == 2
    assert any(c.name == "category1" for c in categories)
    assert any(c.name == "category2" for c in categories)

@pytest.mark.asyncio
async def test_add_duplicate_category(db):
    """Test adding a duplicate category."""
    # Add a category
    await db.add_category("test_category_3", "Test description")
    
    # Try to add the same category again
    with pytest.raises(ValueError, match="Category 'test_category_3' already exists"):
        await db.add_category("test_category_3", "Test description") 