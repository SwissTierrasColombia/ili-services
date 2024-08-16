"""
/***************************************************************************
                              Asistente LADM-COL
                             --------------------
        begin                : 2019-02-21
        git sha              : :%H$
        copyright            : (C) 2019 by Yesid Polanía (BSF Swissphoto)
        email                : yesidpol.3@gmail.com
 ***************************************************************************/
/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License v3.0 as          *
 *   published by the Free Software Foundation.                            *
 *                                                                         *
 ***************************************************************************/
"""
from .db_factory import DBFactory
from ..modelbaker.iliwrapper.globals import DbIliMode
from .gpkg_connector import GPKGConnector


class GPKGFactory(DBFactory):
    def __init__(self):
        DBFactory.__init__(self)
        self._engine = "gpkg"

    def get_name(self):
        return 'GeoPackage'

    def get_model_baker_db_ili_mode(self):
        return DbIliMode.ili2gpkg

    def get_db_connector(self, parameters={}):
        return GPKGConnector(None, conn_dict=parameters)

    def set_ili2db_configuration_params(self, params, configuration):
        configuration.tool_name = 'gpkg'
        configuration.dbfile = params['dbfile']
