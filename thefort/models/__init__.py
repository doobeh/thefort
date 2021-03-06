from thefort.database import db
from flask_security import UserMixin, RoleMixin
from flask_security.utils import hash_password
from datetime import datetime
from slugify import slugify
from thefort.utils import permalink, process_markdown
import readtime


roles_users = db.Table(
    "roles_users",
    db.Column("user_id", db.Integer(), db.ForeignKey("user.id"), index=True),
    db.Column("role_id", db.Integer(), db.ForeignKey("role.id"), index=True),
)


class User(db.Model, UserMixin):
    """ User Representation
    Relationships:
    -   A user can have potentially many posts (Specified on `Post` class)
    -   Can comment on many posts. (Specified on `Comment` class)
    -   Has potentially many roles.
    """

    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), index=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(), nullable=False)
    display_name = db.Column(db.String, default="", nullable=False)
    active = db.Column(db.Boolean(), default=False, nullable=False)
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship(
        "Role", secondary=roles_users, backref=db.backref("users", lazy="dynamic")
    )

    def __init__(
        self,
        username,
        password,
        email,
        roles=None,
        active=None,
        confirmed_at=None,
        display_name=None,
    ):
        self.username = username
        self.password = hash_password(password)
        if roles:
            self.roles = roles
        self.active = active
        self.confirmed_at = confirmed_at
        self.email = email
        if display_name:
            self.display_name = display_name
        else:
            self.display_name = username

    @property
    def is_admin(self):
        return "admin" in [x.name for x in self.roles]

    @permalink
    def absolute_url(self):
        return "frontend.user", {"username": self.username}

    def __repr__(self):
        return self.username


class Role(db.Model, RoleMixin):
    __tablename__ = "role"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, index=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name


tags = db.Table(
    "tags",
    db.Column("tag_id", db.Integer, db.ForeignKey("tag.id")),
    db.Column("article_id", db.Integer, db.ForeignKey("article.id")),
)


class Tag(db.Model):
    __tablename__ = "tag"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))

    @permalink
    def absolute_url(self):
        return "frontend.tag", {"tag": self.name}

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "{name}".format(name=self.name)


class Article(db.Model):
    __tablename__ = "article"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, index=True)
    slug = db.Column(db.String(100))
    intro_markdown = db.Column(db.Text)
    intro = db.Column(db.Text)
    content_markdown = db.Column(db.Text)
    content = db.Column(db.Text)
    last_processed = db.Column(db.DateTime)
    created = db.Column(db.DateTime, default=datetime.now)
    published = db.Column(db.Boolean, default=True)
    tags = db.relationship(
        "Tag", secondary=tags, backref=db.backref("articles", lazy="dynamic")
    )
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = db.relationship(
        "User", backref=db.backref("articles", lazy="dynamic", order_by=created.desc())
    )

    @property
    def reading_time(self):
        return readtime.of_html(self.content).text

    def __init__(self, title, content, intro, tags, user):
        self.title = title
        self.slug = slugify(title)
        self.intro_markdown = intro
        self.content_markdown = content
        self.content = process_markdown(content)
        self.intro = process_markdown(intro)
        self.user = user

        for tag in tags.split(","):
            t = Tag.query.filter_by(name=tag.strip()).first()
            if len(tag):
                if t:
                    self.tags.append(t)
                else:
                    self.tags.append(Tag(tag.strip()))

    def get_tags_csv(self):
        return ",".join(x.name for x in self.tags)

    def set_tags_csv(self, value):
        new = (x for x in value.strip(",; ").split(","))
        self.tags = []
        for tag in new:
            existing_tag = Tag.query.filter_by(name=tag).first()
            if existing_tag is not None:
                self.tags.append(existing_tag)
            else:
                t = Tag(tag.strip())
                self.tags.append(t)
        db.session.commit()

    tags_csv = property(get_tags_csv, set_tags_csv)

    @permalink
    def absolute_url(self):
        return "frontend.article", {"slug": self.slug}

    def __repr__(self):
        return f"{self.title}"


class QuickLink(db.Model):
    __tablename__ = "quick_link"
    id = db.Column(db.Integer, primary_key=True)
    markdown = db.Column(db.Text)
    content = db.Column(db.Text)
    published = db.Column(db.Boolean, default=True)
    created = db.Column(db.DateTime, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = db.relationship("User", backref=db.backref("quick_links", lazy="dynamic", order_by=created.desc()))

    def __init__(self, user, markdown):
        self.markdown = markdown
        self.user = user
        self.content = process_markdown(markdown)

    def __repr__(self):
        return f"{self.content}"


class Category(db.Model):
    """Handles what gets displayed on the main menu"""

    __tablename__ = "category"
    id = db.Column(db.Integer, primary_key=True)
    visible = db.Column(db.Boolean, default=True)
    title = db.Column(db.String)
    tags = db.Column(db.JSON)

    @permalink
    def absolute_url(self):
        return "frontend.category", {"title": self.title}
