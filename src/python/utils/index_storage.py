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
        self._active_partitions = ([]);

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

    def get_s3_keys(self):
        dynamo_client = boto3.client("dynamodb")
        res = dynamo_client.scan(
            TableName="INDEX_PARTITION_METADATA",
            AttributesToGet=[
                's3Key',
            ]
        )
        s3_keys = []
        for i in res['Items']:
            s3_keys.append(i['s3Key']['S'])
        return s3_keys

    def get_active_partitions(self):
        return self._active_partitions

    def write_partition(self, partition_uri, partition):
        partition_uri += '.pkl'
        try:
            partition.serialize(partition_uri)
            payload = open(partition_uri, 'rb')
            res = self._index_storage.put_object(Bucket=self.INDEX_STORAGE,
                                                 Key=partition_uri,
                                                 Body=payload)
            self._active_partitions.add(partition_uri)
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
            self._active_partitions.remove(partition_uri)
        except Exception as ex:
            print "ERROR: Failed to delete partition."
            raise ex
