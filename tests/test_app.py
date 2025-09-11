import pytest
import os
import tempfile
from app import create_app
from models import init_db, User, Post

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app('testing')
    
    with app.app_context():
        init_db()
        yield app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()

class TestAuth:
    """Test authentication functionality."""
    
    def test_register_page(self, client):
        """Test that the register page loads."""
        response = client.get('/auth/register')
        assert response.status_code == 200
        assert b'Register' in response.data
    
    def test_login_page(self, client):
        """Test that the login page loads."""
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert b'Login' in response.data
    
    def test_user_registration(self, client):
        """Test user registration."""
        response = client.post('/auth/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'confirm_password': 'testpass123'
        })
        assert response.status_code == 302  # Redirect after successful registration
    
    def test_user_login(self, client):
        """Test user login."""
        # First register a user
        client.post('/auth/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'confirm_password': 'testpass123'
        })
        
        # Then login
        response = client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        })
        assert response.status_code == 302  # Redirect after successful login

class TestBlog:
    """Test blog functionality."""
    
    def test_homepage(self, client):
        """Test that the homepage loads."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'ECHO' in response.data
    
    def test_create_post_requires_login(self, client):
        """Test that creating a post requires login."""
        response = client.get('/create')
        assert response.status_code == 302  # Redirect to login
    
    def test_my_posts_requires_login(self, client):
        """Test that viewing my posts requires login."""
        response = client.get('/my-posts')
        assert response.status_code == 302  # Redirect to login
    
    def test_weekly_digest(self, client):
        """Test that the weekly digest page loads."""
        response = client.get('/digest')
        assert response.status_code == 200
        assert b'Weekly Digest' in response.data

class TestModels:
    """Test database models."""
    
    def test_user_creation(self, app):
        """Test user creation."""
        with app.app_context():
            success = User.create('testuser', 'test@example.com', 'password123')
            assert success == True
            
            user = User.get_by_username('testuser')
            assert user is not None
            assert user['username'] == 'testuser'
            assert user['email'] == 'test@example.com'
    
    def test_post_creation(self, app):
        """Test post creation."""
        with app.app_context():
            # Create a user first
            User.create('testuser', 'test@example.com', 'password123')
            user = User.get_by_username('testuser')
            
            # Create a post
            post_id = Post.create(
                user['id'],
                'Test Post',
                'This is a test post content.',
                'test, example'
            )
            assert post_id is not None
            
            # Retrieve the post
            post = Post.get_by_id(post_id)
            assert post is not None
            assert post['title'] == 'Test Post'
            assert post['content'] == 'This is a test post content.'
            assert post['tags'] == 'test, example'