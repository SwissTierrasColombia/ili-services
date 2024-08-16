# -*- coding: utf-8 -*-
"""
/***************************************************************************
                              Asistente LADM_COL
                             --------------------
        begin                : 16/01/18
        git sha              : :%H$
        copyright            : (C) 2018 by Jorge Useche (Incige SAS)
        email                : naturalmentejorge@gmail.com
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
import psycopg2
import shutil

from ..config.config_db_supported import ConfigDBsSupported
from ..config.general_config import (ILISERVICES_DB_NAME,
                                     ILISERVICES_DB_USER,
                                     ILISERVICES_DB_PASS,
                                     ILISERVICES_DB_PORT,
                                     ILISERVICES_DB_HOST)


dbs_supported = ConfigDBsSupported()

def get_opened_db_connector_for_tests(db_engine, conn_dict):
    """
    This function is implemented for tests.
    """
    db_factory = dbs_supported.get_db_factory(db_engine)
    db = db_factory.get_db_connector(conn_dict)
    db.open_connection()

    return db

def get_pg_conn(schema):
    dict_conn = dict()
    dict_conn['host'] = ILISERVICES_DB_HOST
    dict_conn['port'] = ILISERVICES_DB_PORT
    dict_conn['database'] = ILISERVICES_DB_NAME
    dict_conn['schema'] = schema
    dict_conn['username'] = ILISERVICES_DB_USER
    dict_conn['password'] = ILISERVICES_DB_PASS

    db = get_opened_db_connector_for_tests('pg', dict_conn)

    return db

def drop_pg_schema(schema):
    print("\nDropping schema {}...".format(schema))
    db_connection = get_pg_conn(schema)
    print("Testing Connection...", db_connection.test_connection())
    cur = db_connection.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    query = cur.execute("""DROP SCHEMA IF EXISTS "{}" CASCADE;""".format(schema))
    db_connection.conn.commit()
    cur.close()
    print("Schema {} removed...".format(schema))
    db_connection.conn.close()
    if query is not None:
        print("The drop schema is not working")

def get_test_path(path):
    basepath = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(basepath, "resources", path)

def get_test_copy_path(path):
    src_path = get_test_path(path)
    dst_path = os.path.split(src_path)
    dst_path = os.path.join(dst_path[0], "_" + dst_path[1])
    shutil.copyfile(src_path, dst_path)
    return dst_path

def get_gpkg_conn_from_path(path):
    dict_conn = dict()
    dict_conn['dbfile'] = path
    db = get_opened_db_connector_for_tests('gpkg', dict_conn)

    return db