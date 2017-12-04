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
    STORAGE_KEY = 's3Key'
    START_TOKEN = 'startingToken'
    END_TOKEN = 'endingToken'
    SIZE = 'size'
    VERSION = 'versionNo'

    # Assign Valid Fields
    VALID_FIELDS = [PKEY,
                    STORAGE_KEY,
                    START_TOKEN,
                    END_TOKEN,
                    SIZE,
                    VERSION]

    def __init__(self):
        self._info = {
            self.SIZE: 0,
            self.VERSION: 0
        }
        self._valid_fields = Set(self.VALID_FIELDS)

    def get_id(self):
        return str(self._info[self.PKEY])

    def get_storage_key(self):
        return str(self._info[self.STORAGE_KEY])

    def get_size(self):
        return self._info[self.SIZE]

    def get_start_token(self):
        return self._info[self.START_TOKEN]

    def get_end_token(self):
        return self._info[self.END_TOKEN]

    def get_version(self):
        return self._info[self.VERSION]

    def get_payload(self):
        return self._info

    def verify(self):
        return (self._valid_fields == Set(self._info.keys()))

    def with_pkey(self, pkey):
        self._info[self.PKEY] = pkey
        return self

    def with_storage_key(self, skey):
        self._info[self.STORAGE_KEY] = skey
        return self

    def with_start_token(self, start_token):
        self._info[self.START_TOKEN] = start_token
        return self

    def with_end_token(self, end_token):
        self._info[self.END_TOKEN] = end_token
        return self

    def with_size(self, size):
        self._info[self.SIZE] = size
        return self

    def with_version(self, version):
        self._info[self.VERSION] = version
        return self
