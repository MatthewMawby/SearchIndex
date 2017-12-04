import boto3
from datetime import datetime
from boto3.dynamodb.conditions import Key, Attr
from document_model import DocumentModel


class DocumentController(object):
    '''
    This class implements the data access for the DOCUMENTS table. It is
    responsible for all operations with the table including creating documents,
    reading documents, and modifying the state of documents.
    '''

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
            raise ex

    # set updating field to true & set lastUpdate timestamp
    def lock_document(self, doc_id):
        now = str(datetime.now())
        update_expression = 'set {0}.{1} = :updating, {2}.{3} = :now'.format(
            DocumentModel.INTERNAL,
            DocumentModel.UPDATING,
            DocumentModel.INTERNAL,
            DocumentModel.LAST_UPDATE)
        try:
            res = self._document_table.update_item(Key={
                DocumentModel.PKEY: doc_id
            }, UpdateExpression=update_expression, ExpressionAttributeValues={
                ':updating': True,
                ':now': now
            })
        except Exception as ex:
            print "ERROR: Failed to acquire lock on document"
            raise ex

    # set updating field to false for given document
    def unlock_document(self, doc_id):
        now = str(datetime.now())
        update_expression = 'set {0}.{1} = :updating'.format(
            DocumentModel.INTERNAL,
            DocumentModel.UPDATING)
        try:
            res = self._document_table.update_item(Key={
                DocumentModel.PKEY: doc_id
            }, UpdateExpression=update_expression, ExpressionAttributeValues={
                ':updating': False
            })
        except Exception as ex:
            print "ERROR: Failed to unlock document"
            raise ex

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
            raise ex
