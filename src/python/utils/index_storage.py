import boto3
import json

from index_partition import IndexPartition


class IndexStorage(object):
    '''
    This class is responsible for interacting with the index partition storage
    solution (in this case S3). It retrieves, stores, and creates partitions.
    '''

    INDEX_STORAGE = 'lspt-index-partitions'

    def __init__(self):
        self._index_storage = boto3.client('s3')

    def get_partition(self, partition_uri):
        try:
            self._index_storage.download_file(self.INDEX_STORAGE,
                                              partition_uri + '.pkl',
                                              partition_uri)
            return partition_uri
        except Exception as ex:
            print ("ERROR: Partition {0} not found in storage"
                   .format(partition_uri))
            raise ex

    def write_partition(self, partition_uri, partition):
        partition_uri += '.pkl'
        try:
            partition.serialize(partition_uri)
            payload = open(partition_uri, 'rb')
            res = self._index_storage.put_object(Bucket=self.INDEX_STORAGE,
                                                 Key=partition_uri,
                                                 Body=payload)
        except Exception as ex:
            print ("ERROR: Failed to write partition {0} to storage."
                   .format(partition_uri))
            raise ex


"""
''' SAMPLE USAGE WITH INDEX_PARTITION CLASS'''
# create partition with test data
partition = IndexPartition()
print "Partition size is {0}".format(partition.size())
print "Partition starting_token is {0}".format(partition.starting_token())
print "Partition ending_token is {0}".format(partition.ending_token())
partition.add_token('test', 'testID', 0, 1, [0])

# write partition, then retrieve it
storage = IndexStorage()
storage.write_partition('test_partition', partition)
payload = storage.get_partition('test_partition')

# load partition from payload
partition2 = IndexPartition()
partition2.deserialize(payload)
print "Partition size is {0}".format(partition2.size())
print "Partition starting_token is {0}".format(partition2.starting_token())
print "Partition ending_token is {0}".format(partition2.ending_token())
"""
