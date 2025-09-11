import sqlite3
from datetime import datetime
from flask_bcrypt import Bcrypt
import os

bcrypt = Bcrypt()

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect('blog.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with tables"""
    conn = get_db_connection()
    
    # Users table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Posts table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER REFERENCES users(id),
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            tags TEXT,
            summary TEXT,
            reading_time INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Post versions table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS post_versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER REFERENCES posts(id),
            title TEXT,
            content TEXT,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

class User:
    @staticmethod
    def create(username, email, password):
        """Create a new user"""
        conn = get_db_connection()
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        
        try:
            conn.execute(
                'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                (username, email, password_hash)
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    @staticmethod
    def get_by_username(username):
        """Get user by username"""
        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM users WHERE username = ?', (username,)
        ).fetchone()
        conn.close()
        return user
    
    @staticmethod
    def get_by_id(user_id):
        """Get user by ID"""
        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM users WHERE id = ?', (user_id,)
        ).fetchone()
        conn.close()
        return user
    
    @staticmethod
    def verify_password(password_hash, password):
        """Verify password"""
        return bcrypt.check_password_hash(password_hash, password)

class Post:
    @staticmethod
    def create(user_id, title, content, tags):
        """Create a new post"""
        conn = get_db_connection()
        
        # Generate summary (first 2-3 sentences)
        sentences = content.split('. ')
        summary = '. '.join(sentences[:2]) + '.' if len(sentences) > 1 else content[:200] + '...'
        
        # Calculate reading time (words per minute = 200)
        word_count = len(content.split())
        reading_time = max(1, word_count // 200)
        
        cursor = conn.execute(
            '''INSERT INTO posts (user_id, title, content, tags, summary, reading_time) 
               VALUES (?, ?, ?, ?, ?, ?)''',
            (user_id, title, content, tags, summary, reading_time)
        )
        conn.commit()
        post_id = cursor.lastrowid
        conn.close()
        return post_id
    
    @staticmethod
    def get_all(page=1, per_page=10):
        """Get all posts with pagination"""
        conn = get_db_connection()
        offset = (page - 1) * per_page
        
        posts = conn.execute(
            '''SELECT p.*, u.username 
               FROM posts p 
               JOIN users u ON p.user_id = u.id 
               ORDER BY p.created_at DESC 
               LIMIT ? OFFSET ?''',
            (per_page, offset)
        ).fetchall()
        
        total = conn.execute('SELECT COUNT(*) FROM posts').fetchone()[0]
        conn.close()
        
        return posts, total
    
    @staticmethod
    def get_by_id(post_id):
        """Get post by ID"""
        conn = get_db_connection()
        post = conn.execute(
            '''SELECT p.*, u.username 
               FROM posts p 
               JOIN users u ON p.user_id = u.id 
               WHERE p.id = ?''',
            (post_id,)
        ).fetchone()
        conn.close()
        return post
    
    @staticmethod
    def update(post_id, title, content, tags):
        """Update a post"""
        conn = get_db_connection()
        
        # Save current version to post_versions
        current_post = conn.execute(
            'SELECT title, content FROM posts WHERE id = ?', (post_id,)
        ).fetchone()
        
        if current_post:
            conn.execute(
                'INSERT INTO post_versions (post_id, title, content) VALUES (?, ?, ?)',
                (post_id, current_post['title'], current_post['content'])
            )
        
        # Generate new summary and reading time
        sentences = content.split('. ')
        summary = '. '.join(sentences[:2]) + '.' if len(sentences) > 1 else content[:200] + '...'
        word_count = len(content.split())
        reading_time = max(1, word_count // 200)
        
        conn.execute(
            '''UPDATE posts 
               SET title = ?, content = ?, tags = ?, summary = ?, reading_time = ?, updated_at = CURRENT_TIMESTAMP 
               WHERE id = ?''',
            (title, content, tags, summary, reading_time, post_id)
        )
        conn.commit()
        conn.close()
        return True
    
    @staticmethod
    def delete(post_id):
        """Delete a post"""
        conn = get_db_connection()
        conn.execute('DELETE FROM posts WHERE id = ?', (post_id,))
        conn.execute('DELETE FROM post_versions WHERE post_id = ?', (post_id,))
        conn.commit()
        conn.close()
        return True
    
    @staticmethod
    def search(query):
        """Search posts by title or content"""
        conn = get_db_connection()
        posts = conn.execute(
            '''SELECT p.*, u.username 
               FROM posts p 
               JOIN users u ON p.user_id = u.id 
               WHERE p.title LIKE ? OR p.content LIKE ? 
               ORDER BY p.created_at DESC''',
            (f'%{query}%', f'%{query}%')
        ).fetchall()
        conn.close()
        return posts
    
    @staticmethod
    def get_by_tag(tag):
        """Get posts by tag"""
        conn = get_db_connection()
        posts = conn.execute(
            '''SELECT p.*, u.username 
               FROM posts p 
               JOIN users u ON p.user_id = u.id 
               WHERE p.tags LIKE ? 
               ORDER BY p.created_at DESC''',
            (f'%{tag}%',)
        ).fetchall()
        conn.close()
        return posts
    
    @staticmethod
    def get_weekly_digest():
        """Get posts grouped by week"""
        conn = get_db_connection()
        posts = conn.execute(
            '''SELECT p.*, u.username, 
               strftime('%Y-%W', p.created_at) as week
               FROM posts p 
               JOIN users u ON p.user_id = u.id 
               ORDER BY p.created_at DESC'''
        ).fetchall()
        conn.close()
        
        # Group by week
        weekly_posts = {}
        for post in posts:
            week = post['week']
            if week not in weekly_posts:
                weekly_posts[week] = []
            weekly_posts[week].append(post)
        
        return weekly_posts
    
    @staticmethod
    def get_tag_cloud():
        """Get tag frequency for tag cloud"""
        conn = get_db_connection()
        posts = conn.execute('SELECT tags FROM posts WHERE tags IS NOT NULL AND tags != ""').fetchall()
        conn.close()
        
        tag_counts = {}
        for post in posts:
            if post['tags']:
                tags = [tag.strip() for tag in post['tags'].split(',')]
                for tag in tags:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        return tag_counts

class PostVersion:
    @staticmethod
    def get_by_post_id(post_id):
        """Get all versions of a post"""
        conn = get_db_connection()
        versions = conn.execute(
            'SELECT * FROM post_versions WHERE post_id = ? ORDER BY updated_at DESC',
            (post_id,)
        ).fetchall()
        conn.close()
        return versions