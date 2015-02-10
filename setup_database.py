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
        reset_db=False, reset_dataset=False)


    print "Adding analyses..."
    if settings.PROTOTYPE:
        analyses = ['emotion', 'language', 'memory', 'pain', 'visual',
                    'attention', 'sensory']
    else:
        analyses = None

    builder.add_term_analyses(analyses=analyses, add_images=True, reset=True)

    print "Adding studies..."
    if settings.PROTOTYPE:
        builder.add_studies(analyses=analyses, limit=500)
    else:
        builder.add_studies(analyses=analyses)

    print "Adding feature-based meta-analysis images..."
    builder.generate_analysis_images(
        analyses=analyses, add_to_db=False, overwrite=True)

    print "Adding topic sets..."
    builder.add_topics(generate_images=True, add_images=True, top_n=40)

    print "Adding cognitive atlas information for available terms..."
    builder.add_cognitive_atlas_nodes()

    print "Memory-mapping key image sets..."
    builder.memory_map_images(include=['terms'], reset=True)

    print "Adding genes..."
    builder.add_genes()

    builder.memory_map_images(include=['terms', 'topics', 'genes'])


if __name__ == '__main__':
    main()
