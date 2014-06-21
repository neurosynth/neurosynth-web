from nsweb.core import create_app, db
from nsweb.initializers.settings import SQLALCHEMY_DATABASE_URI, DEBUG, DATA_DIR, DEBUG_WITH_APTANA, PICKLE_DATABASE, FEATURE_FREQUENCY_THRESHOLD
from nsweb.initializers import database_builder
import os

def main():
    create_app(database_uri=SQLALCHEMY_DATABASE_URI, debug=DEBUG, aptana=DEBUG_WITH_APTANA)
    import nsweb.models #registers models

    ### Uncomment the following lines to initialize the Dataset instance from .txt files the first time
    if not os.path.isfile(PICKLE_DATABASE):
        builder = database_builder.DatabaseBuilder(db, 
        	studies=os.path.join(DATA_DIR, 'studies.txt'),
        	features=os.path.join(DATA_DIR, 'features.txt'))
        builder.dataset.save(PICKLE_DATABASE, keep_mappables=True)

    # Create a new builder from a pickled Dataset instance and populate the DB
    print "Initializing DatabaseBuilder..."
    builder = database_builder.DatabaseBuilder(db, 
        dataset=PICKLE_DATABASE, reset_db=True)
    
    print "Adding features..."
    
    # Use this for rapid testing... set to None to initialize full DB
    features = ['pain','emotion','language','memory','amygdala']

    builder.add_features(features=features)

    print "Adding studies..."
    builder.add_studies(features=features, limit=100)
    
    print "Adding feature-based meta-analysis images..."
    builder.generate_feature_images(features=features)

    print "Adding location-based coactivation images..."
    # builder.generate_location_images(min_studies=500, add_to_db=True)
    builder.add_location_images('/data/neurosynth/data/locations/images', limit=200)

if __name__ == '__main__':
    main()

