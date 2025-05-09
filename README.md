# 🌐 Webpage Knowledge Chatbot (Deployed)

This is a fully functional AI-powered chatbot that lets you scrape any public webpage, embed its content using **Google Gemini**, and ask questions using only that webpage’s content. It’s live at:  
👉 **[https://nhadc-scraper-chatbot.onrender.com](https://nhadc-scraper-chatbot.onrender.com)**

---

## ✅ What It Does

- Scrapes **dynamic or static websites** (via BeautifulSoup and Selenium)
- Extracts visible text and chunks it
- Embeds the chunks using **Gemini Embedding API**
- Stores content + embeddings in a **Supabase pgvector** table
- Uses **Gemini Pro** to answer questions based only on the stored webpage content
- Avoids duplicate entries by normalizing URLs

---

## 🚀 Live Demo

👉 [https://nhadc-scraper-chatbot.onrender.com](https://nhadc-scraper-chatbot.onrender.com)

---

## 🗂️ Project Structure

```
webpage_chatbot/
├── backend/
│   ├── main.py             # FastAPI app: scrape, embed, chat
│   ├── supabase_utils.py   # Supabase interaction helpers
│   ├── requirements.txt
│   └── .env                # (excluded from GitHub)
│
├── frontend/
│   └── index.html          # Simple, clean chatbot UI
│
├── Dockerfile
├── README.md
```

---

## ⚙️ Setup Instructions (Local)

### 1. Clone the Repo

```bash
git clone https://github.com/your-username/webpage_chatbot.git
cd webpage_chatbot
```

### 2. Install Backend Requirements

```bash
cd backend
pip install -r requirements.txt
```

### 3. Setup `.env`

Create a file `backend/.env`:

```env
GOOGLE_API_KEY=your_gemini_key
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role
SUPABASE_TABLE=web_vectors
```

### 4. Run Backend

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 5. Open Frontend

Visit `http://localhost:8000` and use the chatbot.

---

## 🐳 Docker Deployment

Use this Dockerfile to deploy anywhere (including Render):

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY backend /app
COPY frontend /app/frontend

RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Make sure to add your `.env` in Render's dashboard under Environment Variables.

---

## 📦 Supabase Table

Run this SQL inside your Supabase SQL editor:

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

## 🔍 URL Normalization

- Any URL entered like `northlightai.com`, `https://NorthLightAI.com`, `https://northlightai.com/our-team`  
  → is automatically normalized to `https://www.northlightai.com/...`  
  → so no duplicate entries are stored

---

## 📚 Tech Stack

| Feature         | Tool                         |
|----------------|------------------------------|
| Backend API     | FastAPI                      |
| Web Scraping    | BeautifulSoup + Selenium     |
| Embeddings      | Google Gemini Embedding API  |
| Chat Response   | Google Gemini Pro            |
| Vector Storage  | Supabase + pgvector          |
| Frontend        | HTML, CSS, JavaScript        |
| Deployment      | Docker + Render              |

---

## 👤 Author

Made by Roozbeh Ghasemi — follow me on [GitHub](https://github.com/roozbehh)

---

## ⚠️ Legal Note

This project is for educational/demo purposes. Please respect all site terms and conditions.