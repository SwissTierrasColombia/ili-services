import nose2
import unittest
import tempfile

from .utils import (get_pg_conn,
                    drop_pg_schema,
                    get_test_path,
                    get_test_copy_path, 
                    get_gpkg_conn_from_path)

from ..core.ili2db import Ili2DB

import logging
logger = logging.getLogger(__name__)



class TestIli2db(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.ili2db = Ili2DB()

        schema_name = 'ili2db'

        gpkg_path = get_test_copy_path('db/static/gpkg/ili2db.gpkg')
        gpkg_db = get_gpkg_conn_from_path(gpkg_path)

        drop_pg_schema(schema_name)
        pg_db = get_pg_conn(schema_name)

        cls.db_connections = {
            'gpkg': gpkg_db,
            'pg': pg_db
        }

    def test_ili2db(self):
        for db_engine, db in self.db_connections.items():
            print("\nINFO: Validating import schema, import data and export method in {}...".format(db_engine))

            # Run import schema
            models = ['Captura_Geo_V1_2']
            configuration = self.ili2db.get_import_schema_configuration(db, models, create_basket_col=True)
            res_schema_import, msg_schema_import = self.ili2db.import_schema(db, configuration)
            self.assertTrue(res_schema_import, msg_schema_import)

            # Run import data
            xtf_path = get_test_path("xtf/test_field_data_capture_1_2.xtf")
            configuration = self.ili2db.get_import_data_configuration(db, xtf_path)
            res_import_data, msg_import_data = self.ili2db.import_data(db, configuration)
            self.assertTrue(res_import_data, msg_import_data)

            # Export data
            xtf_export_path = tempfile.mktemp() + '.xtf'
            configuration = self.ili2db.get_export_configuration(db, xtf_export_path)
            res_export, msg_export = self.ili2db.export(db, configuration)
            self.assertTrue(res_export, msg_export)

            # Validate data
            xtf_log_path = tempfile.mktemp() + '.xtf'
            configuration = self.ili2db.get_validate_configuration(db, models, xtf_log_path, '')
            res_validation, msg_validation = self.ili2db.validate(db, configuration)
            self.assertTrue(res_validation, msg_validation)

    @classmethod
    def tearDownClass(cls):
        pass

if __name__ == '__main__':
    nose2.main()
