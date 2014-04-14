from nsweb.initializers import settings
from nsweb.core import app, setup_logging, create_app, register_blueprints
from flask_script import Manager
#registers models
import nsweb.models
manager = Manager(app)
def main():
    #sets up the flask app
    create_app(database_uri = settings.SQLALCHEMY_DATABASE_URI)
    
    #creates and registers blueprints in nsweb.blueprints
    
    import nsweb.frontend.controllers.studies
    import nsweb.frontend.controllers.features
    import nsweb.frontend.controllers.locations
    
    #loads blueprints
    register_blueprints()
    
    #sets up logging
    setup_logging(logging_path=settings.LOGGING_PATH,level=settings.LOGGING_LEVEL)
    
    # print app.url_map   # Display all routes--for debugging
    
    # To allow aptana to receive errors, set use_debugger=False
    if app.debug: use_debugger = True
    try:
        # Disable Flask's debugger if external debugger is requested
        use_debugger = not(app.config.get('DEBUG_WITH_APTANA'))
    except:
        pass
    app.run(use_debugger=use_debugger, debug=app.debug,
            use_reloader=use_debugger)

if __name__ == "__main__":
    main()