from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urlunparse

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

import google.generativeai as genai
import os
from dotenv import load_dotenv
from supabase_utils import store_chunks, query_top_chunks, supabase, TABLE

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

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

# Normalize URL to a standard format
def normalize_url(url: str) -> str:
    parsed = urlparse(url.strip().lower())

    # Ensure scheme is present
    scheme = parsed.scheme or "https"

    # Add www if missing
    netloc = parsed.netloc or parsed.path
    if not netloc.startswith("www."):
        netloc = "www." + netloc

    # Remove path/query/fragment
    return urlunparse((scheme, netloc, "", "", "", ""))

# Scrape webpage
def scrape(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)
        if text:
            return text
    except Exception:
        pass  # Fallback to Selenium

    try:
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')

        driver = webdriver.Chrome(options=options)
        driver.get(url)
        time.sleep(3)
        elems = driver.find_elements(By.TAG_NAME, "p")
        text = ' '.join(elem.text for elem in elems).strip()
        driver.quit()
        return text
    except Exception as e:
        print(f"Selenium scrape failed: {e}, URL: {url}")
        return ""

# Chunk text
def chunk_text(text, size=300):
    words = text.split()
    return [' '.join(words[i:i+size]) for i in range(0, len(words), size)]

# Embed text using Gemini
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

# Request Models
class URLInput(BaseModel):
    url: str

class QuestionInput(BaseModel):
    question: str

@app.post("/add_url")
async def add_url(data: URLInput):
    normalized_url = normalize_url(data.url)
    print(f"🔗 Normalized URL: {normalized_url}")

    text = scrape(normalized_url)
    if not text.strip():
        return {"message": f"🚫 No content found for {normalized_url}. Nothing was stored."}

    chunks = chunk_text(text)
    embeddings = embed_texts(chunks)
    if not any(chunks) or not any(embeddings):
        return {"message": f"🚫 Could not generate valid content or embeddings for {normalized_url}."}

    store_chunks(normalized_url, chunks, embeddings)
    return {"message": f"✅ Stored {len(chunks)} chunks from {normalized_url}"}

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
    urls = list({row["url"] for row in response.data})  # remove duplicates
    return {"urls": urls}

# Serve static frontend
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
async def root():
    return FileResponse(os.path.join("frontend", "index.html"))
