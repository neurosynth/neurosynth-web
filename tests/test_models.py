""" Test model functionality. """
from nsweb.models.studies import Study
from nsweb.models.peaks import Peak

def test_studies(db):
    study = Study(pmid=345345, title='test study',
        authors='Jokkin, Eumast',
        journal='Journal of Nonexistent Findings',
        year=2008)
    study.peaks = [Peak(x=-12, y=14, z=40), Peak(x=22, y=22, z=22)]
    db.session.add(study)
    db.session.commit()
    assert Peak.query.count() == 2
    assert Study.query.count() == 1
