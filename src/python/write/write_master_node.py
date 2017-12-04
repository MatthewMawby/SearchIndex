from sets import Set
from datetime import datetime
import boto3
import json
import uuid

from config import Config
from document_controller import DocumentController
from document_model import DocumentModel
from index_controller import IndexController
from index_model import IndexModel
from input_models import WriteInputModel
from kinesis import Kinesis
from write_task_model import WriteTaskModel

'''
GLOBALS
'''
INDEX_METADATA = IndexController()
DOCUMENTS = DocumentController()
KINESIS = Kinesis(Config.WRITE_STREAM)

# lock expiration threshold in seconds
EXPIRATION_THRESH = 0


def lambda_handler(event, context):

    # Set of supported operations for this endpoint
    # operations = Set(['POST'])
    #
    # operation = event['context']['http-method']
    # if operation in operations:
    #     return respond(None, event['body-json'])
    # else:
    #     return respond(ValueError('Unsupported method "{}"'.format(operation)))

    request = {
        "documentID": "testID",
        "tokenCount": 10,
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

    # parse the request to the write input model
    write_input = WriteInputModel()
    write_input.parse_from_request(request)
    if not write_input.verify():
        print "ERROR: Invalid input."
        raise Exception("Invalid input.")

    # retrieve the document & construct document model
    doc_info = DOCUMENTS.get_document(write_input.get_id())
    doc = DocumentModel()
    doc.set_doc_info(doc_info)

    # verify doc exists or create it, then lock it
    if doc.verify():
        last_update = doc.get_last_update()
        lock_age = (datetime.now() - last_update).seconds
        if lock_age < EXPIRATION_THRESH:
            print "ERROR: Document already locked."
            exit("Document Locked")
        else:
            DOCUMENTS.lock_document(doc.get_pkey())
            print "INFO: locked document with id {0}".format(doc.get_pkey())

    # otherwise create it with a lock
    else:
        doc.load_from_write_input(write_input)
        DOCUMENTS.create_new_document(doc)
        print "INFO: created new doc with id: {0}".format(doc.get_pkey())

    write_tasks = create_write_tasks(write_input, doc.get_lock_no() + 1)
    KINESIS.dispatch_tasks(write_tasks)
    print "INFO: sent {0} write tasks to kinesis".format(len(write_tasks))
    # aggregate_results()
    DOCUMENTS.unlock_document(doc.get_pkey())
    print "INFO: unlocked document with id: {0}".format(doc.get_pkey())


# ParamTypes: Error, Dictionary
def respond(err, res=None):
    return {
        'statusCode': '400' if err else '200',
        'body': err.message if err else json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
        },
    }


# TODO: if two tokens are in all of the same partitions, write 2 token ops to
# one task instead of a separate task for each
def create_write_tasks(write_input, lock_next):
    write_tasks = []
    write_id = str(uuid.uuid4())
    tokens = write_input.get_token_info()
    for tok_info in tokens:
        token = tok_info[WriteInputModel.TOKEN].lower()
        locations = tok_info[WriteInputModel.LOCATIONS]
        ngram_size = tok_info[WriteInputModel.NGRAM_SIZE]
        partition = INDEX_METADATA.get_partition_for_token(token)
        write_task = (WriteTaskModel().with_write_id(write_id)
                                      .with_document_id(write_input.get_id())
                                      .with_lock_no_next(lock_next)
                                      .with_write_id(write_id)
                                      .with_token_operation(token,
                                                            ngram_size,
                                                            locations,
                                                            partition))
        if write_task.verify():
            write_tasks.append(write_task)
    return write_tasks


lambda_handler(0, 0)
