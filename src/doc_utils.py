from pdfminer.high_level import extract_text
from docx2python import docx2python
from striprtf.striprtf import rtf_to_text

def extract_text_pdf(file):
    return extract_text(file)

def extract_text_docx(file):
    return docx2python(file).text

def extract_text_file(file):
    if file.type == "application/pdf":
        text = extract_text_pdf(file)
        return text
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        text = extract_text_docx(file)
        return text
    elif file.type == "text/rtf":
        rtf_text = file.getvalue().decode("utf-8")
        return rtf_to_text(rtf_text)
    else:
        return file.getvalue().decode("utf-8")