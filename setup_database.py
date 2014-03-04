from nsweb.core import create_app, db
from nsweb.settings import SQLALCHEMY_DATABASE_URI, DEBUG, DEBUG_WITH_APTANA, DATA_DIR, FEATURE_DATABASE, PICKLE_DATABASE, IMAGE_DIR
from nsweb.helpers import database_builder

def main():
    create_app(database_uri=SQLALCHEMY_DATABASE_URI, debug=DEBUG, aptana=DEBUG_WITH_APTANA)
    import nsweb.models #registers models
    database_builder.init_database(db)
    dataset = database_builder.read_pickle_database(data_dir=DATA_DIR, pickle_database=PICKLE_DATABASE)
    (feature_list,feature_data) = database_builder.read_features_text(data_dir=DATA_DIR,feature_database=FEATURE_DATABASE)
    feature_dict = database_builder.add_features(db,feature_list,image_dir=IMAGE_DIR)
    database_builder.add_studies(db, dataset, feature_list, feature_data, feature_dict)

if __name__ == '__main__':
    main()