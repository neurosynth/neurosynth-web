from tests import *

class ImagesTest(TestCase):
    #TODO: tests are breaking, but what should proper API look like? Shouldn't we just send all relevant since that's easier?
    def test_image_fields(self):
        '''Changing the Model can break things. Images need forward and reverse inference, and specify if they should be displayed and downloaded'''
        self.populate_db()
        images = Image.query.all()
        self.assert_model_contains_fields(feature, ['feature','num_studies','num_activations'])
        self.assert_model_equality([feature], [Feature(feature='f1',
                                                       num_studies=5,
                                                       num_activations=21,
                                                       image_forward_inference=IMAGE_DIR+'_'+feature.feature+'_pAgF_z_FDR_0.05.nii.gz',
                                                       image_reverse_inference=IMAGE_DIR+'_'+feature.feature+'_pFgA_z_FDR_0.05.nii.gz',
                                                       image_download=True,
                                                       image_display=True)])
        
    def test_feature_image_files_path(self):
        self.populate_db()
        images = FeatureImage.query.all()
        for feature in images:
            assert isfile(feature.image_forward_inference)
