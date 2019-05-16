# Used as an inpoint for a WSGI Application Server

from thefort.core import create_app
from waitress import serve

app = create_app()
serve(app, host="0.0.0.0", port=5006)
