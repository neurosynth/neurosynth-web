import flask_testing
import nsweb.models.studies
import nsweb.studies
import settings

class Test(flask_testing.TestCase):

    def create_app(self):
        app = Flask(__name__)
        app.config['TESTING'] = True
        return app


    def create_app(self):
        # pass in test configuration
        return create_app(self)

    def setUp(self):
        db.create_all()

    def tearDown(self):

        db.session.remove()
        db.drop_all()
    

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    flask_testing.unittest.main()