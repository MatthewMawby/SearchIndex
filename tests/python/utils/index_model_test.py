import unittest
import mock

from index_model import IndexModel


class IndexModelTest(unittest.TestCase):

    def test_verify(self):
        fixture = (IndexModel().with_pkey('pkey')
                               .with_storage_key('storage')
                               .with_start_token('start')
                               .with_end_token('end'))
        self.assertTrue(fixture.verify(), "Failed to verify valid model")

    def test_verify_missing_field(self):
        fixture = (IndexModel().with_storage_key('storage')
                               .with_start_token('start')
                               .with_end_token('end'))
        self.assertFalse(fixture.verify(), "Failed to reject invalid model")

    def test_verify_extra_field(self):
        fixture = (IndexModel().with_pkey('pkey')
                               .with_storage_key('storage')
                               .with_start_token('start')
                               .with_end_token('end'))
        fixture._info['randofield'] = 'randoval'
        self.assertFalse(fixture.verify(), "Failed to reject invalid model")
