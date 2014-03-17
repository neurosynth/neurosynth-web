from tests import *

class StudiesTest(TestCase):

    def test_core_fields(self):
        '''Changing the Model can break things. Studies must have peaks, pmid, and space with all other fields being optional.'''
        peak = Peak(x=1,y=2,z=3)
        study = Study(pmid=1, space='NotASpace')
        study.peaks.append(peak)

        db.session.add(study)
        db.session.commit()

        studies = Study.query.all()
        #TODO: peaks should be added, but it brings about unwanted behavior when in init
        self.assert_model_contains_fields(study, ['pmid','space'])#,'peaks'])
        self.assert_model_equality(studies, [study], ['peaks'])

        self.assert_model_contains_fields(peak, ['x','y','z'])
        self.assert_model_equality( [peak],studies[0].peaks)
                
    def test_fields_from_production_dataset(self):
        '''Changing the model can break things, but we don't want to lose any data from production database.'''
        #production data fields
        fields = self.get_prod_data_fields()
        #current fields
        study = Study(pmid=1, doi='Doi1.23', title='Title=Asdf_123*', journal='Journal of journal of journal of journal of Recursively', authors='asdf, qwerty, Z.X.C.V_123', year=1856, space='Random', table_num='101')
        peak = Peak(x=1,y=2,z=3)
        study.peaks.append(peak)

        db.session.add(study)
        db.session.commit()

        studies = Study.query.all()
        self.assert_model_contains_fields(study, fields)
        _=studies[0].peaks.all()
        self.assert_model_equality(studies, [study])
        self.assert_model_equality(studies[0].peaks.all(), [peak])
        
    def test_peaks_relation(self):
            study = Study(pmid=1, doi='Doi1.23', title='Title=Asdf_123*', journal='Journal of journal of journal of journal of Recursively', authors='asdf, qwerty, Z.X.C.V_123', year=1856, space='Random', table_num='101')
            peak1 = Peak(x=1,y=2,z=3)
            peak2 = Peak(x=1,y=2,z=3)
            peak3 = Peak(x=4,y=5,z=6)
            db.session.add(study)
            study.peaks.extend([peak1,peak2,peak3])
            db.session.commit()
            
            studies = Study.query.all()
            self.assert_model_equality([study], studies, ['peaks'])