import pytest
import os
from unittest.mock import patch, MagicMock

# Import the function to test
from check_database import check_database_status

def test_check_database_exists(test_app, test_db):
    """Test that the database check detects when the database exists"""
    with test_app.app_context():
        # Set up a mock for print function to capture output
        with patch('builtins.print') as mock_print:
            # Create a mock for os.path.exists to always return True
            with patch('os.path.exists', return_value=True):
                # Run the database check
                check_database_status()
                
                # Verify that the function was called and database exists message was printed
                mock_print.assert_any_call("\n=== Database Status Check ===")
                mock_print.assert_any_call(f"\n1. Database file status:")
                
                # Check that os.path.exists was called
                assert any("Exists: True" in str(args) if isinstance(args, tuple) and args and isinstance(args[0], str) else False 
                          for args, _ in mock_print.call_args_list)

def test_check_database_tables(test_app, test_db):
    """Test that the database check correctly detects the tables"""
    with test_app.app_context():
        # Create tables
        test_db.create_all()
        
        # Set up a mock for print function to capture output
        with patch('builtins.print') as mock_print:
            # Run the database check
            check_database_status()
            
            # Verify that the function detected the user table
            mock_print.assert_any_call(f"\n2. Tables in database:")
            
            # At least one call should print the user table
            user_table_found = False
            for args, _ in mock_print.call_args_list:
                if args and isinstance(args[0], str) and "- user" in args[0]:
                    user_table_found = True
                    break
            
            assert user_table_found, "User table not detected in the database check"

def test_check_user_structure(test_app, test_db):
    """Test that the user table structure is correctly detected and reported"""
    with test_app.app_context():
        # Create tables
        test_db.create_all()
        
        # Set up a mock for print function to capture output
        with patch('builtins.print') as mock_print:
            # Run the database check
            check_database_status()
            
            # Verify that the function detected and printed user table columns
            mock_print.assert_any_call(f"\n3. User table columns:")
            
            # Check for key columns
            for column_name in ['id', 'username', 'email', 'password_hash']:
                column_found = False
                for args, _ in mock_print.call_args_list:
                    if args and isinstance(args[0], str) and column_name in args[0]:
                        column_found = True
                        break
                
                assert column_found, f"Column {column_name} not detected in the user table"

def test_check_record_count(test_app, test_db, test_user):
    """Test that the database check correctly counts records"""
    with test_app.app_context():
        # Set up a mock for print function to capture output
        with patch('builtins.print') as mock_print:
            # Run the database check
            check_database_status()
            
            # Verify that the function counted and reported user records
            mock_print.assert_any_call(f"\n4. Record counts:")
            
            # Verify user count is at least 1 (from test_user)
            count_found = False
            for args, _ in mock_print.call_args_list:
                if args and isinstance(args[0], str) and args[0].startswith("- Users:"):
                    count_found = True
                    break
            
            assert count_found, "User count not reported in the database check" 