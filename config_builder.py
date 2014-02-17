from ConfigParser import SafeConfigParser
import os

config = SafeConfigParser()

## Constants ##
# Sections #

DATABASE='Database'    
LOGGING='Logging'
TESTING='Testing'

config.add_section(DATABASE)
config.add_section(LOGGING)
config.add_section(TESTING)

config.set(DATABASE, 'PICKLED_DATABASE', '')
config.set(DATABASE, 'FEATURE_DATABASE', '')
config.set(DATABASE, 'SQLALCHEMY_DATABASE_URI', '')

config.set(LOGGING, 'FILE_LOCATION','')
#Levels: 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
config.set(LOGGING, 'LEVEL', 'WARNING')


config.set(TESTING, 'DEBUG', True)
config.set(TESTING, 'DEBUG_WITH_APTANA', True)
config.set()

with open('config.cfg', 'wb') as configfile:
    config.write(configfile)