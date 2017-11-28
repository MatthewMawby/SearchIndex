import boto3
from boto3.dynamodb.conditions import Key, Attr
from index_model import IndexModel


class IndexController(object):
    '''
    This class is responsible for interactions with the
    INDEX_PARTITION_METADATA table. It creates and updates metadata for
    partitions and also determines which partitions contain specified tokens.
    '''

    INDEX_METADATA_TABLE = 'INDEX_PARTITION_METADATA'
    INDEX_GSI = 'INDEX_START'

    def __init__(self):
        self._index_table = (boto3.resource('dynamodb')
                                  .Table(self.INDEX_METADATA_TABLE))

    # create a new index document if the provided model is valid
    def create_new_index(self, index_model):
        if not index_model.verify():
            return
        self._index_table.put_item(
            Item=index_model.get_payload()
        )

    # get pkeys for partitions the provided token might be in
    def get_partitions_for_token(self, token):
        # Yes this is doing a scan, yes I know it's gross
        res = self._index_table.scan(
            FilterExpression=Attr(IndexModel.START_TOKEN).lte(token) &
            Attr(IndexModel.END_TOKEN).gte(token)
        )
        pkeys = []
        for item in res['Items']:
            pkeys.append(item['pKey'])
        return pkeys
