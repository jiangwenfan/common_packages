import logging

from article.models import ArticleInfoModel, ArticleModel
from article.serializers import ArticleSerializer
from django.conf import settings
from elastic_transport import ObjectApiResponse
from elasticsearch import Elasticsearch


class ElasticsearchHandle:
    def __init__(self) -> None:
        print("---\n--:", settings.ELASTICSEARCH_HOSTS)
        self.elasticsearch = Elasticsearch(settings.ELASTICSEARCH_HOSTS)
        self.index = "blog"

    def init_data(self):
        # init mysql to es when project is running.

        # create index
        index_response: ObjectApiResponse = self.elasticsearch.indices.create(
            index=self.index
        )
        if index_response.meta.status != 200:
            raise ValueError("index create failed!")
        index_response_body: dict = index_response.body
        if "acknowledged" not in index_response_body:
            raise ValueError("index create failed!2")
        if index_response_body["acknowledged"] == False:
            logging.error("failed")

        # read all doc
        all_article = ArticleModel.objects.filter(is_delete=False)
        all2 = ArticleSerializer(all_article, many=True).data[:]
        logging.info(f"--- {all2} {type(all2)} {type(list(all2))} --")

        # create document in index
        for record in list(all2):
            self.elasticsearch.create(
                index=self.index, id=record["id"], document=record
            )

    def update_data(self, doc_id, content):
        # update doc content
        self.elasticsearch.update(index=self.index, id=doc_id, body=content)

    def create_data(self, doc_id, content):
        self.elasticsearch.create(index=self.index, id=doc_id, document=content)

    def delete_doc(self, doc_id):
        self.elasticsearch.delete(index=self.index, id=doc_id)

    def search_doc(self, key):
        s = {
            "query": {"match": {"content": key}},
            "highlight": {"fields": {"content": {}}},
        }
        self.elasticsearch.search(index=self.index, body=s)

    def show_info(self):
        """show blog index info"""
        res: ObjectApiResponse = self.elasticsearch.search(index=self.index)
        s: dict = res.body
        return s
