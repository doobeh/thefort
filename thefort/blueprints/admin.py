from flask import Blueprint, render_template
from thefort.models import Article, Tag, QuickLink, User


bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.route('/')
def home():
    return render_template('admin/home.html')


@bp.route('/add-article')
def article_create():
    return render_template('admin/article_create.html')
