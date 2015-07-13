from pytest import fixture
from nsweb.core import create_app, app
from nsweb.core import db as database


@fixture
def db(scope='session'):
    create_app(debug=True, test=True)
    database.app = app  # Set DB context
    database.drop_all()
    database.create_all()
    return database
