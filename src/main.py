import logging
import streamlit as st
# import streamlit_ext as ste
import os
from openai import OpenAI, RateLimitError
from prompts import * #SYSTEM_PROMPT_REC, USER_PROMPT_REC,JOB_TEXT_PLACEHOLDER, RESUME_TEXT_PLACEHOLDER
from doc_utils import extract_text_file
import json
import redis
import time

# logging
logging.basicConfig(level=logging.WARNING) # set root level logger to warning
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def set_data(key, text):
    r.set(key, text)


def load_data(user):
    db_value = r.get(user)
    try:
        return str(db_value)
    except TypeError:
        return None

def wait_for_run(thread, run, secs):
    while run.status in ['queued', 'in_progress']:
        # check for completion and display result
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        # print('run_id:', run.id, 'in_progress')
        print(f'{run.status.capitalize()}... Please wait.')
        time.sleep(secs)

    if run.status == 'completed':
        pass
    else:
        print(f"Run NOT COMPLETED: {run.status}")

    return run

def ask_openai_chatcompletion(summary_prompt, resume_text):
    with st.spinner(text="Asking openAI..."):
        # get summary of job desc from openAI
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT_SUMM},
                {"role": "user", "content": summary_prompt},
            ]
        )
        answer = response.choices[0].message.content
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

        response_rec = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT_REC},
                {"role": "user", "content": rec_prompt},
            ]
        )
    answer = response_rec.choices[0].message.content
    return answer

def ask_openai_assistant(user_data, resume_text, job_text):
    assistant_id = 'asst_mYXHlF2jnkzu8uNS4YJppD8Y'
    assistant = client.beta.assistants.retrieve(assistant_id)
    # redis_key = hash(resume_text)

    with st.spinner(text="Asking openAI Assistant..."):
        # get summary of job desc from openAI
        # try to get existing thread for user, create one if it doesn't exist
        try:
            thread_id = user_data['thread_id']
            if thread_id and thread_id != "":
                thread = client.beta.threads.retrieve(thread_id)
            else:
                thread = client.beta.threads.create()
                # redis_val = f'{{"thread_id": "%s"}}' % thread.id
                # set_data(redis_key, redis_val)

                # add messages if thread is new
                resume_prompt = USER_PROMPT_ASSIST_RESUME.replace(RESUME_TEXT_PLACEHOLDER, resume_text)
                resume_message = client.beta.threads.messages.create(
                    thread_id=thread.id,
                    role="user",
                    content=resume_prompt
                )
        except Exception as e:
            print('an error occurred:', e)

        # logger.debug(thread)

        job_prompt = USER_PROMPT_ASSIST_REC.replace(JOB_TEXT_PLACEHOLDER, job_text)
        job_message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=job_prompt
        )

        # run assistant
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id
        )

        # check for completion and display result
        run = wait_for_run(thread, run, 2)

        # Retrieve all messages from the thread
        messages = client.beta.threads.messages.list(
            thread_id=thread.id
        )

        # Get last message as answer
        msg = messages.data[0]
        answer = msg.content[0].text.value
        # for msg in messages.data:
        #     role = msg.role
        #     content = msg.content[0].text.value
        #     print(f"{role.capitalize()}: {content}")
        #     answer.append(content)

    return answer

# streamlit app
st.set_page_config(
    page_title="GPR",
    page_icon=":clipboard:",
    layout="wide",
    initial_sidebar_state="auto"
)

# DEBUG: check if environment vars set
# try:
#     is_api_key_set = os.environ.get("OPENAI_API_KEY") == st.secrets.get("OPENAI_API_KEY")
#     is_db_hostname_set = os.environ.get("DB_HOSTNAME") != None
# except KeyError:
#     is_api_key_set = False
#     is_db_hostname_set = False
# st.write(
#     "Has environment variables been set:",
#     "  \n api_key:", is_api_key_set,
#     "  \n db_hostname:", is_db_hostname_set,
# )

# redis db
host = os.environ.get("DB_HOSTNAME")
redis_port = 6379

r = redis.Redis(
    host=host,
    port=redis_port,
    decode_responses=True,
)

api_key = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

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

        # create keys for db
        user_key = hash(resume_text)
        job_key = hash(job_text)

        # ask openai
        try:
            # get existing thread or create new
            user_data = load_data(user_key)
            if user_data and user_data != "None":
                user_data = json.loads(user_data)
                # thread_id = user_data['thread_id']
                # thread = client.beta.threads.retrieve(thread_id)
            else:
                # thread = client.beta.threads.create()
                user_data = f'''{{
                    "thread_id": "",
                    "%s": {{
                        "job_description": "",
                        "answer": ""
                    }}
                }}    
                ''' % (job_key)
                logger.debug(user_data)
                user_data = json.loads(user_data)
                user_data[str(job_key)]['job_description'] = job_text

            # answer = ask_openai_chatcompletion(user_data, summary_prompt, resume_text)
            answer = ask_openai_assistant(user_data, resume_text, job_text)
            # print(answer)
            # st.write(answer)
            if answer:
                if str(job_key) in user_data.keys():
                    user_data[str(job_key)]["answer"] = answer
                else:
                    user_data[str(job_key)] = {
                        "job_description": "",
                        "answer": ""
                    }
                    user_data[str(job_key)]["job_description"] = job_text
                    user_data[str(job_key)]["answer"] = answer
                set_data(str(user_key), json.dumps(user_data))
                # st.json(json.loads(answer))
                st.write(json.loads(answer))
                # logger.debug(user_data)

        except RateLimitError as e:
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