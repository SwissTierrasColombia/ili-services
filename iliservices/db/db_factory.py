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
from abc import ABC


class DBFactory(ABC):
    """
    Abstract class
    """
    def __init__(self):
        self._engine = None

    def get_id(self):
        return self._engine

    def get_name(self):
        raise NotImplementedError

    def get_model_baker_db_ili_mode(self):
        raise NotImplementedError

    def get_db_connector(self, parameters=dict()):
        raise NotImplementedError

    def set_ili2db_configuration_params(self, params, configuration):
        raise NotImplementedError
