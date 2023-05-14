from flask import Blueprint, render_template, request, redirect, url_for, session
from ..utilities import is_logged_in, get_current_user, get_recent_comments
from ..models import Comment
from .. import db
from markupsafe import escape

comment_blueprint = Blueprint('comment', __name__)

@comment_blueprint.context_processor
def utility_functions():
    return {
        'is_logged_in': is_logged_in,
        'get_current_user': get_current_user,
        'get_recent_comments': get_recent_comments
    }

@comment_blueprint.route('/comment')
def comment():
    return render_template('comment.html')



@comment_blueprint.route('/add_comment', methods=['POST'])
def add_comment():
    if not is_logged_in():
        return redirect(url_for('comment.login'))

    user = get_current_user()
    comment_text = request.form['comment']

    # Sanitize comment text to prevent XSS attacks
    sanitized_comment_text = escape(comment_text)

    new_comment = Comment(author=user.username, text=sanitized_comment_text, user_id=user.id)
    db.session.add(new_comment)
    db.session.commit()

    return redirect(url_for('comment.comment'))


@comment_blueprint.route('/delete_comment/<int:comment_id>', methods=['POST'])
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

    return redirect(url_for('comment.comment'))