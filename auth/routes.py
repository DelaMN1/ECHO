from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from auth.forms import RegistrationForm, LoginForm
from models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.create(form.username.data, form.email.data, form.password.data):
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Username or email already exists.', 'error')
    return render_template('auth/register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_username(form.username.data)
        if user and User.verify_password(user['password_hash'], form.password.data):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Login successful!', 'success')
            return redirect(url_for('blog.index'))
        else:
            flash('Invalid username or password.', 'error')
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('blog.index'))