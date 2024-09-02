import argparse
from datetime import timedelta
from typing import List

import numpy as np
import pandas as pd
from bertopic import BERTopic
from bertopic.vectorizers import ClassTfidfTransformer
from bson import ObjectId
from hdbscan import HDBSCAN
from sklearn.feature_extraction.text import CountVectorizer
from qdrant_client.http.models import Distance
from tqdm import tqdm
from umap import UMAP

from pulsespotter.config import *
from pulsespotter.db.dao import *
from pulsespotter.ingestion.utils.parse_functions import parse_date
from pulsespotter.utils.logging_utils import get_logger


def get_weeks_in_range(start_date: str, end_date: str):
    mondays = pd.date_range(start_date, end_date, freq="W-MON")
    response = []
    for monday, next_monday in zip(mondays, mondays[1:]):
        sunday = next_monday - timedelta(days=1)
        response.append((monday.strftime("%Y-%m-%d"), sunday.strftime("%Y-%m-%d")))
    return response


def get_articles_and_embeddings(start_date: str, end_date: str):
    # get articles data
    articles_repository = get_articles_repository()
    articles = articles_repository.query(
        q={"parsed_date": {"$gte": start_date, "$lte": end_date}},
        projection=["_id", "url", "parsed_date", "title", "description", "paragraphs"],
    )
    # get vector ids for articles
    articles_vectors_repository = get_articles_vectors_repository()
    article_ids = [article["_id"] for article in articles]
    articles_vectors_response = articles_vectors_repository.batch_get(article_ids)
    vector_ids = [x["vector_id"] for x in articles_vectors_response]
    # retrieve embeddings of each article
    article_embeddings_repository = get_article_embeddings_repository()
    article_embeddings = article_embeddings_repository.get_embeddings(vector_ids)
    # prepare response as two separate lists:
    # one containing the articles data and the other containing the article embeddings
    article_ids_to_idx = {article["_id"]: idx for idx, article in enumerate(articles)}
    embeddings = [x["embedding"] for x in article_embeddings]
    article_ids = [x["article_id"] for x in article_embeddings]
    articles = [articles[article_ids_to_idx[article_id]] for article_id in article_ids]
    return articles, embeddings


def extract_article_content(article: dict):
    """
    Transforms articles content data (documents) by merging the title, description and paragraphs.
    """
    title = (article.get("title") or "").strip()
    description = (article.get("description") or "").strip()
    paragraphs = article.get("paragraphs")
    if isinstance(paragraphs, list):
        paragraphs = (" ".join(p.strip() for p in paragraphs if len(p.strip()) > 0)).strip()
        if description is not None and paragraphs.startswith(description):
            description = ""
    article_items = [title or "", description or "", paragraphs or ""]
    return "\n".join([item for item in article_items if len(item) > 0])


def build_topic_model() -> BERTopic:
    # components of the BERTopic algorithm
    umap_model = UMAP(n_neighbors=3, n_components=3, min_dist=0.0, metric="cosine")
    hdbscan_model = HDBSCAN(min_cluster_size=3, min_samples=1)
    ctfidf_model = ClassTfidfTransformer(bm25_weighting=True, reduce_frequent_words=True)
    vectorizer_model = CountVectorizer(min_df=1, ngram_range=(1, 3))
    return BERTopic(
        umap_model=umap_model,
        hdbscan_model=hdbscan_model,
        ctfidf_model=ctfidf_model,
        vectorizer_model=vectorizer_model,
    )


def batch_add_embeddings(topic_ids: List[str], embeddings: List):
    topic_embeddings_repository = get_topic_embeddings_repository()
    topics_vectors_repository = get_topics_vectors_repository()
    # upsert embeddings into the vector db
    upsert_response = topic_embeddings_repository.batch_add_embeddings(topic_ids=topic_ids, embeddings=embeddings)
    # retrieve the generated vector ids
    vector_ids = [x[0] for x in upsert_response]
    # add mapping from articles to vector ids into the appropriate collection
    return topics_vectors_repository.batch_add(topic_ids, vector_ids)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Content ingestion script.")
    parser.add_argument(
        "--start-date", type=parse_date, required=True,
        help="Start date in the format YYYY-MM-DD."
    )
    parser.add_argument(
        "--end-date", type=parse_date, required=True,
        help="End date in the format YYYY-MM-DD."
    )
    args = parser.parse_args()

    logger = get_logger(__name__)
    logger.info("Environment vars:")
    logger.info(f"{PROJECT_DIR=}")
    logger.info(f"{MONGO_HOST=}")
    logger.info(f"{MONGO_DATABASE=}")
    logger.info(f"{OPENAI_API_KEY=}")
    logger.info(f"{QDRANT_HOST=}")
    logger.info(f"{QDRANT_API_KEY=}")
    logger.info(50 * "-")

    logger.info("Initialising script with following parameters:")
    logger.info(f"Start Date: {args.start_date}")
    logger.info(f"End Date: {args.end_date}")
    logger.info(50 * "-")

    # preparing connections to databases
    topic_embeddings_repository = get_topic_embeddings_repository()
    if not topic_embeddings_repository.collection_exists():
        topic_embeddings_repository.recreate_collection(vector_size=384, distance=Distance.COSINE)
    topic_assignments_repository = get_topic_assignments_repository()

    # main loop
    pbar = tqdm(get_weeks_in_range(args.start_date, args.end_date), desc="Calculating topics")
    logger.info("Process started ...")
    for monday, sunday in pbar:
        if topic_assignments_repository.check_topics_exist(monday, sunday):
            logger.info(f"Skipping topics creation for {monday} - {sunday}. Reason: Topic assignments already exist.")
            continue
        # extract and preprocess
        articles, embeddings = get_articles_and_embeddings(monday, sunday)
        contents = [extract_article_content(article) for article in articles]
        # calculate topics
        topic_model = build_topic_model()
        topics_assignment, assignment_probs = topic_model.fit_transform(
            documents=contents, embeddings=np.array(embeddings),
        )
        # ingest topic assignments
        generated_topic_ids = topic_assignments_repository.batch_add_topic_assignments(
            article_ids=[ObjectId(article["_id"]) for article in articles],
            article_dates=[article["parsed_date"] for article in articles],
            topic_labels=topic_model.topic_labels_,
            topic_assignments=topics_assignment,
            assignment_probabilities=list(assignment_probs.astype(float)),
            topic_start_date=monday,
            topic_end_date=sunday,
        )
        # upsert topic embeddings into the vector db and add mapping from topic id to vector id
        topic_ids, topic_embeddings = [], []
        for topic_index in topic_model.topic_labels_:
            topic_ids.append(str(generated_topic_ids[topic_index]))
            topic_embeddings.append(topic_model.topic_embeddings_[topic_index].astype(float).tolist())
        batch_add_embeddings(topic_ids=topic_ids, embeddings=topic_embeddings)
    logger.info("Process finished successfully!")
