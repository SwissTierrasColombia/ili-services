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
from PyQt5.QtCore import QObject

from ..config.enums import (EnumTestLevel,
                            EnumUserLevel,
                            EnumTestConnectionMsg)


class DBConnector(QObject):
    """
    Superclass for all DB connectors.
    """
    _DEFAULT_VALUES = dict()  # You should set it, so that testing empty parameters can be handled easily.

    def __init__(self, uri, conn_dict=dict()):
        QObject.__init__(self)
        self.engine = ''
        self.provider = '' # QGIS provider name. e.g., postgres
        self._uri = None
        self.schema = None
        self.conn = None
        self._dict_conn_params = None

        if uri is not None:
            self.uri = uri
        else:
            self.dict_conn_params = conn_dict

    @property
    def dict_conn_params(self):
        return self._dict_conn_params.copy()

    @dict_conn_params.setter
    def dict_conn_params(self, dict_values):
        dict_values = {k:v for k,v in dict_values.items() if v}  # To avoid empty values to overwrite default values
        self._dict_conn_params = self._DEFAULT_VALUES.copy()
        self._dict_conn_params.update(dict_values)
        self._uri = self.get_connection_uri(self._dict_conn_params, level=1)

    @property
    def uri(self):
        return self._uri

    @uri.setter
    def uri(self, value):
        raise NotImplementedError

    def equals(self, db):
        return self.dict_conn_params == db.dict_conn_params

    def _table_exists(self, table_name):
        raise NotImplementedError

    def _metadata_exists(self):
        raise NotImplementedError

    def has_basket_col(self):
        raise NotImplementedError

    def close_connection(self):
        raise NotImplementedError

    def get_description(self):
        return "Current connection details: '{}' -> {} {}".format(
            self.engine,
            self._uri,
            'schema:{}'.format(self.schema) if self.schema else '')

    def get_models(self, schema=None):
        raise NotImplementedError

    def get_display_conn_string(self):
        # Do not use to connect to a DB, only for display purposes
        tmp_dict_conn_params = self._dict_conn_params.copy()
        if 'password' in tmp_dict_conn_params:
            del tmp_dict_conn_params['password']

        return ' '.join(["{}={}".format(k, v) for k, v in tmp_dict_conn_params.items()])

    def get_description_conn_string(self):
        raise NotImplementedError

    def get_connection_uri(self, dict_conn, level=1):
        """
        :param dict_conn: (dict) dictionary with the parameters to establish a connection
        :param level: (int) At what level the connection will be established
            0: server level
            1: database level
        :return: (str) string uri to establish a connection
        """
        raise NotImplementedError

    def get_ili2db_version(self):
        raise NotImplementedError

    def _get_ili2db_names(self):
        """Returns field common names of databases, e.g., T_Id, T_Ili_Tid, dispName, t_basket, etc.

        :return: Dictionary with ili2db keys:
                 T_ID_KEY, T_ILI_TID_KEY, etc., from db_mapping_registry
        """
        raise NotImplementedError

    def open_connection(self):
        """
        :return: Whether the connection is opened after calling this method or not
        """
        raise NotImplementedError

    def test_connection(self, test_level=EnumTestLevel.INTERLIS, user_level=EnumUserLevel.CONNECT, models={}):
        """
        'Template method' subclasses should overwrite it, proposing their own way to test a connection.
        """
        raise NotImplementedError

    def _test_connection_to_db(self):
        raise NotImplementedError

    def _test_connection_to_interlis_model(self, models):
        raise NotImplementedError

    @staticmethod
    def _parse_models_from_db_meta_attrs(lst_models):
        """
        Reads a list of models as saved by ili2db and  returns a dict of model dependencies.

        E.g.:
        INPUT-> ["D_G_C_V2_9_6{ LADM_COL_V1_2 ISO19107_PLANAS_V1} D_SNR_V2_9_6{ LADM_COL_V1_2} D_I_I_V2_9_6{ D_SNR_V2_9_6 D_G_C_V2_9_6}", "LADM_COL_V1_2"]
        OUTPUT-> {'D_G_C_V2_9_6': ['LADM_COL_V1_2', 'ISO19107_PLANAS_V1'], 'D_SNR_V2_9_6': ['LADM_COL_V1_2'], 'D_I_I_V2_9_6': ['D_SNR_V2_9_6', 'D_G_C_V2_9_6'], 'LADM_COL_V1_2': []}

        :param lst_models: The list of values stored in the DB meta attrs model table (column 'modelname').
        :return: Dict of model dependencies.
        """
        model_hierarchy = dict()
        for str_model in lst_models:
            parts = str_model.split("}")
            if len(parts) > 1:  # With dependencies
                for part in parts:
                    if part:  # The last element of parts is ''
                        model, dependencies = part.split("{")
                        model_hierarchy[model.strip()] = dependencies.strip().split(" ")
            elif len(parts) == 1:  # No dependencies
                model_hierarchy[parts[0].strip()] = list()

        return model_hierarchy


