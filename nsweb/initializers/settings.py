import os
ROOT_DIR=os.path.realpath(os.path.join(os.path.join(os.path.dirname(__file__), os.path.pardir), os.path.pardir))
DATA_DIR=ROOT_DIR + '/Data/'
IMAGE_DIR=DATA_DIR + 'Images/'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATA_DIR + 'prod.db'
PICKLE_DATABASE = DATA_DIR + 'neurosynth_dataset.pkl'
FEATURE_DATABASE = DATA_DIR + 'abstract_features.txt'
LOGGING_PATH = DATA_DIR + 'log.txt'
LOGGING_LEVEL = 'DEBUG'
DEBUG = True
DEBUG_WITH_APTANA = True
FEATURE_FREQUENCY_THRESHOLD=.001