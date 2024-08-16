"""
/***************************************************************************
                              -------------------
        begin                : 2016
        copyright            : (C) 2016 by OPENGIS.ch
        email                : info@opengis.ch
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

import fnmatch
import os.path
import re
import unicodedata
from abc import ABCMeta
from functools import partial

import requests
from requests.exceptions import RequestException

from PyQt5.QtCore import (
    QCoreApplication,
    QObject,
)
from PyQt5.QtGui import QValidator
from PyQt5.QtWidgets import QApplication, QFileDialog


def selectFileName(line_edit_widget, title, file_filter, parent):
    filename, matched_filter = QFileDialog.getOpenFileName(
        parent, title, line_edit_widget.text(), file_filter
    )
    line_edit_widget.setText(filename)


def make_file_selector(
    widget,
    title=QCoreApplication.translate("modelbaker", "Open File"),
    file_filter=QCoreApplication.translate("modelbaker", "Any file (*)"),
    parent=None,
):
    return partial(
        selectFileName,
        line_edit_widget=widget,
        title=title,
        file_filter=file_filter,
        parent=parent,
    )


def selectFileNameToSave(
    line_edit_widget,
    title,
    file_filter,
    parent,
    extension,
    extensions,
    dont_confirm_overwrite,
):
    filename, matched_filter = QFileDialog.getSaveFileName(
        parent,
        title,
        line_edit_widget.text(),
        file_filter,
        options=QFileDialog.DontConfirmOverwrite
        if dont_confirm_overwrite
        else QFileDialog.Options(),
    )
    extension_valid = False

    if not extensions:
        extensions = [extension]

    if extensions:
        extension_valid = any(filename.endswith(ext) for ext in extensions)

    if not extension_valid and filename:
        filename = filename + extension

    line_edit_widget.setText(filename)


def make_save_file_selector(
    widget,
    title=QCoreApplication.translate("modelbaker", "Open File"),
    file_filter=QCoreApplication.translate("modelbaker", "Any file(*)"),
    parent=None,
    extension="",
    extensions=None,
    dont_confirm_overwrite=False,
):
    return partial(
        selectFileNameToSave,
        line_edit_widget=widget,
        title=title,
        file_filter=file_filter,
        parent=parent,
        extension=extension,
        extensions=extensions,
        dont_confirm_overwrite=dont_confirm_overwrite,
    )


def selectFolder(line_edit_widget, title, parent):
    foldername = QFileDialog.getExistingDirectory(
        parent, title, line_edit_widget.text()
    )
    line_edit_widget.setText(foldername)


def make_folder_selector(
    widget,
    title=QCoreApplication.translate("modelbaker", "Open Folder"),
    parent=None,
):
    return partial(selectFolder, line_edit_widget=widget, title=title, parent=parent)


def slugify(text: str) -> str:
    if not text:
        return text
    slug = unicodedata.normalize("NFKD", text)
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", slug).strip("_")
    slug = re.sub(r"[-]+", "_", slug)
    slug = slug.lower()
    return slug


class NetworkError(RuntimeError):
    def __init__(self, error_code, msg):
        self.msg = msg
        self.error_code = error_code


replies = list()


def download_file(url, filename, on_progress=None, on_finished=None, on_error=None, on_success=None):
    """
    Will download the file from url to a local filename.
    The method will only return once it's finished.

    While downloading it will repeatedly report progress by calling on_progress
    with two parameters bytes_received and bytes_total.

    If an error occurs, it raises a NetworkError exception.

    It will return the filename if everything was ok.
    """

    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            total_length = r.headers.get('content-length')

            with open(filename, 'wb') as f:
                bytes_received = 0
                if total_length is None:  # no content length header
                    f.write(r.content)
                else:
                    total_length = int(total_length)
                    for chunk in r.iter_content(chunk_size=4096):
                        if chunk:  # filter out keep-alive new chunks
                            f.write(chunk)
                            bytes_received += len(chunk)
                            if on_progress:
                                on_progress(bytes_received, total_length)

        if on_success:
            on_success()

    except RequestException as e:
        if on_error:
            on_error(str(e))
        raise  # Optionally re-raise the exception after handling it

    finally:
        if on_finished:
            on_finished()

    return filename


class Validators(QObject):
    def validate_line_edits(self, *args, **kwargs):
        """
        Validate line edits and set their color to indicate validation state.
        """
        senderObj = self.sender()
        validator = senderObj.validator()
        if validator is None:
            color = "#fff"  # White
        else:
            state = validator.validate(senderObj.text().strip(), 0)[0]
            if state == QValidator.Acceptable:
                color = "#fff"  # White
            elif state == QValidator.Intermediate:
                color = "#ffd356"  # Light orange
            else:
                color = "#f6989d"  # Red
        senderObj.setStyleSheet("QLineEdit {{ background-color: {} }}".format(color))


class FileValidator(QValidator):
    def __init__(
        self,
        pattern="*",
        is_executable=False,
        parent=None,
        allow_empty=False,
        allow_non_existing=False,
    ):
        """
        Validates if a string is a valid filename, based on the provided parameters.

        :param pattern: A file glob pattern as recognized by ``fnmatch``, if a list if provided, the validator will try
                        to match every pattern in the list.
        :param is_executable: Only match executable files
        :param parent: The parent QObject
        :param allow_empty: Empty strings are valid
        :param allow_non_existing: Non existing files are valid
        """
        QValidator.__init__(self, parent)
        self.pattern = pattern
        self.is_executable = is_executable
        self.allow_empty = allow_empty
        self.allow_non_existing = allow_non_existing
        self.error = ""

    """
    Validator for file line edits
    """

    def validate(self, text, pos):
        self.error = ""

        if self.allow_empty and not text.strip():
            return QValidator.Acceptable, text, pos

        pattern_matches = False
        if type(self.pattern) is str:
            pattern_matches = fnmatch.fnmatch(text, self.pattern)
        elif type(self.pattern) is list:
            pattern_matches = True in (
                fnmatch.fnmatch(text, pattern) for pattern in self.pattern
            )
        else:
            raise TypeError(
                "pattern must be str or list, not {}".format(type(self.pattern))
            )

        if not text:
            self.error = self.tr("Text field value is empty.")
        elif not self.allow_non_existing and not os.path.isfile(text):
            self.error = self.tr("The chosen file does not exist.")
        elif not pattern_matches:
            self.error = self.tr(
                "The chosen file has a wrong extension (has to be {}).".format(
                    self.pattern
                    if type(self.pattern) is str
                    else ",".join(self.pattern)
                )
            )
        elif self.is_executable and not os.access(text, os.X_OK):
            self.error = self.tr("The chosen file is not executable.")
        if self.error:
            return QValidator.Intermediate, text, pos
        else:
            return QValidator.Acceptable, text, pos


class NonEmptyStringValidator(QValidator):
    def __init__(self, parent=None):
        QValidator.__init__(self, parent)

    def validate(self, text, pos):
        if not text.strip():
            return QValidator.Intermediate, text, pos

        return QValidator.Acceptable, text, pos


class OverrideCursor:
    def __init__(self, cursor):
        self.cursor = cursor

    def __enter__(self):
        QApplication.setOverrideCursor(self.cursor)

    def __exit__(self, exc_type, exc_val, exc_tb):
        QApplication.restoreOverrideCursor()


class AbstractQObjectMeta(ABCMeta, type(QObject)):
    """Metaclass that is used by any class that must be abstract and inherit from QObject.

    If a class must be abstract (ABC or ABCMeta) and inherit from QObject, multiple inheritance fails because
    the classes have different metaclasses. See more:

    https://stackoverflow.com/questions/46837947/how-to-create-an-abstract-base-class-in-python-which-derived-from-qobject
    """
