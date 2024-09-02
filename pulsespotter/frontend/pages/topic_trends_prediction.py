from datetime import datetime, timedelta
from typing import Dict, Optional
from urllib.parse import urljoin

import requests
import streamlit as st

from pulsespotter.config import API_BASE_URL
from pulsespotter.frontend.components import get_topic_summary_card
from pulsespotter.frontend.styles import summary_card
from pulsespotter.frontend.utils import generate_weeks


def get_topic_trends_predictions(start_date: str, end_date: str) -> Optional[Dict]:
    payload = {"start_date": start_date, "end_date": end_date}
    trending_topics_endpoint = urljoin(API_BASE_URL, f"topics/predict-topic-trends")
    try:
        response = requests.post(trending_topics_endpoint, json=payload)
        if response.status_code == 200:
            response = response.json()
            return response
    except:
        return None


if __name__ == "__main__":

    st.title("Topic Trends Prediction")

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

    # retrieve topic trends predictions
    topic_trends_predictions = get_topic_trends_predictions(start_date, end_date)
    if topic_trends_predictions:
        st.header("Overview")

        # Display topic data and links
        for topic_data in topic_trends_predictions:
            topic_data_ = {**topic_data, "topic_start_date": start_date, "topic_end_date": end_date}
            with st.container():
                st.write(get_topic_summary_card(topic_data_), unsafe_allow_html=True)
    else:
        st.write("No topics found for the given date range.")
