import unittest
import mock

from index_partition import IndexPartition


class IndexPartitionTest(unittest.TestCase):

    def setUp(self):
        self.partition = IndexPartition()

    def test_add_token(self):
        res = self.partition.add_token('token', 'doc_id', 1, 1, [1])
        self.assertTrue(res, "Failed to add token to partition")

    def test_get_token_list(self):
        self.partition.add_token('token', 'doc_id', 1, 1, [1])
        res = self.partition.get_token_list()
        self.assertEqual(len(res), 1, "Returned too many tokens")
        self.assertEqual(res[0], 'token', "Returned incorrect token")

    @mock.patch('index_partition.open')
    @mock.patch('index_partition.pickle')
    def test_serialize(self, mock_pickle, mock_open):
        res = self.partition.serialize('out')
        self.assertTrue(res, "Failed to serialize partition")

    @mock.patch('index_partition.open')
    @mock.patch('index_partition.pickle')
    def test_deserialize(self, mock_pickle, mock_open):
        res = self.partition.deserialize('in')
        self.assertTrue(res, "Failed to deserialize partition")

    def test_get_token_count(self):
        self.partition.add_token('token', 'doc_id', 1, 1, [1])
        res = self.partition.get_token_count('token')
        self.assertEqual(res, 1, "Returned incorrect token count")
