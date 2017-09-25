from flask import Blueprint, render_template
from flask_login import login_required
from fernet import app

mod = Blueprint('intranet', __name__)

app.jinja_env.add_extension('jinja2.ext.do')


@mod.before_request
@login_required
def before_request():
    """Make sure user is logged in before request.

    This function does nothing, but the decorators do.
    """
    pass


@mod.route('/')
def index():
    """Show main intra page."""
    return render_template('intranet.html')
