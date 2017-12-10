from index_storage import IndexStorage
from index_partition import IndexPartition
from index_controller import IndexController
from stopword_controller import StopWordController
from stopword_model import StopWordModel

import boto3

class StopWordGenerator:

    def __init__(self):
        self._storage = IndexStorage()
        self._partition = None
        self._tokens = {}
        self._stopword = StopWordController()
        self._index = IndexController()

    '''
    Search a partition and update all_tokens with a given version
    '''
    def search_partition(self,key):
        # lookup partition using key
        payload = self._storage.get_partition(key)
        # deserialize key
        self.partition = IndexPartition()
        self.partition.deserialize(payload)
        # length of the token
        partition_token = self.partition.get_token_list()

        for key in self.partition.get_token_list():
            addamount = self.partition.get_token_count(key)
            if(addamount<=0):
                continue
            if(key in self._tokens.keys()):
                self._tokens[key] += addamount
            else:
                self._tokens[key] = addamount
    '''
    generate stop words by searching through all partitions
    '''
    def generate_stopwords(self):
        partition_ids = self._index.get_partition_ids()
        for k in partition_ids:
            self.search_partition(k)
    '''
    iterate through all tokens and add to stopwords table
    '''
    def add_stopwords_table(self):
        for t in self._tokens.keys():
            sw = StopWordModel()
            sw.set_data(t,self._tokens[t])
            self._stopword.add_word(sw)
    '''
    return all stop words as dictionary
    '''
    def get_stop_words(self):
        return self._tokens
