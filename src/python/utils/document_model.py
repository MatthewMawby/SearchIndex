from sets import Set
from datetime import datetime

from input_models import WriteInputModel


class DocumentModel(object):
    '''
    This class implements the data model required for storing information
    to the DOCUMENTS table. It works in unison with the DocumentControl
    class to create an easy to use interface that is decoupled from the actual
    storage implementation used for documents.
    '''

    # Top Level Fields
    PKEY = 'pKey'
    INTERNAL = 'internal'
    EXTERNAL = 'external'

    # Assign Top Level Fields
    VALID_TOP_LEVEL_FIELDS = [PKEY,
                              INTERNAL,
                              EXTERNAL]

    # Internal Fields
    LOCK_NO = 'lockNo'
    UPDATING = 'updating'
    DELETE = 'delete'
    LAST_UPDATE = 'lastUpdate'
    TOKEN_COUNT = 'tokenCount'

    # Assign Internal Fields
    VALID_INTERNAL_FIELDS = [LOCK_NO,
                             UPDATING,
                             DELETE,
                             LAST_UPDATE,
                             TOKEN_COUNT]

    # External Fields
    WORD_COUNT = 'wordCount'
    LAST_INDEXED = 'lastIndexed'
    TOKEN_RANGES = 'tokenRanges'

    # Assign External Fields
    VALID_EXTERNAL_FIELDS = [WORD_COUNT,
                             LAST_INDEXED,
                             TOKEN_RANGES]

    # Token Range Fields
    RANGE_NAME = 'rangeName'
    RANGE_START = 'rangeStart'
    RANGE_END = 'rangeEnd'

    # Assign Token Range Fields
    VALID_TOKEN_RANGE_FIELDS = [RANGE_NAME,
                                RANGE_START,
                                RANGE_END]

    def __init__(self):
        self._info = {
            self.INTERNAL: {
                self.LOCK_NO: 0,
                self.UPDATING: False,
                self.DELETE: False,
                self.LAST_UPDATE: str(datetime.now())
            },
            self.EXTERNAL: {
                self.TOKEN_RANGES: []
            }
        }
        # for verification
        self._top_level_fields = Set(self.VALID_TOP_LEVEL_FIELDS)
        self._internal_fields = Set(self.VALID_INTERNAL_FIELDS)
        self._external_fields = Set(self.VALID_EXTERNAL_FIELDS)
        self._token_range_fields = Set(self.VALID_TOKEN_RANGE_FIELDS)

    def verify(self):
        for item in self._info[self.EXTERNAL][self.TOKEN_RANGES]:
            if self._token_range_fields != Set(item.keys()):
                return False
        return (self._top_level_fields == Set(self._info.keys()) and
                self._internal_fields == Set(self._info[self.INTERNAL].keys())
                and self._external_fields ==
                Set(self._info[self.EXTERNAL].keys()))

    def get_payload(self):
        return self._info

    def get_pkey(self):
        return self._info[self.PKEY]

    def get_lock_no(self):
        return int(self._info[self.INTERNAL][self.LOCK_NO])

    def get_last_update(self):
        return (datetime.strptime(self._info[self.INTERNAL][self.LAST_UPDATE],
                "%Y-%m-%d %H:%M:%S.%f"))

    def load_from_write_input(self, write_input):
        # set values
        (self.with_pkey(write_input.get_id())
             .with_token_count(write_input.get_token_count())
             .with_word_count(write_input.get_word_count())
             .with_index_time(datetime.now())
             .set_updating(True)
             .set_lockno(0))

        self._info[self.EXTERNAL][self.TOKEN_RANGES] = []
        # add token ranges
        for item in write_input.get_token_ranges():
            range_name = item[WriteInputModel.RANGE_NAME]
            start = item[WriteInputModel.RANGE_START]
            end = item[WriteInputModel.RANGE_END]
            self.with_token_range(range_name, start, end)

    def with_pkey(self, pkey):
        self._info[self.PKEY] = pkey
        return self

    def with_token_count(self, count):
        self._info[self.INTERNAL][self.TOKEN_COUNT] = count
        return self

    def with_word_count(self, count):
        self._info[self.EXTERNAL][self.WORD_COUNT] = count
        return self

    def with_index_time(self, index_time):
        self._info[self.EXTERNAL][self.LAST_INDEXED] = str(index_time)
        return self

    def with_token_range(self, range_name, range_start, range_end):
        token_range = {
            self.RANGE_NAME: range_name,
            self.RANGE_START: range_start,
            self.RANGE_END: range_end
        }
        self._info[self.EXTERNAL][self.TOKEN_RANGES].append(token_range)
        return self

    def set_lockno(self, lock_no):
        self._info[self.INTERNAL][self.LOCK_NO] = lock_no
        return self

    def set_updating(self, updating):
        self._info[self.INTERNAL][self.UPDATING] = updating
        return self

    def set_delete(self, delete):
        self._info[self.INTERNAL][self.DELETE] = delete
        return self

    def set_last_update(self, update_time):
        self._info[self.INTERNAL][self.LAST_UPDATE] = str(update_time)
        return self

    def set_doc_info(self, doc_info):
        if doc_info is None:
            return self
        self._info = doc_info
        return self
