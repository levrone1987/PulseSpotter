from langchain_core.prompts import ChatPromptTemplate


system_message = (
    "You will be used as an intelligent agent that is able to consume a list of strings that correspond to contents "
    "inside HTML elements which are extracted from news articles. This list of texts was extracted by identifying HTML "
    "elements such as headers, paragraphs, etc. and just extracting the contents inside each element. "
    "The goal is to identify which items in this list are content of the news article and not something else. "
    "The inputs are expected to be in German and the output should be in German as well. "
    "The output should be a single string containing the news article content."
)


def extract_news_article_text(elements_list, llm):
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_message),
            ("human", "{input}")
        ]
    )
    chain = prompt | llm
    input_formatted = "[" + ", ".join(elements_list) + "]"
    response = chain.invoke({"input": input_formatted})
    return response
