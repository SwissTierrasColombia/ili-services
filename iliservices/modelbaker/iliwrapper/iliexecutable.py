"""
/***************************************************************************
    begin                :    09/09/23
    git sha              :    :%H$
    copyright            :    (C) 2020 by Yesid Polania
    email                :    yesidpol.3@gmail.com
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
from abc import abstractmethod

from PyQt5.QtCore import QObject, pyqtSignal

from ..utils.qt_utils import AbstractQObjectMeta
from .ili2dbargs import get_ili2db_args
from .ili2dbconfig import Ili2DbCommandConfiguration
from .ili2dbutils import get_ili2db_bin, get_java_path

logger = logging.getLogger(__name__)


class IliExecutable(QObject, metaclass=AbstractQObjectMeta):
    SUCCESS = 0
    # TODO: Insert more codes?
    ERROR = 1000
    ILI2DB_NOT_FOUND = 1001

    stdout = pyqtSignal(str)
    stderr = pyqtSignal(str)

    __done_pattern = re.compile(r"Info: \.\.\.([a-z]+ )?done")
    __result = None

    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        self.filename = None
        self.tool = None
        self.configuration = self._create_config()
        _, self.encoding = locale.getlocale()

        # Lets python try to determine the default locale
        if not self.encoding:
            _, self.encoding = locale.getdefaultlocale()

        # This might be unset
        # (https://stackoverflow.com/questions/1629699/locale-getlocale-problems-on-osx)
        if not self.encoding:
            self.encoding = "UTF8"

    @abstractmethod
    def _create_config(self) -> Ili2DbCommandConfiguration:
        """Creates the configuration that will be used by *run* method.

        :return: ili2db configuration"""

    def _get_ili2db_version(self):
        return self.configuration.db_ili_version

    def _args(self, hide_password):
        """Gets the list of ili2db arguments from configuration.

        :param bool hide_password: *True* to mask the password, *False* otherwise.
        :return: ili2db arguments list.
        :rtype: list
        """
        self.configuration.tool = self.tool

        return get_ili2db_args(self.configuration, hide_password)

    def _ili2db_jar_arg(self):
        ili2db_bin = get_ili2db_bin(
            self.tool, self._get_ili2db_version(), self.stdout, self.stderr
        )
        if not ili2db_bin:
            return self.ILI2DB_NOT_FOUND
        return ["-jar", ili2db_bin]

    def _escaped_arg(self, argument):
        if '"' in argument:
            argument = argument.replace('"', '"""')
        if " " in argument:
            argument = '"' + argument + '"'
        return argument

    def command(self, hide_password):
        ili2db_jar_arg = self._ili2db_jar_arg()
        args = self._args(hide_password)
        java_path = self._escaped_arg(
            get_java_path(self.configuration.base_configuration)
        )
        command_args = ili2db_jar_arg + args

        valid_args = []
        for command_arg in command_args:
            valid_args.append(self._escaped_arg(command_arg))

        command = java_path + " " + " ".join(valid_args)

        return command

    def command_with_password(self, edited_command):
        if "--dbpwd ******" in edited_command:
            args = self._args(False)
            i = args.index("--dbpwd")
            edited_command = edited_command.replace(
                "--dbpwd ******", "--dbpwd " + args[i + 1]
            )
        return edited_command

    def command_without_password(self, edited_command=None):
        if not edited_command:
            return self.command(True)
        regex = re.compile("--dbpwd [^ ]*")
        match = regex.match(edited_command)
        if match:
            edited_command = edited_command.replace(match.group(1), "--dbpwd ******")
        return edited_command

    def _prepare_command(self, edited_command=None):
        """Prepares and returns the command to be executed along with its arguments."""
        java_path = get_java_path(self.configuration.base_configuration)

        if not edited_command:
            ili2db_jar_arg = self._ili2db_jar_arg()
            if ili2db_jar_arg == self.ILI2DB_NOT_FOUND:
                return self.ILI2DB_NOT_FOUND
            args = self._args(False)

            return [java_path] + ili2db_jar_arg + args
        else:
            return [java_path] + self.command_with_password(edited_command)

    def run(self, edited_command=None):
        """Executes the configured command asynchronously."""
        command = self._prepare_command(edited_command)
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


        if self.__done_pattern.search(msg_stderr):
            self.__result = self.SUCCESS
        
        self._search_custom_pattern(msg_stderr)

        exit_code = process.returncode
        self.__result = self.SUCCESS if exit_code == 0 else self.ERROR

        return self.__result

    def _search_custom_pattern(self, text):
        pass
