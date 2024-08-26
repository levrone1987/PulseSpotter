from typing import Optional, Dict
from urllib.parse import urljoin

import requests
import streamlit as st

from pulsespotter.config import API_BASE_URL
from pulsespotter.frontend.components import get_article_summary_card
from pulsespotter.frontend.styles import summary_card
from pulsespotter.frontend.utils import safe_get_article_field


def get_article_data(article_id: str) -> Optional[Dict]:
    articles_info_endpoint = urljoin(API_BASE_URL, f"articles/info/{article_id}")
    response = requests.get(articles_info_endpoint)
    if response.status_code != 200:
        st.error(f"Error retrieving article data.")
    return response.json()


def get_similar_articles(article_id: str) -> Optional[Dict]:
    similar_articles_endpoint = urljoin(API_BASE_URL, f"articles/search-similar/{article_id}")
    response = requests.get(similar_articles_endpoint)
    if response.status_code != 200:
        st.error(f"Error retrieving similar articles.")
    return response.json()


if __name__ == '__main__':

    # extract query parameters
    article_id = st.query_params.get('article_id', None)

    # load required styles
    st.markdown(summary_card, unsafe_allow_html=True)

    # the application will not be loaded correctly without a valid article_id (only available from the db)
    if article_id:
        article_data = get_article_data(article_id)
        if not article_data:
            st.error("No data found for the given article ID.")

        st.title(f"{safe_get_article_field(article_data, 'title')}")
        st.write(safe_get_article_field(article_data, "description"))
        st.markdown(f'<a href="{article_data["url"]}">Visit original article</a>', unsafe_allow_html=True)
        st.write(f"Published by: {safe_get_article_field(article_data, 'site_name')}")
        st.write(f"Published at: {safe_get_article_field(article_data, 'article_date')}")
        st.write("---")

        st.header("Topic assignment")
        topic_id = article_data["topic_id"]
        topic_label = article_data["topic_label"]
        topic_link = f"/topic_info?topic_id={topic_id}"
        st.markdown(f'Assigned topic: <a href="{topic_link}" target="_self">{topic_label}</a>',
                    unsafe_allow_html=True)
        st.write(f"Topic assignment probability: {safe_get_article_field(article_data, 'topic_assignment_probability')}")
        st.write("---")

        st.header("Content")
        st.write(safe_get_article_field(article_data, "paragraphs"))
        st.write("---")

        st.header("Similar articles")
        similar_articles = get_similar_articles(article_id)
        similar_articles = sorted(similar_articles, key=lambda x: (x["score"], x["article_date"]), reverse=True)
        for article_data in similar_articles:
            with st.container():
                st.write(
                    get_article_summary_card(article_data, max_content_length=500),
                    unsafe_allow_html=True,
                )

    else:
        st.error("No article ID provided.")
