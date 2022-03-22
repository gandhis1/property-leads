FROM python:3.10-slim

WORKDIR /usr/src/property-leads

COPY src/ ./
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

#CMD [ "python", "./TODO.py" ] # TODO: Create the web application front-end using Streamlit and launch here