import pytest
from sqlalchemy import inspect
from models import User, UserPreferences

def test_database_tables(test_app, test_db):
    """Test that database tables are created properly"""
    with test_app.app_context():
        # Get inspector
        inspector = inspect(test_db.engine)
        
        # Check if tables exist
        tables = inspector.get_table_names()
        assert 'user' in tables
        assert 'user_preferences' in tables
        
        # Check User table structure
        columns = {col['name']: col for col in inspector.get_columns('user')}
        assert 'id' in columns
        assert 'username' in columns
        assert 'email' in columns
        assert 'password_hash' in columns
        assert 'gender' in columns
        assert 'birthday' in columns

def test_user_model(test_app, test_db):
    """Test User model functionality"""
    with test_app.app_context():
        # Create test user
        user = User(
            username="test_db_user",
            email="testdb@example.com",
            gender="other",
            birthday="1990-01-01"
        )
        user.set_password("securepass123")
        
        # Add to database
        test_db.session.add(user)
        test_db.session.commit()
        
        # Query and verify
        saved_user = User.query.filter_by(username="test_db_user").first()
        assert saved_user is not None
        assert saved_user.email == "testdb@example.com"
        assert saved_user.check_password("securepass123") is True
        assert saved_user.check_password("wrongpass") is False 