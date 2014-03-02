from nsweb import settings
from nsweb.helpers.app_start import setup_logging, create_app
from nsweb.core import app

if __name__ == "__main__":

    create_app(database_uri = settings.SQLALCHEMY_DATABASE_URI)
    
    
    # register is ugly but recommended by flask. Blueprints made things more complex, without any real benefit. http://flask.pocoo.org/docs/patterns/packages/
    # register models
    from nsweb.models import studies, features
    
    #register APIs
    import nsweb.studies.studies
    import nsweb.features.features
    
    
    setup_logging(logging_path=settings.LOGGING_PATH,level=settings.LOGGING_LEVEL)
    
    app=app()
    
    # To allow aptana to receive errors, set use_debugger=False
    if app.debug: use_debugger = True
    try:
        # Disable Flask's debugger if external debugger is requested
        use_debugger = not(app.config.get('DEBUG_WITH_APTANA'))
    except:
        pass
    app.run(use_debugger=use_debugger, debug=app.debug,
            use_reloader=use_debugger)