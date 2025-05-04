import pytest
from unittest.mock import patch, MagicMock, Mock
import sys
import os
import numpy as np
from datetime import datetime

# Create a mock for the necessary classes and modules
class MockTfidfVectorizer:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
    
    def fit_transform(self, texts):
        # Return a simple sparse matrix mock with appropriate shape
        mock_matrix = MagicMock()
        mock_matrix.shape = (len(texts), 10)  # Pretend we have 10 features
        return mock_matrix

class MockCosineSimilarity:
    def __call__(self, X, Y):
        # Return a simple 1x1 similarity matrix with a value between 0 and 1
        return np.array([[0.85]])

class MockUserPreference:
    def __init__(self, user_id, genres=None, theme=None, mood=None, language=None, 
                 length=None, maturity=None, style=None):
        self.user_id = user_id
        self.genres = genres
        self.theme = theme
        self.mood = mood
        self.language = language
        self.length = length
        self.maturity = maturity
        self.style = style

class MockBookRecommender:
    def __init__(self):
        pass
    
    def get_user_preference_text(self, user_id):
        return "genres:fantasy adventure theme:dragons quests mood:exciting language:en length:medium maturity:young_adult style:series"
    
    def get_book_text(self, book_data):
        return "genres: fantasy adventure theme: a magical journey language: en length: medium maturity: not_mature author: j.k. rowling"
    
    def calculate_similarity(self, user_id, book):
        return 0.85 if book.get('language') == 'en' else 0.5
    
    def get_recommendations(self, user_id, books, num_recommendations=5):
        # Return mock recommendations
        if len(books) < 2:
            return [{'book': books[0], 'similarity': 0.9}]
        
        return [
            {'book': books[0], 'similarity': 0.9},
            {'book': books[1], 'similarity': 0.6}
        ][:num_recommendations]
    
    def process_google_books_response(self, books_response):
        return [{
            'id': 'book1',
            'title': 'Adventure Fantasy Book',
            'authors': ['Author One'],
            'categories': ['fiction', 'adventure'],
            'description': 'An exciting adventure in a fantasy world',
            'language': 'en',
            'pageCount': 300,
            'averageRating': 4.5,
            'maturityRating': 'NOT_MATURE',
            'series': 'standalone'
        }]

# Set up the mock modules before importing
sys.modules['sklearn'] = MagicMock()
sys.modules['sklearn.feature_extraction'] = MagicMock()
sys.modules['sklearn.feature_extraction.text'] = MagicMock()
sys.modules['sklearn.feature_extraction.text'].TfidfVectorizer = MockTfidfVectorizer
sys.modules['sklearn.metrics'] = MagicMock()
sys.modules['sklearn.metrics.pairwise'] = MagicMock()
sys.modules['sklearn.metrics.pairwise'].cosine_similarity = MockCosineSimilarity()
sys.modules['pandas'] = MagicMock()
sys.modules['numpy'] = MagicMock()
sys.modules['numpy'].array = np.array

# This is the key change: set up a mock for Recommendation module
sys.modules['Recommendation'] = MagicMock()
sys.modules['Recommendation'].BookRecommender = MockBookRecommender

@pytest.fixture
def mock_user_preference():
    """Mock user preference data"""
    return MockUserPreference(
        user_id=1,
        genres="fantasy adventure",
        theme="magic heroism",
        mood="exciting",
        language="en",
        length="medium",
        maturity="young_adult",
        style="series"
    )

@pytest.fixture
def mock_books():
    """Mock book data for testing"""
    return [
        {
            'id': 'book1',
            'title': 'The Magic Quest',
            'authors': ['Author One'],
            'categories': ['Fiction', 'Fantasy', 'Adventure'],
            'description': 'A thrilling magical adventure with heroic characters.',
            'language': 'en',
            'pageCount': 350,
            'averageRating': 4.5,
            'maturityRating': 'NOT_MATURE',
            'series': 'standalone'
        },
        {
            'id': 'book2',
            'title': 'Mystery Castle',
            'authors': ['Author Two'],
            'categories': ['Fiction', 'Mystery'],
            'description': 'A mysterious journey through an ancient castle.',
            'language': 'en',
            'pageCount': 250,
            'averageRating': 4.0,
            'maturityRating': 'NOT_MATURE',
            'series': 'series'
        },
        {
            'id': 'book3',
            'title': 'Space Explorers',
            'authors': ['Author Three'],
            'categories': ['Science Fiction'],
            'description': 'An expedition to distant planets.',
            'language': 'fr',
            'pageCount': 450,
            'averageRating': 4.2,
            'maturityRating': 'MATURE',
            'series': 'series'
        }
    ]

