from flask import session
from .models import User, Comment

def is_logged_in():
    return 'user_id' in session

def get_current_user():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        return user
    return None

def get_recent_comments():
    comments = Comment.query.order_by(Comment.date.desc()).all()
    return comments
