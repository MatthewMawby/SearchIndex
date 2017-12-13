import unittest
import mock

from document_controller import DocumentController


class DocumentControllerTest(unittest.TestCase):

    # mock dependencies of DocumentController & save references to class
    @mock.patch('document_controller.boto3')
    def setUp(self, mock_boto):
        self.mock_table = mock.Mock()
        self.mock_resource = mock.Mock()
        self.mock_resource.Table.return_value = self.mock_table
        mock_boto.resource.return_value = self.mock_resource
        self.doc_ctrl = DocumentController()

    def test_get_document(self):
        self.mock_table.query.return_value = {
            'Count': 1,
            'Items': ['item']
        }

        res = self.doc_ctrl.get_document('id')
        self.assertEqual('item', res, "Failed to retrieve document correctly")

    def test_get_document_no_item(self):
        self.mock_table.query.return_value = {
            'Count': 0,
            'Items': []
        }

        res = self.doc_ctrl.get_document('id')
        self.assertEqual(None, res, "Failed to retrieve document correctly")

    def test_get_document_exception(self):
        self.mock_table.query.side_effect = Exception("ERROR")

        with self.assertRaises(Exception) as context:
            self.doc_ctrl.get_document('id')

        self.assertTrue('ERROR' in context.exception)

    def test_lock_document(self):
        res = self.doc_ctrl.lock_document("id")
        self.assertTrue(res, "Failed to lock document")

    def test_lock_document_exception(self):
        self.mock_table.update_item.side_effect = Exception("ERROR")

        with self.assertRaises(Exception) as context:
            self.doc_ctrl.lock_document("id")

        self.assertTrue('ERROR' in context.exception)

    def test_unlock_document(self):
        res = self.doc_ctrl.unlock_document("id")
        self.assertTrue(res, "Failed to unlock document")

    def test_unlock_document_exception(self):
        self.mock_table.update_item.side_effect = Exception("ERROR")

        with self.assertRaises(Exception) as context:
            self.doc_ctrl.unlock_document("id")

        self.assertTrue('ERROR' in context.exception)

    def test_create_new_document(self):
        mock_model = mock.Mock()
        mock_model.verify.return_value = True
        res = self.doc_ctrl.create_new_document(mock_model)

        self.assertTrue(res, "Failed to create new document")

    def test_create_new_document_invalid_model(self):
        mock_model = mock.Mock()
        mock_model.verify.return_value = False
        res = self.doc_ctrl.create_new_document(mock_model)

        self.assertFalse(res, "Failed to fail invalid document model")

    def test_create_new_document_exception(self):
        mock_model = mock.Mock()
        mock_model.verify.return_value = True
        self.mock_table.put_item.side_effect = Exception("ERROR")

        with self.assertRaises(Exception) as context:
            self.doc_ctrl.create_new_document(mock_model)

        self.assertTrue('ERROR' in context.exception)
