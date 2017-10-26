## Overview
Creating a search index for a large number of documents is not an easy task. It requires the acquisition, processing, storage, and retrieval of large amounts of
data. One of the main use cases for such an index is a web search engine. A search
engine capable of indexing the web can be divided into several large architectural
components that each perform one of the aforementioned subtasks.

|Component | Sub-task | Responsibilities |
|----------|----------|------------------|
|Crawling  | acquisition | Crawl the web & build a web graph |
|Link Analysis | processing | Apply Page Rank to documents in the web graph |
|Text Transformation | processing | Parse tokens from documents |
|Indexing | storage, retrieval | Store & retrieve data from reverse index |
|Ranking | processing | Sort documents retrieved from index |
|Querying | retrieval | Deconstruct queries & retrieve data from index |


This documentation is focused on the Indexing component, but it is important to
understand the system as a whole in order to understand the behavior the Index must
provide. The diagram below should help provide some clarity on how Indexing
interacts with the other components.


### Constraints
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


### Index Representation
This section will focus primarily on the structure of the index itself. This is
the place to look if you want to know what information the index stores. This
section also describes how the index is partitioned and persisted. The index is
broken up into two major parts, the reverse index containing the tokens, and a
document store containing document metadata.

#### Index Schema
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

#### Index Partitioning & Persistence
Since it is not possible to keep a large index in memory, the index must be
partitioned, persisted, and distributed in some manner. Since one of our constraints
is the lack of hosts, we will need to use a centralized data store rather than
keeping the partitions distributed across hosts in RAM.

One of the easiest, cheapest, and most scalable ways to accomplish this is to
serialize the partitions and to store them in S3. New index partitions can easily
be added, and partitions can be stored and retrieved in batches. This also enables a
host to iterate over the objects in a given S3 bucket, so a host could be instructed
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
down which indice partitions might contain a particular token thus providing
much more performant reads. The major downside to this solution is that we must
perform a read-before-write for each token so that we can ensure we're not
duplicating data across partitions.

#### Index Metadata
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
  pKey: string "startingCharacter|startingToken|endingToken",
  uri: string
}
```
The format of the partition key makes it possible to perform range queries that
retrieve all documents for partitions relevant to a given token. Concatenating
the tokens with the starting character in this format essentially provides sorting
first based on the starting character for tokens in a given partition, secondarily
by the token at the start of the range stored in that partition, and a tertiary
ordering based on the token at the end of the alphabetical range stored in the
partition.

#### Document Schema
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
  pKey: string "docID",
  internal: {
    lockNo: int,
    updating: bool,
    lastUpdate: datetime,
    tokenCount: int
  },
  external: {
    wordCount: int,
    pageCreation: datetime,
    pageLastIndexed: datetime,
    pageRank: float,
    inboundLinks: int,
    outboundLink: int,
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
#### Document Persistence
Documents will be persisted in an external database. DynamoDB is a fitting option
as it works well with other AWS Services, provides the range query functionality
we require, and functions as a scalable black box.

### Index Behavior
This section will focus on index behavior. This section describes how various
operations can be performed on the index as well as the consistency behavior
it will exhibit due to these operations. The three main operations that will be
performed on the index will be reads, writes, and deletes. Background processes
will also need to be run on the index to perform operations that would otherwise
block availability.

#### Read
Read is the core function of the index, and as such this needs to be a quick
operation. Fortunately, partitioning our index enables asynchronous parallel
searches to be run for sets of tokens. 
#### Write
#### Delete
#### Consistency
#### Background Scans
##### Documents
##### Index Partitions
**Cleanup**  
**Resizing**
