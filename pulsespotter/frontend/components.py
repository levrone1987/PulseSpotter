from typing import Dict

from pulsespotter.frontend.utils import safe_get_article_field, truncate_text_content


def get_topic_summary_card(topic_data: Dict) -> str:
    refer_link = (
        f"/topic_info?topic_id={topic_data['topic_id']}"
        f"&start_date={topic_data['topic_start_date']}&end_date={topic_data['topic_end_date']}"
    )
    # present topic trends exist
    score_component = "<span></span>"
    score = topic_data.get("probability")
    if score:
        score_component = f"<span><strong>Trending Score:</strong> {score:.4f}</span><br/>"
    return f"""
    <div class="summary_card">
        <h5>{topic_data['topic_label']}</h5>
        <strong>Number of articles:</strong> {topic_data['num_articles']}<br/>
        {score_component}
        <span><a href="{refer_link}" target="_self">See more</a></span>
    </div>
    """


def get_article_summary_card(article_summary: dict, max_content_length: int = 500) -> str:
    """
    Generates an HTML string for a summary card of an article.

    This function creates an HTML snippet representing a summary card for a given article.
    The summary card includes the article title, a "Read more" link, a description, and
    the first paragraph of the article content truncated to a specified length. Additional
    details such as the site name and article date are also included.

    Parameters:
    -----------
    article_summary : dict
        A dictionary containing the article's details. The expected keys are:
        - "article_id" (str): The unique identifier of the article.
        - "title" (str): The title of the article.
        - "description" (str): A short description of the article.
        - "paragraphs" (str): The main content of the article, with paragraphs separated by double newlines.
        - "site_name" (str): The name of the site where the article is published.
        - "article_date" (str): The date when the article was published.
        - "score" (float): A score for the article.

    max_content_length : int, optional
        The maximum length of the article content to display in the summary card.
        Defaults to 500 characters.
    """
    article_id = article_summary["article_id"]
    article_title = safe_get_article_field(article_summary, "title")
    article_description = safe_get_article_field(article_summary, "description")
    article_content = safe_get_article_field(article_summary, "paragraphs")
    article_content_truncated = truncate_text_content(article_content, max_len=max_content_length)
    # present score if exists
    score_component = "<span></span>"
    score = article_summary.get("score")
    if score:
        score_component = f"<span><strong>Score:</strong> {score:.4f}</span><br/>"
    return f"""
    <div class="summary_card">
        <h4>{(article_title.upper() or "N/A")}</h4>
        <a href="/articles?article_id={article_id}" target="_self">Read more</a><br/>
        {score_component}
        <hr style='margin: 5px 0; padding: 0;'>
        <strong>Description:</strong><br/>
        <span>{(article_description or "N/A")}</span><br/><br/>
        <strong>Content:</strong><br/>
        <span>{(article_content_truncated or "N/A")}</span><br/><br/>
        <hr style='margin: 5px 0; padding: 0;'>
        <span>From {article_summary['site_name']} at {article_summary['article_date']}.</span>
    </div>
    """
