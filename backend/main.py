from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from urllib.parse import urlparse

import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse


from backend.scraper import scrape
from backend.sitemap_parser_visualizer import extract_final_urls
from backend.supabase_utils import store_chunks, query_top_chunks, supabase, TABLE
from backend.aiagent import chat_model, chunk_text, embed_texts



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

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
    url = url.lower().strip() # Remove leading/trailing whitespace and convert to lowercase
    if not url.startswith("http"):
        url = "https://" + url
    
    if url.startswith("https://") and not url.startswith("https://www."):
        url = url.replace("https://", "https://www.", 1)
    elif not url.startswith("https://www."):
        url = "https://www." + url
    parsed = urlparse(url)
    return parsed.geturl()



# --- Endpoints ---
'''
@app.post("/add_url")
async def add_url(data: URLInput):
    base_url = normalize_url(data.url)
    sitemap_url = base_url.rstrip("/") + "/sitemap.xml"
    try:
        links = extract_final_urls(sitemap_url)
    except:
        links = [base_url]

    scraped = []
    print(f"🗂️ Found {len(links)} links in the sitemap.")
    for link in links:
        text = scrape(link)
        if not text.strip():
            continue
        chunks = chunk_text(text)
        embeddings = embed_texts(chunks)
        store_chunks(link, chunks, embeddings)
        scraped.append(link)

    return {"message": f"✅ Scraped {len(scraped)} pages from sitemap.", "scraped_links": scraped}
'''

@app.post("/add_url")
async def add_url(data: URLInput):
    base_url = normalize_url(data.url)
    sitemap_url = base_url.rstrip("/") + "/sitemap.xml"

    try:
        links = extract_final_urls(sitemap_url)
    except Exception as e:
        print(f"⚠️ Failed to fetch sitemap: {e}")
        links = []

    # If links are empty and URL had www, try non-www version
    if not links and "www." in base_url:
        try:
            non_www_url = base_url.replace("://www.", "://")
            sitemap_url = non_www_url.rstrip("/") + "/sitemap.xml"
            links = extract_final_urls(sitemap_url)
        except Exception as e:
            print(f"⚠️ Retry without www failed: {e}")
            links = []

    # Fallback to single base_url if still no links
    if not links:
        links = [base_url]

    scraped = []
    print(f"🗂️ Found {len(links)} links in the sitemap.")
    for link in links:
        text = scrape(link)
        if not text.strip():
            continue
        chunks = chunk_text(text)
        embeddings = embed_texts(chunks)
        store_chunks(link, chunks, embeddings)
        scraped.append(link)

    return {
        "message": f"✅ Scraped {len(scraped)} pages from sitemap.",
        "scraped_links": scraped
    }



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
