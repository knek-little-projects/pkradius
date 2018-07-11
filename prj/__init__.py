"""
    Perform additional work over application consts:
    - connect to database
    - set logging
    etc.
"""
from .const import *
import pymongo, motor, logging


# set logging
verbosity_level = getattr(logging, app["verbosity"].upper())
logging.basicConfig(level=verbosity_level,
                    format='[%(asctime)s %(module)s %(levelname)s] %(message)s',
                    datefmt='%m.%d %H:%M')
logger = logging.getLogger()
logger.setLevel(verbosity_level)

# async db
motor_connection = motor.MotorClient()
motor_database = motor_connection[app["database_name"]]

# sync db
pymongo_connection = pymongo.MongoClient()
pymongo_database = pymongo_connection[app["database_name"]]

# after connecting to database 
# we can include http handlers
# BUT WE SHOULDN'T because of circuit:
#   import database -> import prj -> import handlers -> import database

# const shortcuts
# should be after all wildcard imports!
# otherwise could be name collisions
# for example `url` would be replaced by `tornado.web.url`
url = app["url"]