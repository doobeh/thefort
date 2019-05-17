from flask import Blueprint, render_template
from thefort.models import Article, Tag


bp = Blueprint('frontend', __name__)


@bp.route('/')
def home():
    return render_template('index.html')


@bp.route('/a/<slug>')
def article(slug):
    a = Article.query.filter_by(slug=slug).first_or_404()
    return render_template('article.html', article=a)


@bp.route('/t/<tag>')
def tag(tag):
    t = Tag.query.filter_by(name=tag).first_or_404()
    return render_template('tag.html', tag=t)
