from sets import Set
from datetime import datetime
import boto3
import json

from document_model import DocumentModel
from document_controller import DocumentController
# from index_model import IndexModel
# from index_controller import IndexController

DOCUMENTS = DocumentController()

LOCK_NO = None
LAST_UPDATE = None

# lock expiration threshold in seconds
EXPIRATION_THRESH = 120


# ParamTypes: Error, Dictionary
def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': err.message if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
        },
    }


def get_document(write_info):
    pkey = write_info['documentID']
    return DOCUMENTS.get_document(pkey)

# creates a new document in the locked state
def create_new_doc(write_info):
    pkey = write_info['documentID']
    wc = write_info['wordCount']
    ranges = write_info['importantTokenRanges']

    # init doc model
    doc_model = (DocumentModel().with_pkey(pkey)
                                .with_token_count(wc)
                                .with_word_count(wc)
                                .with_index_time(datetime.now())
                                .set_updating(True))

    # add token ranges
    for item in ranges:
        range_name = item['fieldName']
        start = item['rangeStart']
        end = item['rangeEnd']
        doc_model.with_token_range(range_name, start, end)

    return DOCUMENTS.create_new_document(doc_model)


def lambda_handler(event, context):

    # Set of supported operations for this endpoint
    # operations = Set(['POST'])
    #
    # operation = event['context']['http-method']
    # if operation in operations:
    #     return respond(None, event['body-json'])
    # else:
    #     return respond(ValueError('Unsupported method "{}"'.format(operation)))

    test_write = {
        "documentID": "testID",
        "wordCount": 10,
        "importantTokenRanges": [{
            "fieldName": "title",
            "rangeStart": 0,
            "rangeEnd": 2
        }],
        "tokens": [{
            "token": "Here",
            "ngramSize": 1,
            "locations": [0]
        }, {
            "token": "Be",
            "ngramSize": 1,
            "locations": [1]
        }, {
            "token": "Title",
            "ngramSize": 1,
            "locations": [2]
        }]
    }

    doc = get_document(test_write)

    # if the document is present, acquire a lock on it & start write
    if doc:
        internal_info = doc[DocumentModel.INTERNAL]
        LOCK_NO = internal_info[DocumentModel.LOCK_NO]
        LAST_UPDATE = (datetime.strptime(
                        internal_info[DocumentModel.LAST_UPDATE],
                        "%Y-%m-%d %H:%M:%S.%f"))
        lock_age = (datetime.now() - LAST_UPDATE).seconds
        if lock_age < EXPIRATION_THRESH:
            exit("Document Locked")

    # otherwise create it with a lock
    else:
        if create_new_doc(test_write):
            print "CREATED DOCUMENT"
