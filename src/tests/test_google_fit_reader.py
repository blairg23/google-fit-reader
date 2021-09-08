import faker
from unittest import TestCase, mock
from unittest.mock import patch
import google_fit_reader


module_under_test = "google_fit_reader"

fake = faker.Faker()

class GoogleFitReaderTestCase(TestCase):
    def setUp(self):
        pass
    def tearDown(self):
        pass

    def test_parse_called(self):
        assert 1==1
