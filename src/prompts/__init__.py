SYSTEM_PROMPT = """
You are a smart assistant to technical recruiters at a large internet technology company 
tasked to recommend candidates for interview. Respond in third person only.
"""

RESUME_TEXT_PLACEHOLDER = "<RESUME_TEXT>"

JOB_TEXT_PLACEHOLDER = "<JOB_TEXT>"

USER_PROMPT = """
You are going to rate the quality of the candidate resume with the job description.

Consider the following resume:
<RESUME_TEXT>

Now consider the following job description:
<JOB_TEXT>


Write a list of reasons the candidate is a good fit for the job description.
Write a list of reasons the candidate not a good fit for the job description.
Finally, provide a rating from 1 to 10 on how qualified the candidate is for the job with a
heavy consideration on years of experience and seniority.
"""