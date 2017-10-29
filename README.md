## Overview
Creating a search index for a large number of documents is not an easy task. It requires the acquisition, processing, storage, and retrieval of large amounts of
data. One of the main use cases for such an index is a web search engine. A search
engine capable of indexing the web can be divided into several large architectural
components that each perform one of the aforementioned subtasks.

| Component | Sub-task | Responsibilities |
|-----------|----------|------------------|
| Crawling  | acquisition | Crawl the web & accumulate data |
| Link Analysis | processing | Apply Page Rank to documents in the web graph |
| Text Transformation | processing | Parse tokens and metadata from documents |
| Indexing | storage, retrieval | Store & retrieve data from reverse index |
| Ranking | processing | Sort documents retrieved from index |
| Querying | retrieval | Deconstruct queries & display results |


This documentation is focused on the Indexing component, but it is important to
understand the system as a whole in order to understand the behavior the Index must
provide. The diagram below should help provide some clarity on how Indexing
interacts with the other components.

INSERT DIAGRAM HERE

## Constraints
When designing any large scale data storage service there are certain trade-offs
that must be made. The CAP theorem states that it's impossible for a distributed
data store to provide more than two of the following qualities: Consistency,
Availability, and Partition Tolerance. An indexing solution needs to provide all
of these qualities to some extent, but since it is impossible to fully provide
all qualities, some sacrifices need to be made. In order to search large amounts
of data, an index must be large. This requires that the index be split across
multiple partitions which makes Partition Tolerance a required quality for the
system to function properly. Since the system is distributed it means that writes
take a much longer time, and in order to provide a completely consistent state
reads and writes would need to be blocked until a write completed. If many writes
happen, this completely kills availability. As such, availability is a higher
priority than consistency. In order to be useful, the index must still provide
some consistency, but it doesn't need to always have a consistent internal state.
The system must instead guarantee eventual consistency. This means that after
the completion of writes, all reads will return the same data. Essentially changes
will not be visible until the write finishes.

The constraints inherent to distributed data stores are not the only constraints
present for this project. The other main constraint we must work around is the
inability to retain our indices within RAM. This will drastically reduce the
performance of our index as the index must be partitioned and persisted and
loaded into memory partition by partition. This incurs the overhead of loading
a serialized object into memory as well as the network overhead associated with
retrieving the partitions. While these constraints reduce our performance, they
do make the design easier in that data persistence and distribution can be easily
managed. Since the index partitions must be persisted elsewhere, there is no
concern of losing data and as such no steps must be taken to provide features such
as data replication. The other benefit this provides is that the distribution of
indices across nodes can be dynamically changed at runtime. Since the partitions
are retrieved from persistent storage on each request, we can efficiently
distribute partitions across nodes without needing to coordinate transfer of
partitions between nodes.


## Index Representation
This section will focus primarily on the structure of the index itself. This is
the place to look if you want to know what information the index stores. This
section also describes how the index is partitioned and persisted. The index is
broken up into two major parts, the reverse index containing the tokens, and a
document store containing document metadata.

### Index Schema
This is the part of the index that actually stores the tokens. Aside from storing
tokens, this structure also needs to store metadata that can only be determined
by the functional dependency of token + docID -> metadata. Metadata that fits in
this category includes location of a token in a document, the number of times a
word occurs in a document, and a version number so we know which version of data
is present.

The actual data structure that is used to store this information is a HashMap. This
gives us constant access time for any given token, so searches are extremely quick
once the structure is loaded into memory.

Each index partition will be a HashMap mapping a token to a data object
```java
import java.util.HashMap;
HashMap<String, Object> index_partition = new HashMap();
```

This is the proposed schema of the data object stored for each token:
```javascript
{
  ngramSize: int,
  documentOccurences: [
    {
      documentID: string,
      versions: [
        {
          lockNo: int,
          locations: [int]
        }
      ]
    }
  ]
}
```
This saved data object enables us to save not just the locations of a token
in multiple documents, but it also enables us to save multiple versions of
the locations within a given document. The necessity of this addition is
explained in the consistency section. It is important to note that there will
never be more than two versions of data saved for each token + document combo.

### Index Partitioning & Persistence
Since it is not possible to keep a large index in memory, the index must be
partitioned, persisted, and distributed in some manner. Since one of our constraints
is the lack of hosts, we will need to use a centralized data store rather than
keeping the partitions distributed across hosts in RAM.

