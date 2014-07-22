from nsweb.core import create_app, db
from nsweb.initializers import settings
from nsweb.initializers import database_builder
import os

def main():
    create_app(debug=settings.DEBUG)
    import nsweb.models #registers models

    print "Initializing DatabaseBuilder..."
    # Create a new builder from a pickled Dataset instance and populate the DB
    dataset = settings.PICKLE_DATABASE
    builder = database_builder.DatabaseBuilder(db, dataset=dataset,
        	studies=os.path.join(settings.DATA_DIR, 'studies.txt'),
        	features=os.path.join(settings.DATA_DIR, 'features.txt'),
            # reset_db=True, reset_dataset=True)
            reset_db=False, reset_dataset=False)

    # print "Adding features..."
    # builder.add_features(features=features)

    # print "Adding studies..."
    # builder.add_studies(features=features)

    print "Adding new features to database..."
    builder.add_features_to_database('/Users/tyarkoni/Dropbox/Code/sandbox/cognitive_atlas_features.txt',
                                    min_studies=30)
    
    # print "Adding feature-based meta-analysis images..."
    # builder.generate_feature_images(features=features, add_to_db=False)

    # print "Adding location-based coactivation images..."
    # # builder.generate_location_images(min_studies=500, add_to_db=True)
    # builder.add_location_images('/data/neurosynth/data/locations/images')

    # print "Generating location feature data..."
    # builder.generate_location_features()

    # print "Save decoding data for rapid analysis..."
    # features = ['working', 'emotion', 'pain', 'language', 'motor', 'attention',
    #     'perception', 'reward', 'memory', 'episodic', 'semantic', 'visual', 'auditory',
    #     'conflict', 'inhibition', 'social', 'mind', 'self', 'familiar', 'executive',
    #     'action', 'execution', 'planning', 'olfactory', 'drug', 'depression', 'angry',
    #     'face', 'place', 'placebo', 'regulation', 'music', 'speech', 'motion', 'spatial',
    #     'visuospatial']
    # builder.generate_decoding_data(features)

    # print "Adding genes..."
    # builder.add_genes()


if __name__ == '__main__':
    main()

