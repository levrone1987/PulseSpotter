import numpy as np

from fastapi import FastAPI, Depends

from pulsespotter.api.data_models import DateRangeRequest, ArticleSearchRequest, SimilaritySearchRequest
from pulsespotter.api.dependencies import (
    get_articles_repository, get_topic_assignments_repository, get_article_embeddings_repository
)
from pulsespotter.db.repositories.article_embeddings import ArticleEmbeddingsRepository
from pulsespotter.db.repositories.articles import ArticlesRepository
from pulsespotter.db.repositories.topic_assignments import TopicAssignmentsRepository

app = FastAPI()


@app.get("/api/articles/info/{article_id}")
async def get_article_info(
        article_id: str,
        repository: ArticlesRepository = Depends(get_articles_repository),
        topics_repository: TopicAssignmentsRepository = Depends(get_topic_assignments_repository),
):
    response = repository.get_article_by_id(article_id)
    if response:
        article_assignment_data = topics_repository.get_article_assignment(response["_id"])
        response = {
            "url": response["url"],
            "title": response.get("title") or "",
            "description": response.get("description") or "",
            "paragraphs": response.get("paragraphs") or [],
            "site_name": response["site_name"],
            "article_date": response.get("parsed_date") or "",
            "topic_id": article_assignment_data["topic_id"],
            "topic_label": article_assignment_data["topic_label"],
            "topic_assignment_probability": article_assignment_data["assignment_probability"],
        }
    return response


@app.get("/api/articles/summary/{article_id}")
async def get_article_summary(
        article_id: str,
        repository: ArticlesRepository = Depends(get_articles_repository),
):
    response = repository.get_article_by_id(article_id)
    if response:
        response = {
            "url": response["url"],
            "title": response.get("title") or "",
            "description": response.get("description") or "",
            "paragraphs": response.get("paragraphs") or "",
            "site_name": response["site_name"],
            "article_date": response.get("parsed_date") or "",
        }
    return response


@app.post("/api/articles/search")
async def search_articles(
        request: ArticleSearchRequest,
        repository: ArticlesRepository = Depends(get_articles_repository),
):
    return repository.search_articles(
        phrase=request.phrase,
        site_name=request.site_name,
        start_date=request.start_date,
        end_date=request.end_date,
        limit=request.limit,
        sort=True,
    )


@app.post("/api/articles/search-similar")
async def get_similar_articles(
        request: SimilaritySearchRequest,
        articles_repository: ArticlesRepository = Depends(get_articles_repository),
        embeddings_repository: ArticleEmbeddingsRepository = Depends(get_article_embeddings_repository),
):
    # get article id and embedding
    article = articles_repository.get_article_by_id(request.article_id)
    if not article:
        return {}
    article_embedding = np.array(embeddings_repository.get_by_article_id(article["_id"]))

    # get target articles and their embeddings
    target_articles = articles_repository.search_articles(
        start_date=request.start_date,
        end_date=request.end_date,
        projection=["_id"],
    )
    target_articles = [article["_id"] for article in target_articles]
    # get most similar articles
    similarity_scores = embeddings_repository.similarity_search(
        article_embedding,
        target_articles,
        request.min_similarity,
        request.limit,
    )
    # format response and return
    response = []
    for target_article_id, similarity in similarity_scores:
        target_article = articles_repository.get_article_by_id(target_article_id)
        target_article["similarity"] = similarity
        response.append(target_article)
    return response


@app.post("/api/topics/trending")
async def get_trending_topics(
        request: DateRangeRequest,
        repository: TopicAssignmentsRepository = Depends(get_topic_assignments_repository),
):
    return repository.get_trending_topics(request.start_date, request.end_date)


@app.get("/api/topics/{topic_id}")
async def get_topic_info(
        topic_id: str,
        topics_repository: TopicAssignmentsRepository = Depends(get_topic_assignments_repository),
):
    topic_assignments = topics_repository.get_topic_assignments(topic_id)
    return topic_assignments
