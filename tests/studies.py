import unittest

from flask.json import jsonify
from flask_testing import TestCase

import nsweb.core.create_app
from tests.settings import SQLALCHEMY_DATABASE_URI, DEBUG
from nsweb.helpers import database_builder
from nsweb.models import studies

class StudiesTest():
    app=None, db=None, manager=None
    
    def create_app(self):
            global app, db, manager
            (app,db,manager) = nsweb.core.create_app(SQLALCHEMY_DATABASE_URI, DEBUG)
            app.config['TESTING'] = True
            return (app,db,manager)
    
    def setUp(self):
            database_builder.init_database()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        
    def populate_database(self):
        dataset = database_builder.read_pickle_database(SQLALCHEMY_DATABASE_URI)
        database_builder.add_studies(dataset, ([], {}), {})
        
    class ModelTest(TestCase):
        
        def add_study(self):
            study = studies.Study(pmid=1, doi='Doi1.23', title='Title=Asdf_123*', journal='Journal of journal of journal of journal of Recursively', authors='asdf, qwerty, Z.X.C.V_123', year=1856, space='Random', table_num='101')
            db.session.add(study)
            peak = studies.Peak(x=1,y=2,z=3)
            study.peaks.append(peak)
            db.session.commit()
            assert study in db.session
            assert peak in db.session
            db.session.delete(study)
            db.session.commit()
                
        def remove_study(self):
            study = studies.Study(pmid=1, doi='Doi1.23', title='Title=Asdf_123*', journal='Journal of journal of journal of journal of Recursively', authors='asdf, qwerty, Z.X.C.V_123', year=1856, space='Random', table_num='101')
            db.session.add(study)
            peak = studies.Peak(x=1,y=2,z=3)
            study.peaks.append(peak)
            db.session.commit()
            db.session.delete(study)
            db.session.commit()
            assert study not in db.session
            assert peak not in db.session
                
        def add_peaks_to_study(self):
            study = studies.Study(pmid=1, doi='Doi1.23', title='Title=Asdf_123*', journal='Journal of journal of journal of journal of Recursively', authors='asdf, qwerty, Z.X.C.V_123', year=1856, space='Random', table_num='101')
            db.session.add(study)
            peak1 = studies.Peak(x=1,y=2,z=3)
            peak2 = studies.Peak(x=1,y=2,z=3)
            peak3 = studies.Peak(x=4,y=5,z=6)
            study.peaks.append([peak1,peak2,peak3])
            db.session.commit()
            assert study in db.session
            assert peak1 in db.session
            assert peak2 in db.session
            assert peak3 in db.session
            db.session.delete(study)
            db.session.commit()
                
        def remove_multipeak_study(self):
            study = studies.Study(pmid=1, doi='Doi1.23', title='Title=Asdf_123*', journal='Journal of journal of journal of journal of Recursively', authors='asdf, qwerty, Z.X.C.V_123', year=1856, space='Random', table_num='101')
            db.session.add(study)
            peak1 = studies.Peak(x=1,y=2,z=3)
            peak2 = studies.Peak(x=1,y=2,z=3)
            peak3 = studies.Peak(x=4,y=5,z=6)
            study.peaks.append([peak1,peak2,peak3])
            db.session.commit()
            db.session.delete(study)
            db.session.commit()
            assert study not in db.session
            assert peak1 not in db.session
            assert peak2 not in db.session
            assert peak3 not in db.session

        
    class ApiTest(TestCase):
        
        @app.route('/api/studies')
        def some_json(self):
            return jsonify()
        
        

# if __name__ == "__main__":
#     import sys;sys.argv = ['', 'Test.testName']
#     flask_testing.unittest.main()
