import os
import logging
import tempfile

from PyQt5.QtCore import QObject

from ..config.general_config import (FULL_JAVA_EXE_PATH,
                                     USE_CUSTOM_MODEL_DIR,
                                     CUSTOM_MODEL_DIR,
                                     USE_ILIVALIDATOR_DEBUG_MODE,
                                     JAVA_REQUIRED_VERSION)

from ..config.logging_config import setup_logging
from ..modelbaker.iliwrapper.ilivalidator.ilivalidatorconfig import IliValidatorConfiguration
from ..modelbaker.iliwrapper.ilivalidator import ilivalidator
setup_logging()

logger = logging.getLogger(__name__)


class IliValidator(QObject):
    def __init__(self):
        QObject.__init__(self)
        self._java_path = FULL_JAVA_EXE_PATH
        self._configuration = None
        self._output_dir = None

    def _get_configuration(self):
        if not self._configuration:
            self._configuration = IliValidatorConfiguration()
            self._configuration.java_path = self._java_path

            # Check custom model directories
            if USE_CUSTOM_MODEL_DIR:
                custom_model_directories = CUSTOM_MODEL_DIR
                if not custom_model_directories:
                    self._configuration.custom_model_directories_enabled = False
                else:
                    self._configuration.custom_model_directories = custom_model_directories
                    self._configuration.custom_model_directories_enabled = True

            # Debug mode
            self._configuration.debugging_enabled = USE_ILIVALIDATOR_DEBUG_MODE

            # Log files
            self._output_dir = tempfile.mkdtemp()
            self._configuration.output_dir = self._output_dir

        return self._configuration

    def get_ilivalidator_configuration(self, xtf_file_path: str, ili_models=None, output_dir=None):

        if output_dir is None:
            output_dir = tempfile.mkdtemp()

        if not os.path.exists(output_dir):
            logger.critical("Working directory not exists")
            raise Exception("Working directory not exists")

        if not os.access(output_dir, os.W_OK):
            logger.critical("Working directory not exists")
            raise Exception("Working directory does not have write permissions")

        configuration = self._get_configuration()
        configuration.xtf_file = xtf_file_path
        configuration.output_dir = output_dir

        if ili_models:
            configuration.ilimodels = ';'.join(ili_models)

        return configuration

    def validate_xtf(self, configuration: IliValidatorConfiguration):
        self._show_log_process_info('START ILIVALIDATOR')

        # Configure run
        validator = ilivalidator.IliValidator()
        validator.configuration = configuration

        # Run!
        res = True
        msg = "Validator ran successfully!"
        logger.info("Validating XTF file")

        try:
            if validator.run() != ilivalidator.IliValidator.SUCCESS:
                msg = "An error occurred when try to validate the xtf file (check the logs)."
                res = False
                logger.error(msg)
        except Exception as e:
            msg = ("Java {} could not be found. You can configure the JAVA_HOME " +
                   "environment variable manually and try again.".format(JAVA_REQUIRED_VERSION))
            logger.critical(e)
            logger.error(msg)
            res = False

        self._show_log_process_info('END ILIVALIDATOR')

        return res, msg

    @staticmethod
    def _show_log_process_info(msg):
        logger.info('*' * 10 + msg + '*' * 10)