from nsweb.initializers import settings
from nsweb.core import app, setup_logging, create_app, register_blueprints

# set up the flask app
create_app()

# set up logging
setup_logging(logging_path=settings.LOGGING_PATH, level=settings.LOGGING_LEVEL)


def main():

    app.run(debug=app.debug, port=5001, host='0.0.0.0')

if __name__ == "__main__":
    main()
