from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

import google.generativeai as genai
import os
from dotenv import load_dotenv
from backend.supabase_utils import store_chunks, query_top_chunks, supabase, TABLE


load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
embed_model = genai.GenerativeModel('embedding-001')
chat_model = genai.GenerativeModel('gemini-2.0-flash-001')

app = FastAPI()

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Scrape webpage
def scrape(url):
    try:
        # First attempt: static scraping
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all('p')
        text = ' '.join(p.get_text() for p in paragraphs).strip()

        if text:
            return text
    except Exception as e:
        pass  # Fail silently and try Selenium fallback

    # Second attempt: dynamic scraping using Selenium
    try:
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')

        driver = webdriver.Chrome(options=options)
        driver.get(url)
        time.sleep(3)  # Allow time for JS to render

        elems = driver.find_elements(By.TAG_NAME, "p")
        text = ' '.join(elem.text for elem in elems).strip()
        driver.quit()

        return text
    except Exception as e:
        return ""

# Chunk text
def chunk_text(text, size=300):
    words = text.split()
    return [' '.join(words[i:i+size]) for i in range(0, len(words), size)]

# Embed using Gemini
def embed_texts(texts):
    embeddings = []
    for text in texts:
        response = genai.embed_content(
            model="models/embedding-001",
            content=text,
            task_type="retrieval_document"
        )
        embeddings.append(response["embedding"])
    return embeddings
# Models
class URLInput(BaseModel):
    url: str

class QuestionInput(BaseModel):
    question: str

@app.post("/add_url")
async def add_url(data: URLInput):
    text = scrape(data.url)
    chunks = chunk_text(text)
    embeddings = embed_texts(chunks)
    store_chunks(data.url, chunks, embeddings)
    return {"message": f"Stored {len(chunks)} chunks from {data.url}"}

@app.post("/ask")
async def ask(data: QuestionInput):
    query_embedding = embed_texts([data.question])[0]
    top_chunks = query_top_chunks(query_embedding)
    context = "\n".join(top_chunks)
    prompt = f"""Use only the below information to answer the question:\n\n{context}\n\nQuestion: {data.question}\nAnswer:"""
    response = chat_model.generate_content(prompt)
    return {"answer": response.text}

@app.get("/get_urls")
async def get_urls():
    response = supabase.table(TABLE).select("url").execute()
    urls = list({row["url"] for row in response.data})  # Set to remove duplicates
    return {"urls": urls}