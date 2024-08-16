from PyQt5.QtCore import (QObject)


from ..config.general_config import (DEFAULT_TOML_FILE,
                                     JAVA_REQUIRED_VERSION,
                                     CTM12_PG_SCRIPT_PATH,
                                     CTM12_GPKG_SCRIPT_PATH)

from ..config.ili2db_names import ILI2DBNames
from ..config.config_db_supported import ConfigDBsSupported
from ..modelbaker.iliwrapper.ilicache import IliCache

from ..modelbaker.iliwrapper.ili2dbconfig import (BaseConfiguration,
                                                  SchemaImportConfiguration,
                                                  ImportDataConfiguration,
                                                  ExportConfiguration,
                                                  UpdateDataConfiguration,
                                                  ValidateConfiguration)

from ..modelbaker.iliwrapper import (ili2dbvalidator,
                                     iliimporter,
                                     iliexporter,
                                     iliupdater)


from ..config.general_config import (FULL_JAVA_EXE_PATH,
                                     USE_CUSTOM_MODEL_DIR,
                                     CUSTOM_MODEL_DIR,
                                     USE_ILI2DB_DEBUG_MODE,
                                     LOG_FILE_PATH)

import logging
from ..config.logging_config import setup_logging
setup_logging()

logger = logging.getLogger(__name__)


