from flask import current_app, Blueprint, render_template

bp = Blueprint('frontend', __name__)


@bp.route('/')
def home():
    return render_template('index.html')
