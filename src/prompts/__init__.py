SYSTEM_PROMPT_REC = """
You are a smart assistant to technical recruiters at a large internet technology company 
tasked to recommend candidates to interview. Respond in third person only.
"""

SYSTEM_PROMPT_SUMM = """
You are a smart assistant to technical recruiters at a large internet technology company 
tasked to summarize job descriptions. Respond in JSON schema format only.
"""

SYSTEM_PROMPT_ASSIST = """
You are a smart assistant to technical recruiters at a large internet technology company 
tasked to recommend candidates to interview. Respond in third person only.

Consider the following JSON schema:
{
    company: string;
    position: string;
    positives: string[];
    negatives: string[];
    conclusion: string;
    rating: float;
}

Rate how well the candidate resume matches the job description and provide output based on the JSON schema.
Write a list of reasons the candidate is a good match in the positives section.
Write a list of reasons the candidate is not a good match in the negatives section.
Finally, provide a conclusion on the candidate quality in the conclusion section with heavy consideration on years of experience and seniority.
Provide a rating from 1 to 10 in the rating section.
"""

USER_PROMPT_REC = """
You are going to rate the quality of the candidate resume with the job description.

Consider the following resume:\n
<RESUME_TEXT>

Now consider the following job description :\n
<JOB_COMPANY_TEXT_>\n
<JOB_POSITION_TEXT>

Duties:\n
<JOB_DUTIES_TEXT>

Requirements:\n
<JOB_REQUIREMENTS_TEXT>


Now consider the following JSON schema:\n
{
    company: string;
    position: string;
    positives: string[];
    negatives: string[];
    conclusion: string;
    rating: float;
}

Rate how well the candidate resume matches the job description and provide output based on the JSON schema.
Write a list of reasons the candidate is a good match in the positives section.
Write a list of reasons the candidate is not a good match in the negatives section.
Finally, provide a conclusion on the candidate quality in the conclusion section with heavy consideration on years of experience and seniority.
Provide a rating from 1 to 10 in the rating section.
"""

USER_PROMPT_SUMM = """
You are going to summarize the following job description:\n
<JOB_TEXT>


Now consider the following JSON schema:

{
    company: string;
    position: string;
    duties: string[];
    requirements: string[];
}

Summarize the job description and provide output according to the JSON schema. 
For the duties section provide a list of job duties. 
For the requirements section provide a list of requirements.
"""

USER_PROMPT_ASSIST_RESUME = """
Consider the following resume that will be rated against future job descriptions:\n

<RESUME_TEXT>
"""

USER_PROMPT_ASSIST_REC = """
Now rate resume against the following job description::\n

<JOB_TEXT>

Respond only in JSON format in your instructions.
"""

RESUME_TEXT_PLACEHOLDER = "<RESUME_TEXT>"

JOB_TEXT_PLACEHOLDER = "<JOB_TEXT>"

JOB_COMPANY_TEXT_PLACEHOLDER = "<JOB_COMPANY_TEXT_>"

JOB_POSITION_TEXT_PLACEHOLDER = "<JOB_POSITION_TEXT>"

JOB_DUTIES_TEXT_PLACEHOLDER = "<JOB_DUTIES_TEXT>"

JOB_REQUIREMENTS_TEXT_PLACEHOLDER = "<JOB_REQUIREMENTS_TEXT>"
