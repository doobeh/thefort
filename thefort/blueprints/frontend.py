from flask import Blueprint, render_template
from thefort.models import Article, Tag, QuickLink, User, Category


bp = Blueprint("frontend", __name__)


@bp.context_processor
def inject_data():
    return {
        "navigation": Category.query.filter_by(visible=True)
        .order_by(Category.title.asc())
        .all()
    }


@bp.route("/")
def home():
    articles = (
        Article.query.filter_by(published=True)
        .order_by(Article.created.desc())
        .limit(10)
    )
    quick_links = QuickLink.query.order_by(QuickLink.created.desc()).limit(10)
    return render_template("index.html", articles=articles, quick_links=quick_links)


@bp.route("/about")
def about():
    return render_template("about.html")


@bp.route("/a/<slug>")
def article(slug):
    a = Article.query.filter_by(slug=slug, published=True).first_or_404()
    return render_template("article.html", article=a)


@bp.route("/c/<title>")
def category(title):
    c = Category.query.filter_by(title=title).first_or_404()
    a = (
        Article.query.join(Article.tags)
        .filter(Tag.name.in_(c.tags))
        .order_by(Article.created.desc())
        .all()
    )
    return render_template("category.html", articles=a, category=c)


@bp.route("/u/<username>")
def user(username):
    u = User.query.filter_by(username=username).first_or_404()
    return render_template("user.html", user=u)


@bp.route("/t/<tag>")
def tag(tag):
    t = Tag.query.filter_by(name=tag).first_or_404()
    return render_template("tag.html", tag=t)
