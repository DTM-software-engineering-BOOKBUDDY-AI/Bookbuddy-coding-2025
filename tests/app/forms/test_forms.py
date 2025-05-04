import pytest
from forms import LoginForm, SignupForm
from datetime import date

def test_login_form_validation(test_app):
    """Test the login form validation"""
    with test_app.app_context():
        # Test valid form
        form = LoginForm()
        form.email.data = "testuser@example.com"
        form.password.data = "password123"
        
        # We're testing just our fields, not CSRF which would make it fail
        form.meta = type('obj', (object,), {'csrf': False})
        
        # Validate specific fields manually
        assert form.email.validate(form) is True
        assert form.password.validate(form) is True
        
def test_signup_form_validation(test_app):
    """Test the signup form validation"""
    with test_app.app_context():
        # Test valid form
        form = SignupForm()
        form.username.data = "newuser"
        form.email.data = "newuser@example.com"
        form.password.data = "password123"
        form.confirm_password.data = "password123"
        form.gender.data = "male"
        
        # Use a proper date object instead of a string
        form.birthday.data = date(2000, 1, 1)
        
        # We're testing just our fields, not CSRF which would make it fail
        form.meta = type('obj', (object,), {'csrf': False})
        
        # Validate specific fields
        assert form.username.validate(form) is True
        assert form.email.validate(form) is True
        assert form.password.validate(form) is True
        assert form.confirm_password.validate(form) is True 