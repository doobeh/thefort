from flask import url_for
from werkzeug.routing import BuildError
from mistune import markdown


def usd_filter(value):
    return "${:,.2f}".format(float(value / 100.0))


def decimal_places(value, places=2):
    return f"{value:.{places}f}"


def zfill(value, places=15):
    return str(value).zfill(places)


def permalink(function):
    """ Shortcut to access a url from a SQLAlchemy model easily"""

    def inner(*args, **kwargs):
        endpoint, values = function(*args, **kwargs)
        try:
            return url_for(endpoint, **values)
        except BuildError:
            return

    return inner


def process_markdown(md):
    """ This will process md into html-- and then
    parse it for embed tags to also turn into the
    html representations"""

    # Todo: ui isn't actually generating md yet...

    return md
