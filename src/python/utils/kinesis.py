import boto3
import uuid
import json
import base64


class Kinesis(object):
    '''
    This class is responsible for dispatching tasks to worker threads. This
    implementation wraps kinesis to post records to the stream provided at
    initialization. It also parses data from b64 strings back to python
    dictionaries.
    '''

    def __init__(self, stream_name):
        self._stream_name = stream_name
        self._kinesis = boto3.client('kinesis')

    # post records to kinesis stream
    def dispatch_tasks(self, task_list):
        records = []
        for task in task_list:
            records.append({
                'PartitionKey': str(uuid.uuid4()),
                'Data': json.dumps(task.get_payload())
            })
        try:
            self._kinesis.put_records(
                Records=records, StreamName=self._stream_name
            )
        except Exception as ex:
            print "ERROR: Failed to put records to kinesis stream."
            raise ex

    # parse a list of tasks (dictionaries) from kinesis Records
    def parse_tasks_from_records(self, records):
        tasks = []
        for record in records:
            b64_string = record['kinesis']['data']
            json_payload = base64.b64decode(b64_string)
            tasks.append(json.loads(json_payload))
        return tasks
