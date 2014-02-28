import unittest
import nose
from flask_testing import TestCase
from nsweb.helpers.app_start import create_app
from tests.settings import SQLALCHEMY_DATABASE_URI, DEBUG, DATA_DIR, PICKLE_DATABASE

from json_model_wrapper import restless_json

create_app(SQLALCHEMY_DATABASE_URI, DEBUG)
from nsweb.core import app, db, manager
from nsweb.helpers import database_builder
from nsweb.models import studies
app=app()
db=db()
manager=manager()

class StudiesTest():
#     app=None
#     db=None
#     manager=None
    dataset={}

    def create_app(self):
        global dataset
        
        app.config['TESTING'] = True

        #register view
        import nsweb.studies.studies
        
        database_builder.init_database(db())
        dataset = database_builder.read_pickle_database(data_dir=DATA_DIR, pickle_database=PICKLE_DATABASE)

        app.run()
    
    def setUp(self):
        database_builder.init_database()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        
    def populate_database(self):
        database_builder.add_studies(db(),dataset, [], {}, {})
        
    class ModelTest(TestCase):
        
        def add_study(self):
            study = studies.Study(pmid=1, doi='Doi1.23', title='Title=Asdf_123*', journal='Journal of journal of journal of journal of Recursively', authors='asdf, qwerty, Z.X.C.V_123', year=1856, space='Random', table_num='101')
            peak = studies.Peak(x=1,y=2,z=3)
            study.peaks.append(peak)
            db.session.add(study)
            db.session.commit()
            assert study in studies.Study.query.all()
            assert peak in studies.Peak.query.all()
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
            assert study not in studies.Study.query.all()
            assert peak not in studies.Peak.query.all()
                
        def add_peaks_to_study(self):
            study = studies.Study(pmid=1, doi='Doi1.23', title='Title=Asdf_123*', journal='Journal of journal of journal of journal of Recursively', authors='asdf, qwerty, Z.X.C.V_123', year=1856, space='Random', table_num='101')
            db.session.add(study)
            peak1 = studies.Peak(x=1,y=2,z=3)
            peak2 = studies.Peak(x=1,y=2,z=3)
            peak3 = studies.Peak(x=4,y=5,z=6)
            study.peaks.append([peak1,peak2,peak3])
            db.session.commit()
            assert study in studies.Study.query.all()
            assert peak1 in studies.Peak.query.all()
            assert peak2 in studies.Peak.query.all()
            assert peak3 in studies.Peak.query.all()
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
            assert study not in studies.Study.query.all()
            assert peak1 not in studies.Peak.query.all()
            assert peak2 not in studies.Peak.query.all()
            assert peak3 not in studies.Peak.query.all()

        
    class ApiTest(TestCase):
        
        def Study(self):
            response = self.client.get('/api/studies')
            objects=studies.Study.query.all()
            self.assertEquals(response, restless_json(1, objects, 1))
        
        

if __name__ == "__main__":
    import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
