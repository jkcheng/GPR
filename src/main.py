import logging
import streamlit as st
# import streamlit_ext as ste
import os
import openai
from prompts import SYSTEM_PROMPT, USER_PROMPT,JOB_TEXT_PLACEHOLDER, RESUME_TEXT_PLACEHOLDER

# logging
logging.basicConfig(level=logging.WARNING) # set root level logger to warning
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

# app frontend
st.set_page_config(
    page_title="GPR",
    page_icon=":clipboard:",
    layout="wide",
    initial_sidebar_state="auto"
)

st.markdown(
    f"""
    # GPR (Generative Pre-trained Recruiter)
    """,
    unsafe_allow_html=False,
)

st.markdown(
    f"""Welcome to GPR! 
    Submit your resume and the job description you're interested in into the text box. 
    Click 'Submit' to have ChatGPT assess how well you fit as a candidate!
    """
)

# # check if environment var set
# try:
#     is_api_key_set = os.environ["OPENAI_API_KEY"] == st.secrets["OPENAI_API_KEY"]
# except KeyError:
#     is_api_key_set = False
# st.write(
#     "Has environment variables been set:",
#     is_api_key_set,
# )

api_key = os.getenv("OPENAI_API_KEY")

# input
with st.form("input"):
    # If the OpenAI API Key is not set as an environment variable, prompt the user for it
    if not api_key:
        api_key = st.text_input(
            "Enter your OpenAI API Key: [(click here to generate a new key if you do not have one)](https://platform.openai.com/account/api-keys)",
            type="password",
        )

    resume_text = st.text_area("Enter Resume:", height=200)
    job_text = st.text_area("Enter Job Description:", height=200)
    submitted = st.form_submit_button("Submit")

if submitted and resume_text and job_text:
    filled_prompt = (USER_PROMPT
                     .replace(RESUME_TEXT_PLACEHOLDER, resume_text)
                     .replace(JOB_TEXT_PLACEHOLDER, job_text)
                     )
    logger.debug(filled_prompt) # inspect prompt

    # openai stuff
    try:
        with st.spinner(text="Asking openAI..."):
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": filled_prompt},
                ],
                api_key=api_key
            )
        answer = response["choices"][0]["message"]["content"]
        st.write(answer)
    except openai.error.RateLimitError as e:
        st.markdown(
            "It looks like you do not have OpenAI API credits left. Check [OpenAI's usage webpage for more information](https://platform.openai.com/account/usage)"
        )
        st.write(e)
    except Exception as e:
        st.error("An error occurred. Please try again.")
        st.write(e)
elif submitted and ((resume_text == '') or (job_text == '')):
    st.warning("Resume or job description is missing!", icon="⚠️")
else:
    st.info("Please enter your resume and job description to get started.")

pass