import streamlit as st
import requests
import plotly.express as px
from datetime import datetime, timedelta

from pulsespotter.frontend.utils import generate_weeks

st.title("Trending Topics")

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
payload = {"start_date": start_date, "end_date": end_date}
# todo: refactor such that we have a global variable containing the backend URL
trending_topics_endpoint = "http://backend:8000/api/topics/trending"
response = requests.post(trending_topics_endpoint, json=payload)

if response.status_code != 200:
    st.error(f"Failed to retrieve topics. Error: {response.status_code}")

# Display the topics in a table format
topics = response.json()
st.write("### Trending Topics")
if topics:
    # Extract labels and sizes for the pie chart
    labels = [topic['topic_label'] for topic in topics]
    sizes = [topic['num_articles'] for topic in topics]

    # Create a pie chart using Plotly
    fig = px.pie(
        names=labels,
        values=sizes,
        title='Overview',
        hole=0.1,
    )
    st.plotly_chart(fig)

    # Display topic data and links
    for topic in topics:
        refer_link = (
            f"/topic_info?topic_id={topic['topic_id']}"
            f"&start_date={start_date}&end_date={end_date}"
        )
        topic_label = topic['topic_label']
        st.markdown(f'<a href="{refer_link}" target="_self"><b>Topic Label: {topic_label}</b></a>',
                    unsafe_allow_html=True)
        st.write(f"**Number of Articles**: {topic['num_articles']}")
        st.write("---")
else:
    st.write("No trending topics found for the given date range.")
