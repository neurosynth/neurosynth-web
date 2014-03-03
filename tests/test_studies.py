from tests import *


class StudiesTest(TestCase):

    def test_model_studies_has_core_fields(self):
        '''Changing the Model can break things. Studies must have peaks, pmid, and space with all other fields being optional.'''
#         peak = Peak(x=1,y=2,z=3)
#         study = Study(pmid=1, space='NotASpace')
#         study.peaks.append(peak)
#         db.session.add(study)
#         db.session.add(peak)
#         db.session.commit()
        
        study = Study(pmid=1, doi='Doi1.23', title='Title=Asdf_123*', journal='Journal of journal of journal of journal of Recursively', authors='asdf, qwerty, Z.X.C.V_123', year=1856, space='Random', table_num='101')
        peak = Peak(x=1,y=2,z=3)
        study.peaks.append(peak)
        db.session.add(study)
        db.session.commit()
        
        
        asdf = Study.query.all() 
        assert Study.query.all() 

    def test_model_studies_takes_all_fields_from_production_dataset(self):
        '''Changing the Model can break things. These additional fields probably don't need to be populated, but it's nice to have them.'''
        pass
    
    def test_model_studies_has_custom_fields(self):
        '''Tests for custom fields not related to source data'''
        pass
    
    def test_model_studies_data_validation(self):
        '''We need to make sure we aren't changing the data. If you are manipulating data, please update me'''
        pass
    
    def test_empty_api_studies_returns_200(self):
        '''Check to make sure the api is active. Also need to define empty behaviour'''
        pass
    
    def test_populated_api_studies_returns_200(self):
        '''Check to make sure the api is active. Also need to define behavior when we're actually pulling data'''
        pass
    
    def test_api_data_validation(self):
        '''We need to make sure we aren't changing the data. If you are manipulating data, please update me'''
        pass
    
    def test_core_api_fields(self):
        '''The important fields for view aren't the same as the ones used in the database. We're testing for those here.'''
        pass

    def test_sent_optional_api_fields(self):
        '''The extra fields we send for view aren't the same as the ones used in the database. We're testing for those here.'''
        pass
    
    def test_sent_custom_api_fields(self):
        pass

    def test_no_extra_fields(self):
        '''We don't want to send useless extra information that should stay in database. Such as all information for features related to very study'''
        pass
