import os

ROOT_DIR=os.path.realpath(os.path.join(os.path.join(os.path.dirname(__file__), os.path.pardir), os.path.pardir))

STATIC_FOLDER=ROOT_DIR+'/nsweb/static'

TEMPLATE_FOLDER=ROOT_DIR+'/nsweb/templates'

DATA_DIR=ROOT_DIR + '/data/'

IMAGE_DIR=DATA_DIR + 'images/'

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATA_DIR + 'prod.db'

PICKLE_DATABASE = DATA_DIR + 'neurosynth_dataset.pkl'

LOGGING_PATH = DATA_DIR + 'log.txt'

LOGGING_LEVEL = 'DEBUG'

DEBUG = True

DEBUG_WITH_APTANA = True

FEATURE_FREQUENCY_THRESHOLD=.001