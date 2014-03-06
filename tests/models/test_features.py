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

        
    def test_image_fields(self):
        '''Changing the Model can break things. Images need forward and reverse inference, and specify if they should be displayed and downloaded'''
        self.populate_db()
        feature = Feature.query.filter_by(feature='f1').first()
        self.assert_model_contains_fields(feature, ['feature','num_studies','num_activations'])
        self.assert_model_equality([feature], [Feature(feature='f1',
                                                       num_studies=5,
                                                       num_activations=21,
                                                       image_forward_inference=IMAGE_DIR+'_'+feature.feature+'_pAgF_z_FDR_0.05.nii.gz',
                                                       image_reverse_inference=IMAGE_DIR+'_'+feature.feature+'_pFgA_z_FDR_0.05.nii.gz',
                                                       image_download=True,
                                                       image_display=True)])
        
    def test_image_files_path(self):
        self.populate_db()
        features = Feature.query.all()
        for feature in features:
            assert isfile(feature.image_forward_inference)
            assert isfile(feature.image_reverse_inference)