from tests import *

class locationsTest(TestCase):

    def test_empty_api_features_returns_200(self):
        '''Check to make sure the api is active with an empty db'''
        response = self.client.get('/api/locations')
        assert response.status_code == 200

    def test_empty_api_features_data(self):
        '''Check JSON format is correct for empty db'''
        json = self.restless_json([])
        response = self.client.get('/api/locations')
        assert response.data == json

    def test_populated_api_features_returns_200(self):
        '''Check to make sure the api is active for populated db'''
        self.populate_db()
        response = self.client.get('/api/locations')
        assert response.status_code == 200

    def test_populated_api_features_data(self):
        '''Check json format for populated db'''
        self.populate_db()
        response = self.client.get('/api/locations')
        locations = Location.query.all()
        json = self.restless_json(fields=['id','x','y','z'],page_num=1,objects=locations,total_pages=1)
        assert response.data == json
