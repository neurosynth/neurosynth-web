import os
from os.path import join

ROOT_DIR=os.path.realpath(join(join(os.path.dirname(__file__), os.path.pardir), os.path.pardir))

STATIC_FOLDER = ROOT_DIR + '/nsweb/static'

TEMPLATE_FOLDER = ROOT_DIR + '/nsweb/templates'

# DATA_DIR = ROOT_DIR + '/data/'
DATA_DIR = '/data/neurosynth/data/'

IMAGE_DIR = join(DATA_DIR, 'images')

IMAGE_UPLOAD_DIR = join(DATA_DIR, 'images', 'uploads')

TOPIC_DIR = join(DATA_DIR, 'topics')

LOCATION_FEATURE_DIR = join(DATA_DIR, 'locations', 'features_test')

GENE_IMAGE_DIR = '/Volumes/data/AllenSynth/Data/Maps/GeneMapsRadius6'

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATA_DIR + 'prod.db'

PICKLE_DATABASE = DATA_DIR + 'neurosynth_dataset.pkl'

DECODING_DATA = join(DATA_DIR, 'decoding', 'decoding.msg')

DECODING_RESULTS_DIR = join(DATA_DIR, 'decoding', 'results')

DECODING_SCATTERPLOTS_DIR = join(DATA_DIR, 'decoding', 'scatterplots')

LOGGING_PATH = DATA_DIR + 'log.txt'

LOGGING_LEVEL = 'DEBUG'

CELERY_BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND='redis://localhost:6379'

DEBUG = False

FEATURE_FREQUENCY_THRESHOLD=.001