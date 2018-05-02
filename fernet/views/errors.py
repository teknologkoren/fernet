from flask import render_template
from jinja2.exceptions import TemplateNotFound
from fernet import app


@app.errorhandler(403)
@app.errorhandler(404)
def handle_error(e):
    try:
        response = render_template('errors/{}.html'.format(e.code))
    except TemplateNotFound:
        response = e
    return response, e.code


@app.errorhandler(500)
def handle_server_error(e):
    """Handle Internal Server Errors.

    Handlers for 500 are passed the uncaught exception instead of
    HTTPException (though documentation says "as well", but that
    does not seem to be the case).
    """
    return render_template('errors/500.html'), 500
