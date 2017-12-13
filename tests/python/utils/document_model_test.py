import unittest
import mock

from document_model import DocumentModel


class DocumentModelTest(unittest.TestCase):

    def test_verify(self):
        fixture = (DocumentModel().with_pkey('pkey')
                                  .with_token_count(1)
                                  .with_word_count(1)
                                  .with_index_time(1)
                                  .set_updating(True)
                                  .set_lockno(0))
        self.assertTrue(fixture.verify(), "Failed to verify valid model")

    def test_verify_missing_field(self):
        fixture = (DocumentModel().with_token_count(1)
                                  .with_word_count(1)
                                  .with_index_time(1)
                                  .set_updating(True)
                                  .set_lockno(0))
        self.assertFalse(fixture.verify(), "Failed to reject invalid model")

    def test_verify_extra_field(self):
        fixture = (DocumentModel().with_pkey('pkey')
                                  .with_token_count(1)
                                  .with_word_count(1)
                                  .with_index_time(1)
                                  .set_updating(True)
                                  .set_lockno(0))
        fixture._info['randofield'] = 'randoval'
        self.assertFalse(fixture.verify(), "Failed to reject invalid model")

    @mock.patch('document_model.datetime')
    def test_load_from_write_input(self, mock_dt):
        mock_input = mock.Mock()
        mock_input.get_id.return_value = 'pkey'
        mock_input.get_token_count.return_value = 1
        mock_input.get_word_count.return_value = 1
        mock_dt.now.return_value = 1
        mock_input.get_token_ranges.return_value = []
        fixture = DocumentModel()
        fixture.load_from_write_input(mock_input)

        self.assertTrue(fixture.verify(), "Failed to load from write input")
