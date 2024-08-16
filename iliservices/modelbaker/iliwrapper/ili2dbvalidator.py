"""
/***************************************************************************
                              -------------------
        begin                : 11/11/21
        git sha              : :%H$
        copyright            : (C) 2021 by Dave Signer
        email                : david at opengis ch
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from .ili2dbconfig import ValidateConfiguration
from .iliexecutable import IliExecutable


class Ili2dbValidator(IliExecutable):
    """
    Executes a validate operation using ili2db.
    Note: this is not iliValidator, but ili2db --validate.
    """
    SUCCESS_WITH_VALIDATION_ERRORS = 1
    __done_with_validation_errors = "...validate failed"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.version = 4

    def _create_config(self):
        return ValidateConfiguration()
        
    def _get_ili2db_version(self):
        return self.version
        
    def _args(self, hide_password):
        args = super()._args(hide_password)

        if self.version == 3 and "--export3" in args:
            args.remove("--export3")

        return args

    def _search_custom_pattern(self, text):
        if text.strip().endswith(self.__done_with_validation_errors):
            self._result = self.SUCCESS_WITH_VALIDATION_ERRORS