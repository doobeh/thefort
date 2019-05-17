"""
    sample.py
    ~~~~~~~~~

    Loads the entire site with fake data, to let us really test the UI
    and flow of everything.
"""
import click
from flask.cli import AppGroup
from thefort.database import db
from flask import current_app
import os
import random
from datetime import datetime
from thefort.models import User, Role, Article, QuickLink, Tag
import factory
from faker import Faker


# Move these factories off to a separate file after hacking about is done:


class UserFactory(factory.Factory):
    username = factory.Faker('user_name')
    email = factory.Faker('email')
    password = factory.Faker('password')

    class Meta:
        model = User


class ArticleFactory(factory.Factory):
    title = factory.Faker('sentence')
    markdown = factory.Faker('text', max_nb_chars=2000)
    tags = 'abc,def,ghi'
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = Article


class QuickLinkFactory(factory.Factory):
    user = factory.SubFactory(UserFactory)
    markdown = factory.Faker('text', max_nb_chars=500)

    class Meta:
        model = QuickLink


sample_cli = AppGroup("sample")


@sample_cli.command("load")
def load():
    click.confirm(
        "This process wipes existing data (if any) and loads with fake data\n"
        "Are you sure?",
        abort=True,
    )

    db.drop_all()
    db.create_all()

    # create roles.

    roles = ["contributor", "author", "editor", "administrator", "owner"]
    for role in roles:
        r = Role(name=role)
        db.session.add(r)
    db.session.commit()
    roles = Role.query.all()

    # create users.

    for x in range(10):
        user = UserFactory.build()
        user.roles = random.sample(roles, 2)
        db.session.add(user)
    db.session.commit()
    users = User.query.all()

    for x in users:
        print(x, x.roles)

    # create a few tags to pick from, so we have lots of overlap.

    fake = Faker()
    fake.add_provider('lorem')
    tags = fake.words(nb=20, unique=True)

    # create articles allocated to random users, and with a random
    # sampling of tags for each.

    for x in range(200):
        article = ArticleFactory(
            user=random.choice(users),
            tags=",".join(random.sample(tags, random.randint(1, 5)))
        )

        print(article, article.user, article.tags)
        db.session.add(article)
    db.session.commit()

    # create quicklinks.

    for x in range(100):
        quick_link = QuickLinkFactory(
            user=random.choice(users),
        )
        db.session.add(quick_link)
    db.session.commit()

    ql = QuickLink.query.all()
    for x in ql:
        print(x, x.user)
