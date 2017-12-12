## Write Operation Overview
This directory contains the application logic for the write operation.
This operation is represented visually here:
![Write Operation](/assets/write_operation.png) 

### Write Master Node
This is the node that is triggered by a write call to the AWS API Gateway, 
in the above image this is the first lambda from left to right.
The write event will take the form:

 ```javascript
{
  documentMetadata: {
    documentID: string,
    wordCount: int,
    importantTokenRanges: [
      {
        fieldName: string,
        rangeStart: int,
        rangeEnd: int
      }
    ]
  }
  tokens: [
    token: string,
    ngramSize: int,
    locations: [int]
  ]
}
```

The Master Node is responsible for receiving token information for a document
and creating each write task to write token information to the index. 
The Master Node writes to an AWS Kinesis stream, triggering each worker node to search for its given token(s).

### Write Worker Node
Worker Nodes are triggered when the Master Node writes to the Kinesis stream.
In the above image, this is the second lambda from left to right.
This Worker write event will take the form:

```javascript
{
  tokenOperations: [
    {
      token: string,
      locations: [int],
      partitionURIs: [string]
    }
  ],
  lockNoNext: int,
  documentID: string,
  writeID: string
}
```

The Worker Node is responsible for receiving token information and an associated partition, 
and writing the token to the partition. As of this writing, 
if there are multiple tokens in the same partition, a worker node will be created for each 
token. However, the intent is to allow for a single worker node to interact with a single partition.


### Write Task Model
This class implements a model for creating write tasks. 
These tasks are posted to kinesis and executed by worker nodes.
It contains the following attributes:

* Token Operations - Contains all the token information (token, locations, partition, ngram size)
* Lock Number Next - For document locking
* Document ID - Document ID of the document for this write call
* Write ID - ID Number for identifying which worker nodes are associated with which master node

The Write Task Model can be provided these attributes by using the associated with_ builder functions.
For example: 

```python
write_task = (WriteTaskModel().with_write_id(write_id)
                                      .with_document_id(write_input.get_id())
                                      .with_lock_no_next(lock_next)
                                      .with_write_id(write_id)
                                      .with_token_operation(token,
                                                            ngram_size,
                                                            locations,
                                                            partition))
```

This class also provides the following functionality:

* verify(self) - Used by Master Node, ensures provided attributes are valid.
* load(self, task_info) - Used by Worker Node, loads a dictionary into the WriteTaskModel
* get_payload(self) - Returns the dictionary of the WriteTaskModel attributes
* Getters for individual attributes


