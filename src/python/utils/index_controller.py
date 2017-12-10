import boto3
from boto3.dynamodb.conditions import Key, Attr

from config import Config
from index_model import IndexModel


class IndexController(object):
    '''
    This class is responsible for interactions with the
    INDEX_PARTITION_METADATA table. It creates and updates metadata for
    partitions and also determines which partitions contain specified tokens.
    '''

    INDEX_METADATA_TABLE = 'INDEX_PARTITION_METADATA'

    def __init__(self):
        self._index_table = (boto3.resource('dynamodb')
                                  .Table(self.INDEX_METADATA_TABLE))

    # create a new index document if the provided model is valid
    def create_new_index(self, index_model):
        if not index_model.verify():
            raise Exception("Invalid index model.")
        self._index_table.put_item(
            Item=index_model.get_payload()
        )

    def get_partition_ids(self):
        res = self._index_table.scan(
            TableName="INDEX_PARTITION_METADATA",
            AttributesToGet=[
                's3Key',
            ]
        )
        partition_ids = []
        for i in res['Items']:
            partition_ids.append(i['s3Key'])
        return partition_ids

    # get pkeys for partitions the provided token might be in
    def get_partition_for_token(self, token):
        try:
            # Yes this is doing a scan, yes I know it's gross
            res = self._index_table.scan(
                FilterExpression=Attr(IndexModel.START_TOKEN).lte(token) &
                Attr(IndexModel.END_TOKEN).gte(token)
            )
            min_size = Config.INDEX_MAX_SIZE
            key = ''
            for item in res['Items']:
                if int(item[IndexModel.SIZE]) < min_size:
                    min_size = int(item[IndexModel.SIZE])
                    key = item[IndexModel.PKEY]
            return key
        except Exception as ex:
            print "ERROR: Unable to retrieve partition metadata."
            raise ex

    def update_metadata(self, index_model, is_new):
        if not index_model.verify():
            raise Exception("Invalid index model")
        update_expression = ('set {0} = :endingToken, {1} = :size,'
                             ' {2} = :startingToken, {3} = :lockNo'
                             ', {4} = :storage').format(
            IndexModel.END_TOKEN, IndexModel.SIZE,
            IndexModel.START_TOKEN, IndexModel.VERSION, IndexModel.STORAGE_KEY)
        try:
            if is_new:
                res = self._index_table.update_item(Key={
                    IndexModel.PKEY: index_model.get_id()
                }, UpdateExpression=update_expression,
                   ExpressionAttributeValues={
                    ':endingToken': index_model.get_end_token(),
                    ':size': index_model.get_size(),
                    ':startingToken': index_model.get_start_token(),
                    ':lockNo': index_model.get_version(),
                    ':storage': index_model.get_storage_key()
                })
            else:
                res = self._index_table.update_item(Key={
                    IndexModel.PKEY: index_model.get_id()
                }, UpdateExpression=update_expression,
                   ExpressionAttributeValues={
                    ':endingToken': index_model.get_end_token(),
                    ':size': index_model.get_size(),
                    ':startingToken': index_model.get_start_token(),
                    ':lockNo': index_model.get_version() + 1,
                    ':storage': index_model.get_storage_key()
                }, ConditionExpression=(Attr(IndexModel.VERSION)
                                        .eq(index_model.get_version())))
        except Exception as ex:
            print "ERROR: Failed to update partition metadata."
            raise ex

    def get_version_info(self, partition_id):
        try:
            res = self._index_table.query(
                KeyConditionExpression=Key(IndexModel.PKEY).eq(partition_id)
            )
            data = res['Items'][0]
            return (data[IndexModel.VERSION], data[IndexModel.STORAGE_KEY])
        except Exception as ex:
            print "ERROR: Failed to get version info for partition."
            raise ex
