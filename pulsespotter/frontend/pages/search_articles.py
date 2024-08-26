from datetime import datetime
from typing import Dict, Optional
from urllib.parse import urljoin

import requests
import streamlit as st

from pulsespotter.config import API_BASE_URL
from pulsespotter.frontend.components import get_article_summary_card
from pulsespotter.frontend.styles import summary_card


def search_articles(start_date: str, end_date: str, limit: int, search_phrase: str) -> Optional[Dict]:
    assert 1 <= limit <= 20
    payload = {"start_date": start_date, "end_date": end_date, "limit": limit, "phrase": search_phrase}
    search_articles_endpoint = urljoin(API_BASE_URL, f"articles/search")
    try:
        response = requests.post(search_articles_endpoint, json=payload)
        if response.status_code == 200:
            response = response.json()
            return response
    except:
        return None


def extract_query_params() -> Dict:
    start_date = st.query_params.get("start_date")
    end_date = st.query_params.get("start_date")
    response = {}
    if start_date and end_date:
        response = {
            "start_date": datetime.strptime(start_date, "%Y-%m-%d"),
            "end_date": datetime.strptime(end_date, "%Y-%m-%d"),
        }
    return response


if __name__ == "__main__":

    st.title("Search articles")

    # load required styles
    st.markdown(summary_card, unsafe_allow_html=True)

    # extract query parameters
    query_params = extract_query_params()
    start_date = query_params.get("start_date", datetime.now())
    end_date = query_params.get("end_date", datetime.now())

    start_date = st.date_input("Select start date", value=start_date)
    end_date = st.date_input("Select end date", value=end_date)
    search_phrase = st.text_input("Input a search phrase", value="")
    limit = st.number_input("Response limit", min_value=1, max_value=20, value=1)

    if st.button("Search"):
        articles = search_articles(
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
            search_phrase=search_phrase,
            limit=limit,
        )
        for article_data in articles:
            with st.container():
                st.write(
                    get_article_summary_card(article_data, max_content_length=500),
                    unsafe_allow_html=True,
                )
