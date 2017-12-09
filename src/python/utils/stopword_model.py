from sets import Set
from datetime import datetime

class StopWordModel(object):

    # Top Level Fields
    PKEY = 'pKey'
    SORTKEY = 'sortKey'

    # Assign Top Level Fields
    VALID_TOP_LEVEL_FIELDS = [PKEY,
                              SORTKEY]

    def __init__(self):
        self._top_level_fields = Set(self.VALID_TOP_LEVEL_FIELDS)
        self._info = {self.PKEY:'',self.SORTKEY:-1}

    def verify(self):
        return (self._top_level_fields == Set(self._info.keys()))

    def set_data(self, pKey, sortKey):
        self._info[self.PKEY] = pKey
        self._info[self.SORTKEY] = sortKey
        return self

    def with_pkey(self,pKey):
        self._info[self.PKEY] = pKey
        return self

    def with_sortkey(self,sortKey):
        self._info[self.SORTKEY] = sortKey
        return self

    def load_from_input(self, stop_word_input):
        (self.with_pkey(stop_word_input['pKey'])
             .with_sortkey(stop_word_input['sortKey']))
        return self

    def get_pkey(self):
        return self._info[self.PKEY]

    def get_sortkey(self):
        return self._info[self.SORTKEY]

    def get_payload(self):
        return self._info
