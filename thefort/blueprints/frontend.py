from flask import Blueprint, render_template
from thefort.models import Article, Tag, QuickLink, User


bp = Blueprint("frontend", __name__)


@bp.route("/")
def home():
    articles = Article.query.order_by(Article.created.desc()).limit(10)
    quick_links = QuickLink.query.order_by(QuickLink.created.desc()).limit(10)
    return render_template("index.html", articles=articles, quick_links=quick_links)


@bp.route("/a/<slug>")
def article(slug):
    a = Article.query.filter_by(slug=slug).first_or_404()
    return render_template("article.html", article=a)


@bp.route("/u/<username>")
def user(username):
    u = User.query.filter_by(username=username).first_or_404()
    return render_template("user.html", user=u)


@bp.route("/t/<tag>")
def tag(tag):
    t = Tag.query.filter_by(name=tag).first_or_404()
    return render_template("tag.html", tag=t)
