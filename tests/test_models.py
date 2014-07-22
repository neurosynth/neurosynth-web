
from nsweb.models import Study, Peak, Feature, Frequency, Image, FeatureImage, Location, LocationImage, LocationFeature

class TestModels

    def test_feature(self):
            feature = Feature(feature='test', num_studies=1, num_activations=1)
            features =Feature.query.all()
            self.assert_model_contains_fields(feature, ['feature','num_studies','num_activations'])
            self.assert_model_equality([feature], features)