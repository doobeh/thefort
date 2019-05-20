from flask import Blueprint, render_template, request, jsonify, abort, redirect, url_for
from thefort.models import Article, Tag, QuickLink, User, Category
from flask_security import login_required
from flask_security import current_user
from thefort.database import db
from thefort.forms.admin import (
    ArticleCreateForm,
    QuickLinkCreateForm,
    NavigationCreateForm,
)
from thefort.utils import process_markdown


bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.route("/")
@login_required
def home():
    return render_template("admin/home.html")


@bp.route("/navigation")
@login_required
def navigation():
    c = Category.query.order_by(Category.title.asc()).all()
    return render_template("admin/navigation.html", categories=c)


@bp.route("/add-navigation", methods=['post', 'get'])
@login_required
def navigation_create():
    form = NavigationCreateForm()
    if form.validate_on_submit():
        cat = Category()
        existing_tags = {x.name for x in Tag.query.all()}
        tags = {x for x in form.tags.data.strip(",; ").split(",")}
        matched_tags = tags.intersection(existing_tags)
        cat.tags = list(matched_tags)
        cat.title = form.title.data
        print(cat.title)
        db.session.add(cat)
        db.session.commit()
        return redirect(url_for("admin.navigation"))
    return render_template("admin/navigation_create.html")


@bp.route("/edit-navigation/<int:ref>", methods=["post", "get"])
@login_required
def navigation_edit(ref):
    category = Category.query.filter_by(id=ref).first_or_404()
    form = NavigationCreateForm()
    if form.validate_on_submit():
        title = form.title.data
        category.title = title
        existing_tags = {x.name for x in Tag.query.all()}
        tags = {x for x in form.tags.data.strip(",; ").split(",")}
        matched_tags = tags.intersection(existing_tags)
        category.tags = list(matched_tags)
        db.session.commit()
        return redirect(url_for('admin.navigation'))
    return render_template("admin/navigation_edit.html", form=form, category=category)


@bp.route("/set-navigation", methods=["post", "get"])
@login_required
def navigation_set():
    if not request.is_json:
        return abort(400)
    data = request.json
    status = data.get("status", True)  # default to enabling articles.
    reference = data.get("ref")
    c = Category.query.filter_by(id=reference).first()
    if c:
        c.visible = status
        db.session.commit()
        return jsonify(status=True, ref=reference)
    return abort(404)


@bp.route("/add-article", methods=["post", "get"])
@login_required
def article_create():
    form = ArticleCreateForm()
    if form.validate_on_submit():
        intro = form.intro.data
        title = form.title.data
        content = form.content.data
        tags = form.tags.data
        a = Article(
            title=title, content=content, intro=intro, user=current_user, tags=tags
        )
        db.session.add(a)
        db.session.commit()
        return jsonify(message="success")
    return render_template("admin/article_create.html", form=form)


@bp.route("/edit-article/<int:ref>", methods=["post", "get"])
@login_required
def article_edit(ref):
    article = Article.query.filter_by(id=ref).first_or_404()
    form = ArticleCreateForm()
    if form.validate_on_submit():
        intro = form.intro.data
        title = form.title.data
        content = form.content.data
        tags = form.tags.data
        print(tags)

        article.content_markdown = content
        article.content = process_markdown(content)
        article.intro_markdown = intro
        article.intro = process_markdown(intro)
        article.title = title
        article.tags_csv = tags

        db.session.commit()
        return jsonify(message="success")
    return render_template("admin/article_edit.html", form=form, article=article)


@bp.route("/add-article/added")
@login_required
def article_edited():
    return render_template("admin/article_edited.html")


@bp.route("/add-article/added")
@login_required
def article_created():
    return render_template("admin/article_created.html")


@bp.route("/set-article", methods=["post", "get"])
@login_required
def article_set():
    if not request.is_json:
        return abort(400)
    data = request.json
    status = data.get("status", True)  # default to enabling articles.
    reference = data.get("ref")
    a = Article.query.filter_by(id=reference).first()
    if a:
        a.published = status
        db.session.commit()
        return jsonify(status=True, ref=reference)
    return abort(404)


@bp.route("/add-quicklink", methods=["post", "get"])
@login_required
def quicklink_create():
    form = QuickLinkCreateForm()
    if form.validate_on_submit():
        ql = QuickLink(current_user, form.content.data)
        db.session.add(ql)
        db.session.commit()
        return jsonify(message="success")
    return render_template("admin/quicklink_create.html", form=form)


@bp.route("/add-quicklink/added")
@login_required
def quicklink_created():
    return render_template("admin/quicklink_created.html")
