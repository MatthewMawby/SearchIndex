import unittest
import mock

from index_controller import IndexController


class IndexControllerTest(unittest.TestCase):

    # mock dependencies of IndexController & save references to class
    @mock.patch('index_controller.boto3')
    def setUp(self, mock_boto):
        self.mock_table = mock.Mock()
        self.mock_resource = mock.Mock()
        self.mock_resource.Table.return_value = self.mock_table
        mock_boto.resource.return_value = self.mock_resource
        self.index_control = IndexController()

    def test_create_new_index(self):
        mock_model = mock.Mock()
        mock_model.verify.return_value = True
        res = self.index_control.create_new_index(mock_model)

        self.assertTrue(res, "Failed to create new index metadata")

    def test_create_new_index_invalid_model(self):
        mock_model = mock.Mock()
        mock_model.verify.return_value = False
        res = self.index_control.create_new_index(mock_model)

        self.assertFalse(res, "Failed to reject invalid index model")

    def test_create_new_index_exception(self):
        mock_model = mock.Mock()
        mock_model.verify.return_value = True
        self.mock_table.put_item.side_effect = Exception("ERROR")

        with self.assertRaises(Exception) as context:
            self.index_control.create_new_index(mock_model)

        self.assertTrue('ERROR' in context.exception)

    def test_get_partition_ids(self):
        self.mock_table.scan.return_value = {
            'Items': [
                {
                    's3Key': 'test_key'
                }
            ]
        }

        res = self.index_control.get_partition_ids()
        self.assertEqual(res[0], 'test_key', "Failed to retrieve partitions")

    def test_get_partition_ids_exception(self):
        self.mock_table.scan.side_effect = Exception("ERROR")

        with self.assertRaises(Exception) as context:
            res = self.index_control.get_partition_ids()

        self.assertTrue('ERROR' in context.exception)
