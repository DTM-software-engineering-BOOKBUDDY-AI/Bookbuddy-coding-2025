import pytest
from flask import url_for
from unittest.mock import patch, MagicMock
from models import User, UserPreferences, Book, ReadingList

def test_homepage(test_client):
    """Test that the homepage loads properly"""
    response = test_client.get('/')
    assert response.status_code == 200
    assert b'BookBuddy' in response.data

def test_login_page(test_client):
    """Test that the login page loads properly"""
    response = test_client.get('/login')
    assert response.status_code == 200
    assert b'login' in response.data.lower()
    assert b'email' in response.data.lower()
    assert b'password' in response.data.lower()

def test_signup_page(test_client):
    """Test that the signup page loads properly"""
    response = test_client.get('/signup')
    assert response.status_code == 200
    assert b'signup' in response.data.lower() or b'register' in response.data.lower()
    assert b'email' in response.data.lower()
    assert b'password' in response.data.lower()
    assert b'username' in response.data.lower()

def test_login_submission(test_client, test_user):
    """Test the login form submission"""
    response = test_client.post('/login', data={
        'email': 'testuser@example.com',
        'password': 'password123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Login successful' in response.data

def test_login_invalid_credentials(test_client, test_user):
    """Test login with invalid credentials"""
    response = test_client.post('/login', data={
        'email': 'testuser@example.com',
        'password': 'wrongpassword'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Invalid email or password' in response.data

def test_logout(test_client, test_user):
    """Test user logout"""
    # Login first
    test_client.post('/login', data={
        'email': 'testuser@example.com',
        'password': 'password123'
    }, follow_redirects=True)
    
    # Then logout
    response = test_client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'You have been logged out' in response.data

def test_profile_page_requires_login(test_client):
    """Test that profile page requires login"""
    response = test_client.get('/profile', follow_redirects=True)
    assert response.status_code == 200
    assert b'login' in response.data.lower()

def test_profile_page_with_login(test_client, test_user):
    """Test that profile page works when logged in"""
    # Login first
    test_client.post('/login', data={
        'email': 'testuser@example.com',
        'password': 'password123'
    }, follow_redirects=True)
    
    # Access profile page
    response = test_client.get('/profile')
    assert response.status_code == 200
    assert b'profile' in response.data.lower()
    assert b'testuser' in response.data

def test_form_page_requires_login(test_client):
    """Test that form page requires login"""
    response = test_client.get('/form', follow_redirects=True)
    assert response.status_code == 200
    assert b'login' in response.data.lower()

def test_my_lib_requires_login(test_client):
    """Test that my_lib page requires login"""
    response = test_client.get('/my_lib', follow_redirects=True)
    assert response.status_code == 200
    assert b'login' in response.data.lower()

@patch('Recommendation.BookRecommender')
def test_recommendation_page_requires_login(mock_recommender, test_client):
    """Test that recommendation page requires login"""
    response = test_client.get('/recommendation', follow_redirects=True)
    assert response.status_code == 200
    assert b'login' in response.data.lower()

@patch('Recommendation.BookRecommender')
def test_recommendation_page_with_login(mock_recommender, test_client, test_user):
    """Test that recommendation page works when logged in"""
    # Login first
    test_client.post('/login', data={
        'email': 'testuser@example.com',
        'password': 'password123'
    }, follow_redirects=True)
    
    # Access recommendation page
    response = test_client.get('/recommendation')
    assert response.status_code == 200
    assert b'recommendation' in response.data.lower()

@patch('app.BookRecommender')
@patch('app.get_search_queries_from_preferences')
@patch('app.fetch_books_from_google_api')
@patch('app.process_google_books_response')
def test_recommendation_post(mock_process, mock_fetch, mock_queries, mock_recommender, test_client, test_db, test_user):
    """Test recommendation form submission"""
    # Mock the recommendation process
    mock_queries.return_value = ['fantasy adventure']
    mock_fetch.return_value = [{'id': 'book1', 'volumeInfo': {'title': 'Test Book'}}]
    mock_process.return_value = [{'id': 'book1', 'title': 'Test Book'}]
    
    recommender_instance = MagicMock()
    recommender_instance.get_user_preference_text.return_value = "fantasy adventure"
    recommender_instance.get_recommendations.return_value = [
        {'book': {'id': 'book1', 'title': 'Test Book'}, 'similarity': 0.9}
    ]
    mock_recommender.return_value = recommender_instance
    
    # Login first
    test_client.post('/login', data={
        'email': 'testuser@example.com',
        'password': 'password123'
    }, follow_redirects=True)
    
    # Submit recommendation form
    response = test_client.post('/recommendation', data={
        'genres': ['fantasy', 'adventure'],
        'themes': ['magic', 'heroism'],
        'mood': 'exciting',
        'length': 'medium',
        'maturity_rating': 'young_adult',
        'series': 'series',
        'preferred_languages': ['en']
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'recommendations' in response.data.lower()
    # Verify the recommender was called
    assert mock_recommender.called
    assert recommender_instance.get_recommendations.called

def test_test_db_route(test_client):
    """Test the test_db route"""
    response = test_client.get('/test_db')
    assert response.status_code == 200
    assert b'Database connection successful' in response.data

def test_check_users_in_debug_mode(test_client, test_app, test_user):
    """Test the check_users route in debug mode"""
    # Set debug mode to True
    test_app.debug = True
    
    response = test_client.get('/check_users')
    assert response.status_code == 200
    assert b'testuser' in response.data

def test_check_users_in_production_mode(test_client, test_app, test_user):
    """Test the check_users route in production mode"""
    # Set debug mode to False
    test_app.debug = False
    
    response = test_client.get('/check_users')
    assert response.status_code == 403
    assert b'Not available in production' in response.data

def test_search_user_found(test_client, test_user):
    """Test searching for an existing user"""
    response = test_client.get('/search_user?username=testuser')
    assert response.status_code == 200
    data = response.get_json()
    assert data['found'] is True
    assert data['username'] == 'testuser'

def test_search_user_not_found(test_client):
    """Test searching for a non-existent user"""
    response = test_client.get('/search_user?username=nonexistentuser')
    assert response.status_code == 200
    data = response.get_json()
    assert data['found'] is False

def test_view_public_profile(test_client, test_user, test_db):
    """Test viewing a public user profile"""
    with test_db.session.begin():
        # Set user profile to public
        test_user.privacy = 'public'
        test_db.session.commit()
    
    response = test_client.get(f'/profile/{test_user.username}')
    assert response.status_code == 200
    assert test_user.username.encode() in response.data

def test_view_private_profile_redirect(test_client, test_user, test_db):
    """Test that viewing a private profile redirects when not logged in"""
    with test_db.session.begin():
        # Set user profile to private
        test_user.privacy = 'private'
        test_db.session.commit()
    
    response = test_client.get(f'/profile/{test_user.username}', follow_redirects=True)
    assert response.status_code == 200
    assert b'This profile is private' in response.data

@patch('app.os.path.exists')
@patch('app.os.path.join')
def test_my_lib_with_books(mock_join, mock_exists, test_client, test_user, test_db):
    """Test my_lib page with books in the reading list"""
    # Mock the image check
    mock_exists.return_value = True
    mock_join.return_value = '/path/to/image.jpg'
    
    # Login first
    test_client.post('/login', data={
        'email': 'testuser@example.com',
        'password': 'password123'
    }, follow_redirects=True)
    
    # Create test book and reading list entries
    with test_db.session.begin():
        book = Book(
            id=1,
            title="Test Book",
            author="Test Author",
            cover_image="test.jpg"
        )
        test_db.session.add(book)
        
        reading_list = ReadingList(
            user_id=test_user.id,
            book_id=1,
            status='current',
            progress=50
        )
        test_db.session.add(reading_list)
        test_db.session.commit()
    
    # Access my_lib page
    response = test_client.get('/my_lib')
    assert response.status_code == 200
    assert b'Test Book' in response.data
    assert b'Test Author' in response.data

@patch('requests.get')
@patch('app.os.path.exists')
def test_add_to_reading_list(mock_exists, mock_requests_get, test_client, test_user, test_db):
    """Test adding a book to the reading list"""
    # Mock image handling
    mock_exists.return_value = True
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b'fake image data'
    mock_requests_get.return_value = mock_response
    
    # Login first
    test_client.post('/login', data={
        'email': 'testuser@example.com',
        'password': 'password123'
    }, follow_redirects=True)
    
    # Add a book to the reading list
    response = test_client.post('/add-to-reading-list', 
                              json={
                                  'book_id': 'test_external_id',
                                  'title': 'Test Book Title',
                                  'author': 'Test Author',
                                  'cover_image': '01.jpg',
                                  'status': 'want'
                              },
                              content_type='application/json')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    
    # Verify the book was added to the database
    with test_db.session.begin():
        books = Book.query.filter(Book.summary.like('%External ID: test_external_id%')).all()
        assert len(books) > 0
        book = books[0]
        assert book.title == 'Test Book Title'
        
        # Verify the reading list entry was created
        reading_list = ReadingList.query.filter_by(user_id=test_user.id, book_id=book.id).first()
        assert reading_list is not None
        assert reading_list.status == 'want' 