from pulsespotter.db.repositories.article_embeddings import ArticleEmbeddingsRepository
from pulsespotter.db.repositories.articles import ArticlesRepository
from pulsespotter.db.repositories.topic_assignments import TopicAssignmentsRepository
from pulsespotter.db.repositories.topic_embeddings import TopicEmbeddingsRepository

articles_repository = ArticlesRepository()
article_embeddings_repository = ArticleEmbeddingsRepository()
topic_assignments_repository = TopicAssignmentsRepository()
topic_embeddings_repository = TopicEmbeddingsRepository()


def get_articles_repository():
    return articles_repository


def get_article_embeddings_repository():
    return article_embeddings_repository


def get_topic_assignments_repository():
    return topic_assignments_repository


def get_topic_embeddings_repository():
    return topic_embeddings_repository
