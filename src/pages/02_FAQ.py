import streamlit as st

st.markdown(
    f"""
    # Frequently Asked Questions
    """,

)

st.markdown(
    """
    
    ## Why was this made?
    
    This was made primarily as a learning project on building and deploying a python-based web application 
    leveraging the new publicly available LLM apis.
    
    ## Why is an OpenAI API Key required?

    Currently, only ChatGPT is supported as the LLM for assessing resume and job description fit.
    OpenAI requires an api key for authentication, and since it costs money for each request I'd rather not use 
    my own key as a free service. You can generate your own at [OpenAI's website](https://platform.openai.com/account/api-keys)
    
    """
)