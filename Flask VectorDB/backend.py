from flask import Flask, request
from flask_cors import CORS

import os, shutil, PyPDF2, re, urllib, requests

from io import BytesIO

from bs4 import BeautifulSoup

from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.vectorstores.base import VectorStoreRetriever
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import TextLoader

base_path = os.environ.get('OPENAI_API_BASE', 'http://localhost:44444/v1')
os.environ['OPENAI_API_KEY'] = 'anykey'
api_key = os.environ.get('OPENAI_API_KEY', 'anykey')

current_model = 'hermes-2-pro-mistral_q8'
available_models = []
source_dir = 'storage'
vdb_persist_dir = 'db'

app = Flask(__name__)
CORS(app)

@app.route('/files/upload', methods=['POST'])
def upload_files():
    files = request.files.getlist('files')
    for file in files:
        if file.filename.split('.')[1] == "pdf":
            pdf_reader = PyPDF2.PdfReader(BytesIO(file.read()))
            text = ''
            for page in pdf_reader.pages:
                text += page.extract_text()
            output = open("./storage/" + file.filename.split('.')[0] + '.txt', 'w')
            output.write(re.sub(r'[^\x00-\x7F\n]+', ' ', text))
            output.close()
        else:
            content = file.read().decode('utf-8', errors='ignore')
            cleaned_content = re.sub(r'[^\x00-\x7F\n]+', ' ', content)
            output_filename = "./storage/" + file.filename
            with open(output_filename, 'w') as output:
                output.write(cleaned_content)
    return "Files uploaded successfully"

@app.route('/from-link', methods=['POST'])
def fromlink():
    link = request.json['url']
    try:
        soup = BeautifulSoup(requests.get(link).text)
        output = open("./storage/"+link.replace('/', '__').replace(':', '-').replace('.', '_'), "a")
        output.write(re.sub(r'\n\s*\n+', '\n\n', re.sub(r'[^\x00-\x7F\n]+', ' ', soup.get_text()))+"\n")
        output.close()
        return "Link fetched properly"
    except Exception as e:
        return "Error while trying to extract data from URL", 404

@app.route('/files/index', methods=['POST'])
def index_files():
    try:
        os.system("rm -r db/*")
    except Exception as e:
        print(e)
    documents = []
    for file in os.listdir('./'+source_dir):
        loader = TextLoader('./'+source_dir+'/'+file)
        data = loader.load()
        for doc in data:
            doc.metadata['source'] = file
        documents.extend(data)

    texts = CharacterTextSplitter(chunk_size=2000, chunk_overlap=300).split_documents(documents)
    try:
        embedding = OpenAIEmbeddings(model="bert-large-uncased", openai_api_base=base_path)
        vectordb = Chroma.from_documents(documents=texts, embedding=embedding, persist_directory=vdb_persist_dir)
        vectordb.persist()
        vectordb = None
        return "Data indexed correctly"
    except Exception as e:
        print(e)
        return "Model not responding", 404

@app.route('/files/clean', methods=['POST'])
def clean_files():
    os.system('rm storage/*')
    return "Files cleared"

@app.route('/current')
def get_current_model():
    return current_model

@app.route('/models')
def get_list_models():
    response = 'curl http://localhost:8080/v1/models'
    for model in response['data']:
        if model['object'] == 'model': #Is it necessary to compare? Everything is a model!
            available_models.append(model['id'])
    return available_models

@app.route('/query', methods=['POST'])
def ask():
    try:
        return_value = {
            'source': set()
        }
        embedding = OpenAIEmbeddings(model="bert-large-uncased", openai_api_base=base_path)
        llm = ChatOpenAI(temperature=request.json['temperature'], model_name=current_model, openai_api_base=base_path)
        vectordb = Chroma(persist_directory=vdb_persist_dir, embedding_function=embedding)
        #qa = RetrievalQA.from_llm(llm=llm, retriever=VectorStoreRetriever(vectorstore=vectordb, search_type="similarity_score_threshold", search_kwargs={"score_threshold": 0.5, "k": 2}))
        qa = RetrievalQA.from_llm(llm=llm, retriever=VectorStoreRetriever(vectorstore=vectordb, search_kwargs={"k": 2}))
        results = qa.retriever.get_relevant_documents(request.json['query'])
        for x in results:
            return_value['source'].add(x.metadata.get('source'))
        return_value['source'] = list(return_value['source'])
        return_value['answer'] = qa.invoke(request.json['query'])['result']
        return return_value
    except Exception as e:
        print(e)
    return "Model not responding", 404
