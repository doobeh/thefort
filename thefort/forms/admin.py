from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField


class ArticleCreateForm(FlaskForm):
    title = StringField("Title")
    intro = TextAreaField("Intro")
    content = TextAreaField("Content")
    tags = StringField("Tags")


class ArticleEditForm(ArticleCreateForm):
    id = IntegerField("Reference")


class QuickLinkCreateForm(FlaskForm):
    content = TextAreaField("Content")


class NavigationCreateForm(FlaskForm):
    title = StringField("Title")
    tags = StringField("Tags")
