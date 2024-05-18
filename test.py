import os
os.environ['DATABASE_URL'] = 'sqlite://'

from datetime import datetime, timezone, timedelta
import unittest
from app import app, db
from app.models import User, Post
from unittest.mock import patch, MagicMock
from delete_posts import delete_all_posts
from app.forms import LoginForms, RegistrationForm
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
from app.models import Post
from app.routes import register
from flask import render_template_string
from app.routes import leaderboard, search, submit_guess
from flask import Flask, request



class UserModelCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client() 

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        u = User(username='susan', email='susan@example.com')
        u.set_password('cat')
        self.assertFalse(u.check_password('dog'))
        self.assertTrue(u.check_password('cat'))

    def test_avatar(self):
        u = User(username='john', email='john@example.com')
        self.assertEqual(u.avatar(128), ('https://www.gravatar.com/avatar/'
                                         'd4c74594d841139328695756648b6bd6'
                                         '?d=identicon&s=128'))

    def test_delete_all_posts(self):
        with self.app_context:  # Correctly using app context
            with patch('app.db.session') as mock_session:
                mock_query = MagicMock()
                mock_session.query.return_value = mock_query
                mock_query.delete.return_value = None
                mock_session.commit.return_value = None

                # First delete call
                delete_all_posts()
                mock_session.query.assert_called_once_with(Post)
                mock_query.delete.assert_called_once()
                mock_session.commit.assert_called_once()

                # Reset mock calls
                mock_session.reset_mock()
                mock_query.reset_mock()

                # Simulate exception on commit
                mock_session.commit.side_effect = Exception("Database Error")
                mock_session.rollback.return_value = None

                # Second delete call to trigger rollback
                delete_all_posts()
                mock_session.query.assert_called_once_with(Post)
                mock_query.delete.assert_called_once()
                mock_session.commit.assert_called_once()
                mock_session.rollback.assert_called_once()

    def test_set_password(self):
        # Create a test user
        test_user = User(username='test_user', email='test@example.com')

        # Set a password for the test user
        test_password = 'test_password'
        test_user.set_password(test_password)

        # Check if the password hash is set
        self.assertTrue(test_user.password_hash is not None)
        self.assertTrue(check_password_hash(test_user.password_hash, test_password))

    
    def test_check_password(self):
        # Create a test user
        test_user = User(username='test_user', email='test@example.com')

        # Set a password for the test user
        test_password = 'test_password'
        hashed_password = generate_password_hash(test_password)
        test_user.password_hash = hashed_password

        # Check the password
        self.assertTrue(test_user.check_password(test_password))
        self.assertFalse(test_user.check_password('wrong_password'))

    def test_register_success(self):
        with self.app.test_client() as client:
            response = client.post('/register', data={
                'username': 'test_user',
                'email': 'test@example.com',
                'password': 'test_password',
                'password2': 'test_password'
            }, follow_redirects=True)

            # Assert that the response redirects to the login page
            self.assertEqual(response.status_code, 200)

    def test_leaderboard(self):
    # Simulate a request to the leaderboard endpoint
        with self.app.test_client() as client:
            response = client.get('/leaderboard')

            # Check if the response status code is 200
            self.assertEqual(response.status_code, 200)

    def test_submit_guess_valid(self):
     with self.app.test_client() as client:
        # Mock the Post query
        with patch('app.routes.Post.query.get_or_404') as mock_get_or_404:
            mock_post = Post(sold_price=100.0)  # Assuming sold price is 100.0
            mock_get_or_404.return_value = mock_post

            # Make a POST request to the submit_guess endpoint
            response = client.post('/submit_guess/1', data={'guess_price': '50.0'}, follow_redirects=True)

            # Assert the response status code
            self.assertEqual(response.status_code, 200)

    
    def test_submit_guess_invalid(self):
       with self.app.test_client() as client:
        # Mock the Post query
        with patch('app.routes.Post.query.get_or_404') as mock_get_or_404:
            mock_post = Post(sold_price=100.0)  # Assuming sold price is 100.0
            mock_get_or_404.return_value = mock_post

            # Make a POST request to the submit_guess endpoint
            response = client.post('/submit_guess/1', data={'guess_price': '50.0'}, follow_redirects=True)

            # Assert the response status code
            self.assertEqual(response.status_code, 200)

    
    
        # Create a Flask test app


            
if __name__ == '__main__':
    unittest.main(verbosity=2)