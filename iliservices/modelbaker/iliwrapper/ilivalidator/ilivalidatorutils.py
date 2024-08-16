import os

from .ilivalidatortools import get_tool_path


def get_ilivalidator_bin():
    ilivalidator_file = get_tool_path()

    # TODO: if the library does not exist, it should be downloaded
    # for a quick implementation we do not download the library when it does not exist.
    # it is assumed that the library is downloaded
    if not os.path.isfile(ilivalidator_file):
        return None

    return ilivalidator_file
