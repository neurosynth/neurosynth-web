import os

DATA_DIR=os.path.dirname(os.path.realpath(__file__)) + '/../Data/'
IMAGE_DIR=DATA_DIR + 'Images/'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATA_DIR + 'prod.db'
PICKLE_DATABASE = DATA_DIR + 'neurosynth_dataset.pkl'
FEATURE_DATABASE = DATA_DIR + 'abstract_features.txt'
LOGGING_PATH = DATA_DIR + 'log.txt'
LOGGING_LEVEL = 'DEBUG'
DEBUG = True
DEBUG_WITH_APTANA = True
FEATURE_FREQUENCY_THRESHOLD=.001