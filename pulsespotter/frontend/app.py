import streamlit as st


st.title("PulseSpotter")
st.write("This is the index page.")
st.write("Use the sidebar to navigate to different pages.")
st.markdown(f"""
    Start from the <a href="/trending_topics" target="_self">Trending Topics</a> page.
    """,
    unsafe_allow_html=True
)
