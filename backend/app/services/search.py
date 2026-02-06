"""Elasticsearch搜索服务"""
from typing import Dict, List, Optional, Any
from elasticsearch import Elasticsearch
from app.config import settings


class SearchService:
    """Elasticsearch搜索服务"""

    _client: Optional[Elasticsearch] = None

    @classmethod
    def get_client(cls) -> Elasticsearch:
        """获取ES客户端"""
        if cls._client is None:
            cls._client = Elasticsearch(
                hosts=[f"http://{settings.ES_HOST}:{settings.ES_PORT}"],
                request_timeout=settings.ES_TIMEOUT
            )
        return cls._client

    @classmethod
    def init_index(cls) -> None:
        """初始化索引"""
        client = cls.get_client()
        if not client.indices.exists(index=settings.ES_INDEX):
            mapping = {
                "mappings": {
                    "properties": {
                        "id": {"type": "integer"},
                        "isbn": {"type": "keyword"},
                        "title": {
                            "type": "text",
                            "analyzer": "ik_max_word",
                            "search_analyzer": "ik_smart",
                            "fields": {
                                "keyword": {"type": "keyword"}
                            }
                        },
                        "author": {
                            "type": "text",
                            "analyzer": "ik_max_word"
                        },
                        "publisher": {"type": "keyword"},
                        "category_id": {"type": "integer"},
                        "category_name": {"type": "keyword"},
                        "summary": {
                            "type": "text",
                            "analyzer": "ik_max_word"
                        },
                        "status": {"type": "keyword"},
                        "available_stock": {"type": "integer"},
                        "borrow_count": {"type": "integer"},
                        "created_at": {"type": "date"}
                    }
                },
                "settings": {
                    "number_of_shards": 1,
                    "number_of_replicas": 0,
                    "analysis": {
                        "analyzer": {
                            "ik_max_word": {
                                "type": "custom",
                                "tokenizer": "ik_max_word"
                            },
                            "ik_smart": {
                                "type": "custom",
                                "tokenizer": "ik_smart"
                            }
                        }
                    }
                }
            }
            client.indices.create(index=settings.ES_INDEX, body=mapping)

    @classmethod
    def index_book(cls, book) -> None:
        """索引图书"""
        client = cls.get_client()
        doc = {
            "id": book.id,
            "isbn": book.isbn,
            "title": book.title,
            "author": book.author,
            "publisher": book.publisher,
            "category_id": book.category_id,
            "category_name": book.category.name if book.category else None,
            "summary": book.summary,
            "status": book.status,
            "available_stock": book.available_stock,
            "borrow_count": book.borrow_count,
            "created_at": book.created_at.isoformat() if book.created_at else None,
        }
        client.index(index=settings.ES_INDEX, id=str(book.id), body=doc)

    @classmethod
    def delete_book(cls, book_id: int) -> None:
        """删除图书索引"""
        client = cls.get_client()
        try:
            client.delete(index=settings.ES_INDEX, id=str(book_id))
        except Exception:
            pass

    @classmethod
    def bulk_index_books(cls, books: List) -> None:
        """批量索引图书"""
        if not books:
            return

        client = cls.get_client()
        actions = []
        for book in books:
            doc = {
                "id": book.id,
                "isbn": book.isbn,
                "title": book.title,
                "author": book.author,
                "publisher": book.publisher,
                "category_id": book.category_id,
                "category_name": book.category.name if book.category else None,
                "summary": book.summary,
                "status": book.status,
                "available_stock": book.available_stock,
                "borrow_count": book.borrow_count,
                "created_at": book.created_at.isoformat() if book.created_at else None,
            }
            actions.append({"index": {"_index": settings.ES_INDEX, "_id": str(book.id)}})
            actions.append(doc)

        if actions:
            client.bulk(body=actions)

    @classmethod
    def search(
        cls,
        keyword: str,
        category_id: Optional[int] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """搜索图书"""
        client = cls.get_client()

        # 构建查询
        must = [
            {
                "multi_match": {
                    "query": keyword,
                    "fields": ["title^3", "author^2", "summary", "isbn"],
                    "type": "best_fields",
                    "fuzziness": "AUTO"
                }
            }
        ]

        if category_id:
            must.append({"term": {"category_id": category_id}})

        if status:
            must.append({"term": {"status": status}})

        query = {
            "query": {
                "bool": {
                    "must": must,
                    "filter": [{"term": {"is_active": True}}]
                }
            },
            "from": (page - 1) * page_size,
            "size": page_size,
            "sort": [
                {"_score": "desc"},
                {"borrow_count": "desc"},
                {"created_at": "desc"}
            ],
            "highlight": {
                "fields": {
                    "title": {},
                    "author": {},
                    "summary": {"fragment_size": 150}
                }
            }
        }

        result = client.search(index=settings.ES_INDEX, body=query)

        hits = []
        for hit in result["hits"]["hits"]:
            doc = hit["_source"]
            doc["_score"] = hit["_score"]
            if "highlight" in hit:
                doc["highlights"] = hit["highlight"]
            hits.append(doc)

        return {
            "hits": hits,
            "total": result["hits"]["total"]["value"]
        }

    @classmethod
    def suggest(cls, prefix: str, limit: int = 10) -> List[str]:
        """搜索建议"""
        client = cls.get_client()

        query = {
            "query": {
                "multi_match": {
                    "query": prefix,
                    "fields": ["title", "author"],
                    "type": "phrase_prefix"
                }
            },
            "size": limit,
            "_source": ["title"]
        }

        result = client.search(index=settings.ES_INDEX, body=query)
        return [hit["_source"]["title"] for hit in result["hits"]["hits"]]
