import flask_testing
import nsweb.models.studies
import nsweb.studies
import settings
from nsweb.core import create_app
from tests.settings import SQLALCHEMY_DATABASE_URI
from nsweb.settings import DEBUG

class Test(flask_testing.TestCase):

    def create_app(self):
        app = nsweb.core.create_app(SQLALCHEMY_DATABASE_URI, DEBUG)
        app.config['TESTING'] = True
        return app(self)
        pass

    def setUp(self):
        db.create_all()

    def tearDown(self):

        db.session.remove()
        db.drop_all()
    

# if __name__ == "__main__":
#     import sys;sys.argv = ['', 'Test.testName']
#     flask_testing.unittest.main()