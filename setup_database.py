from nsweb.core import create_app, db, app
from nsweb.initializers import settings
from nsweb.initializers import database_builder
import os

def main():
    create_app(debug=settings.DEBUG)
    import nsweb.models     #registers models

    print "Initializing DatabaseBuilder..."
    # Create a new builder from a pickled Dataset instance and populate the DB
    # pass reset_dataset=False after first run to avoid rebuilding dataset
    dataset = settings.PICKLE_DATABASE
    db.app = app  # Set context on DB
    builder = database_builder.DatabaseBuilder(
        db, dataset=dataset,
        studies=os.path.join(settings.ASSET_DIR, 'studies.txt'),
        features=os.path.join(settings.ASSET_DIR, 'features.txt'),
        # reset_db=True, reset_dataset=True)
        reset_db=True, reset_dataset=False)


    print "Adding analyses..."
    if settings.PROTOTYPE:
        analyses = ['emotion', 'language', 'memory', 'pain', 'visual',
                    'attention', 'sensory']
    else:
        analyses = None
    
    builder.add_analyses(analyses=analyses, add_images=True)

    print "Adding studies..."
    if settings.PROTOTYPE:
        builder.add_studies(analyses=analyses, limit=1000)
    else:
        builder.add_studies(analyses=analyses)
    
    print "Adding feature-based meta-analysis images..."
    builder.generate_analysis_images(
        analyses=analyses, add_to_db=False, overwrite=True)

    # print "Adding location-based coactivation images..."
    # builder.generate_location_images(min_studies=500, add_to_db=True)
    # builder.add_location_images('/data/neurosynth/data/locations/images', reset=True)

    # print "Generating location analysis data..."
    # builder.generate_location_analyses()

    # print "Save decoding data for rapid analysis..."
    analyses = ['working memory', 'visual', 'cognitive control', 'perception', 'sensory'
        'motor', 'social', 'language', 'learning', 'semantic', 'recognition', 'words',
        'number', 'emotion', 'hand', 'encoding', 'retrieval', 'faces', 'object',
        'attention', 'verbal', 'somatosensory', 'reward', 'decision making', 'cues', 'executive',
        'sensorimotor', 'risk', 'action', 'pictures', 'body', 'pain', 'emotion regulation',
        'reading', 'episodic', 'monitoring', 'depression', 'motion', 'error', 'rest', 
        'default mode', 'comprehension', 'execution', 'evaluation', 'sex', 'phonological',
        'anxiety', 'ratings', 'judgments', 'alzheimer', 'category', 'interference', 'person',
        'sentences', 'stress', 'imagery', 'response inhibition', 'spatial', 'personality', 'sounds',
        'visuospatial', 'awareness', 'placebo', 'sequence', 'biological', 'associative',
        'repetition', 'arousal', 'switching', 'mirror', 'anticipation', 'drug', 'planning',
        'listening', 'salience', 'color', 'motor control', 'strategy', 'tactile', 'fear', 'recall',
        'autism', 'priming', 'stroop', 'social cognition', 'happy', 'timing', 'identity', 'iq',
        'parkinson', 'spatial attention', 'music', 'self', 'auditory', 'speech production',
        'speech perception']

    builder.generate_decoding_data(analyses)

    print "Adding genes..."
    # builder.add_genes()

    print "Adding topic sets..."
    builder.add_topics()


if __name__ == '__main__':
    main()

