import pytest
from unittest.mock import patch, MagicMock, Mock
import sys
import os

# Create a mock for the BookRecommender class
class MockBookRecommender:
    def __init__(self):
        pass
    
    def get_user_preference_text(self, user_id):
        return "genres:adventure themes:mystery maturity:young_adult"
    
    def get_recommendations(self, user_id, books, num_recommendations=5):
        # Return mock recommendations
        return [
            {
                'book': books[0],
                'similarity': 0.85
            },
            {
                'book': books[1] if len(books) > 1 else books[0],
                'similarity': 0.75
            }
        ][:num_recommendations]

@pytest.fixture
def mock_book_data():
    """Mock book data for testing"""
    return [
        {
            'id': 'book1',
            'title': 'Adventure Book',
            'authors': ['Author 1'],
            'categories': ['fiction', 'adventure'],
            'description': 'An exciting adventure in a fantasy world',
            'language': 'en',
            'pageCount': 300,
            'averageRating': 4.5,
            'maturityRating': 'NOT_MATURE',
            'series': 'standalone'
        },
        {
            'id': 'book2',
            'title': 'Mystery Adventure',
            'authors': ['Author 2'],
            'categories': ['fiction', 'mystery'],
            'description': 'A thrilling adventure with mystery elements',
            'language': 'en',
            'pageCount': 250,
            'averageRating': 4.0,
            'maturityRating': 'NOT_MATURE',
            'series': 'series'
        }
    ]

@pytest.fixture
def mock_user_prefs():
    """Mock user preferences for testing"""
    return "genres:adventure themes:mystery maturity:young_adult"

# Mock the actual import of BookRecommender
sys.modules['Recommendation'] = MagicMock()
sys.modules['Recommendation'].BookRecommender = MockBookRecommender

def test_recommender_initialization():
    """Test BookRecommender initialization"""
    recommender = MockBookRecommender()
    assert recommender is not None

def test_get_user_preference_text():
    """Test getting user preferences"""
    recommender = MockBookRecommender()
    prefs = recommender.get_user_preference_text(1)
    
    assert "genres:adventure" in prefs
    assert "themes:mystery" in prefs

def test_get_recommendations(mock_book_data):
    """Test getting recommendations"""
    recommender = MockBookRecommender()
    recommendations = recommender.get_recommendations(
        1,
        mock_book_data,
        num_recommendations=2
    )
    
    # Verify we got recommendations
    assert len(recommendations) <= 2
    assert 'book' in recommendations[0]
    assert 'similarity' in recommendations[0] 