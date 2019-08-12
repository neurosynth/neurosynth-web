import os
from os.path import join


# The root location of the app. Should not need to be changed.
ROOT_DIR = os.path.realpath(
    join(join(os.path.dirname(__file__), os.path.pardir), os.path.pardir))

### SETTINGS THAT SHOULD ALWAYS BE UPDATED ###
# Root path for generated data
DATA_DIR = join(ROOT_DIR, 'data')


### SHOULD NOT NEED TO BE UPDATED ###

# Path to main assets (pickled Dataset, study files, etc.)
ASSET_DIR = join(DATA_DIR, 'assets')
RESET_ASSETS = True

# Path to pickled Neurosynth Dataset instance
PICKLE_DATABASE = join(ASSET_DIR, 'neurosynth_dataset.pkl')

# Main image folder
IMAGE_DIR = join(DATA_DIR, 'images')

# Path to analysis/location flat filies
LOCATION_ANALYSIS_DIR = join(DATA_DIR, 'locations', 'analyses')

# Static content
STATIC_FOLDER = join(ROOT_DIR, 'nsweb', 'static')

# Templates
TEMPLATE_FOLDER = join(ROOT_DIR, 'nsweb', 'templates')

### SETUP INSTRUCTIONS AND APP BEHAVIOR ####

# A list of analysis names can be provided at database setup time. If a file is
# passed, it must be a tab-delimited file with term names in the first column
# and a binary indicator of whether or not to retain the term in the second
# column (named 'keep'). If None, all analyses are loaded into the DB.
ANALYSIS_FILTER_FILE = None

### DECODER-RELATED PATHS ###
# Path to decoded images
DECODED_IMAGE_DIR = join(DATA_DIR, 'images', 'decoded')

# Path to saved decoding image array--this is kept active in memory
DECODING_DATA = join(ASSET_DIR, 'decoding.msg')

# Path to output decoding results (flat .txt files)
DECODING_RESULTS_DIR = join(DATA_DIR, 'decoding', 'results')

# Path to output decoded image scatter plots
DECODING_SCATTERPLOTS_DIR = join(DATA_DIR, 'decoding', 'scatterplots')

# Whether or not to cache decoder results. When True, will not re-run the
# decoder on an image unless the image has been modified since the
# last decoding; when False, will re-run the decoder every time.
CACHE_DECODINGS = True

# Path to memory-mapped arrays of image data.
# Note: when running a development build inside a docker container or other VM,
# memmapping may fail. In such a case, this shoudl point to a directory on the
# local disk image rather than the host.
MEMMAP_DIR = join(DATA_DIR, 'memmaps')


### CONTENT-SPECIFIC DIRECTORIES ###
MASK_DIR = join(IMAGE_DIR, 'masks')
TOPIC_DIR = join(DATA_DIR, 'topics')
GENE_IMAGE_DIR = join(IMAGE_DIR, 'genes')


### DATABASE CONFIGURATION ###
# Adapter to use--either 'postgres' or 'sqlite'
SQL_ADAPTER = 'sqlite'

# SQLite pat
SQLALCHEMY_SQLITE_URI = 'sqlite:///' + join(DATA_DIR, 'neurosynth.db')

# SQL configuration
SQL_HOST = 'db'
SQL_USER = 'neurosynth'
SQL_PASSWORD = 'neurosynth'
SQL_PRODUCTION_DB = 'neurosynth'
SQL_DEVELOPMENT_DB = 'neurosynth'
SQL_TEST_DB = 'neurosynth_test'
TEST_URL = 'https://test.neurosynth.org'

### Logging ###
LOGGING_PATH = join(DATA_DIR, 'log.txt')
LOGGING_LEVEL = 'DEBUG'

### Celery settings for background tasks ###
CELERY_BROKER_URL = 'redis://redis:6379/0'
CELERY_RESULT_BACKEND = 'redis://redis:6379/0'

### Flask-Mail settings ###
MAIL_ENABLE = True
MAIL_USERNAME = os.getenv('MAIL_USERNAME', 'email@example.com')
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', 'password')
MAIL_DEBUG = False
USER_EMAIL_SENDER_NAME = os.getenv("USER_EMAIL_SENDER_NAME", "My App")
USER_EMAIL_SENDER_EMAIL = os.getenv("USER_EMAIL_SENDER_EMAIL",
                                    "noreply@example.com")
MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
MAIL_PORT = int(os.getenv('MAIL_PORT', '465'))
MAIL_USE_SSL = int(os.getenv('MAIL_USE_SSL', True))

### App-level configuration ###
DEBUG = True
PROTOTYPE = True