class FileDB(DBConnector):
    """
    DB engines consisting of a single file, like GeoPackage, should inherit from this class.
    """
    def _test_db_file(self, is_schema_import=False):
        """
        Checks that the db file is accessible. Subclasses might use the is_schema_import parameter to know how far they
        should check. For instance, a DB file might not exist before a SCHEMA IMPORT operation.

        :param is_schema_import: boolean to indicate whether the tests is for a schema_import operation or not
        :return: boolean, was the connection successful?
        """
        raise NotImplementedError

    def test_connection(self, test_level=EnumTestLevel.INTERLIS, user_level=EnumUserLevel.CONNECT, models={}):
        """We check several levels in order:
            1. FILE SERVER (DB file)
            2. DB
            3. ili2db's SCHEMA_IMPORT
            4. INTERLIS

        Note that we don't check connection to SCHEMAs here.

        :param test_level: (EnumTestLevel) level of connection with postgres
        :param user_level: (EnumUserLevel) level of permissions a user has
        :param models: A dict of model prefixes that are required for this DB connection. If key is REQUIRED_MODELS,
                       models are mandatory, whereas if keys are ROLE_SUPPORTED_MODELS and ROLE_HIDDEN_MODELS, we test
                       the DB has at list all hidden (base) models and at least one non-hidden one.
        :return Triple: boolean result, message code, message text
        """
        is_schema_import = bool(test_level & EnumTestLevel.SCHEMA_IMPORT)
        res, code, msg = self._test_db_file(is_schema_import)
        if not res or test_level == EnumTestLevel.SERVER_OR_FILE or is_schema_import:
            return res, code, msg

        res, code, msg = self._test_connection_to_db()

        if not res or test_level == EnumTestLevel.DB or test_level == EnumTestLevel.DB_FILE:
            return res, code, msg

        res, code, msg = self._test_connection_to_interlis_model(models)

        if not res or test_level == EnumTestLevel.INTERLIS:
            return res, code, msg

        return False, EnumTestConnectionMsg.UNKNOWN_CONNECTION_ERROR, "There was a problem checking the connection. Most likely due to invalid or not supported test_level!"


class ClientServerDB(DBConnector):
    """
    DB engines consisting of client-server connections, like PostgreSQL, should inherit from this class.
    """
    def _test_connection_to_server(self):
        raise NotImplementedError

    def _test_connection_to_schema(self, user_level):
        raise NotImplementedError

    def test_connection(self, test_level=EnumTestLevel.INTERLIS, user_level=EnumUserLevel.CONNECT, models={}):
        """We check several levels in order:
            1. SERVER
            2. DB
            3. SCHEMA
            4. ili2db's SCHEMA_IMPORT
            5. INTERLIS

        :param test_level: (EnumTestLevel) level of connection with postgres
        :param user_level: (EnumUserLevel) level of permissions a user has
        :param models: A list of model prefixes that are required for this DB connection. If key is REQUIRED_MODELS,
                       models are mandatory, whereas if keys are ROLE_SUPPORTED_MODELS and ROLE_HIDDEN_MODELS, we test
                       the DB has at list all hidden (base) models and at least one non-hidden one.
        :return Triple: boolean result, message code, message text
        """
        if test_level == EnumTestLevel.SERVER_OR_FILE:
            return self._test_connection_to_server()

        res, code, msg = self._test_connection_to_db()

        if not res or test_level == EnumTestLevel.DB:
            return res, code, msg

        res, code, msg = self._test_connection_to_schema(user_level)

        if test_level & EnumTestLevel.SCHEMA_IMPORT:
            return True, EnumTestConnectionMsg.CONNECTION_TO_DB_SUCCESSFUL_NO_LADM_COL, "Connection successful!"

        if not res or test_level == EnumTestLevel.DB_SCHEMA:
            return res, code, msg

        res, code, msg = self._test_connection_to_interlis_model(models)

        if not res or test_level == EnumTestLevel.INTERLIS:
            return res, code, msg

        return False, EnumTestConnectionMsg.UNKNOWN_CONNECTION_ERROR, "There was a problem checking the connection. Most likely due to invalid or not supported test_level!"
    def execute_sql_query(self, query):
        raise NotImplementedError

    def vacuum(self):
        pass  # Up to now, only needed for GPKG
