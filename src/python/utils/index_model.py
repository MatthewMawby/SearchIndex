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
    SORT_KEY = 'startingToken'
    S3_KEY = 's3Key'
    SIZE = 'size'
    VERSION = 'versionNo'

    # Assign Valid Fields
    VALID_FIELDS = [PKEY,
                    SORT_KEY,
                    S3_KEY,
                    SIZE,
                    VERSION]

    def __init__(self):
        self._info = {
            self.SIZE: 0,
            self.VERSION: 0
        }
        self._valid_fields = Set(self.VALID_FIELDS)

    def verify(self):
        return (self._valid_fields == Set(self._info.keys()))

    def with_pkey(self, pkey):
        self._info[self.PKEY] = pkey
        return self

    def with_sort_key(self, sort_key):
        self._info[self.SORT_KEY] = sort_key
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
