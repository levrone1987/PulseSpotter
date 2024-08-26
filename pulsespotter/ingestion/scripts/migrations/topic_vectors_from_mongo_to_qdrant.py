import uuid

from more_itertools import first
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from qdrant_client.http.models import Filter, FieldCondition, MatchValue
from tqdm import tqdm

from pulsespotter.config import QDRANT_HOST, QDRANT_API_KEY
from pulsespotter.db.dao import get_topic_embeddings_repository


if __name__ == '__main__':

    # load vectors from mongo and transfer into qdrant
    topic_embeddings_repository = get_topic_embeddings_repository()
    topic_embeddings = topic_embeddings_repository.query(q={"_id": {"$exists": True}})

    sample_record = first(topic_embeddings, None)
    if not sample_record:
        print("Topic embeddings not found!")
        exit(-1)

    # initialize a new vector store collection
    client = QdrantClient(url=QDRANT_HOST, api_key=QDRANT_API_KEY)

    collection_name = "topic_embeddings"
    vector_size = len(sample_record["embedding"])
    distance = Distance.COSINE

    if client.collection_exists(collection_name):
        client.delete_collection(collection_name)

    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=vector_size, distance=distance),
    )

    collections = client.get_collections()
    if collection_name in [col.name for col in collections.collections]:
        print(f"Collection '{collection_name}' created successfully!")
    else:
        print(f"Failed to create collection '{collection_name}'.")

    # ingest vectors into qdrant
    for record in tqdm(topic_embeddings, desc=f"Ingesting embeddings into collection={collection_name}"):
        client.upsert(
            collection_name=collection_name,
            points=[
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=record["embedding"],
                    payload={"topic_id": record["_id"]}
                )
            ]
        )

    # retrieve topics by topic_id
    filter_ = Filter(
        must=[
            FieldCondition(
                key="topic_id",
                match=MatchValue(value=sample_record["_id"])
            )
        ]
    )

    # Search for the vector using the filter
    search_results = client.search(
        collection_name=collection_name,
        query_vector=[0] * vector_size,
        limit=1,
        query_filter=filter_,
        with_vectors=True,
    )

    print(search_results)
