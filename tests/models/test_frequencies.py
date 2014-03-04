from tests import *

class ImagesTest(TestCase):

    def test_feature_has_frequencies(self):
        self.populate_db()
        feature = Feature.query.filter(Feature.feature == 'f1').first()
        frequencies = feature.frequencies
        self.assert_model_contains_fields(feature, ['feature','num_studies','num_activations'])
        self.assert_model_equality([feature], [Feature(feature='f1',num_studies=5,num_activations=21)])

    def test_frequency_field(self):
        self.populate_db()
        Feature(feature='f1',num_studies=5,num_activations=21)
        feature = Feature.query.filter(Feature.feature == 'f1').first()
        frequency = feature.frequencies
        self.assert_model_contains_fields(feature, ['feature','num_studies','num_activations'])
        self.assert_model_equality([feature], [Feature(feature='f1',num_studies=5,num_activations=21)])
