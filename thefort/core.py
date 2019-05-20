from werkzeug.utils import find_modules, import_string
from flask import Flask
from .database import db
from .cli import core_cli, db_cli, user_cli
from .cli.sample import sample_cli
from .models import User, Role
from flask_security import Security, SQLAlchemyUserDatastore
from .utils import usd_filter, zfill, decimal_places
from flask_wtf.csrf import CSRFProtect


def create_app(config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="default",
        SQLALCHEMY_DATABASE_URI="postgresql://localhost/thefort",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SECURITY_PASSWORD_SALT="NOT-SECURE-CHANGE-ME",
        SECURITY_USER_IDENTITY_ATTRIBUTES="username",
    )

    # app.config.from_object('origin.settings')
    app.config.from_pyfile("settings.cfg", silent=True)
    if config:
        app.config.from_pyfile(config)

    register_database(app)
    register_security(app)
    register_cli(app)
    register_blueprints(app)
    register_jinja_filters(app)
    register_csrf(app)
    return app


def register_csrf(app):
    csrf = CSRFProtect()
    csrf.init_app(app)
    return None


def register_security(app):
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security = Security()
    security.init_app(app, user_datastore)
    return None


def register_database(app):
    db.init_app(app)
    return None


def register_blueprints(app):
    """Register all blueprint modules
    Reference: Armin Ronacher, "Flask for Fun and for Profit" PyBay 2016.
    """
    for name in find_modules("thefort.blueprints"):
        mod = import_string(name)
        if hasattr(mod, "bp"):
            app.register_blueprint(mod.bp)
    return None


def register_cli(app):
    app.cli.add_command(db_cli)
    app.cli.add_command(core_cli)
    app.cli.add_command(user_cli)
    app.cli.add_command(sample_cli)


def register_jinja_filters(app):
    """ Helpful filters that we can access from our templates """
    app.jinja_env.filters["usd"] = usd_filter
    app.jinja_env.filters["dp"] = decimal_places
    app.jinja_env.filters["zfill"] = zfill
