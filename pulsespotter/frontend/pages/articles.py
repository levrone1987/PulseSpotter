import requests
import streamlit as st

from pulsespotter.frontend.utils import safe_get_article_field

st.title("Article Info")

# extract query parameters
article_id = st.query_params.get('article_id', None)

# the application will not be loaded correctly without a valid article_id (only available from the db)
if article_id:
    # todo: refactor such that we have a global variable containing the backend URL
    articles_info_endpoint = f"http://backend:8000/api/articles/info/{article_id}"
    response = requests.get(articles_info_endpoint)
    if response.status_code != 200:
        st.error(f"Something went wrong on our server.")

    article_data = response.json()
    if not article_data:
        st.error("No data found for the given article ID.")

    st.write(f"Published by: {safe_get_article_field(article_data, 'site_name')}")
    st.write(f"Published at: {safe_get_article_field(article_data, 'article_date')}")
    st.markdown(f'<a href="{article_data["url"]}">Visit original article</a>', unsafe_allow_html=True)

    topic_id = article_data["topic_id"]
    topic_label = article_data["topic_label"]
    topic_link = f"/topic_info?topic_id={topic_id}"
    st.markdown(f'Assigned topic: <a href="{topic_link}" target="_self">{topic_label}</a>',
                unsafe_allow_html=True)

    st.write(f"Topic assignment probability: {safe_get_article_field(article_data, 'topic_assignment_probability')}")
    st.write(f"**Title**:")
    st.write(safe_get_article_field(article_data, "title"))
    st.write(f"**Description**:")
    st.write(safe_get_article_field(article_data, "description"))
    st.write(f"**Content**:")
    st.write(safe_get_article_field(article_data, "paragraphs"))

else:
    st.error("No article ID provided.")