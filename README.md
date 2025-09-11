# ECHO - Blog Web App

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-2.3.3-green.svg)](https://flask.palletsprojects.com/)

ECHO is a modern, sophisticated CRUD blog web application built with Flask, featuring user authentication, post management, and special features like version history and weekly digest. The application showcases a beautiful, minimalist design with a sophisticated color palette and smooth animations.

## Features

### Core Features
- **User Authentication**: Register, login, logout with password hashing
- **CRUD Operations**: Create, read, update, and delete blog posts
- **Search & Filter**: Search posts by content and filter by tags
- **Responsive Design**: Works on desktop and mobile devices

### Special Features
- **Auto-summary**: Automatically generates post summaries from first 2-3 sentences
- **Reading Time**: Estimates reading time based on word count (200 words/minute)
- **Tag Cloud**: Visual representation of most-used tags
- **Version History**: Tracks and displays post edit history
- **Weekly Digest**: Groups posts by creation week
- **Dark/Light Mode**: Toggle between themes with session persistence

## Tech Stack

- **Backend**: Flask (Python web framework)
- **Database**: SQLite (lightweight, file-based database)
- **Frontend**: HTML, CSS, JavaScript with Bootstrap 5
- **Templates**: Jinja2 templating engine
- **Forms**: Flask-WTF with CSRF protection
- **Security**: Flask-Bcrypt for password hashing

## Installation & Setup

1. **Clone or download the project files**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

4. **Open your browser** and navigate to `http://localhost:5000`

## Project Structure

```
ECHO/
├── app.py                 # Main Flask application
├── models.py              # Database models and operations
├── config.py              # Application configuration
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── auth/                 # Authentication module
│   ├── __init__.py
│   ├── forms.py          # Registration and login forms
│   └── routes.py         # Authentication routes
├── blog/                 # Blog module
│   ├── __init__.py
│   ├── forms.py          # Post creation/edit forms
│   └── routes.py         # Blog routes (CRUD, search, etc.)
├── templates/            # HTML templates
│   ├── base.html         # Base template with navigation
│   ├── auth/             # Authentication templates
│   │   ├── login.html
│   │   └── register.html
│   └── blog/             # Blog templates
│       ├── index.html    # Homepage with post list
│       ├── post.html     # Individual post view
│       ├── create.html   # Create new post
│       ├── edit.html     # Edit existing post
│       ├── my_posts.html # User's posts
│       ├── search.html   # Search results
│       ├── tag.html      # Posts by tag
│       └── digest.html   # Weekly digest
├── static/               # Static files
│   ├── style.css         # Custom CSS with dark/light themes
│   ├── script.js         # JavaScript for UI enhancements
│   └── favicon.png       # Website favicon
└── tests/                # Test files
    ├── __init__.py
    └── test_app.py       # Application tests
```

## Routes

### Authentication
- `/auth/register` - User registration
- `/auth/login` - User login
- `/auth/logout` - User logout

### Blog
- `/` - Homepage with post list and pagination
- `/post/<id>` - View individual post with version history
- `/create` - Create new post (requires login)
- `/edit/<id>` - Edit post (requires login, owner only)
- `/delete/<id>` - Delete post (requires login, owner only)
- `/search?query=<keyword>` - Search posts
- `/tags/<tag>` - Filter posts by tag
- `/digest` - Weekly digest view
- `/toggle-theme` - Toggle dark/light mode

## Database Schema

### Users Table
- `id` - Primary key
- `username` - Unique username
- `email` - Unique email address
- `password_hash` - Hashed password
- `created_at` - Account creation timestamp

### Posts Table
- `id` - Primary key
- `user_id` - Foreign key to users table
- `title` - Post title
- `content` - Post content
- `tags` - Comma-separated tags
- `summary` - Auto-generated summary
- `reading_time` - Estimated reading time in minutes
- `created_at` - Post creation timestamp
- `updated_at` - Last update timestamp

### Post Versions Table
- `id` - Primary key
- `post_id` - Foreign key to posts table
- `title` - Previous title
- `content` - Previous content
- `updated_at` - Version timestamp

## Security Features

- **Password Hashing**: Uses Flask-Bcrypt for secure password storage
- **CSRF Protection**: All forms protected with Flask-WTF CSRF tokens
- **Session Management**: Secure session-based authentication
- **Input Validation**: Form validation on both client and server side
- **Authorization**: Users can only edit/delete their own posts

## Customization

### Adding New Features
1. Create new routes in the appropriate blueprint (`auth/routes.py` or `blog/routes.py`)
2. Add corresponding templates in the `templates/` directory
3. Update the navigation in `templates/base.html` if needed

### Styling
- Modify `static/style.css` for custom styling
- The app includes both light and dark themes
- Bootstrap 5 classes are used throughout for responsive design

### Database
- Currently uses SQLite for simplicity
- Can be easily migrated to PostgreSQL or MySQL by updating the connection in `models.py`

## Development Notes

- ECHO uses Flask blueprints for modular organization
- All forms use Flask-WTF for validation and CSRF protection
- The database is automatically initialized when the app starts
- The app includes comprehensive error handling and user feedback

## Deployment

### Supported Platforms
- **Heroku**: Create a Procfile with `web: gunicorn app:app`
- **Railway**: Deploy directly from GitHub
- **VPS**: Deploy with gunicorn using the provided configuration
- **Local Development**: Run with `python app.py`

### Environment Variables
Create a `.env` file with:
```env
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
```

## Development

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_app.py
```

### Code Quality
```bash
# Check code style
flake8 .

# Format code (if you have black installed)
black .
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is open source and available under the MIT License.

## Future Enhancements

- User profiles and avatars
- Comment system
- Post categories
- Rich text editor
- Image uploads
- Email notifications
- API endpoints
- Admin panel
- Post scheduling
- Social sharing