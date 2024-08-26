from collections import Counter, defaultdict
from datetime import datetime
from urllib.parse import urljoin

import plotly.express as px
import requests
import streamlit as st

from pulsespotter.config import API_BASE_URL
from pulsespotter.frontend.components import get_article_summary_card
from pulsespotter.frontend.styles import summary_card


def get_article_summary(article_id: str):
    endpoint = urljoin(API_BASE_URL, f"articles/summary/{article_id}")
    response = requests.get(endpoint)
    if response.status_code != 200:
        return
    return response.json()


if __name__ == '__main__':

    st.title("Topic Info")

    # load required styles
    st.markdown(summary_card, unsafe_allow_html=True)

    # extract query parameters
    topic_id = st.query_params.get('topic_id', None)
    start_date = st.query_params.get('start_date', None)
    end_date = st.query_params.get('end_date', None)

    # display back button
    trending_topics_url = f"/trending_topics?start_date={start_date}&end_date={end_date}"
    if not start_date or not end_date:
        trending_topics_url = "/trending_topics"
    st.markdown(f'<a href="{trending_topics_url}" target="_self"><b>Back to Trending Topics</b></a>',
                unsafe_allow_html=True)

    # the application will not be loaded correctly without a valid topic_id (only available from the db)
    if topic_id:
        topics_info_endpoint = urljoin(API_BASE_URL, f"topics/{topic_id}")
        response = requests.get(topics_info_endpoint)
        if response.status_code != 200:
            st.error(f"Something went wrong on our server.")

        topic_assignments_data = response.json()
        if not topic_assignments_data:
            st.error("No data found for the given topic ID.")

        # extract and display the topic information
        first_item = topic_assignments_data[0]
        topic_label = first_item.get("topic_label", "N/A")
        topic_start_date = first_item.get("topic_start_date", "N/A")
        topic_end_date = first_item.get("topic_end_date", "N/A")
        st.write(f"**Topic Label:** {topic_label}")
        st.write(f"**Topic Start Date:** {topic_start_date}")
        st.write(f"**Topic End Date:** {topic_end_date}")

        # plot number of articles through time
        st.header("Articles through time")
        article_dates = [item["document_date"] for item in topic_assignments_data]
        date_counts = Counter(article_dates)
        date_counts = sorted(
            date_counts.items(), key=lambda x: datetime.strptime(x[0], "%Y-%m-%d")
        )
        dates, counts = zip(*date_counts)
        fig = px.line(
            x=dates,
            y=counts,
            labels={'x': 'Date', 'y': 'Number of articles'},
        )
        st.plotly_chart(fig)

        # display articles
        st.header("Articles overview")
        dates_articles_map = defaultdict(list)
        for tad in topic_assignments_data:
            dates_articles_map[tad["document_date"]].append(tad["document_id"])

        # Dropdown to select a date
        dates = sorted(set(dates_articles_map))
        selected_date = st.selectbox("Select a date", dates)

        # Filter articles by the selected date
        articles_at_date = dates_articles_map[selected_date]

        # Pagination setup
        items_per_page = 10
        total_pages = len(articles_at_date) // items_per_page + (len(articles_at_date) % items_per_page > 0)
        page_number = st.number_input("Page number", min_value=1, max_value=total_pages, value=1)

        # Calculate the start and end indices for the current page
        start_idx = (page_number - 1) * items_per_page
        end_idx = start_idx + items_per_page
        max_content_length = 500

        for article_id in articles_at_date[start_idx:end_idx]:
            article_summary = get_article_summary(article_id)
            article_summary["article_id"] = article_id
            with st.container():
                st.write(
                    get_article_summary_card(article_summary, max_content_length=max_content_length),
                    unsafe_allow_html=True,
                )
        st.write(f"Page {page_number} of {total_pages}")

    else:
        st.error("No topic ID provided.")
