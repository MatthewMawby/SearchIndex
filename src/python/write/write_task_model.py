from sets import Set


class WriteTaskModel(object):
    '''
    This class implements a model for creating write tasks. These
    tasks are posted to kinesis and executed by worker nodes.
    '''

    # Attribute Field Names
    TOKEN_OPERATIONS = 'tokenOperations'
    LOCK_NO_NEXT = 'lockNoNext'
    DOCUMENT_ID = 'documentID'
    WRITE_ID = 'writeID'

    # Valid Fields
    VALID_FIELDS = [TOKEN_OPERATIONS, LOCK_NO_NEXT, DOCUMENT_ID, WRITE_ID]

    # Token Operation Attributes
    TOKEN = 'token'
    LOCATIONS = 'locations'
    PARTITION = 'partitionID'
    NGRAM_SIZE = 'ngramSize'

    # Valid Token Operation Fields
    VALID_TOKEN_OPERATION_FIELDS = [TOKEN, LOCATIONS, PARTITION, NGRAM_SIZE]

    def __init__(self):
        self._valid_fields = Set(self.VALID_FIELDS)
        self._valid_token_op_fields = Set(self.VALID_TOKEN_OPERATION_FIELDS)
        self._task_info = {
            self.TOKEN_OPERATIONS: []
        }

    def get_operations(self):
        return self._task_info[self.TOKEN_OPERATIONS]

    def get_doc_id(self):
        return self._task_info[self.DOCUMENT_ID]

    def get_write_id(self):
        return self._task_info[self.WRITE_ID]

    def get_lock_no_next(self):
        return self._task_info[self.LOCK_NO_NEXT]

    def verify(self):
        if Set(self._task_info.keys()) == self._valid_fields:
            for op in self._task_info[self.TOKEN_OPERATIONS]:
                if Set(op.keys()) != self._valid_token_op_fields:
                    return False
            return True
        return False

    def load(self, task_info):
        self._task_info = task_info

    def get_payload(self):
        return self._task_info

    def with_document_id(self, doc_id):
        self._task_info[self.DOCUMENT_ID] = doc_id
        return self

    def with_lock_no_next(self, next_no):
        self._task_info[self.LOCK_NO_NEXT] = next_no
        return self

    def with_write_id(self, write_id):
        self._task_info[self.WRITE_ID] = write_id
        return self

    def with_token_operation(self, token, ngram_size, locations, partition):
        token_op = {
            self.TOKEN: token,
            self.NGRAM_SIZE: ngram_size,
            self.LOCATIONS: locations,
            self.PARTITION: partition
        }
        self._task_info[self.TOKEN_OPERATIONS].append(token_op)
        return self
