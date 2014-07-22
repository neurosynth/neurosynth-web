from nsweb.models import Feature
from os.path import isfile

class FeaturesTest(TestCase):

    def test_core_fields(self):
        feature = Feature(feature='test', num_studies=1, num_activations=1)
        db.session.add(feature)
        db.session.commit()
        features =Feature.query.all()
        self.assert_model_contains_fields(feature, ['feature','num_studies','num_activations'])
        self.assert_model_equality([feature], features)
        
 