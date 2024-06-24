import requests
from pymongo import MongoClient, errors
from tqdm import tqdm

from content_ingestion.config import MONGO_HOST, MONGO_DATABASE, MONGO_COLLECTION
from content_ingestion.utils.parse_utils import parse_date

if __name__ == '__main__':
    request_params = {
        "premium_proxy": "true",
        "proxy_country": "de",
    }
    extract_patterns = {
        "title": """//div[contains(@class, 'article-header')]//div[contains(@class, 'header-title')]//text()""",
        "description": """//div[contains(@class, 'article-header')]//div[contains(@class, 'header-teaser')]//text()""",
        "date": """//div[contains(@class, 'article-header')]//div[contains(@class, 'header-detail')]//time//text()""",
        "paragraphs": """//div[contains(@class, 'body-elements-container')]//p[contains(@class, 'body-elements__paragraph')]//text()""",
    }

    try:
        with MongoClient(MONGO_HOST) as mongo_client:
            db = mongo_client[MONGO_DATABASE]
            collection = db[MONGO_COLLECTION]

            query = {"site_name": "spiegel", "parsed_date": {"$exists": False}}
            cursor = collection.find(query)
            num_docs = collection.count_documents(query)
            pbar = tqdm(total=num_docs)

            for doc in cursor:
                # site_name = doc['site_name']
                # site_url = doc["url"]
                # print(site_url)
                # request_params["url"] = site_url
                # request_params["apikey"] = ZENROWS_API_KEY
                # response = requests.get("https://api.zenrows.com/v1/", params=request_params)
                # response.raise_for_status()
                # parsed_content = parse_website(response.text, extract_patterns)

                published_date = doc["published_date"]
                parsed_date = parse_date(published_date, output_format="%Y-%m-%d")

                collection.update_one(
                    filter={"_id": doc["_id"]},
                    update={
                        "$set": {"parsed_date": parsed_date, "raw_date": published_date},
                        # "$set": parsed_content,
                        "$unset": {"published_date": ""},
                    },
                )
                pbar.update(1)

    except errors.PyMongoError as e:
        print(f"MongoDB error: {e}")
    except requests.RequestException as e:
        print(f"HTTP request error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
