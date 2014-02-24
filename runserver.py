# from flask import Flask
# from flask_script import Manager
# 
# if __name__ == "__main__":
#     # To allow aptana to receive errors, set use_debugger=False
#     app = create_app()
# 
#     if app.debug: use_debugger = True
#     try:
#         # Disable Flask's debugger if external debugger is requested
#         use_debugger = not(app.config.get('DEBUG_WITH_APTANA'))
#     except:
#         pass
#     app.run(use_debugger=use_debugger, debug=app.debug,
#             use_reloader=use_debugger, host='0.0.0.0')
from nsweb.core import create_app
from nsweb import settings

app = create_app(database_uri=settings.SQLALCHEMY_DATABASE_URI,debug=settings.DEBUG)

app.run()

if __name__ == "__main__":
    # To allow aptana to receive errors, set use_debugger=False
    if app.debug: use_debugger = False
    try:
        # Disable Flask's debugger if external debugger is requested
        use_debugger = not(app.config.get('DEBUG_WITH_APTANA'))
    except:
        pass
    app.run(use_debugger=use_debugger, debug=app.debug,
            use_reloader=use_debugger, host='127.0.0.1')