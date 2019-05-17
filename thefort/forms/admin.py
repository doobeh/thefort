from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField


class ArticleCreateForm(FlaskForm):
    title = StringField('Title')
    intro = TextAreaField('Intro')
    content = TextAreaField('Content')
    tags = StringField('Tags')
