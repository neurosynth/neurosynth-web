from tests import *

class ImagesTest(TestCase):

    def test_frequency_field(self):
        '''Frequency has fields pmid, feature_id, and frequency'''
        self.populate_db()
        frequency = Frequency.query.first()
        self.assert_model_contains_fields(frequency, ['feature_id','pmid','frequency'])

    def test_frequency_association_proxies(self):
        '''Are Frequency fields study and feature associations working?'''
        self.populate_db()
        frequency = Frequency.query.first()
        assert isinstance(frequency.study,Study)
        assert isinstance(frequency.feature,Feature)
