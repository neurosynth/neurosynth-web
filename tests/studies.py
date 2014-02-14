from flask import Flask
import flask_testing

class Test(flask_testing.TestCase):


    def create_app(self):
        app = Flask(__name__)
        app.config['TESTING'] = True
        return app


    def tearDown(self):
        pass


    def isJSON(self):
        pass
    
    def isPaging(self):
        pass
    

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    flask_testing.unittest.main()