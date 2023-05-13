from flask import Blueprint, render_template, request, redirect, url_for, session
from .utilities import is_logged_in, get_current_user, get_recent_comments
from .models import User, Comment
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from markupsafe import escape
import re

main_blueprint = Blueprint('main', __name__)

@main_blueprint.context_processor
def utility_functions():
    return {
        'is_logged_in': is_logged_in,
        'get_current_user': get_current_user,
        'get_recent_comments': get_recent_comments
    }

@main_blueprint.route('/')
def index():
    return render_template('index.html')


@main_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            if user.username == "admin":
                user.is_admin = True
                db.session.commit()
            return redirect(url_for('main.index'))
        else:
            error_msg = 'Invalid username or password. Please try again.'
            return render_template('login.html', error=error_msg)

    return render_template('login.html')


@main_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm-password']

        if not re.match("^[a-zA-Z0-9_-]{3,20}$", username):
            error_msg = 'Username must be between 3 to 20 characters long and can only contain alphanumeric characters, hyphens, and underscores.'
            return render_template('register.html', error=error_msg)

        if password != confirm_password:
            error_msg = 'Passwords do not match. Please try again.'
            return render_template('register.html', error=error_msg)

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            error_msg = 'Username already exists. Please try another one.'
            return render_template('register.html', error=error_msg)

        hashed_password = generate_password_hash(password)

        user = User(username=username, password=hashed_password)
        db.session.add(user)
        try:
            db.session.commit()
            return redirect(url_for('main.login'))
        except Exception as e:
            db.session.rollback()
            error_msg = 'An error occurred while registering. Please try again.'
            return render_template('register.html', error=error_msg)
    return render_template('register.html')


@main_blueprint.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('main.index'))


@main_blueprint.route('/profile', methods=['GET', 'POST'])
def profile():
    if not is_logged_in():
        return redirect(url_for('main.login'))

    user = get_current_user()

    if request.method == 'POST':
        current_password = request.form['current-password']
        new_password = request.form['password']
        confirm_password = request.form['confirm-password']

        if not check_password_hash(user.password, current_password):
            error_msg = 'Current password is incorrect. Please try again.'
            return render_template('profile.html', user=user, error=error_msg)

        if new_password != confirm_password:
            error_msg = 'Passwords do not match. Please try again.'
            return render_template('profile.html', user=user, error=error_msg)

        user.password = generate_password_hash(new_password)
        db.session.commit()
        success_msg = 'Password successfully updated.'
        return render_template('profile.html', user=user, success=success_msg)

    return render_template('profile.html', user=user)


@main_blueprint.route('/delete_account', methods=['POST'])
def delete_account():
    if not is_logged_in():
        return redirect(url_for('main.login'))

    user = get_current_user()

    db.session.delete(user)
    db.session.commit()

    session.pop('user_id', None)

    return redirect(url_for('main.index'))

@main_blueprint.route('/comment')
def comment():
    return render_template('comment.html')



@main_blueprint.route('/add_comment', methods=['POST'])
def add_comment():
    if not is_logged_in():
        return redirect(url_for('main.login'))

    user = get_current_user()
    comment_text = request.form['comment']

    # Sanitize comment text to prevent XSS attacks
    sanitized_comment_text = escape(comment_text)

    new_comment = Comment(author=user.username, text=sanitized_comment_text, user_id=user.id)
    db.session.add(new_comment)
    db.session.commit()

    return redirect(url_for('main.comment'))


@main_blueprint.route('/delete_comment/<int:comment_id>', methods=['POST'])
def delete_comment(comment_id):
    if not is_logged_in():
        return redirect(url_for('login'))

    comment = Comment.query.get(comment_id)

    if comment:
        if session.get('user_id') == comment.user_id:
            db.session.delete(comment)
            db.session.commit()
        if get_current_user().is_admin:
            db.session.delete(comment)
            db.session.commit()

    return redirect(url_for('main.comment'))