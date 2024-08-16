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
import os
import sqlite3

from ..config.enums import EnumTestConnectionMsg
from ..config.ili2db_keys import *
from ..config.ili2db_names import ILI2DBNames
from .db_connector import (FileDB,
                           DBConnector)

import logging

logger = logging.getLogger(__name__)


class GPKGConnector(FileDB):

    _PROVIDER_NAME = 'ogr'
    _DEFAULT_VALUES = {
        'dbfile': ''
    }

    def __init__(self, uri, conn_dict=dict()):
        DBConnector.__init__(self, uri, conn_dict)
        self.engine = 'gpkg'
        self.conn = None
        self.provider = 'ogr'

    @DBConnector.uri.setter
    def uri(self, value):
        self._dict_conn_params = {'dbfile': value}
        self._uri = value

    def _get_ili2db_names(self):
        dict_names = dict()
        # Custom names
        dict_names[T_ID_KEY] = "T_Id"
        dict_names[T_ILI_TID_KEY] = "T_Ili_Tid"
        dict_names[DISPLAY_NAME_KEY] = "dispName"
        dict_names[ILICODE_KEY] = "iliCode"
        dict_names[DESCRIPTION_KEY] = "description"
        dict_names[THIS_CLASS_KEY] = "thisClass"
        dict_names[T_BASKET_KEY] = "T_basket"
        dict_names[T_ILI2DB_BASKET_KEY] = "T_ILI2DB_BASKET"
        dict_names[T_ILI2DB_DATASET_KEY] = "T_ILI2DB_DATASET"
        dict_names[DATASET_T_DATASETNAME_KEY] = "datasetName"
        dict_names[BASKET_T_DATASET_KEY] = "dataset"
        dict_names[BASKET_T_TOPIC_KEY] = "topic"
        dict_names[BASKET_T_ATTACHMENT_KEY] = "attachmentKey"

        return dict_names

    def _table_exists(self, table_name):
        if self.conn is None:
            res, msg = self.open_connection()
            if not res:
                logger.warning(msg)
                return False

        cursor = self.conn.cursor()
        cursor.execute("""SELECT * from pragma_table_info('{}');""".format(table_name))

        return bool(cursor.fetchall())

    def _metadata_exists(self):
        return self._table_exists(ILI2DBNames.INTERLIS_TEST_METADATA_TABLE_PG)

    def has_basket_col(self):
        if self.conn is None:
            res, msg = self.open_connection()
            if not res:
                logger.warning(msg)
                return False

        cursor = self.conn.cursor()
        cursor.execute("""SELECT *
                          FROM t_ili2db_settings
                          WHERE tag='{}' AND setting='{}';""".format(ILI2DBNames.BASKET_COL_TAG, ILI2DBNames.BASKET_COL_VALUE))

        return bool(cursor.fetchall())

    def get_models(self):
        if self.conn is None:
            res, msg = self.open_connection()
            if not res:
                logger.warning(msg)
                return list()

        # First go for all models registered in t_ili2db_model
        cursor = self.conn.cursor()
        result = cursor.execute("""SELECT modelname FROM t_ili2db_model;""")
        model_hierarchy = dict()
        if result is not None:
            all_models = [db_model['modelname'] for db_model in result]
            model_hierarchy = self._parse_models_from_db_meta_attrs(all_models)

        # Now go for all models listed in t_ili2db_trafo
        result = cursor.execute("""SELECT distinct substr(iliname, 1, pos-1) AS modelname from 
                                   (SELECT *, instr(iliname,'.') AS pos FROM t_ili2db_trafo)""")
        trafo_models = list()
        if result is not None:
            trafo_models = [db_model['modelname'] for db_model in result]

        # Finally, using those obtained from t_ili2db_trafo, go for dependencies found in t_ili2db_model
        dependencies = list()
        for model in trafo_models:
            dependencies.extend(model_hierarchy.get(model, list()))

        res_models = list(set(dependencies + trafo_models))
        logger.debug("Models found: {}".format(res_models))

        return res_models

    def get_description_conn_string(self):
        result = None
        if self.dict_conn_params['dbfile']:
            result = os.path.basename(self.dict_conn_params['dbfile'])
        return result

    def get_connection_uri(self, dict_conn, level=1):
        return dict_conn['dbfile']

    def open_connection(self):
        if os.path.exists(self._uri) and os.path.isfile(self._uri):
            if self.conn:
                self.close_connection()

            self.conn = sqlite3.connect(self._uri)
            self.conn.row_factory = sqlite3.Row
            logger.info("Connection was open! ({})".format(self._uri))
            return (True, "Connection is open!")
        elif not os.path.exists(self._uri):
            return (False, "Connection could not be open! The file ('{}') does not exist!".format(self._uri))
        elif os.path.isdir(self._uri):
            return (False, "Connection could not be open! The URI ('{}') is not a file!".format(self._uri))

    def close_connection(self):
        if self.conn:
            self.conn.close()
            logger.info("Connection was closed! ({})".format(self._uri))
            self.conn = None

    def get_ili2db_version(self):
        if self.conn is None:
            res, msg = self.open_connection()
            if not res:
                logger.warning(msg)
                return -1

        cur = self.conn.cursor()
        cur.execute("""SELECT * from pragma_table_info('t_ili2db_attrname') WHERE name='owner';""")
        if cur.fetchall():
            return 3
        else:
            return 4  # ili2db 4 renamed such column to ColOwner

    def _test_db_file(self, is_schema_import=False):
        uri = self._uri

        # The most basic check first :)
        if not os.path.splitext(uri)[1] == ".gpkg":
            return False, EnumTestConnectionMsg.WRONG_FILE_EXTENSION, "The file should have the '.gpkg' extension!"

        # First we do a very basic check, looking that the directory or file exists
        if is_schema_import:
            # file does not exist, but directory must exist
            directory = os.path.dirname(uri)

            if not os.path.exists(directory):
                return False, EnumTestConnectionMsg.DIR_NOT_FOUND, "GeoPackage directory not found."
        else:
            if not os.path.exists(uri):
                return False, EnumTestConnectionMsg.GPKG_FILE_NOT_FOUND, "GeoPackage file not found."

        return True, EnumTestConnectionMsg.CONNECTION_TO_SERVER_SUCCESSFUL, "Connection to server was successful."

    def _test_connection_to_db(self):
        if self.conn:
            self.close_connection()

        res, msg = self.open_connection()
        if res:
            return True, EnumTestConnectionMsg.CONNECTION_TO_DB_SUCCESSFUL, "Connection to db was successful."
        else:
            return False, EnumTestConnectionMsg.CONNECTION_COULD_NOT_BE_OPEN, msg

    def _test_connection_to_interlis_model(self, models):
        database = os.path.basename(self._dict_conn_params['dbfile'])
        if not self._metadata_exists():
            return False, EnumTestConnectionMsg.INTERLIS_META_ATTRIBUTES_NOT_FOUND, "The database '{}' is not a valid INTERLIS database. That is, the database doesn't have the structure of the INTERLIS model.".format(database)

        if self.get_ili2db_version() != 4:
            return False, EnumTestConnectionMsg.INVALID_ILI2DB_VERSION, "The database '{}' was created with an old version of ili2db (v3), which is no longer supported. You need to migrate it to ili2db4.".format(database)

        return True, EnumTestConnectionMsg.DB_WITH_VALID_INTERLIS_STRUCTURE, "The database '{}' has a valid INTERLIS structure!".format(database)

    def execute_sql_query(self, query):
        """
        Generic function for executing SQL statements

        :param query: SQL Statement
        :return: List of RealDictRow
        """
        cursor = self.conn.cursor()

        try:
            cursor.execute(query)
            return True, cursor.fetchall()
        except sqlite3.ProgrammingError as e:
            return False, e

    def vacuum(self):
        """
        'Sanitize' the DB. See https://www.sqlite.org/lang_vacuum.html
        """
        # See http://bugs.python.org/issue28518
        self.conn.isolation_level = None
        cursor = self.conn.cursor()
        cursor.execute('VACUUM')
        cursor.close()
        self.conn.isolation_level = ''
