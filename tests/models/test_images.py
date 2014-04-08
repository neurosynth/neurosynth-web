from tests import *

class ImagesTest(TestCase):
    def test_Image_fields(self):
        self.populate_db()
        image = Image.query.first()
        self.assert_model_contains_fields(image, ['id','image_file','label','display','download','stat'])
    
    def test_FeatureImage_fields(self):
        self.populate_db()
        feature_image = FeatureImage.query.first()
        self.assert_model_contains_fields(feature_image, ['feature_id'])
        
    def test_LocationImage_fields(self):
        self.populate_db()
        image = Image.query.first()
        location_image = LocationImage.query.first()
        self.assert_model_contains_fields(location_image, ['location_id'])

    def test_image_paths(self):
        self.populate_db()
        for i in Image.query.all():
            assert os.path.isfile(IMAGE_DIR+i.image_file)