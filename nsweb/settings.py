import os

SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/test.db'
DATA_DIR=os.path.dirname(os.path.realpath(__file__)) + '/../Data/'
PICKLE_DATABASE = 'pickled.txt'
FEATURE_DATABASE = 'abstract_features.txt'
LOGGING_PATH = ''
LOGGING_LEVEL = ''
DEBUG = True
DEBUG_WITH_APTANA = True
