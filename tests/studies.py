from flask_testing import TestCase
from nsweb.core import create_app, db
from tests.settings import SQLALCHEMY_DATABASE_URI
from nsweb.settings import DEBUG
from flask.json import jsonify
from mock import patch, Mock, MagickMock
import unittest


class StudiesTest():
   class TestStudiesApi(TestCase):
        def create_app(self):
            (app,db,manager) = create_app(SQLALCHEMY_DATABASE_URI, DEBUG)
            app.config['TESTING'] = True
            return (app,db,manager)

# TODO: Create a seeder with initialize database to both pull random data and test initialize database
        def setUp(self):
            db.create_all()
    
        def tearDown(self):
            db.session.remove()
            db.drop_all()
            
        def some_json(serializable=''):
            return jsonify(serializable)
 

# if __name__ == "__main__":
#     import sys;sys.argv = ['', 'Test.testName']
#     flask_testing.unittest.main()
