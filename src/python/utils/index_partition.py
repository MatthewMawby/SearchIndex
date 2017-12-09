import cPickle as pickle

from config import Config


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
            payload.close()

    def deserialize(self, in_file):
        with open(in_file, 'rb') as payload:
            self._partition = pickle.load(payload)
            payload.close()

    def get_token_list(self):
        return self._partition.get_token_list()

    def get_token_count(self,key):
        if key not in self._partition._partition.keys():
            return -1
        if self._partition._partition[key]['ngram_size']!=1:
            return -1

        count = 0
        for doc in self._partition._partition[key]['documentOccurrences']:
            count += len(doc['versions'][0]['locations'])
        return count

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

    def get_token_list(self):
        return self._partition.keys()

    ''' INDEX FUNCTIONALITY '''
    # adds token to index if not present, replaces oldest version if present
    def add_token(self, token, doc_id, lock_no, ngram_size, locations):
        # set metadata appropriately
        if token < self._starting_token or self._starting_token is None:
            self._starting_token = token
        if token > self._ending_token or self._ending_token is None:
            self._ending_token = token
        version_info = {'lockNo': lock_no, 'locations': locations}

        # add token data to partition if not present
        if token not in self._partition:
            versions = [version_info]
            doc_info = {'documentID': doc_id, 'versions': versions}
            token_info = {'ngram_size': ngram_size,
                          'documentOccurrences': [doc_info]}
            self._partition[token] = token_info
            self._size += 1
        # otherwise update the info for the token
        else:
            # find the document info for this token in the index
            token_info = self._partition[token]
            occurences = token_info['documentOccurrences']
            doc_info = None
            for info in occurences:
                if info['documentID'] == doc_id:
                    doc_info = info
                    break

            # if not present add it
            if doc_info is None:
                versions = [version_info]
                doc_info = {'documentID': doc_id, 'versions': versions}
                self._partition[token]['documentOccurrences'].append(doc_info)
            # otherwise update version info
            else:
                versions = doc_info['versions']
                if len(versions) == 2:
                    versions[1] = versions[0]
                    versions[0] = version_info
                else:
                    versions.insert(0, version_info)
