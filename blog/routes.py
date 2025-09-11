from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from functools import wraps
from blog.forms import PostForm
from models import Post, PostVersion, get_db_connection

blog_bp = Blueprint('blog', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@blog_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    posts, total = Post.get_all(page=page, per_page=10)
    tag_cloud = Post.get_tag_cloud()
    
    # Calculate pagination info
    total_pages = (total + 9) // 10  # Ceiling division
    has_prev = page > 1
    has_next = page < total_pages
    
    return render_template('blog/index.html', 
                         posts=posts, 
                         tag_cloud=tag_cloud,
                         page=page,
                         total_pages=total_pages,
                         has_prev=has_prev,
                         has_next=has_next)

@blog_bp.route('/post/<int:post_id>')
def view_post(post_id):
    post = Post.get_by_id(post_id)
    if not post:
        flash('Post not found.', 'error')
        return redirect(url_for('blog.index'))
    
    versions = PostVersion.get_by_post_id(post_id)
    return render_template('blog/post.html', post=post, versions=versions)

@blog_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        post_id = Post.create(
            session['user_id'],
            form.title.data,
            form.content.data,
            form.tags.data
        )
        flash('Post created successfully!', 'success')
        return redirect(url_for('blog.view_post', post_id=post_id))
    return render_template('blog/create.html', form=form)

@blog_bp.route('/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.get_by_id(post_id)
    if not post:
        flash('Post not found.', 'error')
        return redirect(url_for('blog.index'))
    
    # Check if user owns the post
    if post['user_id'] != session['user_id']:
        flash('You can only edit your own posts.', 'error')
        return redirect(url_for('blog.index'))
    
    form = PostForm()
    if form.validate_on_submit():
        Post.update(post_id, form.title.data, form.content.data, form.tags.data)
        flash('Post updated successfully!', 'success')
        return redirect(url_for('blog.view_post', post_id=post_id))
    elif request.method == 'GET':
        form.title.data = post['title']
        form.content.data = post['content']
        form.tags.data = post['tags']
    
    return render_template('blog/edit.html', form=form, post=post)

@blog_bp.route('/delete/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.get_by_id(post_id)
    if not post:
        flash('Post not found.', 'error')
        return redirect(url_for('blog.index'))
    
    # Check if user owns the post
    if post['user_id'] != session['user_id']:
        flash('You can only delete your own posts.', 'error')
        return redirect(url_for('blog.index'))
    
    Post.delete(post_id)
    flash('Post deleted successfully!', 'success')
    return redirect(url_for('blog.index'))

@blog_bp.route('/search')
def search():
    query = request.args.get('query', '')
    if query:
        posts = Post.search(query)
        return render_template('blog/search.html', posts=posts, query=query)
    return redirect(url_for('blog.index'))

@blog_bp.route('/tags/<tag>')
def posts_by_tag(tag):
    posts = Post.get_by_tag(tag)
    return render_template('blog/tag.html', posts=posts, tag=tag)

@blog_bp.route('/digest')
def weekly_digest():
    weekly_posts = Post.get_weekly_digest()
    return render_template('blog/digest.html', weekly_posts=weekly_posts)

@blog_bp.route('/my-posts')
@login_required
def my_posts():
    """View current user's posts"""
    conn = get_db_connection()
    posts = conn.execute(
        '''SELECT p.*, u.username 
           FROM posts p 
           JOIN users u ON p.user_id = u.id 
           WHERE p.user_id = ? 
           ORDER BY p.created_at DESC''',
        (session['user_id'],)
    ).fetchall()
    conn.close()
    
    return render_template('blog/my_posts.html', posts=posts)
