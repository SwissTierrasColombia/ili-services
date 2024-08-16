"""
/***************************************************************************
                              -------------------
        begin                : 30.05.2024
        git sha              : :%H$
        copyright            : (C) 2024 by Leonardo Cardona
        email                : contacto at ceicol com
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

import subprocess
import logging

import locale
import re

from PyQt5.QtCore import QObject, pyqtSignal

from ..ili2dbutils import get_java_path
from .ilivalidatorutils import get_ilivalidator_bin
from .ilivalidatorconfig import IliValidatorConfiguration

logger = logging.getLogger(__name__)


class IliValidator(QObject):
    SUCCESS = 0
    ERROR = 1000
    ILIVALIDATOR_NOT_FOUND = 1001

    stdout = pyqtSignal(str)
    stderr = pyqtSignal(str)

    __done_pattern = re.compile(r"Info: \.\.\.([a-z]+ )?done")
    __done_with_validation_errors = "...validate failed"
    __result = None

    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        self.configuration = IliValidatorConfiguration()
        _, self.encoding = locale.getlocale()

        # Lets python try to determine the default locale
        if not self.encoding:
            _, self.encoding = locale.getdefaultlocale()

        # This might be unset
        # (https://stackoverflow.com/questions/1629699/locale-getlocale-problems-on-osx)
        if not self.encoding:
            self.encoding = "UTF8"

    def _ilivalidator_jar_arg(self):
        ilivalidator_bin = get_ilivalidator_bin()
        if not ilivalidator_bin:
            return self.ILIVALIDATOR_NOT_FOUND
        return ["-jar", ilivalidator_bin]

    @staticmethod
    def _escaped_arg(argument):
        if '"' in argument:
            argument = argument.replace('"', '"""')
        if " " in argument:
            argument = '"' + argument + '"'
        return argument

    def command(self):
        ilivalidator_jar_arg = self._ilivalidator_jar_arg()
        args = self.configuration.to_ilivalidator_args()

        java_path = self._escaped_arg(
            get_java_path(self.configuration)
        )
        command_args = ilivalidator_jar_arg + args

        valid_args = []
        for command_arg in command_args:
            valid_args.append(self._escaped_arg(command_arg))

        command = java_path + " " + " ".join(valid_args)

        return command

    def _prepare_command(self):
        """Prepares and returns the command to be executed along with its arguments."""
        java_path = get_java_path(self.configuration)
        ilivalidator_jar_arg = self._ilivalidator_jar_arg()
        if ilivalidator_jar_arg == self.ILIVALIDATOR_NOT_FOUND:
            return self.ILIVALIDATOR_NOT_FOUND

        args = self.configuration.to_ilivalidator_args()
        return [java_path] + ilivalidator_jar_arg + args

    def run(self):
        """Executes the configured command asynchronously."""
        command = self._prepare_command()
        self.__result = self.ERROR

        logger.debug(command)
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        msg_stdout = stdout.decode(self.encoding)
        msg_stderr = stderr.decode(self.encoding)

        logger.debug('stdout')
        logger.debug(msg_stdout)

        logger.debug('stderr')
        logger.debug(msg_stderr)

        if msg_stderr.strip().endswith(self.__done_with_validation_errors):
            self.__result = self.ERROR
            return self.__result

        if self.__done_pattern.search(msg_stderr):
            self.__result = self.SUCCESS

        exit_code = process.returncode
        self.__result = self.SUCCESS if exit_code == 0 else self.ERROR

        return self.__result
