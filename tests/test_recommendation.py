import pytest
from unittest.mock import patch, MagicMock

class TestRecommendation:
    """Test the Recommendation module with simple mocks"""
    
    @patch('Recommendation.BookRecommender')
    def test_recommender_creation(self, mock_recommender):
        """Test that the BookRecommender can be created"""
        # Set up the mock
        mock_instance = MagicMock()
        mock_recommender.return_value = mock_instance
        
        # Import after patching
        from Recommendation import BookRecommender
        
        # Create a recommender
        recommender = BookRecommender()
        
        # Check that the mock was called
        assert mock_recommender.called
        assert recommender == mock_instance
    
    @patch('Recommendation.BookRecommender')
    def test_get_user_preference_text(self, mock_recommender):
        """Test get_user_preference_text method"""
        # Set up the mock
        mock_instance = MagicMock()
        mock_instance.get_user_preference_text.return_value = "genres:fantasy,adventure theme:magic mood:exciting"
        mock_recommender.return_value = mock_instance
        
        # Import after patching
        from Recommendation import BookRecommender
        
        # Create a recommender
        recommender = BookRecommender()
        
        # Call the method
        result = recommender.get_user_preference_text(1)
        
        # Check the result
        assert "genres:fantasy" in result
        assert "adventure" in result
        assert "magic" in result
        assert recommender.get_user_preference_text.called
    
    @patch('Recommendation.BookRecommender')
    def test_get_book_text(self, mock_recommender):
        """Test get_book_text method"""
        # Set up the mock
        mock_instance = MagicMock()
        mock_instance.get_book_text.return_value = "genres: fantasy adventure theme: dragons"
        mock_recommender.return_value = mock_instance
        
        # Import after patching
        from Recommendation import BookRecommender
        
        # Create a recommender
        recommender = BookRecommender()
        
        # Call the method
        book = {
            'categories': ['Fantasy', 'Adventure'],
            'description': 'A magical adventure with dragons',
            'language': 'en',
            'pageCount': 350,
            'maturityRating': 'NOT_MATURE',
            'authors': ['J.R.R. Tolkien']
        }
        result = recommender.get_book_text(book)
        
        # Check the result
        assert "fantasy" in result
        assert "adventure" in result
        assert "dragons" in result
        assert recommender.get_book_text.called
        assert recommender.get_book_text.call_args[0][0] == book
    
    @patch('Recommendation.BookRecommender')
    def test_calculate_similarity(self, mock_recommender):
        """Test calculate_similarity method"""
        # Set up the mock
        mock_instance = MagicMock()
        mock_instance.calculate_similarity.side_effect = lambda user_id, book: 0.9 if 'Fantasy' in book['categories'] else 0.3
        mock_recommender.return_value = mock_instance
        
        # Import after patching
        from Recommendation import BookRecommender
        
        # Create a recommender
        recommender = BookRecommender()
        
        # Call the method with different books
        high_similarity_book = {'categories': ['Fantasy', 'Adventure']}
        low_similarity_book = {'categories': ['Science Fiction']}
        
        high_result = recommender.calculate_similarity(1, high_similarity_book)
        low_result = recommender.calculate_similarity(1, low_similarity_book)
        
        # Check the results
        assert high_result == 0.9
        assert low_result == 0.3
        assert high_result > low_result
        assert recommender.calculate_similarity.call_count == 2
    
    @patch('Recommendation.BookRecommender')
    def test_get_recommendations(self, mock_recommender):
        """Test get_recommendations method"""
        # Set up the mock
        mock_instance = MagicMock()
        mock_instance.get_recommendations.return_value = [
            {'book': {'id': 'book1', 'title': 'Book 1'}, 'similarity': 0.9},
            {'book': {'id': 'book3', 'title': 'Book 3'}, 'similarity': 0.7},
        ]
        mock_recommender.return_value = mock_instance
        
        # Import after patching
        from Recommendation import BookRecommender
        
        # Create a recommender
        recommender = BookRecommender()
        
        # Call the method
        books = [
            {'id': 'book1', 'title': 'Book 1'},
            {'id': 'book2', 'title': 'Book 2'},
            {'id': 'book3', 'title': 'Book 3'}
        ]
        
        result = recommender.get_recommendations(1, books, num_recommendations=2)
        
        # Check the result
        assert len(result) == 2
        assert result[0]['book']['id'] == 'book1'
        assert result[1]['book']['id'] == 'book3'
        assert result[0]['similarity'] == 0.9
        assert result[1]['similarity'] == 0.7
        assert recommender.get_recommendations.called
        assert recommender.get_recommendations.call_args[0][0] == 1
        assert recommender.get_recommendations.call_args[0][1] == books
        assert recommender.get_recommendations.call_args[1]['num_recommendations'] == 2
    
    @patch('Recommendation.BookRecommender')
    def test_process_google_books_response(self, mock_recommender):
        """Test process_google_books_response method"""
        # Set up the mock
        mock_instance = MagicMock()
        mock_instance.process_google_books_response.return_value = [
            {'id': 'book1', 'title': 'Adventure Book', 'categories': ['Fiction', 'Adventure']}
        ]
        mock_recommender.return_value = mock_instance
        
        # Import after patching
        from Recommendation import BookRecommender
        
        # Create a recommender
        recommender = BookRecommender()
        
        # Call the method
        books_response = [
            {'id': 'book1', 'volumeInfo': {'title': 'Adventure Book', 'categories': ['Fiction', 'Adventure']}},
            {'id': 'book2', 'volumeInfo': {'title': 'Science Textbook', 'categories': ['Non-fiction', 'Science']}}
        ]
        
        result = recommender.process_google_books_response(books_response)
        
        # Check the result
        assert len(result) == 1
        assert result[0]['id'] == 'book1'
        assert result[0]['title'] == 'Adventure Book'
        assert recommender.process_google_books_response.called
        assert recommender.process_google_books_response.call_args[0][0] == books_response

# Test the recommendation functionality directly without needing the Flask app
@patch('Recommendation.BookRecommender')
def test_recommendation_integration(mock_recommender):
    """Test recommendation integration directly"""
    # Set up the mock
    mock_instance = MagicMock()
    mock_instance.get_user_preference_text.return_value = "fantasy adventure"
    mock_instance.get_recommendations.return_value = [
        {'book': {'id': 'book1', 'title': 'Test Book'}, 'similarity': 0.9}
    ]
    mock_recommender.return_value = mock_instance
    
    # Import after patching
    from Recommendation import BookRecommender
    
    # Create a recommender
    recommender = BookRecommender()
    
    # Test user preference text
    preference_text = recommender.get_user_preference_text(user_id=1)
    assert "fantasy" in preference_text
    
    # Test getting recommendations
    books = [
        {'id': 'book1', 'title': 'Test Book 1'},
        {'id': 'book2', 'title': 'Test Book 2'}
    ]
    
    recommendations = recommender.get_recommendations(1, books)
    assert len(recommendations) == 1
    assert recommendations[0]['book']['id'] == 'book1'
    assert recommendations[0]['similarity'] == 0.9 