#testing modules
import unittest
#import nose #we use nose, but we don't need 
from mock import MagicMock, Mock, patch
from flask_testing import TestCase

from nsweb.helpers.app_start import create_app
from tests.settings import SQLALCHEMY_DATABASE_URI, DEBUG, DEBUG_WITH_APTANA, DATA_DIR, PICKLE_DATABASE


create_app(SQLALCHEMY_DATABASE_URI, DEBUG)
from nsweb.core import app, db, apimanager
from nsweb.helpers import database_builder
from nsweb.models import studies


class Test(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass

    def setup_module(self):
        pass
    
    def teardown_module(self):
        pass

    def test_create_app_creates_app(self):
        '''Create_app needs to create a flask 'app' instance, the 'db' instance, and a flask-restless 'apimanager' instance'''
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()