from nsweb.core import db
from sqlalchemy.ext.associationproxy

class Snapshot(db.Model):

    """ A snapshot of the entire Database (i.e., all studies/activations) at a
    given moment in time. """
    id = db.Column(db.Integer, primary_key=True)
    n_studies = db.Column(db.Integer)