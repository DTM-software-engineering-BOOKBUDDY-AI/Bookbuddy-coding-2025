import pytest
from unittest.mock import patch, MagicMock, PropertyMock
from flask import url_for, current_app
import json

class MockGoogleBooksAPI:
    def __init__(self, api_key=None):
        self.api_key = api_key or 'test_api_key'
        
    def search_books(self, query, max_results=10):
        """Mock search books method"""
        if not query:
            return []
            
        return [
            {
                'id': 'test_book_1',
                'volumeInfo': {
                    'title': 'Test Book 1',
                    'authors': ['Test Author'],
                    'description': 'This is a test book about ' + query,
                    'imageLinks': {
                        'thumbnail': 'http://example.com/test_book_1.jpg'
                    },
                    'categories': ['Fiction', 'Test'],
                    'pageCount': 200,
                    'averageRating': 4.5,
                    'language': 'en'
                }
            },
            {
                'id': 'test_book_2',
                'volumeInfo': {
                    'title': 'Test Book 2',
                    'authors': ['Another Author'],
                    'description': 'Another test book about ' + query,
                    'imageLinks': {
                        'thumbnail': 'http://example.com/test_book_2.jpg'
                    },
                    'categories': ['Non-fiction', 'Test'],
                    'pageCount': 300,
                    'averageRating': 4.0,
                    'language': 'en'
                }
            }
        ]
        
    def get_book_details(self, book_id):
        """Mock get book details method"""
        if book_id == 'test_book_1':
            return {
                'id': 'test_book_1',
                'volumeInfo': {
                    'title': 'Test Book 1',
                    'authors': ['Test Author'],
                    'description': 'This is a test book',
                    'imageLinks': {
                        'thumbnail': 'http://example.com/test_book_1.jpg'
                    },
                    'categories': ['Fiction', 'Test'],
                    'pageCount': 200,
                    'averageRating': 4.5,
                    'language': 'en',
                    'previewLink': 'http://example.com/preview/test_book_1'
                }
            }
        elif book_id == 'test_book_2':
            return {
                'id': 'test_book_2',
                'volumeInfo': {
                    'title': 'Test Book 2',
                    'authors': ['Another Author'],
                    'description': 'Another test book',
                    'imageLinks': {
                        'thumbnail': 'http://example.com/test_book_2.jpg'
                    },
                    'categories': ['Non-fiction', 'Test'],
                    'pageCount': 300,
                    'averageRating': 4.0,
                    'language': 'en'
                    # No preview link for this book
                }
            }
        else:
            return None

@pytest.fixture
def mock_books_api():
    """Fixture to create a mock books API instance"""
    return MockGoogleBooksAPI()

@patch('services.google_books.GoogleBooksAPI', MockGoogleBooksAPI)
def test_search_books_api(test_client, test_app):
    """Test the search_books API endpoint"""
    response = test_client.get('/books/search?q=fantasy')
    assert response.status_code == 200
    
    # Check response content
    data = json.loads(response.data)
    assert len(data) == 2
    assert data[0]['id'] == 'test_book_1'
    assert data[0]['volumeInfo']['title'] == 'Test Book 1'
    assert 'fantasy' in data[0]['volumeInfo']['description'].lower()

@patch('services.google_books.GoogleBooksAPI', MockGoogleBooksAPI)
def test_search_books_api_empty_query(test_client, test_app):
    """Test the search_books API endpoint with an empty query"""
    response = test_client.get('/books/search?q=')
    assert response.status_code == 200
    
    # Check response content
    data = json.loads(response.data)
    assert len(data) == 0

@patch('services.google_books.GoogleBooksAPI', MockGoogleBooksAPI)
def test_search_books_api_error(test_client, test_app):
    """Test the search_books API endpoint when an error occurs"""
    # Use the special error trigger in our test routes
    response = test_client.get('/books/search?q=fantasy&error=true')
    assert response.status_code == 500
    
    # Check response content
    data = json.loads(response.data)
    assert 'error' in data
    assert 'API error' in data['error']

@patch('services.google_books.GoogleBooksAPI', MockGoogleBooksAPI)
def test_search_results_page(test_client, test_app):
    """Test the search results page"""
    # Set a flag to indicate we're in testing mode
    test_app.config['TESTING'] = True
    
    # Now just check that the route responds
    response = test_client.get('/books/search/results?q=fantasy')
    assert response.status_code == 200

@patch('services.google_books.GoogleBooksAPI', MockGoogleBooksAPI)
def test_search_results_page_empty_query(test_client, test_app):
    """Test the search results page with empty query"""
    # Set a flag to indicate we're in testing mode
    test_app.config['TESTING'] = True
    
    # Test the redirect behavior for empty query
    response = test_client.get('/books/search/results', follow_redirects=True)
    assert response.status_code == 200

@patch('services.google_books.GoogleBooksAPI', MockGoogleBooksAPI)
def test_search_results_page_error(test_client, test_app):
    """Test the search results page when an error occurs"""
    # Set a flag to indicate we're in testing mode
    test_app.config['TESTING'] = True
    
    # Use error parameter to trigger the error path
    response = test_client.get('/books/search/results?q=fantasy&error=true')
    assert response.status_code == 200

@patch('services.google_books.GoogleBooksAPI', MockGoogleBooksAPI)
def test_book_details_page(test_client, test_app):
    """Test the book details page"""
    # Set a flag to indicate we're in testing mode
    test_app.config['TESTING'] = True
    
    response = test_client.get('/books/book/test_book_1')
    assert response.status_code == 200
    
    # Check that the book details are displayed
    assert b'Test Book 1' in response.data
    assert b'Test Author' in response.data
    assert b'This is a test book' in response.data

@patch('services.google_books.GoogleBooksAPI', MockGoogleBooksAPI)
def test_book_details_page_error(test_client, test_app):
    """Test the book details page when an error occurs"""
    # Set a flag to indicate we're in testing mode
    test_app.config['TESTING'] = True
    
    # Use error parameter to trigger the error path
    response = test_client.get('/books/book/test_book_1?error=true', follow_redirects=True)
    assert response.status_code == 200
    
    # Check for error message and redirect
    assert b'Error fetching book details' in response.data

@patch('services.google_books.GoogleBooksAPI', MockGoogleBooksAPI)
def test_book_preview_page(test_client, test_app):
    """Test the book preview page"""
    # Set a flag to indicate we're in testing mode
    test_app.config['TESTING'] = True
    
    response = test_client.get('/books/preview/test_book_1')
    assert response.status_code == 200
    
    # Check that the preview page is displayed
    assert b'Test Book 1' in response.data

@patch('services.google_books.GoogleBooksAPI', MockGoogleBooksAPI)
def test_book_preview_page_no_preview(test_client, test_app):
    """Test the book preview page when no preview is available"""
    # Set a flag to indicate we're in testing mode
    test_app.config['TESTING'] = True
    
    response = test_client.get('/books/preview/test_book_2', follow_redirects=True)
    assert response.status_code == 200
    
    # Check for warning message and redirect
    assert b'Preview not available for this book' in response.data

@patch('services.google_books.GoogleBooksAPI', MockGoogleBooksAPI)
def test_book_preview_page_error(test_client, test_app):
    """Test the book preview page when an error occurs"""
    # Set a flag to indicate we're in testing mode
    test_app.config['TESTING'] = True
    
    # Use error parameter to trigger the error path
    response = test_client.get('/books/preview/test_book_1?error=true', follow_redirects=True)
    assert response.status_code == 200
    
    # Check for error message and redirect
    assert b'Error loading book preview' in response.data 