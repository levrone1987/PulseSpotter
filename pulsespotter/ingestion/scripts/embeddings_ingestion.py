import argparse
import re
from typing import List

import nltk
import torch
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from qdrant_client.http.models import Distance
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

from pulsespotter.config import *
from pulsespotter.db.dao import get_article_embeddings_repository
from pulsespotter.db.dao import get_articles_repository
from pulsespotter.db.dao import get_articles_vectors_repository
from pulsespotter.ingestion.utils.common import generate_batches, join_strings
from pulsespotter.ingestion.utils.parse_functions import parse_date
from pulsespotter.utils.logging_utils import get_logger


def load_nltk_files():
    nltk.download('punkt')
    nltk.download('punkt_tab')
    nltk.download('stopwords')
    nltk.download('wordnet')


def load_model():
    model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", device="cpu")
    model.eval()
    return model


def get_articles(start_date: str = None, end_date: str = None):
    date_filters = {"$exists": True, "$ne": None}
    if start_date:
        date_filters["$gte"] = start_date
    if end_date:
        date_filters["$lte"] = end_date
    q = {
        "$and": [
            {
                "visited": True,
                "parsed_date": date_filters,
                "site_name": {"$exists": True, "$nin": ["faz"]},
            },
            {
                "$or": [
                    {"title": {"$exists": True, "$not": {"$in": ["", None]}}},
                    {"description": {"$exists": True, "$not": {"$in": ["", None]}}},
                    {"paragraphs": {"$exists": True, "$not": {"$in": ["", None]}}},
                ]
            }
        ]
    }
    articles_repository = get_articles_repository()
    response = articles_repository.query(q=q)
    return response


def get_articles_without_embeddings(article_ids: list):
    # get vector ids for passed article ids
    articles_vectors_repository = get_articles_vectors_repository()
    vector_ids = []
    for article_id in article_ids:
        article_vector_response = articles_vectors_repository.get(article_id)
        vector_ids.append((article_vector_response or {}).get("vector_id"))
    # return article ids for which the retrieved vector id is None
    response = []
    for i in range(len(vector_ids)):
        if vector_ids[i] is None:
            response.append(article_ids[i])
    return response


def preprocess_document(text):
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    words = word_tokenize(text, language='german')
    words = [word for word in words if word not in stop_words]
    return ' '.join(words)


def create_document_for_record(record):
    title = join_strings(record.get("title") or []) or None
    description = join_strings(record.get("description") or []) or None
    paragraphs = join_strings(record.get("paragraphs") or []) or None
    document = " ".join([x.strip() for x in [title, description, paragraphs] if x is not None])
    return preprocess_document(document)


@torch.no_grad()
def batch_embed_documents(documents: list, model):
    return model.encode(documents).tolist()


def batch_add_embeddings(article_ids: List[str], embeddings: List):
    article_embeddings_repository = get_article_embeddings_repository()
    articles_vectors_repository = get_articles_vectors_repository()
    # upsert embeddings into the vector db
    upsert_response = article_embeddings_repository.batch_add_embeddings(article_ids=article_ids, embeddings=embeddings)
    # retrieve the generated vector ids
    vector_ids = [x[0] for x in upsert_response]
    # add mapping from articles to vector ids into the appropriate collection
    return articles_vectors_repository.batch_add(article_ids, vector_ids)


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
    parser.add_argument(
        "--batch-size", type=int, default=16,
        help="Number of articles to process as part of a single batch."
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
    logger.info(f"Batch Size: {args.batch_size}")
    logger.info(50 * "-")

    # creating vector db collection if not exists
    article_embeddings_repository = get_article_embeddings_repository()
    if not article_embeddings_repository.collection_exists():
        article_embeddings_repository.recreate_collection(vector_size=384, distance=Distance.COSINE)

    logger.info("Loading utility files for document preprocessing ...")
    load_nltk_files()
    stop_words = set(stopwords.words("german"))

    logger.info("Initialising embedding model ...")
    model = load_model()

    logger.info("Retrieving articles ...")
    articles = list(get_articles(start_date=args.start_date, end_date=args.end_date))
    num_articles = len(articles)
    num_steps = num_articles // args.batch_size + int(num_articles % args.batch_size > 0)
    pbar = tqdm(total=num_steps)

    logger.info("Process started ...")
    for batch in generate_batches(articles, args.batch_size):
        batch_article_ids = [doc["_id"] for doc in batch]
        article_ids_without_embeddings = get_articles_without_embeddings(batch_article_ids)
        if len(article_ids_without_embeddings) != 0:
            effective_batch = [doc for doc in batch if doc["_id"] in set(article_ids_without_embeddings)]
            documents = [create_document_for_record(record) for record in effective_batch]
            embeddings = batch_embed_documents(documents, model)
            batch_add_embeddings(article_ids=article_ids_without_embeddings, embeddings=embeddings)
        pbar.update()
    logger.info("Process finished successfully!")
