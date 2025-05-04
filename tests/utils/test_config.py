import pytest
import os
from dotenv import load_dotenv

load_dotenv()

def test_app_config(test_app):
    """Test the application configuration"""
    assert test_app.config['TESTING'] is True
    assert test_app.config['SQLALCHEMY_DATABASE_URI'] == 'sqlite:///:memory:'
    assert test_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] is False
    assert test_app.config['WTF_CSRF_ENABLED'] is False

def test_google_books_api_key():
    """Test that Google Books API key is available"""
    api_key = os.getenv('GOOGLE_BOOKS_API_KEY')
    if api_key is None:
        # For testing purposes, set a dummy key if not available
        os.environ['GOOGLE_BOOKS_API_KEY'] = 'dummy_key_for_testing'
        api_key = os.getenv('GOOGLE_BOOKS_API_KEY')
    assert api_key is not None
    assert len(api_key) > 0 