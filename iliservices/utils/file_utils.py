import tempfile
import os

from config.general_config import (WORKING_DIR,
                                   PREFIX_PROCESS_DIR)

def create_tmp_geopackage(gpkg_name:str):
    working_dir = create_working_dir()
    return os.path.join(working_dir, gpkg_name)

def create_working_dir(path:str):
    temp_dir = tempfile.mkdtemp(dir=WORKING_DIR, prefix=PREFIX_PROCESS_DIR)
    return temp_dir

def get_resource_dir():
    basepath = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(basepath, 'resources')

def get_resource_path(resource:str):
    return os.path.join(get_resource_dir(), resource)