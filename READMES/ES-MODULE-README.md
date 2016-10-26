### Goal of this module:

A module that indexes a postgreSQL DB with Elastic-Search. It will also be responsible for searches against the ES documents.


### Input:
Search phrase: `/api/search?q=<search-phrase>` 

### Output: 
JSON response containing the most relevant articles in elastic search that match the search keywords.
Relevance is computed in the following order:
- Title
- Keywords
- tags
- NLP (Automatic Analysis done by Newspaper3k)
- Summary (Summary delivered by the page itself)
- authors
- text

### Technical Implementation:
#### Step 1: Initial index of postgreSQL DB in ES
A django `python manage.py index` command will be implemented for indexing the DB


#### Step 2: Index new and updated records
A `post_save` signal and receiver  will be set on the Articles Model. These will handle indexing of new and updated records

#### Step 3: Expose an /api/search/ end-point in the django app that makes use of ES MODULE
A search api will be exposed on `/api/search?q=<search-phrase>` 
If `q` is not supplied, a `match_all` query will be used

#### Step 4: Implement pagination and filtering
The api will accept parameters `size` and `from` which denote the `number of results returned` and `offset` respectively.

Any other parameter sent will be treated as a filter.

The api will also accept comma-separated strings as filter values.  Documents that match any of the supplied values 
will be returned

A sample request is `/api/search?q=Brain&size=10&from=0&is_trusted_source=true&domain=abc.com,xyz.com`
