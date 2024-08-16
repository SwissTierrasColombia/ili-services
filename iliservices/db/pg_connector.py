# -*- coding: utf-8 -*-
"""
/***************************************************************************
                              Asistente LADM_COL
                             --------------------
        begin                : 2017-11-20
        git sha              : :%H$
        copyright            : (C) 2017 by Germán Carrillo (BSF Swissphoto)
        email                : gcarrillo@linuxmail.org
 ***************************************************************************/
/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License v3.0 as          *
 *   published by the Free Software Foundation.                            *
 *                                                                         *
 ***************************************************************************/
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import psycopg2.extras
from psycopg2 import ProgrammingError

from ..config.enums import (EnumTestLevel,
                          EnumUserLevel,
                          EnumTestConnectionMsg)

from .db_connector import (ClientServerDB,
                                  DBConnector)

from ..config.ili2db_names import ILI2DBNames
from ..config.ili2db_keys import *
from ..config.query_names import QueryNames

from ..config.general_config import (ILISERVICES_DB_NAME,
                                     ILISERVICES_DB_USER,
                                     ILISERVICES_DB_PASS,
                                     ILISERVICES_DB_PORT,
                                     ILISERVICES_DB_HOST)

import logging

logger = logging.getLogger(__name__)


class PGConnector(ClientServerDB):
    _PROVIDER_NAME = 'postgres'
    _DEFAULT_VALUES = {
        'host': ILISERVICES_DB_HOST,
        'port': ILISERVICES_DB_PORT,
        'database': ILISERVICES_DB_NAME,
        'username': ILISERVICES_DB_USER,
        'password': ILISERVICES_DB_PASS,
        'schema': ''
    }

    def __init__(self, uri, conn_dict=dict()):
        DBConnector.__init__(self, uri, conn_dict)
        self.engine = 'pg'
        self.conn = None
        self.schema = conn_dict['schema'] if 'schema' in conn_dict else ''
        self.provider = 'postgres'
        self._tables_info = None


    @DBConnector.uri.setter
    def uri(self, value):
        conn_params = value

        self._dict_conn_params = {
            'host': conn_params['host'],
            'port': conn_params['port'],
            'username': conn_params['username'],
            'password': conn_params['password'],
            'database': conn_params['database'],
            'schema': self.schema
        }

        self._uri = value


    def get_description_conn_string(self):
        result = None
        if self._dict_conn_params['database'] and self._dict_conn_params['database'].strip("'") and \
                self._dict_conn_params['schema']:
            result = self._dict_conn_params['database'] + '.' + self._dict_conn_params['schema']

        return result

    def _postgis_exists(self):
        # Todo: Use it in test_connection()
        cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("""
                    SELECT
                        count(extversion)
                    FROM pg_catalog.pg_extension
                    WHERE extname='postgis'
                    """)

        return bool(cur.fetchone()[0])

    def _schema_exists(self, schema=None):
        if schema is None:
            schema = self.schema

        if schema:
            cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute("""
                        SELECT EXISTS(SELECT 1 FROM pg_namespace WHERE nspname = '{}');
            """.format(schema))

            return bool(cur.fetchone()[0])

        return False

    def _table_exists(self, table_name):
        if self.schema:
            cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute("""
                        SELECT
                          count(tablename)
                        FROM pg_catalog.pg_tables
                        WHERE schemaname = '{}' and tablename = '{}'
            """.format(self.schema, table_name))

            return bool(cur.fetchone()[0])

        return False

    def _metadata_exists(self):
        return self._table_exists(ILI2DBNames.INTERLIS_TEST_METADATA_TABLE_PG)

    def has_basket_col(self):
        sql_query = """SELECT count(tag)
                       FROM {schema}.t_ili2db_settings
                       WHERE tag ='{tag}' and setting='{value}';""".format(schema=self.schema,
                                                                           tag=ILI2DBNames.BASKET_COL_TAG,
                                                                           value=ILI2DBNames.BASKET_COL_VALUE)
        cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(sql_query)
        return bool(cur.fetchone()[0])

    def open_connection(self, uri=None):
        if uri is None:
            uri = self._uri
        else:
            self.conn.close()

        if self.conn is None or self.conn.closed:
            try:
                self.conn = psycopg2.connect(uri)
            except (psycopg2.OperationalError, psycopg2.ProgrammingError) as e:
                return False, "Could not open connection! Details: {}".format(e)

            logger.info("Connection was open! ({})".format(self.get_description_conn_string()))
        else:
            logger.info("Connection is already open! ({})".format(self.get_description_conn_string()))

        return True, "Connection is open!"

    def close_connection(self):
        if self.conn:
            self.conn.close()
            logger.info("Connection was closed ({}) !".format(self.get_description_conn_string()))
            self.conn = None

    def _get_ili2db_names(self):
        dict_names = dict()
        # Add required key-value pairs that do not come from the DB query
        dict_names[T_ID_KEY] = "t_id"
        dict_names[T_ILI_TID_KEY] = "t_ili_tid"
        dict_names[DISPLAY_NAME_KEY] = "dispname"
        dict_names[ILICODE_KEY] = "ilicode"
        dict_names[DESCRIPTION_KEY] = "description"
        dict_names[THIS_CLASS_KEY] = "thisclass"
        dict_names[T_BASKET_KEY] = "t_basket"
        dict_names[T_ILI2DB_BASKET_KEY] = "t_ili2db_basket"
        dict_names[T_ILI2DB_DATASET_KEY] = "t_ili2db_dataset"
        dict_names[DATASET_T_DATASETNAME_KEY] = "datasetname"
        dict_names[BASKET_T_DATASET_KEY] = "dataset"
        dict_names[BASKET_T_TOPIC_KEY] = "topic"
        dict_names[BASKET_T_ATTACHMENT_KEY] = "attachmentkey"

        return dict_names

    def check_and_fix_connection(self):
        if self.conn is None or self.conn.closed:
            res, code, msg = self.test_connection()
            if not res:
                return res, msg

        if self.conn.get_transaction_status() == psycopg2.extensions.TRANSACTION_STATUS_INERROR:  # 3
            self.conn.rollback()  # Go back to TRANSACTION_STATUS_IDLE (0)
            if self.conn.get_transaction_status() != psycopg2.extensions.TRANSACTION_STATUS_IDLE:
                return (False, "Error: PG transaction had an error and couldn't be recovered...")

        return True, ''

    def execute_sql_query(self, query):
        """
        Generic function for executing SQL statements
        :param query: SQL Statement
        :return: List of RealDictRow
        """
        res, msg = self.check_and_fix_connection()
        if not res:
            return res, msg

        cur = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        try:
            cur.execute(query)
            return True, cur.fetchall()
        except ProgrammingError as e:
            return False, e

    def execute_sql_query_dict_cursor(self, query):
        """
        Generic function for executing SQL statements
        :param query: SQL Statement
        :return: List of DictRow
        """
        res, msg = self.check_and_fix_connection()
        if not res:
            return (res, msg)

        cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(query)
        return cur.fetchall()

    def get_models(self, schema=None):
        # First go for all models registered in t_ili2db_model
        query = "SELECT modelname FROM {schema}.t_ili2db_model".format(schema=schema if schema else self.schema)
        res, result = self.execute_sql_query(query)
        model_hierarchy = dict()
        if res:
            all_models = [db_model['modelname'] for db_model in result]
            model_hierarchy = self._parse_models_from_db_meta_attrs(all_models)
        else:
            logger.error("Error getting models: {}".format(result))

        # Now go for all models listed in t_ili2db_trafo
        query = "SELECT distinct split_part(iliname,'.',1) as modelname FROM {schema}.t_ili2db_trafo".format(
            schema=schema if schema else self.schema)
        res, result = self.execute_sql_query(query)
        trafo_models = list()
        if res:
            trafo_models = [db_model['modelname'] for db_model in result]

        # Finally, using those obtained from t_ili2db_trafo, go for dependencies found in t_ili2db_model
        dependencies = list()
        for model in trafo_models:
            dependencies.extend(model_hierarchy.get(model, list()))

        res_models = list(set(dependencies + trafo_models))
        logger.debug("Models found: {}".format(res_models))

        return res_models

    def create_database(self, uri, db_name):
        """
        Create a database
        :param uri: (str) Connection uri only: (host, port, user, pass)
        :param db_name: (str) Database name to be created
        :return: tuple(bool, str)
            bool: True if everything was executed successfully and False if not
            str: Message to the user indicating the type of error or if everything was executed correctly
        """
        sql = """CREATE DATABASE "{}" WITH ENCODING = 'UTF8' CONNECTION LIMIT = -1""".format(db_name)
        conn = psycopg2.connect(uri)

        if conn:
            try:
                conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
                cur = conn.cursor()
                cur.execute(sql)
            except psycopg2.ProgrammingError as e:
                return (False, "An error occurred while trying to create the '{}' database: {}".format(db_name, e))
        cur.close()
        conn.close()
        return (True, "Database '{}' was successfully created!".format(db_name))

    def create_schema(self, uri, schema_name):
        """
        Create a schema
        :param uri:  (str) connection uri only: (host, port, user, pass, db)
        :param schema_name: (str) schema name to be created
        :return: tuple(bool, str)
            bool: True if everything was executed successfully and False if not
            str: Message to the user indicating the type of error or if everything was executed correctly
        """
        sql = 'CREATE SCHEMA "{}"'.format(schema_name)
        conn = psycopg2.connect(uri)

        if conn:
            try:
                conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
                cur = conn.cursor()
                cur.execute(sql)
            except psycopg2.ProgrammingError as e:
                return (False, "An error occurred while trying to create the '{}' schema: {}".format(schema_name, e))
        cur.close()
        conn.close()
        return (True, "Schema '{}' was successfully created!".format(schema_name))

    def get_dbnames_list(self, uri):
        res, code, msg = self.test_connection(EnumTestLevel.SERVER_OR_FILE)
        if not res:
            return (False, msg)

        dbnames_list = list()
        try:
            conn = psycopg2.connect(uri)
            cur = conn.cursor()
            query = """SELECT datname FROM pg_database WHERE datistemplate = false AND datname <> 'postgres' ORDER BY datname"""
            cur.execute(query)
            dbnames = cur.fetchall()
            for dbname in dbnames:
                dbnames_list.append(dbname[0])
            cur.close()
            conn.close()
        except Exception as e:
            return (False, "There was an error when obtaining the list of existing databases. : {}".format(e))
        return (True, dbnames_list)

    def get_dbname_schema_list(self, uri):
        schemas_list = list()
        try:
            conn = psycopg2.connect(uri)
            cur = conn.cursor()
            query = """
                SELECT n.nspname as "{schema_name}" FROM pg_catalog.pg_namespace n 
                WHERE n.nspname !~ '^pg_' AND n.nspname <> 'information_schema' AND nspname <> 'public' ORDER BY "{schema_name}"
            """.format(schema_name=QueryNames.SCHEMA_NAME)
            cur.execute(query)
            schemas = cur.fetchall()
            for schema in schemas:
                schemas_list.append(schema[0])
            cur.close()
            conn.close()
        except Exception as e:
            return (False, "There was an error when obtaining the list of existing schemas: {}".format(e))
        return (True, schemas_list)

    def has_schema_privileges(self, uri, schema, user_level=EnumUserLevel.CREATE):
        try:
            conn = psycopg2.connect(uri)
            cur = conn.cursor()
            query = """
                        SELECT
                            CASE WHEN pg_catalog.has_schema_privilege(current_user, '{schema}', 'CREATE') = True  THEN 1 ELSE 0 END AS "create",
                            CASE WHEN pg_catalog.has_schema_privilege(current_user, '{schema}', 'USAGE')  = True  THEN 1 ELSE 0 END AS "usage";
                    """.format(schema=schema)

            cur.execute(query)
            schema_privileges = cur.fetchone()
            if schema_privileges:
                privileges = {'create': bool(int(schema_privileges[0])),  # 'create'
                              'usage': bool(int(schema_privileges[1]))}  # 'usage'
            else:
                return False, "No information for schema '{}'.".format(schema)
            cur.close()
            conn.close()
        except Exception as e:
            return False, "There was an error when obtaining privileges for schema '{}'. Details: {}".format(schema, e)

        if user_level == EnumUserLevel.CREATE and privileges['create'] and privileges['usage']:
            return True, "The user has both Create and Usage privileges over the schema."
        elif user_level == EnumUserLevel.CONNECT and privileges['usage']:
            return True, "The user has Usage privileges over the schema."
        else:
            return False, "The user has not enough privileges over the schema."


    def get_connection_uri(self, dict_conn, level=1):
        uri = []
        uri += ['host={}'.format(dict_conn['host'])]
        uri += ['port={}'.format(dict_conn['port'])]
        if dict_conn['username']:
            uri += ['user={}'.format(dict_conn['username'])]
        if dict_conn['password']:
            uri += ['password={}'.format(dict_conn['password'])]
        if level == 1 and dict_conn['database']:
            uri += ['dbname={}'.format(dict_conn['database'])]
        else:
            # It is necessary to define the database name for listing databases
            # PostgreSQL uses the db 'postgres' by default and it cannot be deleted, so we use it as last resort
            uri += ["dbname={}".format(self._PROVIDER_NAME)]

        return ' '.join(uri)

    def get_ili2db_version(self):
        res, msg = self.check_and_fix_connection()
        if not res:
            return (res, msg)

        # Borrowed from Model Baker
        cur = self.conn.cursor()
        cur.execute("""SELECT *
                       FROM information_schema.columns
                       WHERE table_schema = '{schema}'
                       AND(table_name='t_ili2db_attrname' OR table_name='t_ili2db_model' )
                       AND(column_name='owner' OR column_name = 'file' )
                    """.format(schema=self.schema))
        if cur.rowcount > 1:
            return 3
        else:
            return 4

    def _test_connection_to_server(self):
        uri = self.get_connection_uri(self._dict_conn_params, 0)
        res, msg = self.open_connection()
        if res:
            return True, EnumTestConnectionMsg.CONNECTION_TO_SERVER_SUCCESSFUL, "Connection to server was successful."
        else:
            return False, EnumTestConnectionMsg.CONNECTION_TO_SERVER_FAILED, msg

    def _test_connection_to_db(self):
        if not self._dict_conn_params['database'].strip("'") or self._dict_conn_params['database'] == 'postgres':
            return False, EnumTestConnectionMsg.DATABASE_NOT_FOUND, "You should first select a database."

        # Client side check
        if self.conn is None or self.conn.closed:
            res, msg = self.open_connection()
            if not res:
                return res, EnumTestConnectionMsg.CONNECTION_COULD_NOT_BE_OPEN, msg
        if self.conn.get_transaction_status() == psycopg2.extensions.TRANSACTION_STATUS_INERROR:  # 3
            self.conn.rollback()  # Go back to TRANSACTION_STATUS_IDLE (0)

        try:
            # Server side check
            cur = self.conn.cursor()
            cur.execute('SELECT 1')  # This query will fail if the db is no longer connected
            cur.close()
        except psycopg2.OperationalError:
            # Reopen the connection if it is closed due to timeout
            self.conn.close()
            res, msg = self.open_connection()
            if not res:
                return res, EnumTestConnectionMsg.CONNECTION_COULD_NOT_BE_OPEN, msg

        return True, EnumTestConnectionMsg.CONNECTION_TO_DB_SUCCESSFUL, "Connection to the database was successful."

    def _test_connection_to_schema(self, user_level):
        if not self._dict_conn_params['schema'] or self._dict_conn_params['schema'] == '':
            return False, EnumTestConnectionMsg.SCHEMA_NOT_FOUND, "You should first select a schema."

        if not self._schema_exists():
            return False, EnumTestConnectionMsg.SCHEMA_NOT_FOUND, "The schema '{}' does not exist in the database!".format(self.schema)

        res, msg = self.has_schema_privileges(self._uri, self.schema, user_level)
        if not res:
            return False, EnumTestConnectionMsg.USER_HAS_NO_PERMISSION, "User '{}' has not enough permissions over the schema '{}'.".format(self._dict_conn_params['username'], self.schema)

        return True, EnumTestConnectionMsg.CONNECTION_TO_SCHEMA_SUCCESSFUL, "Connection to the database schema was successful."

    def _test_connection_to_interlis_model(self, models):
        if not self._metadata_exists():
            return False, EnumTestConnectionMsg.INTERLIS_META_ATTRIBUTES_NOT_FOUND, "The schema '{}' is not a valid INTERLIS schema. That is, the schema doesn't have the structure of the INTERLIS model.".format(self.schema)

        if self.get_ili2db_version() != 4:
            return False, EnumTestConnectionMsg.INVALID_ILI2DB_VERSION, "The DB schema '{}' was created with an old version of ili2db (v3), which is no longer supported. You need to migrate it to ili2db4.".format(self.schema)

        return True, EnumTestConnectionMsg.SCHEMA_WITH_VALID_INTERLIS_STRUCTURE, "The schema '{}' has a valid INTERLIS structure!".format(self.schema)
