from nsweb.core import create_app, db
from nsweb.settings import SQLALCHEMY_DATABASE_URI, DEBUG, DEBUG_WITH_APTANA, DATA_DIR, FEATURE_DATABASE, PICKLE_DATABASE, IMAGE_DIR, FREQUENCY_THRESHOLD
from nsweb.helpers import database_builder

def main():
    create_app(database_uri=SQLALCHEMY_DATABASE_URI, debug=DEBUG, aptana=DEBUG_WITH_APTANA)
    import nsweb.models #registers models

    ### Uncomment the following lines to initialize the Dataset instance from .txt files the first time
    # builder = database_builder.DatabaseBuilder(db, 
    # 	studies='/Users/tal/Downloads/full_database_revised.txt',
    # 	features=DATA_DIR+ 'abstract_features.txt')
    # builder.dataset.save('/Users/tal/Downloads/neurosynth_dataset.pkl', keep_mappables=True)

    # Create a new builder from a pickled Dataset instance and populate the DB
    print "Initializing DatabaseBuilder..."
    builder = database_builder.DatabaseBuilder(db, 
        dataset='/Users/tal/Downloads/neurosynth_dataset.pkl', reset_db=True)
    
    print "Adding features..."
    
    # Use this for rapid testing... set to None to initialize full DB
    feature_list = ['pain','emotion','language','memory','amygdala']

    builder.add_features(feature_list=feature_list)

    print "Adding studies..."
    builder.add_studies(feature_list=feature_list)
    
    print "Adding meta-analysis images..."
    builder.generate_feature_images(feature_list=feature_list)

if __name__ == '__main__':
    main()

