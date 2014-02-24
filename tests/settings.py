import os

SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
DATA_DIR=os.path.dirname(os.path.realpath(__file__)) + '/../Data/'
PICKLE_DATABASE = 'test_pickled.pkl'
FEATURE_DATABASE = 'test_features.txt'
LOGGING_PATH = ''
LOGGING_LEVEL = ''
DEBUG = True
DEBUG_WITH_APTANA = True
