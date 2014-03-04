import os

DATA_DIR=os.path.dirname(os.path.realpath(__file__)) + '/../Data/'
IMAGE_DIR=DATA_DIR + 'Images/'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATA_DIR + 'test.db'
PICKLE_DATABASE = 'test_pickled.pkl'
FEATURE_DATABASE = 'test_features.txt'
LOGGING_PATH = DATA_DIR + 'log.txt'
LOGGING_LEVEL = 'DEBUG'
DEBUG = True
DEBUG_WITH_APTANA = True
