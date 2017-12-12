## Overview

This directory contains the models and classes used to facilitate various index operations.
These models are intended to be easily deployed to AWS and used in the Write, Search, and Stop Word services.

### Config

Contains a variety of configurable constants

### Document Controller

This class implements the data access for the DOCUMENTS table. 
It isresponsible for all operations with the table including 
creating documents,reading documents, and modifying the state of documents. 
Example usage of document locking can be seen in the Write Master Node. 
It allows for the following functions to be called:

* get_document(self, doc_id)
  * Retrieves the document if present. 
  * Returns None if not present or if a failure occurred
* lock_document(self, doc_id)
  * Sets updating field and lastUpdate timestamp of document.
  * Raises exception on failure
* unlock_document(self, doc_id)
  * Sets updating field to false for a given document.
  * Raises exception on failure
* create_new_document(self, document_model)
  * Create a new index document if the provided DocumentModel is valid.
  * Raises exception on failure

### Document Model

This class implements the data model required for storing information
to the DOCUMENTS table. It works in unison with the DocumentControl
class to create an easy to use interface that is decoupled from the actual
storage implementation used for documents. 
Documents store information related to internal use and information used by 
other components of the search engine. The external related fields are:

* Word Count
  * Count of all single words within document
* Last Indexed
  * Last time this document was indexed
* Token Ranges
  * Important token ranges such as title or author
  * Has a name, a start, and an end
  
The fields related to internal index usage are:
 
* Lock Number
  * Used for locking documents when being written to
* Updating
  * Whether or not the document is currently being updated
* Delete
  * Whether or not this document should be deleted from the database
* Last Update
  * Time the Document was last updated
* Token Count
  * Number of tokens (includes N-Grams) in the document
  
The DocumentModel also has a pKey, a key unique to a specific document. 
The most important functionality to note are as follows:

* get_payload
  * Returns the internal and external info for the document
* load_from_write_input(self, write_input)
  * Assigns all internal and external info based upon given input
* verify(self)
  * verifies that the provided information is valid
 
There are also setters provided for the various fields.

### Index Controller

This class is responsible for interactions with the
INDEX_PARTITION_METADATA table. It creates and updates metadata for
partitions and also determines which partitions contain specified tokens.
It allows for the following functions to be called:

* create_new_index(self, index_model)
  * Create a new index if the provided model is valid
* get_partition_ids(self)
  * Scans the partition table for all S3 Keys
* get_partition_for_token(self, token)
  * Gets pKeys for paritions the provided token might be in
  * Currently scans the entire index partition table
  * Raises Exception on failure
* update_metadata(self, index_model, is_new)
  * Updates the table entry for a given IndexModel
  * Raises exception on failure
* get_version_info(self, partition_id)
  * Retrieves version info for a particular partition
  * Raises exception on failure
  
### Index Model

This class implements the data model required for storing information
to the INDEX_METADATA table. It works in unison with the IndexControl
class to create an easy to use interface that is decoupled from the actual
storage implementation used for index metadata.
Contains the following attributes:

* PKey
  * Key identifying the particular partition in the metadata table this IndexModel is associated with
* Storage Key
  * Key identifying which Partition in S3 this IndexModel is associated with
* Start Token
  * First token in index alphabetically
* End token
  * Last token in index alphabetically
* Size
  * Number of tokens in partition
* Version
  * Version Number of this partition
  
These attributes can be asssigned using the provided with_ builder functions.
Getters for these attributes have also been provided

### Index Partition
This class wraps the _IndexPartition class to provide serialization. 
It stores and loads an _IndexPartition object internally. 
Its various functions tend to simply call the internal object's functions. 

* size(self)
  * Return the number of tokens stored in this partition
* starting_token(self)
  * Returns the first token in the partition alphabetically
* ending_token(self)
  * Returns the last token in the partition alphabetically
* add_token(self, token, doc_id, lock_no, ngram_size, locations)
  * Adds token to index if not present
  * Replaces oldest version if present
* serialize(self, out_file)
  * Use pickle to serialize the partition data to out_file
* deserialize(self, in_file)
  * Use pickle to deserialize the serialized data received
  * Stores deserialized data within object
* get_token_list(self)
  * Returns a list of all tokens within the partition
* get_token_count(self, key)
  * Returns the total count of all tokens within all documents
  
### Index Storage

This class is responsible for interacting with the index partition storage
solution (in this case S3). It retrieves, stores, and creates partitions. 
Provides the following functionality

* get_partition(self, partition_uri)
  * Provided a partition key, retrieve that partition from storage
  * Raises exception on failure
* write_partition(self, partition_uri, partition)
  * Provided a partition key and an IndexPartition, write that IndexPartition's data to storage
  * Raises exception on failure
* delete_partition(self, patition_uri)
  * Deletes the partition in storage given that partition's key
  
### Write Input Model

This class implements the data model & functions for parsing an
input request into an input object for the write service. This
class initializes and retrieves input information from the request.
