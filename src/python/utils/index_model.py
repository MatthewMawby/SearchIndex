from sets import Set


class IndexModel(object):
    '''
    This class implements the data model required for storing information
    to the INDEX_METADATA table. It works in unison with the IndexControl
    class to create an easy to use interface that is decoupled from the actual
    storage implementation used for index metadata.
    '''

    # Attributes
    PKEY = 'pKey'
    START_TOKEN = 'startingToken'
    END_TOKEN = 'endingToken'
    S3_KEY = 's3Key'
    SIZE = 'size'
    VERSION = 'versionNo'

    # Assign Valid Fields
    VALID_FIELDS = [PKEY,
                    START_TOKEN,
                    END_TOKEN,
                    S3_KEY,
                    SIZE,
                    VERSION]

    def __init__(self):
        self._info = {
            self.SIZE: 0,
            self.VERSION: 0
        }
        self._valid_fields = Set(self.VALID_FIELDS)

    def get_payload(self):
        return self._info

    def verify(self):
        return (self._valid_fields == Set(self._info.keys()))

    def with_pkey(self, pkey):
        self._info[self.PKEY] = pkey
        return self

    def with_start_token(self, start_token):
        self._info[self.START_TOKEN] = start_token
        return self

    def with_end_token(self, end_token):
        self._info[self.END_TOKEN] = end_token
        return self

    def with_s3_key(self, s3_key):
        self._info[self.S3_KEY] = s3_key
        return self

    def set_size(self, size):
        self._info[self.SIZE] = size
        return self

    def set_version(self, version):
        self._info[self.VERSION] = version
        return self
