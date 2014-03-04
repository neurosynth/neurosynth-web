from tests import *

class ImagesTest(TestCase):

    def test_frequency_field(self):
        peak = Peak(x=1,y=2,z=3)
        study = Study(pmid=1, space='NotASpace', peaks=[peak])
        db.session.add(study)
        feature = Feature(feature='test',num_studies=1,num_activations=1)
        db.session.add(feature)

        db.session.commit()
        frequency = feature.frequencies
        self.assert_model_contains_fields(feature, ['feature','num_studies','num_activations'])

    def test_study_has_valid_frequencies(self):
        self.populate_db()
        studies = Study.query.all()
        
        frequencies = feature.frequencies
        self.assert_model_contains_fields(feature, ['feature','num_studies','num_activations'])
        self.assert_model_equality([feature], [Feature(feature='f1',num_studies=5,num_activations=21)])

    def test_feature_has_valid_frequencies(self):
        self.populate_db()
        feature = Feature.query.all()
        frequencies = feature.frequencies
        self.assert_model_contains_fields(feature, ['feature','num_studies','num_activations'])
        self.assert_model_equality([feature], [Feature(feature='f1',num_studies=5,num_activations=21)])