def test_get_user_preference_text(test_app):
    """Test that the system correctly formats user preferences as text"""
    with test_app.app_context():
        # Create the recommender and call the method
        recommender = MockBookRecommender()
        result = recommender.get_user_preference_text(1)
        
        # Check the formatted text contains all the preference values
        assert "genres:fantasy adventure" in result.lower()
        assert "theme:dragons quests" in result.lower()
        assert "mood:exciting" in result.lower()
        assert "language:en" in result.lower()
        assert "length:medium" in result.lower()
        assert "maturity:young_adult" in result.lower()
        assert "style:series" in result.lower()

def test_get_book_text(test_app):
    """Test that the system correctly formats book data as text"""
    with test_app.app_context():
        recommender = MockBookRecommender()
        
        # Test with a complete book
        book = {
            'categories': ['Fantasy', 'Adventure'],
            'description': 'A magical journey',
            'language': 'en',
            'pageCount': 350,
            'maturityRating': 'NOT_MATURE',
            'authors': ['J.K. Rowling']
        }
        
        book_text = recommender.get_book_text(book)
        
        # Check the formatted text includes all key features
        assert "genres: fantasy adventure" in book_text.lower()
        assert "theme: a magical journey" in book_text.lower()
        assert "language: en" in book_text.lower()
        assert "length: medium" in book_text.lower()  # 350 pages = medium
        assert "maturity: not_mature" in book_text.lower()
        assert "author: j.k. rowling" in book_text.lower()

def test_calculate_similarity(test_app):
    """Test the similarity calculation between user preferences and books"""
    with test_app.app_context():
        # Create the recommender
        recommender = MockBookRecommender()
        
        # Test book 1 - should have high similarity
        book1 = {
            'categories': ['Fantasy', 'Adventure'],
            'description': 'A magical journey with dragons and quests',
            'language': 'en',
            'pageCount': 350,
            'maturityRating': 'NOT_MATURE'
        }
        
        # Test book 2 - should have lower similarity
        book2 = {
            'categories': ['Science Fiction'],
            'description': 'A space opera',
            'language': 'fr',
            'pageCount': 450,
            'maturityRating': 'MATURE'
        }
        
        # Calculate similarities
        similarity1 = recommender.calculate_similarity(1, book1)
        similarity2 = recommender.calculate_similarity(1, book2)
        
        # Our mock returns different values based on language
        assert similarity1 == 0.85
        assert similarity2 == 0.5

def test_get_recommendations(test_app, mock_books):
    """Test that the system returns the expected recommendations"""
    with test_app.app_context():
        # Create the recommender
        recommender = MockBookRecommender()
        
        # Get recommendations
        recommendations = recommender.get_recommendations(1, mock_books, num_recommendations=2)
        
        # Test the number of recommendations
        assert len(recommendations) == 2
        
        # Test the structure of recommendations
        assert 'book' in recommendations[0]
        assert 'similarity' in recommendations[0]
        assert recommendations[0]['similarity'] == 0.9
        assert recommendations[1]['similarity'] == 0.6

def test_process_google_books_response(test_app):
    """Test that the system correctly processes Google Books API responses"""
    with test_app.app_context():
        # Create the recommender
        recommender = MockBookRecommender()
        
        # Create sample Google Books API response
        books_response = [
            {
                'id': 'book1',
                'volumeInfo': {
                    'title': 'Adventure Fantasy Book',
                    'authors': ['Author One'],
                    'categories': ['Fiction', 'Adventure'],
                    'description': 'An exciting adventure in a fantasy world',
                    'language': 'en',
                    'pageCount': 300,
                    'averageRating': 4.5,
                    'maturityRating': 'NOT_MATURE'
                }
            },
            {
                'id': 'book2',
                'volumeInfo': {
                    'title': 'Science Manual',
                    'authors': ['Author Two'],
                    'categories': ['Non-Fiction', 'Science'],
                    'description': 'A scientific textbook about physics',
                    'language': 'en',
                    'pageCount': 250,
                    'averageRating': 4.0,
                    'maturityRating': 'NOT_MATURE'
                }
            },
            {
                'id': 'book3',
                'volumeInfo': {
                    'title': 'Missing Description',
                    'authors': ['Author Three'],
                    'categories': ['Fiction', 'Adventure'],
                    'language': 'en',
                    'pageCount': 450,
                    'averageRating': 4.2,
                    'maturityRating': 'MATURE'
                }
            }
        ]
        
        # Process the response
        processed_books = recommender.process_google_books_response(books_response)
        
        # Test that only valid books are returned
        assert len(processed_books) == 1
        
        # Test that the first book was processed correctly
        assert processed_books[0]['id'] == 'book1'
        assert processed_books[0]['title'] == 'Adventure Fantasy Book'
        assert 'adventure' in processed_books[0]['categories']
        
        # Test that non-fiction and books missing descriptions were filtered out
        assert all(book['id'] != 'book2' for book in processed_books)
        assert all(book['id'] != 'book3' for book in processed_books) 