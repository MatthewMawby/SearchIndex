import boto3
from boto3.dynamodb.conditions import Key, Attr
from document_model import DocumentModel


class DocumentController(object):

    DOCUMENT_TABLE = 'DOCUMENTS'

    def __init__(self):
        self._dynamodb = boto3.client('dynamodb')
        self._document_table = (boto3.resource('dynamodb')
                                .Table(self.DOCUMENT_TABLE))

    # retrieves the document if present, None if not present or failure
    def get_document(self, doc_id):
        try:
            res = self._document_table.query(
                KeyConditionExpression=Key(DocumentModel.PKEY).eq(doc_id)
            )
            if res['Count'] == 0:
                return None
            return res['Items'][0]
        except Exception as ex:
            print "ERROR: Failed to query {0} \
            table: {1}".format(self.DOCUMENT_TABLE, ex)
            return None

    # create a new index document if the provided model is valid
    def create_new_document(self, document_model):
        if not document_model.verify():
            return False
        try:
            self._document_table.put_item(
                Item=document_model.get_payload()
            )
            return True
        except Exception as ex:
            print "ERROR: Failed to create new document: {0}".format(ex)
            return False

    # acquire a lock on the document
    def lock_document(self, doc_id):
        return "hi"