One of the easiest, cheapest, and most scalable ways to accomplish this is to
serialize the partitions and to store them in S3. New index partitions can easily
be added, and partitions can be stored and retrieved in batches. This also enables a
node to iterate over the objects in a given S3 bucket, so a node could be instructed
to process a particular range of index partitions by being provided with a starting
and ending partition key.

The size of each index is also important. Partitions need to be large enough that
the overhead of de-serializing each partition into memory doesn't take too much time,
but they also must remain small enough that they can be easily transferred across
a network. They must also remain small enough that a host is able to load multiple
indices into memory. This allows the host to process multiple partitions sequentially
by loading the next partition into memory as it's searching the current partition.
Indices will also need to be merged as tokens are added/removed from the index. This
will be performed by a background process. More information on how this will work
can be found below.

The final important aspect to consider when partitioning an index is how tokens
are distributed across index partitions. Given a write heavy load, it would make
sense to distribute tokens randomly across all partitions as this would prevent
hot spots and would enable performant writes. The downside to this arrangement is
twofold: First, duplicate tokens might be stored since a token may already be
present in a different partition. Second, this makes read inefficient as every
index partition must be searched to guarantee that all data was retrieved. A
different solution that would be more optimal for a read heavy load is to partition
the index based upon the ranges of tokens in each segment. Each partition will
contain tokens beginning with the same character, and each partition will know
which alphabetical range of tokens it contains. This enables us to easily narrow
down which index partitions might contain a particular token thus providing
much more performant reads.

### Index Metadata
Given that the index is partitioned and persisted externally, we need some way
to determine which tokens are in which partitions as well as where each partition
is stored. This needs to be done without having to load partitions into memory,
thus this metadata must be stored externally. As mentioned in the previous section,
the index is partitioned based on the starting character of tokens, and each
partition stores tokens within a certain range. The starting character for each
partition will not change after creation of the partition, but the range of tokens
stored in each index can change with updates. This necessitates that the database
documents containing indices ranges must be stratified by partition in order to
avoid a database partition hotspot. We don't want to update the same document every
time we write to a partition.

```javascript
INDEX_PARTITION_METADATA_TABLE
{
  pKey: string,
  sortKey: string,
  uri: string,
  size: int
}
```

The sortKey will have the format "startingToken|endingToken"
The format of the sort key makes it possible to perform range queries that
retrieve all documents for partitions relevant to a given token. Concatenating
the tokens in this format essentially provides sorting first based on first by the
token at the start of the range stored in that partition, and secondarily based on
the token at the end of the alphabetical range stored in the partition.

### Document Schema
In addition to storing information about which tokens are found in which documents,
the search index must also store and retrieve metadata regarding each document.
The types of metadata stored can be broken up into two categories: internal and
external.

**Internal**  
Internal metadata is metadata saved for each document that is needed to provide
synchronization and consistency across nodes.

**External**  
External metadata is metadata that is stored for each document that is not used
by the index itself, but is instead needed for Ranking to use in their algorithm.

The proposed document metadata schema is this:
```javascript
DOCUMENT_TABLE
{
  pKey: string,
  internal: {
    lockNo: int,
    updating: bool,
    markedForDeletion: bool,
    lastUpdate: datetime,
    tokenCount: int
  },
  external: {
    wordCount: int,
    pageLastIndexed: datetime,
    importantTokenRanges: [
      {
        fieldName: string,
        rangeStart: int,
        rangeEnd: int
      }
    ]
  }
}
```
### Document Persistence
Documents will be persisted in an external database. DynamoDB is a fitting option
as it works well with other AWS Services, provides the range query functionality
we require, and functions as a scalable black box.

## Index Behavior
This section will focus on index behavior. This section describes how various
operations can be performed on the index as well as the consistency behavior
it will exhibit due to these operations. The three main operations that will be
performed on the index will be reads, writes, and deletes. Background processes
will also need to be run on the index to perform operations that would otherwise
block availability.

### Read
Read is the core function of the index, and as such this needs to be a quick
operation. Fortunately, partitioning our index enables asynchronous parallel
searches to be run for sets of tokens. In order to launch async searches of
different partitions we will make use of AWS Lambda. Searches will begin with
a REST call to an API Gateway that trigger a Lambda. This first lambda is
responsible for deconstructing the invocation and determining which index partitions
should be searched. The input for this call should simply be JSON containing
the tokens to be queried.

