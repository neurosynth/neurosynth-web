import os

DATA_DIR=os.path.dirname(os.path.realpath(__file__)) + '/../Data/'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATA_DIR + 'test.db'
PICKLE_DATABASE = 'pickled.pkl'
FEATURE_DATABASE = 'abstract_features.txt'
LOGGING_PATH = ''
LOGGING_LEVEL = ''
DEBUG = True
DEBUG_WITH_APTANA = True
