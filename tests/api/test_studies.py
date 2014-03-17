from tests import *

class StudiesTest(TestCase):

    def test_empty_api_studies_returns_200(self):
        '''Check to make sure the api is active with an empty db'''
        response = self.client.get('/api/studies')
        assert response.status_code == 200

    def test_empty_api_studies_data(self):
        '''Check JSON format is correct for empty db'''
        json = self.restless_json([])
        response = self.client.get('/api/studies')
        assert response.data == json

    def test_populated_api_studies_returns_200(self):
        '''Check to make sure the api is active for populated db'''
        self.populate_db()
        response = self.client.get('/api/studies')
        assert response.status_code == 200

    def test_populated_api_studies_tests_updated(self):
        '''Check json format for populated db'''
        self.populate_db()
        response = self.client.get('/api/studies')
        studies = Study.query.all()
        json = self.restless_json(fields=['pmid','title','authors','journal','year'],page_num=1,objects=studies,total_pages=1)
        assert response.data == json

    def test_populated_api_studies_data(self):
        '''Check json format for populated db'''
        self.populate_db()
        response = self.client.get('/api/studies')
        studies = Study.query.all()
        from nsweb.blueprints.studies import includes
        json = self.restless_json(fields=includes,page_num=1,objects=studies,total_pages=1)
        assert response.data == json
