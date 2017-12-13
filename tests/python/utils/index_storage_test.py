import unittest
import mock

from index_storage import IndexStorage


class IndexStorageTest(unittest.TestCase):

    # mock dependencies of IndexStorage & save references to class
    @mock.patch('index_storage.boto3')
    def setUp(self, mock_boto):
        self.mock_client = mock.Mock()
        mock_boto.client.return_value = self.mock_client
        self.index_storage = IndexStorage()

    def test_get_partition(self):
        res = self.index_storage.get_partition('part_id')
        self.assertEqual(res, 'part_id', "Failed to download partition")

    def test_get_partition_exception(self):
        self.mock_client.download_file.side_effect = Exception("ERROR")

        with self.assertRaises(Exception) as context:
            self.index_storage.get_partition('part_id')

        self.assertTrue('ERROR' in context.exception)

    @mock.patch('index_storage.open')
    def test_write_partition(self, mock_open):
        mock_part = mock.Mock()
        res = self.index_storage.write_partition('uri', mock_part)

        self.assertTrue(res, "Failed to write partition to storage")

    @mock.patch('index_storage.open')
    def test_write_partition_exception(self, mock_open):
        mock_part = mock.Mock()
        self.mock_client.put_object.side_effect = Exception("ERROR")

        with self.assertRaises(Exception) as context:
            self.index_storage.write_partition('uri', mock_part)

        self.assertTrue('ERROR' in context.exception)

    def test_delete_partition(self):
        res = self.index_storage.delete_partition('key')
        self.assertTrue(res, "Failed to delete partition")

    def test_delete_partition_exception(self):
        self.mock_client.delete_object.side_effect = Exception("ERROR")

        with self.assertRaises(Exception) as context:
            self.index_storage.delete_partition('key')

        self.assertTrue('ERROR' in context.exception)