class Ili2DB(QObject):
    """
    Execute ili2db operations via Model Baker API
    """

    def __init__(self):
        QObject.__init__(self)

        self._java_path = FULL_JAVA_EXE_PATH

        self.dbs_supported = ConfigDBsSupported()

        self._base_configuration = None
        self._ilicache = None
        self._log = ''

    def _get_base_configuration(self):
        """
        :return: BaseConfiguration object. If it's already configured, it returns the existing object, so that it can
                 be shared among chained operations (e.g., export DB1-->schema import DB2-->import DB2).
        """
        if not self._base_configuration:
            self._base_configuration = BaseConfiguration()
            self._ilicache = IliCache(self._base_configuration)

            self._base_configuration.java_path = self._java_path 

            # Check custom model directories
            if USE_CUSTOM_MODEL_DIR:
                custom_model_directories = CUSTOM_MODEL_DIR
                if not custom_model_directories:
                    self._base_configuration.custom_model_directories_enabled = False
                else:
                    self._base_configuration.custom_model_directories = custom_model_directories
                    self._base_configuration.custom_model_directories_enabled = True

            # Debug mode
            self._base_configuration.debugging_enabled = USE_ILI2DB_DEBUG_MODE

            self._base_configuration.logfile_path = LOG_FILE_PATH

            #self._ilicache.refresh()  # Always call it after setting custom_model_directories

        return self._base_configuration

    def get_import_schema_configuration(self, db, ili_models=list(), create_basket_col=False):
        db_factory = self.dbs_supported.get_db_factory(db.engine)

        configuration = SchemaImportConfiguration()
        db_factory.set_ili2db_configuration_params(db.dict_conn_params, configuration)
        configuration.inheritance = ILI2DBNames.DEFAULT_INHERITANCE
        configuration.create_basket_col = create_basket_col
        configuration.create_import_tid = ILI2DBNames.CREATE_IMPORT_TID
        configuration.stroke_arcs = ILI2DBNames.STROKE_ARCS
        configuration.tomlfile = DEFAULT_TOML_FILE

        configuration.base_configuration = self._get_base_configuration()
        configuration.ilimodels = ';'.join(ili_models)

        if db.engine == 'gpkg':
            # EPSG:9377 support for GPKG (Ugly, I know) We need to send known parameters, we'll fix this in the post_script
            configuration.srs_auth = 'EPSG'
            configuration.srs_code = 3116
            configuration.post_script = CTM12_GPKG_SCRIPT_PATH
        elif db.engine == 'pg':
            configuration.srs_auth = 'EPSG'
            configuration.srs_code = 9377
            configuration.pre_script = CTM12_PG_SCRIPT_PATH

        return configuration

    def get_import_data_configuration(self, db, xtf_path, dataset='', baskets=list(), disable_validation=False):
        db_factory = self.dbs_supported.get_db_factory(db.engine)
        configuration = ImportDataConfiguration()
        db_factory.set_ili2db_configuration_params(db.dict_conn_params, configuration)
        configuration.with_importtid = True
        configuration.xtffile = xtf_path
        configuration.disable_validation = disable_validation
        configuration.dataset = dataset
        configuration.baskets = baskets  # list with basket UUIDs

        configuration.base_configuration = self._get_base_configuration()
        ili_models = db.get_models()
        if ili_models:
            configuration.ilimodels = ';'.join(ili_models)

        return configuration

    def get_export_configuration(self, db, xtf_path, dataset='', baskets=list(), disable_validation=False):
        db_factory = self.dbs_supported.get_db_factory(db.engine)
        configuration = ExportConfiguration()
        db_factory.set_ili2db_configuration_params(db.dict_conn_params, configuration)
        configuration.with_exporttid = True
        configuration.xtffile = xtf_path
        configuration.disable_validation = disable_validation
        configuration.dataset = dataset
        configuration.baskets = baskets  # List with basket UUIDs

        configuration.base_configuration = self._get_base_configuration()
        ili_models = db.get_models()
        if ili_models:
            configuration.ilimodels = ';'.join(ili_models)

        return configuration

    def get_update_configuration(self, db, xtf_path, dataset_name):
        db_factory = self.dbs_supported.get_db_factory(db.engine)
        configuration = UpdateDataConfiguration()
        db_factory.set_ili2db_configuration_params(db.dict_conn_params, configuration)

        configuration.base_configuration = self._get_base_configuration()
        ili_models = db.get_models()
        if ili_models:
            configuration.ilimodels = ';'.join(ili_models)

        configuration.dataset = dataset_name
        configuration.with_importbid = True
        configuration.with_importtid = True
        configuration.xtffile = xtf_path

        return configuration

    def get_validate_configuration(self, db, model_names, xtflog_path, valid_config_path):
        db_factory = self.dbs_supported.get_db_factory(db.engine)
        configuration = ValidateConfiguration()
        db_factory.set_ili2db_configuration_params(db.dict_conn_params, configuration)

        configuration.base_configuration = self._get_base_configuration()
        # Since BaseConfiguration can be shared, avoid a --trace in --validate operation (not supported by ili2db)
        configuration.base_configuration.debugging_enabled = False

        if model_names:
            configuration.ilimodels = ';'.join(model_names)
        if xtflog_path:
            configuration.xtflog = xtflog_path
        if valid_config_path:
            configuration.valid_config = valid_config_path

        return configuration
    
    def import_schema(self, db, configuration: SchemaImportConfiguration):

        self._show_log_process_info('START IMPORT SCHEMA')

        # Configure command parameters
        db_factory = self.dbs_supported.get_db_factory(db.engine)

        # Configure run
        importer = iliimporter.Importer()
        importer.tool = db_factory.get_model_baker_db_ili_mode()
        importer.configuration = configuration

        # Run!
        res = True
        msg = "Schema import ran successfully!"
        self._log = ''
        logger.info("Creating INTERLIS model structure into {}...".format(db.engine.upper()))
        
        try:
            if importer.run() != iliimporter.Importer.SUCCESS:
                msg = "An error occurred when importing a schema into a DB (check the logs)."
                res = False
                logger.error(msg)
                logger.critical(self._log)
        except Exception as e:
            msg = "Java {} could not be found. You can configure the JAVA_HOME environment variable manually and try again.".format(JAVA_REQUIRED_VERSION)
            logger.critical(e)
            logger.error(msg)
            res = False

        self._show_log_process_info('END IMPORT SCHEMA')

        return res, msg
    
    def import_data(self, db, configuration: ImportDataConfiguration):

        self._show_log_process_info('START IMPORT DATA')

        # Configure command parameters
        db_factory = self.dbs_supported.get_db_factory(db.engine)

        # Configure run
        importer = iliimporter.Importer(dataImport=True)
        importer.tool = db_factory.get_model_baker_db_ili_mode()
        importer.configuration = configuration

        # Run!
        res = True
        msg = "XTF '{}' imported successfully!".format(configuration.xtffile)
        self._log = ''
        logger.info("Importing XTF into {}...".format(db.engine.upper()))

        try:
            if importer.run() != iliimporter.Importer.SUCCESS:
                msg = "An error occurred when importing from XTF (check the logs)."
                res = False
                logger.error(msg)
                logger.critical(self._log)
        except Exception as e:
            msg = "Java {} could not be found. You can configure the JAVA_HOME environment variable manually and try again.".format(JAVA_REQUIRED_VERSION)
            logger.critical(e)
            logger.error(msg)
            res = False

        self._show_log_process_info('END IMPORT DATA')

        return res, msg

    def export(self, db, configuration: ExportConfiguration):

        self._show_log_process_info('START EXPORT DATA')

        db_factory = self.dbs_supported.get_db_factory(db.engine)

        # Configure run
        exporter = iliexporter.Exporter()
        exporter.tool = db_factory.get_model_baker_db_ili_mode()
        exporter.configuration = configuration

        # Run!
        res = True
        msg = "XTF '{}' exported successfully!".format(configuration.xtffile)
        self._log = ''
        logger.info("Exporting from {} to XTF...".format(db.engine.upper()))

        try:
            if exporter.run() != iliexporter.Exporter.SUCCESS:
                msg = "An error occurred when exporting data to XTF (check the logs)."
                res = False
                logger.error(msg)
                logger.critical(self._log)
            else:
                logger.info(msg)

        except Exception as e:
            msg = "Java {} could not be found. You can configure the JAVA_HOME environment variable manually and try again.".format(JAVA_REQUIRED_VERSION)
            logger.critical(e)
            logger.error(msg)
            res = False

        self._show_log_process_info('END EXPORT DATA')

        return res, msg

    def update(self, db, configuration: UpdateDataConfiguration):
        self._show_log_process_info('START UPDATE DATA')
        db_factory = self.dbs_supported.get_db_factory(db.engine)

        # Configure run
        updater = iliupdater.Updater()
        updater.tool = db_factory.get_model_baker_db_ili_mode()
        updater.configuration = configuration

        # Run!
        res = True
        msg = "DB updated successfully from XTF file '{}'!".format(configuration.xtffile)
        self._log = ''
        logger.info("Updating {} DB from XTF '{}'...".format(db.engine.upper(), configuration.xtffile))
        
        try:
            if updater.run() != iliupdater.Updater.SUCCESS:
                msg = "An error occurred when updating the DB from an XTF (check the logs)."
                res = False
                logger.error(msg)
                logger.critical(self._log)
            else:
                logger.info(msg)

        except Exception as e:
            msg = "Java {} could not be found. You can configure the JAVA_HOME environment variable manually and try again.".format(JAVA_REQUIRED_VERSION)
            logger.critical(e)
            logger.error(msg)
            res = False

        self._show_log_process_info('END UPDATE DATA')
        return res, msg

    def validate(self, db, configuration: ValidateConfiguration):

        self._show_log_process_info('STARTS DATA VALIDATION')

        # Configure command parameters
        db_factory = self.dbs_supported.get_db_factory(db.engine)

        # Configure run
        validator = ili2dbvalidator.Ili2dbValidator()
        validator.tool = db_factory.get_model_baker_db_ili_mode()
        validator.configuration = configuration

        # Run!
        res = True
        msg = "Data successfully validated from DB '{}'!".format(db.get_description_conn_string())
        self._log = ''
        logger.info("Validating data from '{}' DB...".format(db.get_description_conn_string()))
        try:
            res_validation = validator.run()
            if (res_validation != ili2dbvalidator.Ili2dbValidator.SUCCESS
                    and res_validation != ili2dbvalidator.Ili2dbValidator.SUCCESS_WITH_VALIDATION_ERRORS):
                msg = "An error occurred when validating data from a DB (check the logs)."
                res = False
                logger.error(msg)
                logger.critical(self._log)
            else:
                logger.info(msg)
        except Exception as e:
            msg = "Java {} could not be found. You can configure the JAVA_HOME environment variable manually and try again.".format(JAVA_REQUIRED_VERSION)
            logger.critical(e)
            logger.error(msg)
            res = False

        self._show_log_process_info('END DATA VALIDATION')

        return res, msg

    @staticmethod
    def _show_log_process_info(msg):
        logger.info('*' * 10 + msg + '*' * 10)
