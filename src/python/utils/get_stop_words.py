from index_storage import IndexStorage
from index_partition import IndexPartition

from stopword_controller import StopWordController
from stopword_model import StopWordModel

import boto3


'''
Return all partion keys from dynamodb
'''
def get_s3_keys():
    dynamo_client = boto3.client("dynamodb")
    res = dynamo_client.scan(
        TableName="INDEX_PARTITION_METADATA",
        AttributesToGet=[
            's3Key',
        ]
    )
    s3_keys = []
    for i in res['Items']:
        s3_keys.append(i['s3Key']['S'])
    return s3_keys

'''
Search a partition and update all_tokens with a given version
'''
def search_partition(key,all_tokens,cversion):
    # lookup partition using key
    storage = IndexStorage()
    payload = storage.get_partition(key)
    # deserialize key
    partition = IndexPartition()
    partition.deserialize(payload)

    # length of the token
    partition_token = partition.get_token_list()


    for key in partition.get_token_list():
        addamount = partition.get_token_count(key,cversion)
        if(addamount<=0):
            continue

        if(key in all_tokens.keys()):
            all_tokens[key] += addamount
        else:
            all_tokens[key] = addamount

#todo
# add result to stop words table



all_tokens = {}
s3_keys = get_s3_keys()

all_tokens = {}
s3_keys = get_s3_keys()
cversion = 1

for key in s3_keys:
    search_partition(key,all_tokens,cversion)

STOP_WORD = StopWordController()
for t in all_tokens.keys():
    sw = StopWordModel()
    sw.set_data(t,all_tokens[t],cversion)
    STOP_WORD.add_word(sw)


print(all_tokens)
