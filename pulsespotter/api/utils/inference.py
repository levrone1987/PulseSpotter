from itertools import product
from typing import List

import pandas as pd
import torch

from pulsespotter.config import RESOURCES_DIR
from pulsespotter.db.repositories.topic_assignments import TopicAssignmentsRepository
from pulsespotter.db.repositories.topic_embeddings import TopicEmbeddingsRepository
from pulsespotter.db.repositories.topics_vectors import TopicsVectorsRepository
from pulsespotter.training.utils.model import Model

model = None


# model IO
def load_model(model_filename: str):
    if not model_filename:
        return
    global model
    if model:
        return model
    model_path = RESOURCES_DIR.joinpath(model_filename)
    if model_path.exists():
        model = Model(embedding_dim=384, counts_dim=7, counts_hidden_size=64)
        model.load_state_dict(torch.load(model_path))
        model = model.eval()


def get_model() -> Model:
    global model
    return model


def delete_model():
    global model
    if model:
        del model
        model = None


# inference
def get_topics_data(
        topic_start_date: str,
        topic_end_date: str,
        topic_assignments_repository: TopicAssignmentsRepository,
        topic_embeddings_repository: TopicEmbeddingsRepository,
        topic_vectors_repository: TopicsVectorsRepository
):
    # retrieve topic assignments
    topic_assignments = topic_assignments_repository.search_topic_assignments(
        topic_start_date=topic_start_date,
        topic_end_date=topic_end_date,
    )
    topic_assignments = pd.DataFrame(topic_assignments)
    if topic_assignments.shape[0] == 0:
        return None

    # retrieve topic embeddings
    topic_assignments["topic_id"] = topic_assignments["topic_id"].apply(str)
    topics_vectors = topic_vectors_repository.batch_get(topic_assignments["topic_id"].unique().tolist())
    topic_embeddings = topic_embeddings_repository.get_embeddings([tv["vector_id"] for tv in topics_vectors])
    topic_embeddings = {te["topic_id"]: te["embedding"] for te in topic_embeddings}

    # filter on topics which have embeddings
    topic_ids = list(topic_embeddings)
    topic_assignments = topic_assignments.loc[topic_assignments["topic_id"].isin(topic_ids)]

    # extract all dates within the topics date range
    dates = pd.date_range(topic_start_date, topic_end_date).strftime("%Y-%m-%d").tolist()

    # collect document counts per topic-date pairs
    dataset_df = topic_assignments[["topic_id", "document_date", "document_id"]]
    dataset_df = dataset_df.rename(columns={"document_date": "date", "document_id": "count"})
    dataset_df = dataset_df.groupby(by=["topic_id", "date"])["count"].nunique()
    dataset_df = dataset_df.reset_index()

    # fill missing values
    topic_ids = dataset_df["topic_id"].unique().tolist()
    dataset_df = pd.merge(
        dataset_df,
        pd.DataFrame(list(product(topic_ids, dates)), columns=["topic_id", "date"]),
        on=["topic_id", "date"],
        how="right"
    )
    dataset_df["count"] = dataset_df["count"].fillna(value=0).astype(int)

    # format the dataset
    dataset_df = dataset_df.sort_values(by=["topic_id", "date"])
    dataset_df = dataset_df.groupby(by="topic_id").agg({"date": list, "count": list})
    dataset_df = dataset_df.reset_index()

    # add the embeddings
    dataset_df["embedding"] = dataset_df["topic_id"].map(topic_embeddings)
    dataset_df = dataset_df.rename(columns={"count": "counts", "embedding": "topic_embedding"})
    dataset_df = dataset_df.merge(
        topic_assignments[["topic_id", "topic_label"]].drop_duplicates(), how="left", on="topic_id",
    )
    return dataset_df


@torch.no_grad()
def predict_trending_topic_score(article_counts: List, topic_embedding: List):
    model = get_model()
    logits = model(
        counts=torch.FloatTensor([article_counts]),
        topic_emb=torch.FloatTensor([topic_embedding]),
    )
    probability = torch.sigmoid(logits).squeeze().item()
    return probability


__all__ = [
    "load_model",
    "get_model",
    "delete_model",
    "get_topics_data",
    "predict_trending_topic_score",
]
