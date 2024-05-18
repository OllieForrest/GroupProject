import pytest
from unittest.mock import patch, Mock
from app import app, db
from app.models import Post
from delete_posts import delete_all_posts
from app.forms import LoginForms, RegistrationForm
from flask import Flask
from wtforms.validators import ValidationError

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'testkey'
    return app

def test_delete_all_posts():
    with app.app_context():
        with patch('app.db.session') as mock_session:
            mock_session.query.return_value.delete.return_value = None
            mock_session.commit.return_value = None

            delete_all_posts()
            assert mock_session.query(Post).delete.called, "Delete method was not called"
            assert mock_session.commit.called, "Commit was not called"
            mock_session.commit.side_effect = Exception("Database Error")

            delete_all_posts()
            assert mock_session.rollback.called, "Rollback was not called"

def test_login_form(app):
    with app.test_request_context():
        form = LoginForms(data={'username': '', 'password': '', 'remember_me': False})
        assert not form.validate(), "Empty fields should fail validation"
        form = LoginForms(data={'username': 'user', 'password': 'pass', 'remember_me': True})
        assert form.validate(), "Correct fields should pass validation"

def test_registration_form(app):
    with app.test_request_context():
        form = RegistrationForm(data={
            'username': 'user',
            'email': 'user@example.com',
            'password': 'password',
            'password2': 'password'
        })
        assert form.validate(), "Correct data should pass validation"

        form = RegistrationForm(data={
            'username': 'user',
            'email': 'user',
            'password': 'password',
            'password2': 'different'
        })
        assert not form.validate(), "Mismatched passwords or invalid email should fail validation"

def test_custom_validation(app):
    with app.test_request_context():
        # Assuming db.session.scalar will need to be mocked
        with patch('app.forms.db.session.scalar') as mock_scalar:
            # Simulate finding a user
            mock_scalar.return_value = Mock()
            form = RegistrationForm(data={
                'username': 'existing_user',
                'email': 'newuser@example.com',
                'password': 'password',
                'password2': 'password'
            })
            with pytest.raises(ValidationError):
                form.validate_username(form.username)

            mock_scalar.return_value = None
            assert form.validate_username(form.username) is None, "Non-existing user should pass validation"

            mock_scalar.return_value = Mock()
            form = RegistrationForm(data={
                'username': 'newuser',
                'email': 'existing@example.com',
                'password': 'password',
                'password2': 'password'
            })
            with pytest.raises(ValidationError):
                form.validate_email(form.email)
