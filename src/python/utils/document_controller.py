import boto3
from boto3.dynamodb.conditions import Key, Attr
from document_model import DocumentModel


class DocumentController(object):

    DOCUMENT_TABLE = 'DOCUMENTS'

    def __init__(self):
        self._dynamodb = boto3.client('dynamodb')
        self.document_table = (boto3.resource('dynamodb')
                                  .Table(self.DOCUMENT_TABLE))


    # create a new index document if the provided model is valid
    def create_new_document(self, document_model):
        if not document_model.verify():
            return
        self._index_table.put_item(
            Item=index_model.get_payload()
        )

    # acquire a lock on the document
    def lock_document(self, doc_id):
        return "hi"
