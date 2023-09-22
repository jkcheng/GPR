# Base image
FROM python:3.11

# Working directory, Streamlit does not work at root
WORKDIR /app

# Copy the python dependencies file to the working directory
COPY requirements.txt /app/

# Install dependencies
RUN pip install -r requirements.txt

# Copy the current code to the working dir
COPY . /app/

# Run with Streamlit
CMD [ "streamlit", "run", "src/main.py" ]