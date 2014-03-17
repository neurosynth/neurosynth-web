from nsweb.core import create_app, db
from nsweb.settings import SQLALCHEMY_DATABASE_URI, DEBUG, DEBUG_WITH_APTANA, FEATURE_DATABASE, PICKLE_DATABASE, FEATURE_FREQUENCY_THRESHOLD
from nsweb.helpers import database_builder
import os

def main():
    create_app(database_uri=SQLALCHEMY_DATABASE_URI, debug=DEBUG, aptana=DEBUG_WITH_APTANA)
    import nsweb.models #registers models

    ### Uncomment the following lines to initialize the Dataset instance from .txt files the first time
    if not os.path.isfile(PICKLE_DATABASE):
        builder = database_builder.DatabaseBuilder(db, 
        	studies='/Users/rahul/Downloads/full_database_revised.txt',
        	features=FEATURE_DATABASE)
        builder.dataset.save(PICKLE_DATABASE, keep_mappables=True)

    # Create a new builder from a pickled Dataset instance and populate the DB
    print "Initializing DatabaseBuilder..."
    builder = database_builder.DatabaseBuilder(db, 
        dataset=PICKLE_DATABASE, reset_db=True)
    
    print "Adding features..."
    
    # Use this for rapid testing... set to None to initialize full DB
    feature_list = ['pain','emotion','language','memory','amygdala']

    builder.add_features(feature_list=feature_list)

    print "Adding studies..."
    builder.add_studies(feature_list=feature_list)
    
    print "Adding feature-based meta-analysis images..."
    builder.generate_feature_images(feature_list=feature_list)

    print "Adding location-based coactivation images..."
    builder.generate_location_images(min_studies=500, add_to_db=True)

if __name__ == '__main__':
    main()

