from sets import Set


class WriteInputModel(object):
    '''
    This class implements the data model & functions for parsing an
    input request into an input object for the write service. This
    class initializes and retrieves input information from the request.
    '''

    # Attributes
    DOCUMENT_ID = 'documentID'
    TOKEN_COUNT = 'tokenCount'
    TOKEN_RANGES = 'importantTokenRanges'
    TOKENS = 'tokens'

    # Assign Valid Fields
    VALID_FIELDS = [DOCUMENT_ID, TOKEN_COUNT, TOKEN_RANGES, TOKENS]

    # Token Range Attributes
    RANGE_NAME = 'fieldName'
    RANGE_START = 'rangeStart'
    RANGE_END = 'rangeEnd'

    # Assign Token Range Valid Fields
    VALID_TOKEN_RANGE_FIELDS = [RANGE_NAME, RANGE_END, RANGE_START]

    # Token Attributes
    TOKEN = 'token'
    NGRAM_SIZE = 'ngramSize'
    LOCATIONS = 'locations'

    # Assign Token Valid Fields
    VALID_TOKEN_FIELDS = [TOKEN, NGRAM_SIZE, LOCATIONS]

    def __init__(self):
        self._info = {}
        self._valid_fields = Set(self.VALID_FIELDS)
        self._valid_token_range_fields = Set(self.VALID_TOKEN_RANGE_FIELDS)
        self._valid_token_fields = Set(self.VALID_TOKEN_FIELDS)

    def get_id(self):
        return self._info[self.DOCUMENT_ID]

    def get_token_count(self):
        return self._info[self.TOKEN_COUNT]

    def get_word_count(self):
        count = 0
        for token in self._info[self.TOKENS]:
            if token[self.NGRAM_SIZE] == 1:
                count += 1
        return count

    def get_token_info(self):
        return self._info[self.TOKENS]

    def get_token_ranges(self):
        return self._info[self.TOKEN_RANGES]

    def verify(self):
        if Set(self._info.keys()) == self._valid_fields:
            for token_range in self._info[self.TOKEN_RANGES]:
                if Set(token_range.keys()) != self._valid_token_range_fields:
                    return False
            for token in self._info[self.TOKENS]:
                if Set(token.keys()) != self._valid_token_fields:
                    return False
            return True
        return False

    def parse_from_request(self, req):
        self._info = req
