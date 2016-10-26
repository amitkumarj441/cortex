from elasticsearch import Elasticsearch
from django.conf import settings


class ArticleIndex(object):
    ES_HOST = settings.ES['host']
    ES_INDEX = settings.ES['index']
    ES_ARTICLE_TYPE = settings.ES['article_type']
    # fields and their boost values
    FIELDS = {
        "title": 6,
        "tags": 5,
        "summary": 4,
        "authors": 3,
        "text": 2
    }

    def __init__(self):
        self.es = Elasticsearch([self.ES_HOST])
        self.SIZE = 10
        self.OFFSET = 0
        self.PHRASE = None
        self.FILTERS = {}

    def index(self, body, id=''):
        if id:
            self.es.index(index=self.ES_INDEX,
                          doc_type=self.ES_ARTICLE_TYPE,
                          body=body,
                          id=id)
        else:
            self.es.index(index=self.ES_INDEX,
                          doc_type=self.ES_ARTICLE_TYPE,
                          body=body)

    def build_search_query(self):
        search_query = []

        for key, value in self.FIELDS.items():
            search_query.append({
                    "match": {
                        key: {
                            "query": self.PHRASE,
                            "boost": value
                        }
                    }
                })
        return search_query

    def build_filter_query(self):
        filter_query = []
        for key, value in self.FILTERS.items():
            filter_query.append({
                    "terms": {
                        key: [value.split(',')],
                    }
                })
        return filter_query

    def find(self):
        body = {
            "query": {
                "match_all": {}
            }
        }

        if self.PHRASE:
            body = {
                "query": {
                    "bool": {}
                }
            }
            search_query = self.build_search_query()
            body["query"]["bool"]["should"] = search_query

        if self.FILTERS:
            filter_query = self.build_filter_query()

            if "bool" in body["query"]:
                body["query"]["bool"]["filter"] = filter_query
            else:
                body = {
                    "query": {
                        "bool": {}
                    }
                }
                body["query"]["bool"]["filter"] = filter_query
        body['size'] = self.SIZE
        body['from'] = self.OFFSET
        return self.es.search(index=self.ES_INDEX,
                              doc_type=self.ES_ARTICLE_TYPE,
                              body=body)
