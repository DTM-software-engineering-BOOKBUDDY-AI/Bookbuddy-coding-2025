import pytest
import os
import sys
from unittest.mock import patch, MagicMock
import numpy as np

# Make sure we can import the module directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../Bookbuddy_app')))

# Set up mocks for sklearn
class MockTfidfVectorizer:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        
    def fit_transform(self, texts):
        # Create a simple sparse matrix for testing
        matrix = np.zeros((len(texts), 5))
        # Add some features based on text content
        for i, text in enumerate(texts):
            matrix[i, 0] = 1 if 'fantasy' in text.lower() else 0
            matrix[i, 1] = 1 if 'adventure' in text.lower() else 0
            matrix[i, 2] = 1 if 'en' in text.lower() else 0
            matrix[i, 3] = 1 if 'medium' in text.lower() else 0
            matrix[i, 4] = 1 if 'young_adult' in text.lower() else 0
        return matrix

# Create mock cosine_similarity function
def mock_cosine_similarity(X, Y):
    # Calculate a simple similarity score based on feature overlap
    return np.sum(X * Y, axis=1) / (np.sqrt(np.sum(X**2)) * np.sqrt(np.sum(Y**2)))

# Set up the mocks
sys.modules['sklearn'] = MagicMock()
sys.modules['sklearn.feature_extraction'] = MagicMock()
sys.modules['sklearn.feature_extraction.text'] = MagicMock()
sys.modules['sklearn.feature_extraction.text'].TfidfVectorizer = MockTfidfVectorizer
sys.modules['sklearn.metrics'] = MagicMock()
sys.modules['sklearn.metrics.pairwise'] = MagicMock()
sys.modules['sklearn.metrics.pairwise'].cosine_similarity = mock_cosine_similarity
sys.modules['pandas'] = MagicMock()
sys.modules['numpy'] = MagicMock()
sys.modules['numpy'].array = np.array
sys.modules['numpy'].sum = np.sum
sys.modules['numpy'].sqrt = np.sqrt

# Import the actual module after setting up mocks
from Recommendation import BookRecommender

@pytest.fixture
def mock_user_preferences():
    """Create mock user preferences"""
    preferences = [
        MagicMock(
            user_id=1,
            genres="fantasy,adventure",
            theme="magic,dragons",
            mood="exciting",
            language="en",
            length="medium",
            maturity="young_adult",
            style="series"
        ),
        MagicMock(
            user_id=2,
            genres="science fiction",
            theme="space,technology",
            mood="mysterious",
            language="en",
            length="long",
            maturity="mature",
            style="standalone"
        )
    ]
    return preferences

@pytest.fixture
def mock_db_session():
    """Create a mock db session with query methods"""
    mock_query = MagicMock()
    
    # Set up the query.filter_by().first() chain
    mock_filter_by = MagicMock()
    mock_filter_by.first.return_value = MagicMock(
        user_id=1,
        genres="fantasy,adventure",
        theme="magic,dragons",
        mood="exciting",
        language="en",
        length="medium",
        maturity="young_adult",
        style="series"
    )
    mock_query.filter_by.return_value = mock_filter_by
    
    # Set up the query.all() method
    mock_query.all.return_value = [
        MagicMock(
            user_id=1,
            genres="fantasy,adventure",
            theme="magic,dragons",
            mood="exciting",
            language="en",
            length="medium",
            maturity="young_adult",
            style="series"
        ),
        MagicMock(
            user_id=2,
            genres="science fiction",
            theme="space,technology",
            mood="mysterious",
            language="en",
            length="long",
            maturity="mature",
            style="standalone"
        )
    ]
    
    # Create the mock session
    mock_session = MagicMock()
    mock_session.query.return_value = mock_query
    
    return mock_session

@patch('Recommendation.UserPreferences')
def test_recommender_initialization(mock_user_preferences_patch, mock_user_preferences):
    """Test that the BookRecommender initializes correctly"""
    # Make sure the query.all() method returns our mock preferences
    mock_user_preferences_patch.query.all.return_value = mock_user_preferences
    
    # Create a BookRecommender instance
    recommender = BookRecommender()
    
    # Check that it initialized correctly
    assert recommender.preferences == mock_user_preferences
    assert isinstance(recommender.vectorizer, MockTfidfVectorizer)

