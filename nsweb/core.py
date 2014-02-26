_app=None
_db=None
_manager=None

def set(app,db,manager):
    global _app
    global _db
    global _manager
    _app=app
    _db=db
    _manager=manager

def db():
    return _db
def app():
    return _app
def manager():
    return _manager