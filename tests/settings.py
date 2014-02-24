from nsweb.core import app


SQLALCHEMY_DATABASE_URI = "sqlite://"
TESTING = True

if not app.debug:
    import logging
    file_handler = logging.handlers.RotatingFileHandler
    file_handler.setLevel(logging.DEBUG)
    loggers = [app.logger, logging.getLogger('sqlalchemy')]

    for logger in loggers:
        logger.addHandler(file_handler)