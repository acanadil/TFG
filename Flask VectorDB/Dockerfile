FROM ubuntu:22.04

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3.11-dev\
    python3-pip\
    python3-dev\
    libpython3.11-dev

RUN pip3 install Flask
RUN pip install langchain
RUN pip install -U langchain_openai
RUN pip3 install chromadb
RUN pip install PyPDF2
RUN pip install fitz
RUN pip install -U langchain-community
RUN pip install bs4
RUN pip install -U flask-cors

COPY backend.py /app/backend.py
RUN mkdir /app/storage
RUN mkdir /app/db

WORKDIR /app

CMD flask --app backend run
