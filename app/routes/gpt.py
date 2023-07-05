import os
import openai
from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from ..utilities import is_logged_in, get_current_user

gpt_blueprint = Blueprint('gpt', __name__)

@gpt_blueprint.context_processor
def utility_functions():
    return {
        'is_logged_in': is_logged_in,
        'get_current_user': get_current_user
    }

@gpt_blueprint.route('/gpt')
def index():
    if not is_logged_in():
        return redirect(url_for('main.index'))
    return render_template('gpt.html')

@gpt_blueprint.route('/gpt/api', methods=['POST'])
def gpt_api():
    if not is_logged_in():
        return redirect(url_for('main.index'))
    prompt = request.form.get('prompt')
    openai.api_key = os.getenv('OPENAI_API_KEY')
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=4000,
        n=1,
        stop=None,
        temperature=0.5,
    )
    generated_text = response.choices[0].text.strip()
    return jsonify({'response': generated_text})
