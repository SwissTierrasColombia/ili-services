import os


def get_tool_version():
    return "1.14.1"


def get_tool_url():
    return "https://downloads.interlis.ch/ilivalidator/ilivalidator-{version}.zip".format(
        version=get_tool_version()
    )


def get_tool_path():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    ilivalidator_dir = "ilivalidator-{}".format(get_tool_version())

    ilivalidator_file = os.path.join(
        dir_path,
        "bin",
        ilivalidator_dir,
        "ilivalidator-{version}.jar".format(version=get_tool_version()),
    )

    return ilivalidator_file
