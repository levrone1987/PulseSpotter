from fastapi import FastAPI, Depends

from pulsespotter.api.data_models import DateRangeRequest, ArticleSearchRequest
from pulsespotter.api.utils.inference import load_model, delete_model, get_topics_data, \
    predict_trending_topic_score
from pulsespotter.config import MODEL_FILENAME
from pulsespotter.db.dao import *
from pulsespotter.db.repositories.article_embeddings import ArticleEmbeddingsRepository
from pulsespotter.db.repositories.articles import ArticlesRepository
from pulsespotter.db.repositories.topic_assignments import TopicAssignmentsRepository
from pulsespotter.db.repositories.topic_embeddings import TopicEmbeddingsRepository
from pulsespotter.db.repositories.topics_vectors import TopicsVectorsRepository

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    load_model(MODEL_FILENAME)


@app.on_event("shutdown")
async def shutdown_event():
    delete_model()


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


@app.post("/api/topics/predict-topic-trends")
async def predict_topic_trends(
        request: DateRangeRequest,
        topic_assignments_repository: TopicAssignmentsRepository = Depends(get_topic_assignments_repository),
        topic_embeddings_repository: TopicEmbeddingsRepository = Depends(get_topic_embeddings_repository),
        topic_vectors_repository: TopicsVectorsRepository = Depends(get_topics_vectors_repository),
):
    topics_data = get_topics_data(
        topic_start_date=request.start_date,
        topic_end_date=request.end_date,
        topic_assignments_repository=topic_assignments_repository,
        topic_embeddings_repository=topic_embeddings_repository,
        topic_vectors_repository=topic_vectors_repository,
    )
    if topics_data is None:
        return {}
    topics_data["num_articles"] = topics_data["counts"].apply(sum)
    topics_data["probability"] = topics_data.apply(
        lambda x: predict_trending_topic_score(x["counts"], x["topic_embedding"]),
        axis=1,
    )
    topics_data = topics_data.loc[topics_data["probability"] >= 0.5]
    topics_data = topics_data.sort_values(by="probability", ascending=False, ignore_index=True)
    response = topics_data[["topic_id", "topic_label", "num_articles", "probability"]].to_dict("records")
    return response
