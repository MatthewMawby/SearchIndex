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
        local_path = partition_uri
        try:
            self._index_storage.download_file(self.INDEX_STORAGE,
                                              partition_uri + '.pkl',
                                              local_path)
            return local_path
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

    def delete_partition(self, partition_uri):
        partition_uri = partition_uri
        partition_uri += '.pkl'
        try:
            self._index_storage.delete_object(
                Bucket=self.INDEX_STORAGE,
                Key=partition_uri
            )
        except Exception as ex:
            print "ERROR: Failed to delete partition."
            raise ex
