import os
from subprocess import call

from libs.modelbaker.iliwrapper.globals import DbIliMode
from libs.modelbaker.db_factory.db_simple_factory import DbSimpleFactory
from libs.modelbaker.iliwrapper.ili2dbconfig import ExportConfiguration
from utils.file_utils import get_resource_path


def get_pg_conn(schema):
    myenv = os.environ.copy()

    call(
        [
            "pg_restore",
            "-Fc",
            "-h" + os.environ.get('PG_HOST'),
            "-U{}".format(os.environ.get('PG_USER')),
            "-d{}".format(os.environ.get('PG_DB')),
            get_resource_path("dumps/{}_dump".format(schema)),
        ],
        env=myenv,
    )

    db_factory = DbSimpleFactory().create_factory(DbIliMode.pg)
    configuration = ExportConfiguration()

    configuration.database = os.environ.get('PG_DB')
    configuration.dbhost = os.environ.get('PG_HOST')
    configuration.dbusr = os.environ.get('PG_USER')
    configuration.dbpwd = os.environ.get('PG_PASSWORD')
    configuration.dbport = os.environ.get('PG_PORT')

    config_manager = db_factory.get_db_command_config_manager(configuration)
    db_connector = db_factory.get_db_connector(config_manager.get_uri(), schema)
    return db_connector

def get_pg_connection_string():
    return "dbname={pg_db} user={pg_user} password={pg_password} host={pg_host}".format(
        pg_db=os.environ.get('PG_DB'),
        pg_user=os.environ.get('PG_USER'),
        pg_password=os.environ.get('PG_PASSWORD'),
        pg_host=os.environ.get('PG_HOST')
    )

def get_gpkg_conn(gpkg):
    db_factory = DbSimpleFactory().create_factory(DbIliMode.gpkg)
    db_connector = db_factory.get_db_connector(
        get_resource_path("geopackage/{}.gpkg".format(gpkg)), None
    )
    return db_connector

