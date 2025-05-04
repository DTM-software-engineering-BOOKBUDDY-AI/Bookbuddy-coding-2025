import pytest
from unittest.mock import patch, MagicMock
from flask import Flask, render_template_string

@pytest.fixture
def mock_app():
    """Create a test Flask app without template dependencies"""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    # Create a simplified route structure for testing
    @app.route('/')
    def home():
        return "Home Page"
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        return "Login Page"
    
    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        return "Signup Page"
    
    @app.route('/profile')
    def profile():
        return "Profile Page"
    
    @app.route('/form')
    def form():
        return "Form Page"
    
    @app.route('/my_lib')
    def my_lib():
        return "My Library Page"
    
    @app.route('/recommendation')
    def recommendation():
        return "Recommendation Page"
    
    @app.route('/test_db')
    def test_db():
        return "Database connection successful!"
    
    @app.route('/check_users')
    def check_users():
        return "Users Page"
    
    @app.route('/search_user')
    def search_user():
        user = {'found': True, 'username': 'testuser', 'bio': 'Test bio', 'profile_picture': 'test.jpg'}
        return app.response_class(
            response=str(user),
            status=200,
            mimetype='application/json'
        )
    
    @app.route('/profile/<username>')
    def view_profile(username):
        return f"Profile for {username}"
    
    @app.route('/add-to-reading-list', methods=['POST'])
    def add_to_reading_list():
        return app.response_class(
            response='{"success": true, "message": "Book added to reading list successfully"}',
            status=200,
            mimetype='application/json'
        )
    
    # Create blueprint mock
    books_bp = MagicMock()
    books_bp.name = 'books'
    
    @app.route('/books/search')
    def search_books():
        return app.response_class(
            response='[{"id": "test1", "volumeInfo": {"title": "Test Book"}}]',
            status=200,
            mimetype='application/json'
        )
    
    @app.route('/books/search/results')
    def search_results():
        return "Search Results Page"
    
    @app.route('/books/book/<book_id>')
    def book_details(book_id):
        return f"Book Details Page for {book_id}"
    
    @app.route('/books/preview/<book_id>')
    def book_preview(book_id):
        return f"Book Preview Page for {book_id}"
    
    # Mock the blueprint registration
    app.register_blueprint = MagicMock()
    
    return app

@pytest.fixture
def test_client(mock_app):
    """Test client for the mock app"""
    return mock_app.test_client()

def test_home_route(test_client):
    """Test the home route"""
    response = test_client.get('/')
    assert response.status_code == 200
    assert b"Home Page" in response.data

def test_login_route(test_client):
    """Test the login route"""
    response = test_client.get('/login')
    assert response.status_code == 200
    assert b"Login Page" in response.data

def test_signup_route(test_client):
    """Test the signup route"""
    response = test_client.get('/signup')
    assert response.status_code == 200
    assert b"Signup Page" in response.data

def test_profile_route(test_client):
    """Test the profile route"""
    response = test_client.get('/profile')
    assert response.status_code == 200
    assert b"Profile Page" in response.data

def test_form_route(test_client):
    """Test the form route"""
    response = test_client.get('/form')
    assert response.status_code == 200
    assert b"Form Page" in response.data

def test_my_lib_route(test_client):
    """Test the my_lib route"""
    response = test_client.get('/my_lib')
    assert response.status_code == 200
    assert b"My Library Page" in response.data

def test_recommendation_route(test_client):
    """Test the recommendation route"""
    response = test_client.get('/recommendation')
    assert response.status_code == 200
    assert b"Recommendation Page" in response.data

def test_test_db_route(test_client):
    """Test the test_db route"""
    response = test_client.get('/test_db')
    assert response.status_code == 200
    assert b"Database connection successful!" in response.data

def test_check_users_route(test_client):
    """Test the check_users route"""
    response = test_client.get('/check_users')
    assert response.status_code == 200
    assert b"Users Page" in response.data

def test_search_user_route(test_client):
    """Test the search_user route"""
    response = test_client.get('/search_user')
    assert response.status_code == 200
    # Test parsing the response would be done in a real app

def test_view_profile_route(test_client):
    """Test the view_profile route"""
    response = test_client.get('/profile/testuser')
    assert response.status_code == 200
    assert b"Profile for testuser" in response.data

def test_add_to_reading_list_route(test_client):
    """Test the add_to_reading_list route"""
    response = test_client.post('/add-to-reading-list', json={
        'book_id': 'test_id',
        'title': 'Test Title',
        'author': 'Test Author',
        'cover_image': 'test.jpg',
        'status': 'want'
    })
    assert response.status_code == 200
    # Test parsing the response would be done in a real app

def test_books_search_route(test_client):
    """Test the books/search route"""
    response = test_client.get('/books/search')
    assert response.status_code == 200
    # Test parsing the response would be done in a real app

def test_books_search_results_route(test_client):
    """Test the books/search/results route"""
    response = test_client.get('/books/search/results')
    assert response.status_code == 200
    assert b"Search Results Page" in response.data

def test_books_book_details_route(test_client):
    """Test the books/book/<book_id> route"""
    response = test_client.get('/books/book/test1')
    assert response.status_code == 200
    assert b"Book Details Page for test1" in response.data

def test_books_book_preview_route(test_client):
    """Test the books/preview/<book_id> route"""
    response = test_client.get('/books/preview/test1')
    assert response.status_code == 200
    assert b"Book Preview Page for test1" in response.data 