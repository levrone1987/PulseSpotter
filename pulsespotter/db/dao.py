from pulsespotter.db.repositories.article_embeddings import ArticleEmbeddingsRepository
from pulsespotter.db.repositories.articles import ArticlesRepository
from pulsespotter.db.repositories.articles_vectors import ArticlesVectorsRepository
from pulsespotter.db.repositories.topic_assignments import TopicAssignmentsRepository
from pulsespotter.db.repositories.topic_embeddings import TopicEmbeddingsRepository
from pulsespotter.db.repositories.topics_vectors import TopicsVectorsRepository

articles_repository = ArticlesRepository()
article_embeddings_repository = ArticleEmbeddingsRepository()
topic_assignments_repository = TopicAssignmentsRepository()
topic_embeddings_repository = TopicEmbeddingsRepository()
articles_vectors_repository = ArticlesVectorsRepository()
topics_vectors_repository = TopicsVectorsRepository()


def get_articles_repository():
    return articles_repository


def get_article_embeddings_repository():
    return article_embeddings_repository


def get_topic_assignments_repository():
    return topic_assignments_repository


def get_topic_embeddings_repository():
    return topic_embeddings_repository


def get_articles_vectors_repository():
    return articles_vectors_repository


def get_topics_vectors_repository():
    return topics_vectors_repository


__all__ = [
    "get_articles_repository",
    "get_article_embeddings_repository",
    "get_topic_assignments_repository",
    "get_topic_embeddings_repository",
    "get_articles_vectors_repository",
    "get_topics_vectors_repository",
]
