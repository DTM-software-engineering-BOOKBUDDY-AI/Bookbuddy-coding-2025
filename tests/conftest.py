import pytest
import os
import sys
from unittest.mock import MagicMock, patch
from dotenv import load_dotenv
import json

# Add the application directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Bookbuddy_app')))

# Create mocks for problematic imports
class MockSklearnModule(MagicMock):
    # This allows accessing nested attributes like sklearn.metrics.pairwise
    def __getattr__(self, name):
        return MagicMock()

sklearn_mock = MockSklearnModule()
sys.modules['sklearn'] = sklearn_mock
sys.modules['sklearn.feature_extraction'] = sklearn_mock
sys.modules['sklearn.feature_extraction.text'] = sklearn_mock
sys.modules['sklearn.metrics'] = sklearn_mock
sys.modules['sklearn.metrics.pairwise'] = sklearn_mock

# Mock the Recommendation module to avoid importing it
recommendation_mock = MagicMock()
recommendation_mock.BookRecommender = MagicMock()
sys.modules['Recommendation'] = recommendation_mock

# Mock the routes modules since they're imported by app.py
books_bp_mock = MagicMock()
books_bp_mock.name = 'books'

# Define all required endpoints for the blueprint
search_books_mock = MagicMock()
search_books_mock.__name__ = 'search_books'
books_bp_mock.search_books = search_books_mock

search_results_mock = MagicMock()
search_results_mock.__name__ = 'search_results'
books_bp_mock.search_results = search_results_mock

book_details_mock = MagicMock()
book_details_mock.__name__ = 'book_details'
books_bp_mock.book_details = book_details_mock

book_preview_mock = MagicMock()
book_preview_mock.__name__ = 'book_preview'
books_bp_mock.book_preview = book_preview_mock

# Setup route method
books_bp_mock.route = MagicMock()
books_bp_mock.route.return_value = lambda x: x

# Register all mocked routes
books_bp_mock.route('/search')(search_books_mock)
books_bp_mock.route('/search/results')(search_results_mock)
books_bp_mock.route('/book/<book_id>')(book_details_mock)
books_bp_mock.route('/preview/<book_id>')(book_preview_mock)

routes_books_mock = MagicMock()
routes_books_mock.books_bp = books_bp_mock
routes_books_mock.get_books_api = MagicMock()
sys.modules['routes'] = MagicMock()
sys.modules['routes.books'] = routes_books_mock

# Mock services.google_books for tests
sys.modules['services'] = MagicMock()
sys.modules['services.google_books'] = MagicMock()
sys.modules['services.google_books'].GoogleBooksAPI = MagicMock

# Mock requests for testing
sys.modules['requests'] = MagicMock()

# Load environment variables
load_dotenv()

# Set up the Google Books API key if not present
if not os.getenv('GOOGLE_BOOKS_API_KEY'):
    os.environ['GOOGLE_BOOKS_API_KEY'] = 'dummy_key_for_testing'

# Define a patch to mock the render_template function
def mock_render_template(template_name, **context):
    # For testing, bypass template rendering by returning a mock output
    # that doesn't depend on actual template files or template parsing
    if app.config.get('TESTING', False):
        # Create a simplified output for testing
        output = {
            'template': template_name,
            'context': {k: str(v) if not isinstance(v, (list, dict)) else v for k, v in context.items()}
        }
        return str(output)
    
    # Return proper JSON for the /books/search endpoint
    if template_name.endswith('/search'):
        # This should be JSON data
        return json.dumps(context.get('books', []))
    # For tests, just return a basic HTML with template name and context data
    context_str = ", ".join([f"{k}={v}" for k, v in context.items()])
    return f"<html><body><h1>Mock Template: {template_name}</h1><p>{context_str}</p></body></html>"

# Define a patch for url_for
def mock_url_for(endpoint, **values):
    # For test endpoints
    if endpoint.startswith('books.'):
        # Remap blueprint endpoints to direct routes
        direct_route = endpoint.replace('.', '_')
        endpoint = direct_route
    
    # Return a mock URL for all endpoints
    params = "&".join([f"{k}={v}" for k, v in values.items()])
    return f"/{endpoint}?{params}" if params else f"/{endpoint}"

# Import app and db after adding to path and setting up mocks
from app import app, db
from models import User, UserPreferences, ReadingList, Book

# Apply template patching
app.jinja_env.is_template_loading = False

@pytest.fixture(scope='function')
def test_app():
    """Test Flask application with test config"""
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'WTF_CSRF_ENABLED': False
    })
    
    # Register blueprint routes for testing
    from routes.books import books_bp
    
    # Save reference to the real blueprint routes for testing
    route_endpoints = {}
    for rule in app.url_map.iter_rules():
        if rule.endpoint.startswith('books.'):
            route_endpoints[rule.endpoint] = rule.rule
    
    with app.app_context():
        db.create_all()
        
        # Apply mocks for template rendering and URL generation
        with patch('flask.render_template', side_effect=mock_render_template):
            with patch('flask.url_for', side_effect=mock_url_for):
                yield app
        
        db.drop_all()

@pytest.fixture(scope='function')
def test_client(test_app):
    """Test Flask client for making requests"""
    # Add patch for render_template to avoid template errors
    with patch('flask.render_template', side_effect=mock_render_template):
        with patch('flask.url_for', side_effect=mock_url_for):
            yield test_app.test_client()

@pytest.fixture(scope='function')
def test_db(test_app):
    """Test database instance"""
    return db

@pytest.fixture(scope='function')
def test_user(test_app, test_db):
    """Create a test user for testing"""
    with test_app.app_context():
        # Clear any existing data to avoid conflicts
        test_db.session.query(ReadingList).delete()
        test_db.session.query(UserPreferences).delete()
        test_db.session.query(User).delete()
        test_db.session.commit()
        
        user = User(
            username='testuser',
            email='testuser@example.com'
        )
        user.set_password('password123')
        test_db.session.add(user)
        
        # Create user preferences
        preferences = UserPreferences(
            user_id=1,
            genres='fantasy adventure',
            theme='magic heroism',
            mood='exciting',
            language='en',
            length='medium',
            maturity='young_adult',
            style='series'
        )
        test_db.session.add(preferences)
        test_db.session.commit()
        
        yield user
        
        try:
            # Clean up - delete child records first
            test_db.session.query(ReadingList).filter_by(user_id=user.id).delete()
            test_db.session.query(UserPreferences).filter_by(user_id=user.id).delete()
            test_db.session.query(User).filter_by(id=user.id).delete()
            test_db.session.commit()
        except Exception as e:
            print(f"Error during test cleanup: {e}")
            test_db.session.rollback()
            
# Add missing imports for testing
from models import ReadingList, Book 