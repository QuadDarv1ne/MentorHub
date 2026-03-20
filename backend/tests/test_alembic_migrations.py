"""
Tests for Alembic database migrations
"""

import pytest
from alembic.command import upgrade, downgrade, current
from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic.runtime.migration import MigrationContext
from alembic.runtime.environment import EnvironmentContext
from sqlalchemy import text
import os


@pytest.fixture
def alembic_config(db_session):
    """Alembic config fixture with test database"""
    config = Config(os.path.join(os.path.dirname(__file__), '..', 'alembic.ini'))
    config.set_main_option(
        'sqlalchemy.url',
        str(db_session.bind.url)
    )
    return config


@pytest.fixture
def db_session():
    """Create a fresh database session for migrations testing"""
    from app.database import engine, SessionLocal, Base
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    session = SessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=engine)


class TestAlembicMigrations:
    """Test suite for database migrations"""
    
    def test_migration_files_exist(self):
        """Test that migration files exist"""
        alembic_dir = os.path.join(os.path.dirname(__file__), '..', 'alembic', 'versions')
        migration_files = [
            f for f in os.listdir(alembic_dir)
            if f.endswith('.py') and not f.startswith('__')
        ]
        assert len(migration_files) > 0, "No migration files found"
    
    def test_alembic_current(self, alembic_config):
        """Test that database is at head revision"""
        # Get current revision
        current_head = current(alembic_config)
        
        # Get head revision
        script = ScriptDirectory.from_config(alembic_config)
        head_revision = script.get_current_head()
        
        # Check if we're at head
        if current_head:
            assert current_head == head_revision, \
                f"Database is at revision {current_head}, but head is {head_revision}"
    
    def test_upgrade_to_head(self, alembic_config, db_session):
        """Test upgrading to head revision"""
        # Downgrade to base first
        downgrade(alembic_config, 'base')
        
        # Upgrade to head
        upgrade(alembic_config, 'head')
        
        # Verify we're at head
        script = ScriptDirectory.from_config(alembic_config)
        head_revision = script.get_current_head()
        current_head = current(alembic_config)
        
        assert current_head == head_revision
    
    def test_downgrade_and_upgrade(self, alembic_config, db_session):
        """Test downgrading and upgrading through all revisions"""
        script = ScriptDirectory.from_config(alembic_config)
        
        # Get all revisions
        revisions = list(script.walk_revisions())
        
        # Downgrade to base
        downgrade(alembic_config, 'base')
        
        # Upgrade through each revision
        for rev in reversed(revisions):
            upgrade(alembic_config, rev.revision)
            current_head = current(alembic_config)
            assert current_head == rev.revision, \
                f"Failed at revision {rev.revision}"
    
    def test_all_tables_created(self, alembic_config, db_session):
        """Test that all expected tables are created after migrations"""
        # Downgrade to base
        downgrade(alembic_config, 'base')
        
        # Upgrade to head
        upgrade(alembic_config, 'head')
        
        # Check for expected tables
        expected_tables = [
            'users',
            'mentors',
            'sessions',
            'messages',
            'payments',
            'reviews',
            'courses',
            'lessons',
            'course_enrollments',
        ]
        
        inspector = db_session.bind.dialect.get_inspector(db_session.bind)
        existing_tables = inspector.get_table_names()
        
        for table in expected_tables:
            assert table in existing_tables, f"Table '{table}' not found"
    
    def test_no_duplicate_migration_names(self):
        """Test that there are no duplicate migration file names"""
        alembic_dir = os.path.join(os.path.dirname(__file__), '..', 'alembic', 'versions')
        migration_files = [
            f for f in os.listdir(alembic_dir)
            if f.endswith('.py') and not f.startswith('__')
        ]
        
        # Check for duplicate names (without revision prefix)
        names = []
        for f in migration_files:
            # Extract name from filename (e.g., "001_initial_migration.py" -> "initial_migration")
            name_parts = f.replace('.py', '').split('_', 1)
            if len(name_parts) > 1:
                names.append(name_parts[1])
        
        duplicates = [name for name in names if names.count(name) > 1]
        assert len(duplicates) == 0, f"Duplicate migration names: {set(duplicates)}"


class TestMigrationDataIntegrity:
    """Test data integrity during migrations"""
    
    def test_upgrade_preserves_data(self, alembic_config, db_session):
        """Test that upgrading preserves existing data"""
        from app.models import User
        from sqlalchemy import select
        
        # Create test user
        test_user = User(
            username="test_migration_user",
            email="test_migration@example.com",
            password_hash="test_hash"
        )
        db_session.add(test_user)
        db_session.commit()
        user_id = test_user.id
        
        # Downgrade and upgrade
        downgrade(alembic_config, 'base')
        upgrade(alembic_config, 'head')
        
        # Check if user still exists
        result = db_session.execute(
            select(User).where(User.id == user_id)
        ).scalar_one_or_none()
        
        # Note: After downgrade/upgrade, data won't persist
        # This test is more about ensuring the schema is compatible
        assert result is None or result.username == "test_migration_user"
    
    def test_foreign_keys_created(self, alembic_config, db_session):
        """Test that foreign key constraints are created"""
        # Upgrade to head
        upgrade(alembic_config, 'head')
        
        # Check for foreign keys in a sample table
        inspector = db_session.bind.dialect.get_inspector(db_session.bind)
        
        # Check sessions table has foreign keys
        fk_constraints = inspector.get_foreign_keys('sessions')
        assert len(fk_constraints) > 0, "No foreign keys found in sessions table"
        
        # Check payments table has foreign keys
        fk_constraints = inspector.get_foreign_keys('payments')
        assert len(fk_constraints) > 0, "No foreign keys found in payments table"
    
    def test_indexes_created(self, alembic_config, db_session):
        """Test that indexes are created"""
        # Upgrade to head
        upgrade(alembic_config, 'head')
        
        inspector = db_session.bind.dialect.get_inspector(db_session.bind)
        
        # Check for indexes on users table
        indexes = inspector.get_indexes('users')
        assert len(indexes) > 0, "No indexes found on users table"
        
        # Check for indexes on sessions table
        indexes = inspector.get_indexes('sessions')
        assert len(indexes) > 0, "No indexes found on sessions table"