```javascript
{
  tokens: [string]
}
```

Once this has been determined, the Lambda posts records to a kinesis stream which
will trigger asynchronous Lambdas to process their given partitions. The documents
posted to kinesis, and thus the inputs for the second Lambdas will be of this format:

```javascript
{
  partitionURIs: [string],
  searchTokens: [string],
  queryID: string
}
```

These intermediary Lambdas will retrieve the partitions they need to search from S3,
search for their specified tokens, and relay the results to an aggregator. The
results sent to the aggregator will be of this format:

```javascript
{
  tokens: [
    {
      token: string,
      ngramSize: int,
      documentOccurences: [
        {
          documentID: string,
          lockNo: int,
          locations: [int]
        }
      ]
    }
  ],
  queryID: string
}
```

The aggregator is responsible for combining the results of the parallel
searches and resolving any consistency issues. This is done by ensuring that
if multiple tokens match to the same document, the returned values must be for
the correct lockNo. If the lockNo differs then the search is repeated for those
specific tokens. Once the results have been combined, the aggregator retrieves
document metadata for the resulting documents. Once again, the aggregator will
compare the lockNo of the document and re-launch queries for tokens that appeared
in a given document if there is a mismatch. If a document has been deleted while
a read was in progress, tokens for the deleted document will be discarded from
the results sent to the aggregator. Once all documents have been successfully
retrieved, the aggregator sends a response of the following format to the initial
requestor.

```javascript
{
  returnCode: int,
  error: string,
  documents: [
    {
      documentID: string,
      wordCount: int,
      pageLastIndexed: datetime,
      importantTokenRanges: [
        {
          fieldName: string,
          rangeStart: int,
          rangeEnd: int
        }
      ]
    }
  ],
  tokens: [
    token: string,
    ngramSize: int,
    documentOccurences: [
      {
        documentID: string,
        locations: [int]
      }
    ]
  ]
}
```

Valid return codes are:  

| return code | meaning | description |
|-------------|---------|-------------|
| 0 | success | Read completed in its entirety without error. |
| 1 | partial failure | Read failed for one or more tokens |
| 2 | throttling failure | Read failed due to database throttling. |
| 3 | internal failure | Read failed due to internal error. |

It is important to note that the role of the aggregator can also be performed
by the initial node that dispatched the search query.

This diagram shows the flow & separation of roles in search:  
INSERT DIAGRAM HERE

### Write
Like read, writes can also be performed concurrently. Writing to the index is more
involved than reads. Writes begin with a call to index a document. This call will
pass an object such as the one detailed below to pass all information needed to
perform the write.

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

The first step for a write to proceed is for it to acquire a lock on a the document.
To do this it retrieves the current lockNo of the document from the database and
sets the updating field to true. If the updating field was already true the write
is abandoned and the appropriate returnCode is set in the response. If the document
does not exist already, then the write continues. The next step in the write is
to dispatch records of the following format to a kinesis stream which will trigger
a Lambda to write the given token.

```javascript
{
  tokens: [
    {
      token: string,
      locations: [int]
    }
  ],
  lockNoNext: int,
  documentID: string,
  writeID: string
}
```

Each triggered Lambda will then determine which index partitions it needs to write
to. If more than one potential partition exists for the given token range, it will
prioritize writing to the smaller partition. If only one partition exists, but it is
at maximum size, then a new partition will be created. Writes must also appropriately
update the INDEX_PARTITION_METADATA_TABLE appropriately. After writing to the
partition, the Lambda sends a record in the format below to an aggregator.

```javascript
{
  returnCode: int,
  failedTokens: [string],
  writeID: string
}
```

The aggregator sends a response back to the requestor in the following format:

```javascript
{
  returnCode: int,
  failedTokens: [string],
  documentID: string
}
```

Valid return codes are:  

| return code | meaning | description |
|-------------|---------|-------------|
| 0 | success | Write completed in its entirety without error. |
| 1 | partial failure | One or more tokens failed to write. |
| 2 | lock failure | Write failed because the document is locked. |
| 3 | throttling failure | Write failed due to database throttling. |
| 4 | internal failure | Write failed due to internal error. |

This diagram depicts the flow of the write operation:  
INSERT DIAGRAM HERE

### Delete
The delete operation has differing behavior depending on the input. The input
comes in the following format:  

