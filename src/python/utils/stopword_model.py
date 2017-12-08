from sets import Set
from datetime import datetime


class StopWordModel(object):

    # Top Level Fields
    PKEY = 'pKey'
    SORTKEY = 'sortKey'
    VERSION = 'version'

    # Assign Top Level Fields
    VALID_TOP_LEVEL_FIELDS = [PKEY,
                              SORTKEY,VERSION]

    def __init__(self):
        self._top_level_fields = Set(self.VALID_TOP_LEVEL_FIELDS)
        self._info = {self.PKEY:'',self.SORTKEY:-1,self.VERSION:-1}

    def set_data(self, pKey, sortKey,version):
        self._info[self.PKEY] = pKey
        self._info[self.SORTKEY] = sortKey
        self._info[self.VERSION] = version
        return self

    def get_pkey(self):
        return self._info[self.PKEY]

    def get_sortkey(self):
        return self._info[self.SORTKEY]

    def get_payload(self):
        return self._info
