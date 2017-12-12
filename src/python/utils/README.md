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
