"""
/***************************************************************************
                              -------------------
        begin                : 23.05.2024
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
import os

from ..ili2dbutils import get_all_modeldir_in_path


class IliValidatorConfiguration:
    # For more information on the parameters you can consult
    # https://github.com/claeis/ilivalidator/blob/master/docs/ilivalidator.rst

    def __init__(self) -> None:
        self.output_dir = None

        self.config_id = ''
        self.metaconfig_id = ''
        self.force_type_validation = False
        self.disable_area_validation = False
        self.disable_constraint_validation = False
        self.all_objects_are_accessible = True
        self.multiplicity_off = False
        self.single_validation_pass = False
        self.ilimodels = ''
        self.logtime = False
        self.plugins_dir = ''

        self.java_path = ''
        self.custom_model_directories_enabled = False
        self.custom_model_directories = ""

        self.logfile_path = ''
        self.xtf_logfile_path = ''
        self.csv_logfile_path = ''
        self.xtf_file = ''

        self.generate_xtf_logfile = False
        self.generate_csv_logfile = False

        self.debugging_enabled = False

    def to_ilivalidator_args(self, with_modeldir=True):
        """
        Create an ilivalidator command line argument string from this configuration
        """
        args = list()

        # needs to start with "ilidata:" or should be a local file path
        if self.config_id:
            args += ["--config", self.config_id]

        # needs to start with "ilidata:" or should be a local file path
        if self.metaconfig_id:
            args += ["--metaConfig", self.metaconfig_id]

        if self.force_type_validation:
            args += ["--forceTypeValidation"]

        if self.disable_area_validation:
            args += ["--disableAreaValidation"]

        if self.disable_constraint_validation:
            args += ["--disableConstraintValidation"]

        if self.all_objects_are_accessible:
            args += ["--allObjectsAccessible"]

        if self.multiplicity_off:
            args += ["--multiplicityOff"]

        if self.single_validation_pass:
            args += ["--singlePass"]

        if self.ilimodels:
            args += ["--models", self.ilimodels]

        if self.logtime:
            args += ["--logtime"]

        if self.plugins_dir:
            args += ["--plugins", self.plugins_dir]

        if with_modeldir:
            if self.custom_model_directories_enabled and self.custom_model_directories:
                str_model_directories = [
                    get_all_modeldir_in_path(path)
                    for path in self.custom_model_directories.split(";")
                ]
                str_model_directories = ";".join(str_model_directories)
                args += ["--modeldir", str_model_directories]

        # logfile always be generated
        self.logfile_path = os.path.join(self.output_dir, "ilivalidator.log")
        args += ["--log", self.logfile_path]

        if self.generate_xtf_logfile:
            self.xtf_logfile_path = os.path.join(self.output_dir, "ilivalidator.xtf")
            args += ["--xtflog", self.xtf_logfile_path]

        if self.generate_csv_logfile:
            self.csv_logfile_path = os.path.join(self.output_dir, "ilivalidator.csv")
            args += ["--csvlog", self.csv_logfile_path]

        if self.debugging_enabled:
            args += ["--trace"]

        if self.xtf_file:
            args += [self.xtf_file]

        return args
