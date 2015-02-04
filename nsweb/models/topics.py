# from nsweb.models import Analysis
# from nsweb.core import db


# class Topic(Analysis):

#     __tablename__ = 'topic'
#     id = db.Column(db.Integer, db.ForeignKey('analysis.id'), primary_key=True)
#     topic_set_id = db.Column(db.Integer, db.ForeignKey('topic_set.id'))
#     topic_set = db.relationship('TopicSet', backref=db.backref('topics', cascade='all, delete-orphan'))
#     terms = db.Column(db.Text)

#     __mapper_args__ = {
#         'polymorphic_identity': 'topic'
#     }


# class TopicSet(db.Model):

#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.Integer, unique=True)
#     description = db.Column(db.Text)
#     n_topics = db.Column(db.Integer)
