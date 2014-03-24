from flask import Blueprint, render_template

from . import route

bp = Blueprint('home', __name__)


@route(bp, '/')
def index():
    """Returns the homepage."""
    return render_template('home.html')
