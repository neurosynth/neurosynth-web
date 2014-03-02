from flask_testing import TestCase, unittest
from flask import request

import re

from nsweb.helpers.app_start import create_app
from tests.settings import SQLALCHEMY_DATABASE_URI, DEBUG, DATA_DIR, PICKLE_DATABASE, FEATURE_DATABASE

from json_model_wrapper import restless_json
from nsweb.models.features import Frequency

create_app(SQLALCHEMY_DATABASE_URI, DEBUG)
from nsweb.core import app, db, apimanager
from nsweb.helpers import database_builder
from nsweb.models import studies, features
app=app()
db=db()
apimanager=apimanager()

class StudiesTest():
#     app=None
#     db=None
#     apimanager=None
    dataset={}
    feature_list=[]
    feature_data={}

    def setUp(self):
        global dataset, feature_list, feature_data
        
        app.config['TESTING'] = True

        #register view
        import nsweb.features.features
        
        database_builder.init_database(db())
        dataset = database_builder.read_pickle_database(data_dir=DATA_DIR, pickle_database=PICKLE_DATABASE)
        (feature_list,feature_data) = database_builder.read_features_text(data_dir=DATA_DIR,feature_database=FEATURE_DATABASE)
        dataset = database_builder.read_pickle_database(data_dir=DATA_DIR, pickle_database=PICKLE_DATABASE)
        
        app.run()
    
    def tearDown(self):
        database_builder.init_database(db())
        request.environ.get('werkzeug.server.shutdown')
        
    def populate_database(self):
        feature_dict = database_builder.add_features(db(),feature_list)
        database_builder.add_studies(db(),dataset, feature_list, feature_data, feature_dict)
        
    class ModelTest(TestCase):

        def add_feature(self):
            study = studies.Study(pmid=1, doi='Doi1.23', title='Title=Asdf_123*', journal='Journal of journal of journal of journal of Recursively', authors='asdf, qwerty, Z.X.C.V_123', year=1856, space='Random', table_num='101')
            peak = studies.Peak(x=1,y=2,z=3)
            feature=features.Feature(feature='Hairy',num_studies=1,num_activations=1)
            freq=features.Frequency(study,feature,.55999)

            db.session.add(study)
            study.peaks.append(peak)
            db.session.add(feature)
            db.session.add(freq)
            db.session.commit()

            assert feature in features.Feature.query.all()
            assert freq in features.Frequency.query.all()
            db.session.delete(study)
            db.session.delete(feature)
            
            db.session.commit()
                
        def remove_feature(self):
            study = studies.Study(pmid=1, doi='Doi1.23', title='Title=Asdf_123*', journal='Journal of journal of journal of journal of Recursively', authors='asdf, qwerty, Z.X.C.V_123', year=1856, space='Random', table_num='101')
            peak = studies.Peak(x=1,y=2,z=3)
            feature=features.Feature(feature='Hairy',num_studies=1,num_activations=1)
            freq=features.Frequency(study,feature,.55999)

            db.session.add(study)
            study.peaks.append(peak)
            db.session.add(feature)
            db.session.add(freq)
            db.session.commit()


            db.session.delete(study)
            db.session.delete(feature)
            
            db.session.commit()
                
            assert feature not in features.Feature.query.all()
            assert freq not in features.Frequency.query.all()
                
        def add_studies_to_feature(self):
            study1 = studies.Study(pmid=1, doi='Doi1.23', title='Title=Asdf_123*', journal='Journal of journal of journal of journal of Recursively', authors='asdf, qwerty, Z.X.C.V_123', year=1856, space='Random', table_num='101')
            study2 = studies.Study(pmid=2, doi='Doi1.23', title='Title=Asdf_123*', journal='Journal of journal of journal of journal of Recursively', authors='asdf, qwerty, Z.X.C.V_123', year=1856, space='Random', table_num='101')
            study3 = studies.Study(pmid=3, doi='Doi1.23', title='Title=Asdf_123*', journal='Journal of journal of journal of journal of Recursively', authors='asdf, qwerty, Z.X.C.V_123', year=1856, space='Random', table_num='101')
            feature=features.Feature(feature='Hairy',num_studies=3,num_activations=0)
            freq1=features.Frequency(study1,feature,.58699)
            freq2=features.Frequency(study2,feature,.55999)
            freq3=features.Frequency(study3,feature,.099)

            db.session.add(study1)
            db.session.add(study2)
            db.session.add(study3)
            db.session.add(feature)
            db.session.add(freq1)
            db.session.add(freq2)
            db.session.add(freq3)
            db.session.commit()
            assert feature in features.Feature.query.all()
            assert freq1 in features.Frequency.query.all()
            assert freq2 in features.Frequency.query.all()
            assert freq3 in features.Frequency.query.all()
            db.session.delete(study1)
            db.session.delete(study2)
            db.session.delete(study3)
            db.session.delete(feature)
            db.session.commit()
                
        def remove_multiple_studies_from_feature(self):
            study1 = studies.Study(pmid=1, doi='Doi1.23', title='Title=Asdf_123*', journal='Journal of journal of journal of journal of Recursively', authors='asdf, qwerty, Z.X.C.V_123', year=1856, space='Random', table_num='101')
            study2 = studies.Study(pmid=2, doi='Doi1.23', title='Title=Asdf_123*', journal='Journal of journal of journal of journal of Recursively', authors='asdf, qwerty, Z.X.C.V_123', year=1856, space='Random', table_num='101')
            study3 = studies.Study(pmid=3, doi='Doi1.23', title='Title=Asdf_123*', journal='Journal of journal of journal of journal of Recursively', authors='asdf, qwerty, Z.X.C.V_123', year=1856, space='Random', table_num='101')
            feature=features.Feature(feature='Hairy',num_studies=3,num_activations=0)
            freq1=features.Frequency(study1,feature,.58699)
            freq2=features.Frequency(study2,feature,.55999)
            freq3=features.Frequency(study3,feature,.099)

            db.session.add(study1)
            db.session.add(study2)
            db.session.add(study3)
            db.session.add(feature)
            db.session.add(freq1)
            db.session.add(freq2)
            db.session.add(freq3)
            db.session.commit()
            db.session.delete(study1)
            db.session.delete(study2)
            db.session.delete(study3)
            db.session.commit()
            assert feature in features.Feature.query.all()
            assert freq1 not in features.Frequency.query.all()
            assert freq2 not in features.Frequency.query.all()
            assert freq3 not in features.Frequency.query.all()
            db.session.delete(feature)
            db.session.commit()
            assert feature not in features.Feature.query.all()
            
        def add_features_to_study(self):
            study = studies.Study(pmid=1, doi='Doi1.23', title='Title=Asdf_123*', journal='Journal of journal of journal of journal of Recursively', authors='asdf, qwerty, Z.X.C.V_123', year=1856, space='Random', table_num='101')
            feature1=features.Feature(feature='Hairy',num_studies=1,num_activations=0)
            feature2=features.Feature(feature='Furry',num_studies=1,num_activations=0)
            feature3=features.Feature(feature='Fluffy',num_studies=1,num_activations=0)
            freq1=features.Frequency(study,feature1,.58699)
            freq2=features.Frequency(study,feature2,.55999)
            freq3=features.Frequency(study,feature3,.099)

            db.session.add(study)
            db.session.add(feature1)
            db.session.add(feature2)
            db.session.add(feature3)
            db.session.add(freq1)
            db.session.add(freq2)
            db.session.add(freq3)
            db.session.commit()
            assert feature1 in features.Feature.query.all()
            assert feature2 in features.Feature.query.all()
            assert feature3 in features.Feature.query.all()
            assert freq1 in features.Frequency.query.all()
            assert freq2 in features.Frequency.query.all()
            assert freq3 in features.Frequency.query.all()

            db.session.delete(study)
            db.session.delete(feature1)
            db.session.delete(feature2)
            db.session.delete(feature3)
            db.session.commit()
                
        def remove_multiple_features_from_study(self):
            study = studies.Study(pmid=1, doi='Doi1.23', title='Title=Asdf_123*', journal='Journal of journal of journal of journal of Recursively', authors='asdf, qwerty, Z.X.C.V_123', year=1856, space='Random', table_num='101')
            feature1=features.Feature(feature='Hairy',num_studies=1,num_activations=0)
            feature2=features.Feature(feature='Furry',num_studies=1,num_activations=0)
            feature3=features.Feature(feature='Fluffy',num_studies=1,num_activations=0)
            freq1=features.Frequency(study,feature1,.58699)
            freq2=features.Frequency(study,feature2,.55999)
            freq3=features.Frequency(study,feature3,.099)

            db.session.add(study)
            db.session.add(feature1)
            db.session.add(feature2)
            db.session.add(feature3)
            db.session.add(freq1)
            db.session.add(freq2)
            db.session.add(freq3)
            db.session.commit()
            
            assert feature1 in features.Feature.query.all()
            assert feature2 in features.Feature.query.all()
            assert feature3 in features.Feature.query.all()
            assert freq1 in features.Frequency.query.all()
            assert freq2 in features.Frequency.query.all()
            assert freq3 in features.Frequency.query.all()

            db.session.delete(study)
            db.session.commit()

            assert feature1 in features.Feature.query.all()
            assert feature2 in features.Feature.query.all()
            assert feature3 in features.Feature.query.all()
            assert freq1 not in features.Frequency.query.all()
            assert freq2 not in features.Frequency.query.all()
            assert freq3 not in features.Frequency.query.all()

            db.session.add(study)
            db.session.add(freq1)
            db.session.add(freq2)
            db.session.add(freq3)
            db.session.commit()

            assert freq1 in features.Frequency.query.all()
            assert freq2 in features.Frequency.query.all()
            assert freq3 in features.Frequency.query.all()

            db.session.delete(feature1)
            db.session.commit()

            assert feature1 not in features.Feature.query.all()
            assert feature2 in features.Feature.query.all()
            assert feature3 in features.Feature.query.all()
            assert freq1 not in features.Frequency.query.all()
            assert freq2 in features.Frequency.query.all()
            assert freq3 in features.Frequency.query.all()


            db.session.delete(feature1)
            db.session.delete(feature2)
            db.session.delete(feature3)
            db.session.delete(study)
            db.session.commit()

            assert feature1 not in features.Feature.query.all()
            assert feature2 not in features.Feature.query.all()
            assert feature3 not in features.Feature.query.all()
            assert freq1 not in features.Frequency.query.all()
            assert freq2 not in features.Frequency.query.all()
            assert freq3 not in features.Frequency.query.all()

    class ApiTest(TestCase):
        
        def Study(self):
            response = self.client.get('/api/studies')
            objects=features.Feature.query.all()
            self.assertEquals(response, restless_json(1, objects, 1))
        
if __name__ == "__main__":
    import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
    