import uuid
import os

from config import Config
from index_controller import IndexController
from index_model import IndexModel
from index_partition import IndexPartition
from index_storage import IndexStorage
from kinesis import Kinesis
from write_task_model import WriteTaskModel


KINESIS_STREAM = 'writeMastertoWorker'
KINESIS = Kinesis(KINESIS_STREAM)
INDEX_METADATA = IndexController()
INDEX_STORAGE = IndexStorage()


def lambda_handler(event, context):
    os.chdir(Config.FILE_DIRECTORY)
    # tasks = KINESIS.parse_tasks_from_records(event['Records'])
    tasks = [{'writeID': '5005dbda-7889-49a7-bdb2-2a44609f0ef7',
              'tokenOperations': [{'token': 'here',
                                   'locations': [0],
                                   'partitionID':
                                   '',
                                   'ngramSize': 1}],
              'lockNoNext': 1,
              'documentID': 'testID2'}]
    for task in tasks:
        write_task = WriteTaskModel()
        write_task.load(task)
        execute_task(write_task)


def execute_task(task):
    # task info
    doc_id = task.get_doc_id()
    write_id = task.get_write_id()
    doc_lock = task.get_lock_no_next()

    # execute all the token operations
    for token_op in task.get_operations():
        # token op info
        token = token_op[WriteTaskModel.TOKEN]
        ngram_size = token_op[WriteTaskModel.NGRAM_SIZE]
        partition_id = token_op[WriteTaskModel.PARTITION]
        locations = token_op[WriteTaskModel.LOCATIONS]

        # always write with a new storage key for optimistic locking
        storage_key = str(uuid.uuid4())

        # create partition object, load from storage if id provided
        partition = IndexPartition()
        new_partition = False
        lock_no = 0
        old_storage_key = None
        if partition_id == '':
            partition_id = str(uuid.uuid4())
            new_partition = True
            print ("INFO: Creating new partition with id: {0}"
                   .format(partition_id))
        else:
            # read-before-write, get the current lockno & storage key
            (lock_no, old_storage_key) = (INDEX_METADATA
                                          .get_version_info(partition_id))
            # retrieve & load existing partition
            payload = INDEX_STORAGE.get_partition(old_storage_key)
            partition.deserialize(payload)

        # update the partition
        partition.add_token(token, doc_id, doc_lock, ngram_size, locations)

        # save the partition
        INDEX_STORAGE.write_partition(storage_key, partition)
        print ("INFO: Wrote partition with pkey {0} and storage key {1}"
               .format(partition_id, storage_key))

        # update index metadata
        index_update = (IndexModel().with_pkey(partition_id)
                        .with_start_token(partition.starting_token())
                        .with_storage_key(storage_key)
                        .with_end_token(partition.ending_token())
                        .with_size(partition.size())
                        .with_version(lock_no))

        INDEX_METADATA.update_metadata(index_update, new_partition)
        print ("INFO: updated metadata for partition: {0}"
               .format(partition_id))
        if not new_partition:
            INDEX_STORAGE.delete_partition(old_storage_key)
            print "INFO: removed partition: {0}".format(old_storage_key)

        # write result back to master node
        # TODO


lambda_handler(0, 0)
