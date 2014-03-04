from tests import *

class ImagesTest(#TestCase):

    def test_model_images_has_core_fields(self):
        '''Changing the Model can break things. images must have peaks, pmid, and space with all other fields being optional.'''
    
#     def test_model_images_takes_all_fields_from_production_dataset(self):
#         '''Changing the Model can break things. These additional fields probably don't need to be populated, but it's nice to have them.'''
#         from cPickle import load
#         pass
#     
#     def test_model_images_has_custom_fields(self):
#         '''Tests for custom fields not related to source data'''
#         pass
#     
#     def test_model_images_data_validation(self):
#         '''We need to make sure we aren't changing the data. If you are manipulating data, please update me'''
#         pass
#     
#     def test_empty_api_images_returns_200(self):
#         '''Check to make sure the api is active. Also need to define empty behaviour'''
#         pass
#     
#     def test_populated_api_images_returns_200(self):
#         '''Check to make sure the api is active. Also need to define behavior when we're actually pulling data'''
#         pass
#     
#     def test_api_data_validation(self):
#         '''We need to make sure we aren't changing the data. If you are manipulating data, please update me'''
#         pass
#     
#     def test_core_api_fields(self):
#         '''The important fields for view aren't the same as the ones used in the database. We're testing for those here.'''
#         pass
# 
#     def test_sent_optional_api_fields(self):
#         '''The extra fields we send for view aren't the same as the ones used in the database. We're testing for those here.'''
#         pass
#     
#     def test_sent_custom_api_fields(self):
#         pass
# 
#     def test_no_extra_fields(self):
#         '''We don't want to send useless extra information that should stay in database. Such as all the study information related to a feature related to an image'''
#         pass
