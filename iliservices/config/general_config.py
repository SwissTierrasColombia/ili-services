import os
import logging

APP_DIR = os.path.dirname(os.path.dirname(__file__))

WORKING_DIR = os.environ.get('PROCESSING_DIR')
PREFIX_PROCESS_DIR = 'proc_'

##############################################################################
# LOGGING CONFIGURATION
##############################################################################
DEFAULT_LOG_MODE = logging.DEBUG
DEFAULT_LOG_FORMAT='%(name)-12s %(asctime)s %(levelname)-8s %(filename)s:%(funcName)s %(message)s'
#DEFAULT_LOG_FORMAT='%(asctime)s - %(levelname)s - %(name)s - %(message)s'

##############################################################################
# JAVA CONFIGURATION
##############################################################################
FULL_JAVA_EXE_PATH = '/usr/bin/java'
JAVA_REQUIRED_VERSION = 1.8

##############################################################################
# ILI2DB AND ILIVALIDATOR PARAMETERS CONFIGURATION
##############################################################################
USE_CUSTOM_MODEL_DIR = True
CUSTOM_MODEL_DIR = os.path.join(APP_DIR, 'resources', 'ilimodels')
# CUSTOM_MODEL_DIR = 'https://ceicol.com/models/'

DEFAULT_TOML_FILE = os.path.join(APP_DIR, 'resources', 'toml', 'configuration.toml')
USE_ILI2DB_DEBUG_MODE = False
LOG_FILE_PATH = ''

USE_ILIVALIDATOR_DEBUG_MODE = False

CTM12_PG_SCRIPT_PATH = os.path.join(APP_DIR, 'resources', 'sql', 'insert_ctm12_pg.sql')
CTM12_GPKG_SCRIPT_PATH = os.path.join(APP_DIR, 'resources', 'sql', 'insert_ctm12_gpkg.sql')

##############################################################################
# ILI-SERVICES DATABASE CONNECTION PARAMETERS
##############################################################################
ILISERVICES_DB_NAME = os.environ.get("ILISERVICES_DB_NAME")
ILISERVICES_DB_USER = os.environ.get("ILISERVICES_DB_USER")
ILISERVICES_DB_PASS = os.environ.get("ILISERVICES_DB_PASS")
ILISERVICES_DB_PORT = os.environ.get("ILISERVICES_DB_PORT")
ILISERVICES_DB_HOST = os.environ.get("ILISERVICES_DB_HOST")

