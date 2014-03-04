from tests import *
from os.path import isfile

class FeaturesTest(TestCase):

    def test_core_fields(self):
        '''Changing the Model can break things. features must have name(feature), number of studies, and number of activations with all other fields being optional.'''
        self.populate_db(images=False)
        feature = Feature.query.filter(Feature.feature == 'f1').first()
        self.assert_model_contains_fields(feature, ['feature','num_studies','num_activations'])
        self.assert_model_equality([feature], [Feature(feature='f1',num_studies=5,num_activations=21)])
#        self.assert_model_contains_fields(peak, ['x','y','z'])
#        self.assert_model_equality(studies[0].peaks.all(), [peak])
        
    def test_image_fields
        '''Changing the Model can break things. Images need forward and reverse inference, and specify if they should be displayed and downloaded'''
        self.populate_db()
        Feature(feature='f1',num_studies=5,num_activations=21)
        feature = Feature.query.filter(Feature.feature == 'f1').first()
        self.assert_model_contains_fields(feature, ['feature','num_studies','num_activations'])
        self.assert_model_equality([feature], [Feature(feature='f1',num_studies=5,num_activations=21)])

        
    def test_image_files_path(self):
        self.populate_db()
        features = Feature.query.all()
        for feature in features:
            assert isfile(feature.image_forward_inference)
            assert isfile(feature.image_reverse_inference)