@patch('Recommendation.UserPreferences')
def test_get_user_preference_text(mock_user_preferences, mock_db_session):
    """Test that get_user_preference_text returns formatted text"""
    # Set up UserPreferences.query
    mock_user_preferences.query = mock_db_session.query()
    
    # Create a BookRecommender instance
    recommender = BookRecommender()
    
    # Get user preference text
    text = recommender.get_user_preference_text(1)
    
    # Check that the text includes all preference fields
    assert "genres:fantasy,adventure" in text.lower()
    assert "theme:magic,dragons" in text.lower()
    assert "mood:exciting" in text.lower()
    assert "language:en" in text.lower()
    assert "length:medium" in text.lower()
    assert "maturity:young_adult" in text.lower()
    assert "style:series" in text.lower()

def test_get_book_text():
    """Test that get_book_text returns formatted text"""
    # Create a BookRecommender instance (without mocking UserPreferences)
    with patch('Recommendation.UserPreferences'):
        recommender = BookRecommender()
    
    # Test book data
    book = {
        'categories': ['Fantasy', 'Adventure'],
        'description': 'A magical adventure with dragons',
        'language': 'en',
        'pageCount': 350,
        'maturityRating': 'NOT_MATURE',
        'authors': ['J.R.R. Tolkien']
    }
    
    # Get book text
    text = recommender.get_book_text(book)
    
    # Check that the text includes all book fields
    assert "genres: fantasy adventure" in text.lower()
    assert "theme: a magical adventure with dragons" in text.lower()
    assert "language: en" in text.lower()
    assert "length: medium" in text.lower()  # 350 pages = medium
    assert "maturity: not_mature" in text.lower()
    assert "author: j.r.r. tolkien" in text.lower()

@patch('Recommendation.UserPreferences')
def test_calculate_similarity(mock_user_preferences, mock_db_session):
    """Test that calculate_similarity returns a valid similarity score"""
    # Set up UserPreferences.query
    mock_user_preferences.query = mock_db_session.query()
    
    # Create a BookRecommender instance
    recommender = BookRecommender()
    
    # High similarity book (matches user preferences)
    high_similarity_book = {
        'categories': ['Fantasy', 'Adventure'],
        'description': 'A magical adventure with dragons',
        'language': 'en',
        'pageCount': 350,
        'maturityRating': 'NOT_MATURE'
    }
    
    # Low similarity book (doesn't match user preferences)
    low_similarity_book = {
        'categories': ['Science Fiction'],
        'description': 'A space opera',
        'language': 'fr',
        'pageCount': 500,
        'maturityRating': 'MATURE'
    }
    
    # Calculate similarities
    high_similarity = recommender.calculate_similarity(1, high_similarity_book)
    low_similarity = recommender.calculate_similarity(1, low_similarity_book)
    
    # Check that the high similarity book has a higher score
    assert high_similarity > low_similarity
    assert 0 <= high_similarity <= 1
    assert 0 <= low_similarity <= 1

@patch('Recommendation.UserPreferences')
def test_get_recommendations(mock_user_preferences, mock_db_session):
    """Test that get_recommendations returns sorted recommendations"""
    # Set up UserPreferences.query
    mock_user_preferences.query = mock_db_session.query()
    
    # Create a BookRecommender instance
    with patch.object(BookRecommender, 'calculate_similarity') as mock_calculate_similarity:
        # Set up mock similarity values
        mock_calculate_similarity.side_effect = lambda user_id, book: {
            'book1': 0.9,
            'book2': 0.5,
            'book3': 0.7
        }[book['id']]
        
        recommender = BookRecommender()
        
        # Test books
        books = [
            {'id': 'book1', 'title': 'Book 1'},
            {'id': 'book2', 'title': 'Book 2'},
            {'id': 'book3', 'title': 'Book 3'}
        ]
        
        # Get recommendations
        recommendations = recommender.get_recommendations(1, books, num_recommendations=2)
        
        # Check that recommendations are sorted by similarity
        assert len(recommendations) == 2
        assert recommendations[0]['book']['id'] == 'book1'  # Highest similarity (0.9)
        assert recommendations[1]['book']['id'] == 'book3'  # Second highest (0.7)
        assert recommendations[0]['similarity'] == 0.9
        assert recommendations[1]['similarity'] == 0.7

