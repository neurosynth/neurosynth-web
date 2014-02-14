# Lost in the initial commitcreate project. Rebuild this ASAP!!!

from sqlalchemy import Column, Integer, Unicode, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker


session = scoped_session(sessionmaker())
#engine = create_engine('sqlite://')
session.configure(bind=engine)
Base = declarative_base()

class AppFactory(SQLAlchemyModelFactory):