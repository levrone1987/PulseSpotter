from fastapi import FastAPI, Depends

from pulsespotter.api.data_models import DateRangeRequest, ArticleSearchRequest
from pulsespotter.db.dao import *
from pulsespotter.db.repositories.article_embeddings import ArticleEmbeddingsRepository
from pulsespotter.db.repositories.articles import ArticlesRepository
from pulsespotter.db.repositories.topic_assignments import TopicAssignmentsRepository
from pulsespotter.db.repositories.topic_embeddings import TopicEmbeddingsRepository

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
        article_assignment_data = article_assignment_data or {}
        response = {
            "url": response["url"],
            "title": response.get("title") or "",
            "description": response.get("description") or "",
            "paragraphs": response.get("paragraphs") or [],
            "site_name": response.get("site_name"),
            "article_date": response.get("parsed_date") or "",
            "topic_id": article_assignment_data.get("topic_id"),
            "topic_label": article_assignment_data.get("topic_label"),
            "topic_assignment_probability": article_assignment_data.get("assignment_probability"),
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
            "paragraphs": response.get("paragraphs") or [],
            "site_name": response["site_name"],
            "article_date": response.get("parsed_date") or "",
        }
    return response


@app.post("/api/articles/search")
async def search_articles(
        request: ArticleSearchRequest,
        repository: ArticlesRepository = Depends(get_articles_repository),
):
    results = repository.search_articles(
        phrase=request.phrase,
        site_name=request.site_name,
        start_date=request.start_date,
        end_date=request.end_date,
        limit=request.limit,
        projection=["title", "description", "paragraphs", "parsed_date", "url", "site_name", "_id"],
        sort=True,
    )
    response = []
    for res in results:
        response.append({
            "title": res.get("title") or "",
            "description": res.get("description") or "",
            "paragraphs": res.get("paragraphs") or [],
            "article_date": res.get("parsed_date") or "",
            "article_id": res["_id"],
            "site_name": res.get("site_name") or "",
            "url": res.get("url") or "",
        })
    return response


@app.get("/api/articles/search-similar/{article_id}")
async def get_similar_articles(
        article_id: str,
        articles_repository: ArticlesRepository = Depends(get_articles_repository),
        embeddings_repository: ArticleEmbeddingsRepository = Depends(get_article_embeddings_repository),
):
    search_response = embeddings_repository.search_similar(article_id=article_id, limit=10, min_similarity=0.5)
    response = []
    for record in search_response:
        target_article = articles_repository.get_article_by_id(record["article_id"])
        target_article["similarity"] = record["score"]
        response.append({
            "title": target_article.get("title") or "",
            "description": target_article.get("description") or "",
            "paragraphs": target_article.get("paragraphs") or [],
            "article_date": target_article.get("parsed_date") or "",
            "article_id": target_article["_id"],
            "site_name": target_article.get("site_name") or "",
            "url": target_article.get("url") or "",
            "score": record["score"],
        })
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


@app.get("/api/topics/search-similar/{topic_id}")
async def get_similar_topics(
        topic_id: str,
        embeddings_repository: TopicEmbeddingsRepository = Depends(get_topic_embeddings_repository),
):
    response = embeddings_repository.search_similar(topic_id=topic_id, limit=10, min_similarity=0.5)
    return response
