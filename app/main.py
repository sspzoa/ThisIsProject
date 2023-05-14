from flask import Blueprint, render_template
from .utilities import is_logged_in, get_current_user, get_recent_comments

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
