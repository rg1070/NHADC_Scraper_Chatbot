
# 🌎 Webpage Knowledge Chatbot

A professional chatbot web app that allows you to:
- Scrape a webpage URL
- Extract and embed the webpage text using **Google Gemini Embedding API**
- Store the vector embeddings in a **Supabase vector database** (pgvector extension)
- Chat with an intelligent agent that answers questions based purely on the scraped content
- View the live webpage inside an `<iframe>` while chatting

---

## 📂 Project Structure

```
webpage_chatbot/
├── backend/
│   ├── main.py             # FastAPI server: scrape, embed, ask
│   ├── supabase_utils.py   # Supabase vector insertion and search
│   ├── requirements.txt    # Backend dependencies
│   ├── .env                # API keys and secrets (DO NOT COMMIT)
│
├── frontend/
│   ├── index.html          # Chatbot User Interface
│
├── .gitignore
├── README.md
```

---

## ⚙️ Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/webpage_chatbot.git
cd webpage_chatbot
```

### 2. Install Backend Requirements
```bash
cd backend
pip install -r requirements.txt
```

### 3. Setup Environment Variables

Create a `backend/.env` file:

```env
GOOGLE_API_KEY=your_gemini_api_key
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
SUPABASE_TABLE=web_vectors
```

> 🚨 Never share your `.env` publicly.

---

### 4. Create Supabase Table

Run this SQL in your Supabase SQL editor:

```sql
create extension if not exists vector;

create table web_vectors (
  id uuid default gen_random_uuid() primary key,
  url text,
  chunk text,
  embedding vector(768)
);
```

---

### 5. Run the Backend Server

```bash
uvicorn backend.main:app --reload
```

API will be available at `http://localhost:8000`.

---

### 6. Open Frontend

- Open `frontend/index.html` directly in your browser
- (Or use Live Server extension in VS Code for better dev experience)

---

## 🚀 Features

- 🌐 Scrape any public webpage
- 🧠 Store text + semantic vectors in Supabase
- 🧠 Intelligent question-answering using Gemini Pro
- 🎨 Beautiful and clean frontend interface
- 📈 Automatically improves knowledge as you add more websites

---

## 📌 Tech Stack

| Component        | Technology                      |
|------------------|----------------------------------|
| Backend API      | FastAPI                          |
| Web Scraping     | BeautifulSoup                    |
| Embeddings       | Google Gemini Embedding API      |
| Vector Storage   | Supabase + pgvector extension    |
| LLM Q&A          | Google Gemini Pro (Text Gen)     |
| Frontend UI      | HTML + CSS + Vanilla JavaScript  |

---

## ✨ Future Improvements (Optional)

- Auto-crawl full websites or sitemaps
- Add PDF ingestion
- Streamlit / React frontend
- Dockerize full application
- Deploy to Render, Vercel, or Hugging Face Spaces

---

## 👨‍💻 Author

Made by Roozbeh Ghasemi

---

## ⚠️ Disclaimer

This project is developed purely for **learning and educational purposes**.
It is intended as a demonstration of web scraping, vector storage, and chatbot integration.
Please ensure that your usage of the app complies with all applicable copyright and website terms of service.

