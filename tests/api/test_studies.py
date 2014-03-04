from tests import *

class StudiesTest(#TestCase):

    def test_empty_api_studies_returns_200(self):
        '''Check to make sure the api is active. Also need to define behavior when we're actually pulling data'''

        response = self.client.get('/api/studies')

        self.assert200(response)
    
    def test_populated_api_studies_returns_200(self):
        '''Check to make sure the api is active. Also need to define behavior when we're actually pulling data'''

        self.populate_db()
        
        response = self.client.get('/api/studies')
        
        self.assert200(response)
        
    def test_core_api_fields_present(self):
        '''The important fields for view aren't the same as the ones used in the database. We're testing for those here.'''
        pass

    def test_api_data_validation(self):
        '''We need to make sure we aren't changing the data. If you are manipulating data, please update me'''
        pass

    def test_sent_custom_api_fields(self):
        pass

    def test_no_extra_fields(self):
        '''We don't want to send useless extra information that should stay in database. Such as all information for features related to very study'''
        pass
