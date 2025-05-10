from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import time
import os
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from backend.app import parse_sitemap
from supabase_utils import store_chunks, query_top_chunks, supabase, TABLE
import google.generativeai as genai

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
chat_model = genai.GenerativeModel('gemini-2.0-flash-001')

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
async def serve_index():
    return FileResponse(os.path.join("frontend", "index.html"))

# --- Models ---
class URLInput(BaseModel):
    url: str

class QuestionInput(BaseModel):
    question: str

# --- Core Functions ---
def normalize_url(url: str) -> str:
    url = url.lower().strip()
    if not url.startswith("http"):
        url = "https://" + url
    parsed = urlparse(url)
    domain = parsed.netloc or parsed.path
    return f"https://{domain}"

def scrape(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)
        if text:
            return text
    except:
        pass

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
    except:
        return ""

def chunk_text(text, size=300):
    words = text.split()
    return [' '.join(words[i:i + size]) for i in range(0, len(words), size)]

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

# --- Endpoints ---
@app.post("/add_url")
async def add_url(data: URLInput):
    base_url = normalize_url(data.url)
    sitemap_url = base_url.rstrip("/") + "/sitemap.xml"
    try:
        links = parse_sitemap(sitemap_url)
    except:
        links = [base_url]

    scraped = []
    for link in links:
        text = scrape(link)
        if not text.strip():
            continue
        chunks = chunk_text(text)
        embeddings = embed_texts(chunks)
        store_chunks(base_url, chunks, embeddings)
        scraped.append(link)

    return {"message": f"✅ Scraped {len(scraped)} pages from sitemap.", "scraped_links": scraped}

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
    urls = list({row["url"] for row in response.data})
    return {"urls": urls}
