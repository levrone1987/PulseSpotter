from typing import Dict, Optional
from urllib.parse import urljoin

import streamlit as st
import requests
import plotly.express as px
from datetime import datetime, timedelta

from pulsespotter.config import API_BASE_URL
from pulsespotter.frontend.components import get_topic_summary_card
from pulsespotter.frontend.styles import summary_card
from pulsespotter.frontend.utils import generate_weeks


def get_trending_topics(start_date: str, end_date: str) -> Optional[Dict]:
    payload = {"start_date": start_date, "end_date": end_date}
    trending_topics_endpoint = urljoin(API_BASE_URL, f"topics/trending")
    try:
        response = requests.post(trending_topics_endpoint, json=payload)
        if response.status_code == 200:
            response = response.json()
            return response
    except:
        return None


def create_trending_topics_pie_chart(trending_topics_data: Dict):
    topic_labels = [topic['topic_label'] for topic in trending_topics_data]
    topic_labels = ["_".join(topic_label.split("_")[1:]) for topic_label in topic_labels]
    return px.pie(
        names=topic_labels,
        values=[topic['num_articles'] for topic in trending_topics_data],
        hole=0.2,
    )


if __name__ == "__main__":

    st.title("Trending Topics")

    # load required styles
    st.markdown(summary_card, unsafe_allow_html=True)

    # extract query parameters
    today = datetime.now()
    start_date = st.query_params.get("start_date") or today.strftime("%Y-%m-%d")
    end_date = st.query_params.get("end_date") or today.strftime("%Y-%m-%d")

    # display week picker
    week_ranges = generate_weeks(today - timedelta(weeks=12), today)
    selected_week = None
    selected_index = -1
    if start_date and end_date:
        selected_week = (start_date, end_date)
        if selected_week in week_ranges:
            selected_index = week_ranges.index(selected_week)

    selected_week = st.selectbox(
        label="Select week",
        options=[f"{sd} - {ed}" for sd, ed in week_ranges],
        index=selected_index if selected_index > -1 else 0
    )
    start_date, end_date = selected_week.split(" - ")

    # retrieve trending topics
    trending_topics_data = get_trending_topics(start_date, end_date)
    if trending_topics_data:
        st.header("Overview")
        st.plotly_chart(create_trending_topics_pie_chart(trending_topics_data))

        # Display topic data and links
        for topic_data in trending_topics_data:
            topic_data_ = {**topic_data, "topic_start_date": start_date, "topic_end_date": end_date}
            with st.container():
                st.write(get_topic_summary_card(topic_data_), unsafe_allow_html=True)
    else:
        st.write("No trending topics found for the given date range.")
