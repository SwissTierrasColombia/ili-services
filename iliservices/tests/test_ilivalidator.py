import nose2
import unittest
import tempfile

from .utils import get_test_path

from ..core.ilivalidator import IliValidator

import logging
logger = logging.getLogger(__name__)


class TestIliValidator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.ilivalidator = IliValidator()

    def test_valid_data_without_indicate_models(self):
        print("\nINFO: Validate data without indicating the model to be used")
        xtf_path = get_test_path("xtf/test_valid_data_fdc_12.xtf")

        output_dir = tempfile.mkdtemp()
        configuration = self.ilivalidator.get_ilivalidator_configuration(xtf_path, output_dir=output_dir)
        res_validation, msg_validation = self.ilivalidator.validate_xtf(configuration)
        self.assertTrue(res_validation, msg_validation)

    def test_valid_data_for_specific_model(self):
        print("\nINFO: Validate data for a specific model")
        xtf_path = get_test_path("xtf/test_valid_data_fdc_12.xtf")
        models = ['Captura_Geo_V1_2']

        output_dir = tempfile.mkdtemp()
        configuration = self.ilivalidator.get_ilivalidator_configuration(xtf_path,
                                                                         ili_models=models,
                                                                         output_dir=output_dir)
        res_validation, msg_validation = self.ilivalidator.validate_xtf(configuration)
        self.assertTrue(res_validation, msg_validation)

    def test_invalid_data(self):
        print("\nINFO: Validate a xtf with invalid data")
        xtf_path = get_test_path("xtf/test_invalid_data_fdc_12.xtf")
        output_dir = tempfile.mkdtemp()
        configuration = self.ilivalidator.get_ilivalidator_configuration(xtf_path, output_dir=output_dir)
        res_validation, msg_validation = self.ilivalidator.validate_xtf(configuration)
        self.assertFalse(res_validation, msg_validation)

    def test_wrong_data_section(self):
        print("\nINFO: Validate xtf with a wrong data section")
        xtf_path = get_test_path("xtf/test_wrong_data_section.xtf")
        output_dir = tempfile.mkdtemp()
        configuration = self.ilivalidator.get_ilivalidator_configuration(xtf_path, output_dir=output_dir)
        res_validation, msg_validation = self.ilivalidator.validate_xtf(configuration)
        self.assertFalse(res_validation, msg_validation)

    def test_wrong_model_section(self):
        print("\nINFO: Validate xtf with a wrong model section")
        xtf_path = get_test_path("xtf/test_wrong_model_section.xtf")
        output_dir = tempfile.mkdtemp()
        configuration = self.ilivalidator.get_ilivalidator_configuration(xtf_path, output_dir=output_dir)
        res_validation, msg_validation = self.ilivalidator.validate_xtf(configuration)
        self.assertFalse(res_validation, msg_validation)

    def test_model_not_found(self):
        print("\nINFO: Validate xtf with a model not found in the repository")
        xtf_path = get_test_path("xtf/test_model_not_found.xtf")
        output_dir = tempfile.mkdtemp()
        configuration = self.ilivalidator.get_ilivalidator_configuration(xtf_path, output_dir=output_dir)
        res_validation, msg_validation = self.ilivalidator.validate_xtf(configuration)
        self.assertFalse(res_validation, msg_validation)

    def test_empty_file(self):
        print("\nINFO: Validate a empty xtf")
        xtf_path = get_test_path("xtf/test_empty_file.xtf")
        output_dir = tempfile.mkdtemp()
        configuration = self.ilivalidator.get_ilivalidator_configuration(xtf_path, output_dir=output_dir)
        res_validation, msg_validation = self.ilivalidator.validate_xtf(configuration)
        self.assertFalse(res_validation, msg_validation)

    @classmethod
    def tearDownClass(cls):
        pass


if __name__ == '__main__':
    nose2.main()
