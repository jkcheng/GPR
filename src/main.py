import logging
import streamlit as st
# import streamlit_ext as ste
import os
from openai import OpenAI, RateLimitError
from prompts import * #SYSTEM_PROMPT_REC, USER_PROMPT_REC,JOB_TEXT_PLACEHOLDER, RESUME_TEXT_PLACEHOLDER
from doc_utils import extract_text_file
import json
import redis

# logging
logging.basicConfig(level=logging.WARNING) # set root level logger to warning
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# redis db
host = "localhost"
redis_port = 6379

r = redis.Redis(
    host=host,
    port=redis_port,
    decode_responses=True,
)

def set_data(key, text):
    r.set(key, text)


def load_data(user):
    db_value = r.get(user)
    try:
        return str(db_value)
    except TypeError:
        return None

def ask_openai_chatcompletion(summary_prompt, resume_text):
    with st.spinner(text="Asking openAI..."):
        # get summary of job desc from openAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT_SUMM},
                {"role": "user", "content": summary_prompt},
            ],
            api_key=api_key
        )
        answer = response["choices"][0]["message"]["content"]
        answer = json.loads(answer)

        # parse answer for job description parts
        job_company = answer["company"]
        job_position = answer["position"]
        job_duties = answer["duties"]
        job_requirements = answer["requirements"]

        # build rec prompt
        rec_prompt = (USER_PROMPT_REC
                      .replace(RESUME_TEXT_PLACEHOLDER, resume_text)
                      .replace(JOB_COMPANY_TEXT_PLACEHOLDER, job_company)
                      .replace(JOB_POSITION_TEXT_PLACEHOLDER, job_position)
                      .replace(JOB_DUTIES_TEXT_PLACEHOLDER, '  \n'.join(job_duties))
                      .replace(JOB_REQUIREMENTS_TEXT_PLACEHOLDER, '  \n'.join(job_requirements))
                      )
        logger.debug(rec_prompt)

        response_rec = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT_REC},
                {"role": "user", "content": rec_prompt},
            ],
            api_key=api_key
        )
    answer = response_rec["choices"][0]["message"]["content"]
    return answer

# def ask_openai_assistant(summary_prompt, resume_text):
#     with st.spinner(text="Asking openAI Assistant..."):
#         # get summary of job desc from openAI
#         response = openai.ChatCompletion.create(
#             model="gpt-3.5-turbo",
#             messages=[
#                 {"role": "system", "content": SYSTEM_PROMPT_SUMM},
#                 {"role": "user", "content": summary_prompt},
#             ],
#             api_key=api_key
#         )
#         answer = response["choices"][0]["message"]["content"]
#         answer = json.loads(answer)
#
#         # parse answer for job description parts
#         job_company = answer["company"]
#         job_position = answer["position"]
#         job_duties = answer["duties"]
#         job_requirements = answer["requirements"]
#
#         # build rec prompt
#         rec_prompt = (USER_PROMPT_REC
#                       .replace(RESUME_TEXT_PLACEHOLDER, resume_text)
#                       .replace(JOB_COMPANY_TEXT_PLACEHOLDER, job_company)
#                       .replace(JOB_POSITION_TEXT_PLACEHOLDER, job_position)
#                       .replace(JOB_DUTIES_TEXT_PLACEHOLDER, '  \n'.join(job_duties))
#                       .replace(JOB_REQUIREMENTS_TEXT_PLACEHOLDER, '  \n'.join(job_requirements))
#                       )
#         logger.debug(rec_prompt)
#
#         response_rec = openai.ChatCompletion.create(
#             model="gpt-3.5-turbo",
#             messages=[
#                 {"role": "system", "content": SYSTEM_PROMPT_REC},
#                 {"role": "user", "content": rec_prompt},
#             ],
#             api_key=api_key
#         )
#     answer = response_rec["choices"][0]["message"]["content"]
#     return answer

# streamlit app start
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
    Upload or enter your resume in the text box to get started.
    Enter the job description you're interested in into the text box and 
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
client = OpenAI(api_key=api_key)

resume = st.file_uploader("Choose a file", type=["pdf", "docx", "txt", "rtf"])
if resume:
    resume_text = extract_text_file(resume)
else:
    st.write("**OR**")
    resume_text = st.text_area("Enter Resume:", height=200)

if not resume and not resume_text:
    st.info("Please enter or upload your resume to get started.")

# form for submitting job evaluation
if resume_text:
    redis_key = hash(resume_text)

    with st.form("input"):
        # If the OpenAI API Key is not set as an environment variable, prompt the user for it
        if not api_key:
            api_key = st.text_input(
                "Enter your OpenAI API Key: [(click here to generate a new key if you do not have one)](https://platform.openai.com/account/api-keys)",
                type="password",
            )

        job_text = st.text_area("Enter Job Description:", height=200)
        submitted = st.form_submit_button("Submit")

    if submitted and resume_text and job_text:
        summary_prompt = (USER_PROMPT_SUMM
                          .replace(JOB_TEXT_PLACEHOLDER, job_text)
                          )
        logger.debug(summary_prompt)

        # ask openai
        try:
            answer = ask_openai_chatcompletion(summary_prompt, resume_text)
            if answer:
                set_data(redis_key, answer)
                st.write(load_data(redis_key))

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

pass