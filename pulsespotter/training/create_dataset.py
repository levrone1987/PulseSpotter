import argparse
from datetime import timedelta
from itertools import product

import numpy as np
import pandas as pd
from tqdm import tqdm

from pulsespotter.config import PROJECT_DIR, MONGO_HOST, MONGO_DATABASE, QDRANT_API_KEY, QDRANT_HOST, RESOURCES_DIR
from pulsespotter.db.dao import get_topic_assignments_repository
from pulsespotter.db.dao import get_topic_embeddings_repository
from pulsespotter.db.dao import get_topics_vectors_repository
from pulsespotter.utils.logging_utils import get_logger


def get_weeks_in_range(start_date: str, end_date: str):
    mondays = pd.date_range(start_date, end_date, freq="W-MON")
    response = []
    for monday, next_monday in zip(mondays, mondays[1:]):
        sunday = next_monday - timedelta(days=1)
        response.append((monday.strftime("%Y-%m-%d"), sunday.strftime("%Y-%m-%d")))
    return response


def retrieve_topics_data(topic_start_date: str, topic_end_date: str):
    topic_assignments_repository = get_topic_assignments_repository()
    topic_embeddings_repository = get_topic_embeddings_repository()
    topic_vectors_repository = get_topics_vectors_repository()

    topic_assignments = {}
    topic_embeddings = {}
    for sd, ed in tqdm(get_weeks_in_range(topic_start_date, topic_end_date), desc="Retrieving topics data"):
        # get topic assignments
        ta = topic_assignments_repository.search_topic_assignments(
            topic_start_date=sd, topic_end_date=ed, skip_noise_topics=True,
        )
        ta = pd.DataFrame(ta)
        ta["topic_id"] = ta["topic_id"].apply(str)
        topic_assignments[(sd, ed)] = ta
        # get topic ids to vector ids
        topics_vector_ids = topic_vectors_repository.batch_get(ta["topic_id"].unique().tolist())
        vector_ids = [record["vector_id"] for record in topics_vector_ids]
        # retrieve topic embedding by querying the vector db using vector ids
        vectors_response = topic_embeddings_repository.get_embeddings(vector_ids)
        for record in vectors_response:
            topic_id = record["topic_id"]
            topic_embedding = record["embedding"]
            topic_embeddings[topic_id] = topic_embedding

    return topic_assignments, topic_embeddings


def pairwise_cosine_similarity(array1, array2, normalize: bool = False):
    """
    Calculate pairwise cosine similarity between rows of two 2D numpy arrays.

    :param array1: A 2D numpy array where each row is a vector.
    :param array2: A 2D numpy array where each row is a vector.
    :param normalize: A boolean flag to control whether input arrays will be normalized before any calculations.
    :return: A 2D numpy array containing the cosine similarity scores.
    """

    if normalize:
        # Normalize the vectors in each array
        norms1 = np.linalg.norm(array1, axis=1, keepdims=True)
        norms2 = np.linalg.norm(array2, axis=1, keepdims=True)

        # Handle cases where norm is zero to avoid division by zero
        norms1[norms1 == 0] = 1
        norms2[norms2 == 0] = 1

        normalized_array1 = array1 / norms1
        normalized_array2 = array2 / norms2

        # Compute the pairwise cosine similarity
        similarity_matrix = np.dot(normalized_array1, normalized_array2.T)
    else:
        similarity_matrix = np.dot(array1, array2.T)

    return similarity_matrix


def match_topics(
    sim_matrix,
    src_topics: list,
    dst_topics: list,
    topk: int = 5,
    min_similarity: float = 0.9,
    return_scores: bool = False,
):
    """
    Matches src_topics to dst_topics.
    min_similarity - minimum cosine similarity for a topic pair to be considered similar
    topk - maximum number of dst topics to be matched to each src topic
    """
    result = {}
    for idx, topic_id in enumerate(src_topics):
        similarities = sorted(zip(dst_topics, sim_matrix[idx]), key=lambda x: x[-1], reverse=True)
        similarities = list(filter(lambda x: x[-1] >= min_similarity, similarities))
        similarities = similarities[:topk]
        if return_scores:
            result[topic_id] = similarities[:]
        else:
            result[topic_id] = [x[0] for x in similarities]
    return result


def get_topic_counts(topic_assignments):
    """
    Calculates the total number of articles of each topic inside `topic_assignments`.
    """
    result = topic_assignments.groupby(by="topic_id")["document_id"].nunique()
    result = result.reset_index()
    result = result.rename(columns={"document_id": "count"})
    result = result.set_index("topic_id")["count"].to_dict()
    return result


def get_trending_topics(topic_assignments, top_pct: float = 0.05):
    topic_counts = get_topic_counts(topic_assignments)
    topic_counts = pd.Series(topic_counts)
    threshold = topic_counts.quantile(1 - top_pct)
    trending_topics = topic_counts[topic_counts >= threshold]
    return trending_topics.index.tolist()