def test_process_google_books_response():
    """Test that process_google_books_response filters books correctly"""
    # Create a BookRecommender instance (without mocking UserPreferences)
    with patch('Recommendation.UserPreferences'):
        recommender = BookRecommender()
    
    # Test books response
    books_response = [
        # Valid book - adventure fiction with adventure in description
        {
            'id': 'book1',
            'volumeInfo': {
                'title': 'Adventure Book',
                'authors': ['Author One'],
                'categories': ['Fiction', 'Adventure'],
                'description': 'An exciting adventure with quests and journeys',
                'language': 'en',
                'pageCount': 300,
                'maturityRating': 'NOT_MATURE'
            }
        },
        # Invalid - non-fiction
        {
            'id': 'book2',
            'volumeInfo': {
                'title': 'Science Textbook',
                'authors': ['Author Two'],
                'categories': ['Non-fiction', 'Science', 'Education'],
                'description': 'A textbook about physics',
                'language': 'en',
                'pageCount': 500,
                'maturityRating': 'NOT_MATURE'
            }
        },
        # Invalid - missing description
        {
            'id': 'book3',
            'volumeInfo': {
                'title': 'Mystery Book',
                'authors': ['Author Three'],
                'categories': ['Fiction', 'Mystery'],
                'language': 'en',
                'pageCount': 250,
                'maturityRating': 'NOT_MATURE'
            }
        },
        # Invalid - no adventure terms in description
        {
            'id': 'book4',
            'volumeInfo': {
                'title': 'Romance Novel',
                'authors': ['Author Four'],
                'categories': ['Fiction', 'Romance'],
                'description': 'A love story between two people',
                'language': 'en',
                'pageCount': 400,
                'maturityRating': 'MATURE'
            }
        }
    ]
    
    # Process the response
    processed_books = recommender.process_google_books_response(books_response)
    
    # Check that only the valid book was returned
    assert len(processed_books) == 1
    assert processed_books[0]['id'] == 'book1'
    assert processed_books[0]['title'] == 'Adventure Book'
    assert 'adventure' in processed_books[0]['categories']

def test_get_weighted_text():
    """Test that get_weighted_text properly repeats text based on weight"""
    # Create a BookRecommender instance (without mocking UserPreferences)
    with patch('Recommendation.UserPreferences'):
        recommender = BookRecommender()
    
    # Test with weight 1
    text_weight_1 = recommender.get_weighted_text('fantasy', 1, 'genre')
    assert text_weight_1 == 'genre: fantasy'
    
    # Test with weight 3
    text_weight_3 = recommender.get_weighted_text('fantasy', 3, 'genre')
    assert text_weight_3 == 'genre: fantasy fantasy fantasy'
    
    # Test with different feature name
    text_different_feature = recommender.get_weighted_text('exciting', 2, 'mood')
    assert text_different_feature == 'mood: exciting exciting'

def test_debug_similarity():
    """Test that debug_similarity outputs the expected information"""
    # Create a BookRecommender instance (without mocking UserPreferences)
    with patch('Recommendation.UserPreferences') as mock_user_preferences:
        # Mock the required methods
        mock_filter_by = MagicMock()
        mock_filter_by.first.return_value = MagicMock(
            user_id=1,
            genres="fantasy,adventure",
            theme="magic,dragons",
            mood="exciting",
            language="en",
            length="medium",
            maturity="young_adult",
            style="series"
        )
        mock_query = MagicMock()
        mock_query.filter_by.return_value = mock_filter_by
        mock_user_preferences.query = mock_query
        
        # Create a BookRecommender instance
        with patch.object(BookRecommender, 'calculate_similarity', return_value=0.75):
            recommender = BookRecommender()
            
            # Test book
            book = {
                'categories': ['Fantasy', 'Adventure'],
                'description': 'A magical adventure with dragons',
                'language': 'en',
                'pageCount': 350,
                'maturityRating': 'NOT_MATURE',
                'authors': ['J.R.R. Tolkien']
            }
            
            # Capture print output
            with patch('builtins.print') as mock_print:
                recommender.debug_similarity(1, book)
                
                # Check that the print statements were called
                assert mock_print.call_count >= 5
                
                # Check that the key print statements include expected content
                assert any('User Preferences' in str(args) for args, _ in mock_print.call_args_list)
                assert any('Book Features' in str(args) for args, _ in mock_print.call_args_list)
                assert any('Similarity Score: 0.75' in str(args) for args, _ in mock_print.call_args_list) 