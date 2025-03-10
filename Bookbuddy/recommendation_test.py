from flask import Flask
from extensions import db
from Recommendation import BookRecommender
import requests
import os
from dotenv import load_dotenv
from models import User, UserPreferences
import logging

# Load environment variables
load_dotenv()

# Create test Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookbuddy.db'
db.init_app(app)

def get_search_queries_from_preferences(user_prefs):
    """Extract meaningful search terms from user preferences"""
    features = {}
    for pref in user_prefs.split():
        if ':' in pref:
            label, value = pref.split(':', 1)
            if label not in features:
                features[label] = []
            features[label].append(value)
    
    # Define natural language templates
    templates = [
        "{genre} books with {theme} themes",
        "{mood} {genre} novels",
        "{genre} {style} for {maturity} readers",
        "best {genre} books about {theme}",
        "{theme} stories in {genre} style",
        "{maturity} {genre} {theme} novels"
    ]
    
    queries = []
    
    # Generate queries using templates
    for template in templates:
        try:
            query = template.format(
                genre=features.get('genres', [''])[0],
                theme=features.get('theme', [''])[0],
                mood=features.get('mood', [''])[0],
                style=features.get('style', [''])[0],
                maturity=features.get('maturity', [''])[0]
            )
            # Only add non-empty queries (no leading/trailing spaces)
            if query.strip() and not query.startswith(' ') and not query.endswith(' '):
                queries.append(query)
        except (KeyError, IndexError):
            continue
    
    # Remove any duplicate queries while preserving order
    final_queries = list(dict.fromkeys(queries))
    
    # Log the generated queries
    logging.debug(f"Generated queries: {final_queries}")
    
    return final_queries

def fetch_books_from_google_api(query, user_prefs=None, max_results=40):
    """Fetch books from Google Books API with improved filtering"""
    api_key = os.getenv('GOOGLE_BOOKS_API_KEY')
    base_url = "https://www.googleapis.com/books/v1/volumes"
    
    # Build query parameters with explicit English language
    params = {
        'q': f'{query} language:english',
        'maxResults': max_results,
        'key': api_key,
        'printType': 'books',
        'langRestrict': 'en',
        'orderBy': 'relevance'
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        return response.json().get('items', [])
    except Exception as e:
        print(f"Error fetching books: {str(e)}")
        return []

def process_google_books_response(books):
    """Process and clean the Google Books API response"""
    processed_books = []
    for book in books:
        volume_info = book.get('volumeInfo', {})
        
        # Skip books without essential information
        if not all([
            volume_info.get('title'),
            volume_info.get('authors'),
            volume_info.get('description')
        ]):
            continue
        
        # Strict category filtering
        categories = [cat.lower() for cat in volume_info.get('categories', [])]
        if not any(cat in ' '.join(categories) for cat in [
            'fiction',
            'adventure',
            'action and adventure',
            'juvenile fiction'
        ]):
            continue
            
        # Skip non-fiction and educational materials
        if any(cat in ' '.join(categories) for cat in [
            'non-fiction',
            'education',
            'textbook',
            'manual',
            'guide',
            'science',
            'copyright'
        ]):
            continue
        
        # Check description for adventure content
        description = volume_info.get('description', '').lower()
        if not any(term in description for term in [
            'adventure',
            'quest',
            'journey',
            'expedition',
            'explore',
            'discovery'
        ]):
            continue
        
        processed_book = {
            'id': book['id'],
            'title': volume_info['title'],
            'authors': volume_info['authors'],
            'categories': categories,
            'description': description,
            'language': volume_info.get('language', 'unknown'),
            'pageCount': volume_info.get('pageCount', 0),
            'averageRating': volume_info.get('averageRating', 0),
            'maturityRating': volume_info.get('maturityRating', 'NOT_MATURE'),
            'series': 'series' if 'series' in volume_info.get('title', '').lower() else 'standalone'
        }
        
        processed_books.append(processed_book)
    
    return processed_books

def test_recommendation_system():
    """Test the recommendation system"""
    with app.app_context():
        # Create test user with preferences
        create_test_user()
        
        # Create recommender instance
        recommender = BookRecommender()
        test_user_id = 1
        
        # Get user preferences
        user_prefs = recommender.get_user_preference_text(test_user_id)
        print("\nUser Preferences:", user_prefs)
        
        # Get search queries
        search_queries = get_search_queries_from_preferences(user_prefs)
        print("\nSearch Queries:", search_queries)
        
        # Fetch and process books
        all_books = []
        for query in search_queries:
            print(f"\nFetching books for query: {query}")
            books = fetch_books_from_google_api(query, user_prefs)
            processed_books = process_google_books_response(books)
            print(f"Found {len(processed_books)} matching books")
            all_books.extend(processed_books)
        
        # Remove duplicates based on book ID
        unique_books = {book['id']: book for book in all_books}.values()
        all_books = list(unique_books)
        
        print(f"\nTotal unique books found: {len(all_books)}")
        
        # Get recommendations
        recommendations = recommender.get_recommendations(
            test_user_id,
            all_books,
            num_recommendations=5
        )
        
        # Print recommendations
        print("\nTop 5 Book Recommendations:")
        print("-" * 50)
        for i, rec in enumerate(recommendations, 1):
            book = rec['book']
            similarity = rec['similarity']
            
            print(f"\n{i}. {book['title']}")
            print(f"   Authors: {', '.join(book['authors'])}")
            print(f"   Similarity Score: {similarity:.2f}")
            print(f"   Categories: {', '.join(book['categories']) if book['categories'] else 'N/A'}")
            print(f"   Language: {book['language']}")
            print(f"   Rating: {book['averageRating']}/5" if book['averageRating'] else "   Rating: N/A")
            if book['description']:
                # Truncate description to 150 characters
                desc = book['description'][:150] + "..." if len(book['description']) > 150 else book['description']
                print(f"   Description: {desc}")
            
            # Debug similarity calculation
            recommender.debug_similarity(test_user_id, book)
            print("-" * 50)  # Add separator between recommendations

if __name__ == "__main__":
    test_recommendation_system()