def find_matches_to_trending_topics(prev_week_date_range, next_week_date_range, topk: int = 5, min_similarity: float = 0.9):
    """
    Matches trending topics from next_topics_date_range to topics from prev_week_date_range by:
    1. Calculating the similarity matrix between start_topics and next_topics
    2. Matching start_topics to next_topics using similarity scores
    3. Applying the min_similarity threshold
    4. Yielding at most topk matches per start topic
    """

    dst_topics = topic_assignments[prev_week_date_range]["topic_id"].unique().tolist()
    src_topics = get_trending_topics(topic_assignments[next_week_date_range], top_pct=0.2)

    dst_topics_embeddings = np.array([topic_embeddings[topic_id] for topic_id in dst_topics])
    src_topics_embeddings = np.array([topic_embeddings[topic_id] for topic_id in src_topics])

    similarity_matrix = pairwise_cosine_similarity(src_topics_embeddings, dst_topics_embeddings)
    topics_matching = match_topics(similarity_matrix, src_topics, dst_topics, topk, min_similarity)

    topics_matched_trending = []
    for matched_topics in topics_matching.values():
        topics_matched_trending.extend(matched_topics)
    return list(set(topics_matched_trending))


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Content ingestion script.")
    parser.add_argument(
        "--start-date", type=str, required=True,
        help="Start date in the format YYYY-MM-DD."
    )
    parser.add_argument(
        "--end-date", type=str, required=True,
        help="End date in the format YYYY-MM-DD."
    )
    parser.add_argument(
        "--matching-topk", type=int, default=10,
        help="Maximum number of topics from week T that will be matched to trending topics of week T+1."
    )
    parser.add_argument(
        "--matching-min-similarity", type=float, default=0.85,
        help="Minimum similarity threshold when performing topic matching."
    )
    parser.add_argument(
        "--output-filename", type=str, default="trending_topics_dataset.json",
        help=f"Name of the output dataset file. The file will be located in `{RESOURCES_DIR}`."
    )
    args = parser.parse_args()

    logger = get_logger(__name__)
    logger.info("Environment vars:")
    logger.info(f"{PROJECT_DIR=}")
    logger.info(f"{MONGO_HOST=}")
    logger.info(f"{MONGO_DATABASE=}")
    logger.info(f"{QDRANT_HOST=}")
    logger.info(f"{QDRANT_API_KEY=}")
    logger.info(50 * "-")

    logger.info("Initialising script with following parameters:")
    logger.info(f"Start Date: {args.start_date}")
    logger.info(f"End Date: {args.end_date}")
    logger.info(f"Matching minimum similarity: {args.matching_min_similarity}")
    logger.info(f"Matching topk: {args.matching_topk}")
    logger.info(f"Output filename: {args.output_filename}")
    logger.info(50 * "-")

    # retrieve topics data per week
    topic_assignments, topic_embeddings = retrieve_topics_data(args.start_date, args.end_date)
    logger.info(f"{len(topic_assignments)=}")
    logger.info(f"{len(topic_embeddings)=}")

    # get all matches of previous week's topics to next week's trending topics
    topics_matched_trending = []
    date_ranges = sorted(list(topic_assignments))
    for prev_week_date_range, next_week_date_range in zip(date_ranges, date_ranges[1:]):
        topics_matched_trending.extend(find_matches_to_trending_topics(
            prev_week_date_range,
            next_week_date_range,
            topk=args.matching_topk,
            min_similarity=args.matching_min_similarity,
        ))
    logger.info(f"{len(topics_matched_trending)=}")

    # cross join topics to all dates in their date range (required to fill in NAs in topics daily counts)
    dates_per_week = {}
    for date_range in date_ranges:
        dates_per_week[date_range] = pd.date_range(date_range[0], date_range[-1]).strftime("%Y-%m-%d").tolist()

    topics_per_week = {}
    for date_range, ta in topic_assignments.items():
        topics_per_week[date_range] = ta["topic_id"].unique().tolist()

    topics_dates_index = []
    for date_range in date_ranges:
        dates_in_week = dates_per_week[date_range]
        topics_in_week = topics_per_week[date_range]
        topics_dates_index.extend(list(product(topics_in_week, dates_in_week)))

    topics_dates_index = pd.DataFrame(topics_dates_index, columns=["topic_id", "date"])
    logger.info(f"{topics_dates_index.shape=}")

    # get daily counts per topic
    topic_assignments_df = pd.concat(list(topic_assignments.values()))
    topics_daily_counts = topic_assignments_df.groupby(by=["topic_id", "document_date"])["document_id"].nunique()
    topics_daily_counts = topics_daily_counts.reset_index()
    topics_daily_counts = topics_daily_counts.rename(columns={"document_id": "count", "document_date": "date"})

    # join with topics_daily_counts to fill in NAs
    topics_daily_counts = pd.merge(
        topics_dates_index,
        topics_daily_counts,
        how="left",
        on=["topic_id", "date"]
    )
    topics_daily_counts["count"] = topics_daily_counts["count"].fillna(value=0).astype(int)

    # sort topics_daily_counts for simplified transformations
    topics_daily_counts = topics_daily_counts.sort_values(by=["date", "topic_id", "count"])
    topics_daily_counts = topics_daily_counts.reset_index(drop=True)
    logger.info(f"{topics_daily_counts.shape=}")

    # transform counts into a list representation per topic
    dataset = topics_daily_counts.groupby(by="topic_id").agg({"date": list, "count": list})
    dataset = dataset.reset_index()

    # assign labels
    dataset["matches_trending"] = 0
    dataset.loc[dataset["topic_id"].isin(topics_matched_trending), "matches_trending"] = 1
    logger.info(f"{dataset.shape=}")
    logger.info("Distribution of labels:")
    logger.info(dataset["matches_trending"].value_counts())

    # add topic embeddings
    dataset["embedding"] = dataset["topic_id"].apply(topic_embeddings.get)
    num_missing_embeddings = dataset["embedding"].isna().sum()
    logger.info(f"Missing embeddings: {num_missing_embeddings}")
    logger.info(f"{dataset.shape=}")

    # save the dataset
    dataset_path = RESOURCES_DIR.joinpath(args.output_filename)
    logger.info(f"Saving dataset into: {dataset_path.resolve()} ...")
    dataset.to_json(dataset_path)
