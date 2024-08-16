import os

from libs.modelbaker.iliwrapper.globals import DbIliMode
from libs.modelbaker.iliwrapper.ili2dbconfig import (
    BaseConfiguration,
    ExportConfiguration,
    ImportDataConfiguration,
    SchemaImportConfiguration,
    UpdateDataConfiguration,
    ValidateConfiguration,
)

from utils.file_utils import get_resource_path


def iliimporter_config(tool=DbIliMode.ili2pg, modeldir=None):
    base_config = BaseConfiguration()
    if modeldir is None:
        base_config.custom_model_directories_enabled = False
    else:
        base_config.custom_model_directories = local_model_repository_path()
        base_config.custom_model_directories_enabled = True

    configuration = SchemaImportConfiguration()
    configuration.tool = tool
    if tool == DbIliMode.ili2pg:
        configuration.dbhost = os.environ.get('PG_HOST')
        configuration.dbusr = os.environ.get('PG_USER')
        configuration.dbpwd = os.environ.get('PG_PASSWORD')
        configuration.database = os.environ.get('PG_DB')
    configuration.base_configuration = base_config

    return configuration


def iliexporter_config(tool=DbIliMode.ili2pg, modeldir=None, gpkg_path="geopackage/test_export.gpkg"):
    base_config = BaseConfiguration()
    if modeldir is None:
        base_config.custom_model_directories_enabled = False
    else:
        base_config.custom_model_directories = local_model_repository_path()
        base_config.custom_model_directories_enabled = True

    configuration = ExportConfiguration()
    if tool == DbIliMode.ili2pg:
        configuration.dbhost = os.environ.get('PG_HOST')
        configuration.dbusr = os.environ.get('PG_USER')
        configuration.dbpwd = os.environ.get('PG_PASSWORD')
        configuration.database = os.environ.get('PG_DB')
    elif tool == DbIliMode.ili2gpkg:
        configuration.dbfile = get_resource_path(gpkg_path)
    configuration.base_configuration = base_config

    return configuration


def ilidataimporter_config(tool=DbIliMode.ili2pg, modeldir=None):
    base_config = BaseConfiguration()
    if modeldir is None:
        base_config.custom_model_directories_enabled = False
    else:
        base_config.custom_model_directories = local_model_repository_path()
        base_config.custom_model_directories_enabled = True

    configuration = ImportDataConfiguration()
    if tool == DbIliMode.ili2pg:
        configuration.dbhost = os.environ.get('PG_HOST')
        configuration.dbusr = os.environ.get('PG_USER')
        configuration.dbpwd = os.environ.get('PG_PASSWORD')
        configuration.database = os.environ.get('PG_DB')
    elif tool == DbIliMode.ili2gpkg:
        configuration.dbfile = get_resource_path("geopackage/test_export.gpkg")
    configuration.base_configuration = base_config

    return configuration


def iliupdater_config(tool=DbIliMode.ili2pg, modeldir=None):
    base_config = BaseConfiguration()
    if modeldir is None:
        base_config.custom_model_directories_enabled = False
    else:
        base_config.custom_model_directories = local_model_repository_path()
        base_config.custom_model_directories_enabled = True

    configuration = UpdateDataConfiguration()
    if tool == DbIliMode.ili2pg:
        configuration.dbhost = os.environ.get('PG_HOST')
        configuration.dbusr = os.environ.get('PG_USER')
        configuration.dbpwd = os.environ.get('PG_PASSWORD')
        configuration.database = os.environ.get('PG_DB')

    configuration.base_configuration = base_config

    return configuration


def ilivalidator_config(
    tool=DbIliMode.ili2pg, modeldir=None, gpkg_path="geopackage/test_validate.gpkg"
):
    base_config = BaseConfiguration()
    if modeldir is None:
        base_config.custom_model_directories_enabled = False
    else:
        base_config.custom_model_directories = local_model_repository_path()
        base_config.custom_model_directories_enabled = True

    configuration = ValidateConfiguration()
    if tool == DbIliMode.ili2pg:
        configuration.dbhost = os.environ.get('PG_HOST')
        configuration.dbusr = os.environ.get('PG_USER')
        configuration.dbpwd = os.environ.get('PG_PASSWORD')
        configuration.database = os.environ.get('PG_DB')
    elif tool == DbIliMode.ili2gpkg:
        configuration.dbfile = get_resource_path(gpkg_path)
    configuration.base_configuration = base_config

    return configuration


def local_model_repository_path(path):
    basepath = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(basepath, 'resources', 'models')

def remote_model_repository_url(path):
    uri_repository = 'https://ceicol.com/models/'
    return uri_repository
