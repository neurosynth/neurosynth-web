from tests import *
from os.path import isfile

class FeaturesTest(TestCase):

    def test_core_fields(self):
        '''Changing the Model can break things. features must have name(feature), number of studies, and number of activations with all other fields being optional.'''
        feature = Feature(feature='test',num_studies=1,num_activations=1)
        db.session.add(feature)
        db.session.commit()
        features =Feature.query.all()
        self.assert_model_contains_fields(feature, ['feature','num_studies','num_activations'])
        self.assert_model_equality([feature], features)
        
 