```javascript
{
  documentID: string,
  tokens: [string]
}
```

If the documentID is provided without any tokens the delete operation will delete
the document and all associated tokens. If both the documentID and tokens are
provided, then the provided tokens will be deleted for the given document.

**Deleting a document**  
Deleting a document is a simple operation. The document is simply marked for removal
and the document and its associated tokens will be cleaned up by a background scan.  

**Deleting specific tokens for a given document**  
This operation is performed in a similar manner to read and write. The initial
Lambda processes the delete command and posts records triggering delete operation
lambdas. The posted records are of the following format:  

```javascript
{
  documentID: string,
  tokens: [string],
  deleteID: string
}
```

The delete operation lambda acquires a lock on the given document and determines
which partitions the given tokens are present in and removes the tokens from the
partition. For each deleted token, the tokenCount for the document is decremented.
When the tokenCount reaches 0, the document is also deleted.

After completing a delete operation, the lambdas will post a record of the following
format to an aggregator:

```javascript
{
  returnCode: int,
  deleteID: string
}
```

The Aggregator will merge results and return a response of the following format
to the requestor:

```javascript
{
  returnCode: int,
  errorMessage: string
}
```

Valid return codes are:  

| return code | meaning | description |
|-------------|---------|-------------|
| 0 | success | Delete completed in its entirety without error. |
| 1 | partial failure | One or more tokens failed to delete. |
| 2 | lock failure | Delete failed because the document is locked. |
| 3 | throttling failure | Delete failed due to database throttling. |
| 4 | internal failure | Delete failed due to internal error. |

### Consistency
Since the index is partitioned and distributed, maintaining consistency can
be quite challenging. There are a couple of scenarios which can create an
inconsistent state. This section will enumerate those scenarios and describe
the ramifications this has on index usage.

**Write finishes during read**  
If a version is updated while a read is executing, it is possible that results
from differing versions of documents could be returned. The way this consistency
issue is resolved is described in more detail in the read operation. Users can
expect to see the results of a successful write in any read that completes after
the write finishes. This is true no matter which operation was invoked first.

**Delete occurs during read**  
If a document is deleted during a read, it is possible that a read will retrieve
tokens for a document that has been marked for deletion. Upon aggregation of results
the read operation will discard any results that point to a deleted document. Once
again this behavior only occurs if a delete operation terminates prior to termination
of the read operation. Again, the order of invocation has no bearing on this
behavior.

**Writing**  
Writing can cause consistency issues if multiple writes are started for the same
document at the same time. This consistency concern is avoided in this implementation
by providing a lock on the document. Pessimistic locking is used since it is easier
to implement than optimistic locking, despite multiple updates for the same document
occurring at once being an extremely unlikely scenario. Pessimistic locking is
used simply due to the ease of implementing it. There is also no risk of deadlock
since each Lambda will never need to acquire more than one lock at a time.

### Background Scans
There are some operations that require a linear scan of the index. These operations
will be run periodically and automatically in the background. These are largely
maintenance operations.

#### N-Gram Operations
There are two operations that must be performed with respect to N-Gram maintenance.
The first operation is to determine the most common words in the index. The second
operation involves removing N-Grams that are no longer valid.

**Determining stop words**
This operation requires a process to iterate over all partitions of the index and
count the number of occurrences for all tokens within the index. Only tokens with
ngramSize of 1 are checked. The top N most frequently occurring tokens are added
to the stopwords table.

```javascript
STOPWORDS_TABLE
{
  pKey: string
  sortKey: int
}
```

The partition key is the token and the sort key is the number of occurences.

**N-Gram Invalidation**  
After the stop words have been updated, a scan can be performed that iterates
over all tokens, and removes tokens of ngramSize > 1 that contain one of the
newly calculated stop words. This operation requires that text Transformation
sends ngrams in an easily parsable format. Invalid ngrams are removed from the
index and the tokencount for the related document is decremented.

#### Index Partition Operations
Index partitions require linear scans in order to delete tokens and documents
that have been invalidated. Indexes also need resizing and redistribution as the
size of the overall index grows.

**Cleanup**  
This operation will iterate over all tokens in the index and check if the token
belongs to a document that was marked for deletion. If so, the token is removed
from the index and the tokenCount for the given document is decremented. When the
tokenCount for a document reaches 0, it is removed from the index.

**Resizing**  
Details to come, design not completed.
