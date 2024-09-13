import json
from datetime import datetime

import pandas as pd
from bson import ObjectId
from fundus import CCNewsCrawler, PublisherCollection, Article


def extract_article_data(article: Article):
    published_date = article.publishing_date
    if not published_date:
        published_date = "unknown-date"
    else:
        published_date = published_date.strftime("%Y-%m-%d")
    return {
        "url": article.html.requested_url,
        "title": article.title,
        "body": article.body.serialize(),
        "publisher": article.publisher,
        "published_date": published_date,
        "topics": article.topics,
        "language": article.lang,
        "free_access": article.free_access,
    }


if __name__ == '__main__':

    language = "de"
    start_date = "2024-08-01"
    end_date = "2024-09-10"
    output_path = "pulsespotter/resources/data/articles/fundus_duisburg.json"

    crawler = CCNewsCrawler(
        PublisherCollection.de,
        start=datetime.strptime(start_date, "%Y-%m-%d"),
        end=datetime.strptime(end_date, "%Y-%m-%d"),
        processes=2,
    )

    results = []
    for article in crawler.crawl():
        article_data = extract_article_data(article)
        should_ingest = start_date <= article_data.get("published_date") <= end_date
        should_ingest = should_ingest and article_data.get("language", "en") == language
        if should_ingest:
            results.append(article_data)

    df = pd.DataFrame(results)

    # preparing fields to build a mask
    df["summary"] = df["body"].apply(lambda x: x["summary"])
    df["sections"] = df["body"].apply(lambda x: x["sections"])
    df["summary"] = df["summary"].apply(lambda x: " ".join(x))
    df["content"] = df["sections"].apply(
        lambda x: " ".join([" ".join(y["headline"]) + " " + " ".join(y["paragraphs"]) for y in x])
    )

    # finding articles with duisburg-relevant content
    mask = (
        df["title"].str.lower().str.contains("duisburg") |
        df["summary"].str.lower().str.contains("duisburg") |
        df["content"].str.lower().str.contains("duisburg")
    )
    duisburg = df.loc[mask]
    duisburg = duisburg[["url", "title", "publisher", "published_date", "body"]]

    # preparing dates
    duisburg["raw_date"] = duisburg["published_date"]
    duisburg["parsed_date"] = duisburg["published_date"]
    duisburg["visited"] = True
    duisburg = duisburg.drop(columns=["published_date"])

    # preparing description
    duisburg["description"] = duisburg["body"].apply(lambda x: (" ".join(x["summary"])).strip())
    duisburg["description"] = duisburg["description"].apply(lambda x: x or None)

    # preparing paragraphs
    duisburg["paragraphs"] = duisburg["body"].apply(lambda x: [[(" ".join(s["headline"])).strip(), (" ".join(s["paragraphs"])).strip()] for s in x["sections"]])
    duisburg["paragraphs"] = duisburg["paragraphs"].apply(lambda x: sum(x, []))
    duisburg["paragraphs"] = duisburg["paragraphs"].apply(lambda x: [y for y in x if y])
    duisburg = duisburg.drop(columns=["body"])

    # preparing site_name
    duisburg["site_name"] = duisburg["publisher"].apply(lambda x: "-".join(x.lower().split()))
    duisburg = duisburg.drop(columns=["publisher"])

    # prepare _id field
    duisburg["_id"] = [{"$oid": str(ObjectId())} for _ in range(len(duisburg))]

    # adding flag for simpler navigation in the db
    duisburg["external_ingestion"] = True

    json.dump(duisburg.to_dict("records"), open(output_path, "w"), ensure_ascii=False)
