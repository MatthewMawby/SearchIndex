import cPickle as pickle


class IndexPartition(object):
    '''
    This class wraps the _IndexPartition class to provide serialization.
    It stores and loads an _IndexPartition object internally.
    '''

    def __init__(self):
        self._partition = _IndexPartition()

    def size(self):
        return self._partition.size()

    def starting_token(self):
        return self._partition.starting_token()

    def ending_token(self):
        return self._partition.ending_token()

    def add_token(self, token, doc_id, lock_no, ngram_size, locations):
        self._partition.add_token(token, doc_id, lock_no, ngram_size,
                                  locations)

    def serialize(self, out_file):
        with open(out_file, 'wb') as payload:
            pickle.dump(self._partition, payload, pickle.HIGHEST_PROTOCOL)

    def deserialize(self, in_file):
        with open(in_file, 'rb') as payload:
            self._partition = pickle.load(payload)


class _IndexPartition(object):
    '''
    This class is provides a uniform way of reading from, writing to,
    and creating index partitions. It stores some metadata about the
    partition as well as the the token metadata.
    '''

    def __init__(self):
        self._partition = {}
        self._size = 0
        self._starting_token = None
        self._ending_token = None

    ''' GETTERS '''
    def size(self):
        return self._size

    def starting_token(self):
        return self._starting_token

    def ending_token(self):
        return self._ending_token

    ''' INDEX FUNCTIONALITY '''
    # adds token to index if not present, replaces oldest version if present
    def add_token(self, token, doc_id, lock_no, ngram_size, locations):
        # set metadata appropriately
        if token < self._starting_token or self._starting_token is None:
            self._starting_token = token
        if token > self._ending_token or self._ending_token is None:
            self._ending_token = token
        # add token data to partition
        version_info = {'lockNo': lock_no, 'locations': locations}
        if token not in self._partition:
            versions = [version_info]
            doc_info = {'documentID': doc_id, 'versions': versions}
            token_info = {'ngram_size': ngram_size,
                          'documentOccurrences': doc_info}
            self._size += 1
        else:
            token_info = self._partition[token]
            doc_info = token_info[doc_id]
            versions = doc_info['versions']
            # newest version is always first version
            versions[1] = versions[0]
            versions[0] = version_info
