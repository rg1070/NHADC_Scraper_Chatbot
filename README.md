# 🌐 Website Knowledge Chatbot

This is a full-stack web application that allows you to enter any website URL, scrape its content (including sitemap if available), store the data in Supabase, and interact with it using a Gemini-powered chatbot.

## 🔧 Features

- 🔗 Normalize and handle all URL formats (with or without `www`, `https`, etc.)
- 🕷️ Automatically parse and crawl full sitemaps
- 🧠 Embed content with Google Gemini embeddings (limit-safe chunking)
- 🧾 Store vector data in Supabase with deduplication
- 💬 Ask questions via Gemini Flash chatbot
- 📑 References section with paginated display of scraped URLs
- 🌐 Visualize website structure via interactive graph
- ✅ Popup loading/success indicators

---

## 🗂️ Project Structure

```
.
├── backend
│   ├── main.py               # FastAPI app
│   ├── aiagent.py            # Gemini chunking + embedding logic
│   ├── scraper.py            # BeautifulSoup & Selenium logic
│   ├── sitemap_parser.py     # Graph + sitemap parsing
│   └── supabase_utils.py     # Supabase insert/query helpers
├── frontend
│   ├── index.html            # Main UI with embedded JS
│   └── style.css             # Styling (used via <link>)
├── requirements.txt          # Python dependencies
├── dockerfile                # For container deployment (Render-ready)
├── render.yaml               # Render deployment config
└── README.md
```

---

## ⚙️ Technologies Used

- FastAPI
- Google Generative AI (Gemini Flash & Embeddings)
- Supabase (Postgres + RPC)
- Selenium + BeautifulSoup
- PyVis + NetworkX (Graph visualization)
- Vanilla HTML/CSS/JavaScript

---

## 🚀 How to Run Locally

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Setup environment**
   Create a `.env` file in the root and define:

   ```env
   GOOGLE_API_KEY=your_google_key
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
   SUPABASE_TABLE=web_chunks
   ```

3. **Run the backend**
   ```bash
   uvicorn backend.main:app --reload
   ```

4. **Access the frontend**
   Open your browser at:
   ```
   http://localhost:8000
   ```

---

## 🐳 Docker (Render Deployment)

1. Ensure `render.yaml` exists and points to:
   ```yaml
   services:
     - type: web
       name: website-chatbot
       env: docker
       plan: free
       dockerfilePath: ./dockerfile
       buildCommand: ""
       startCommand: uvicorn backend.main:app --host 0.0.0.0 --port 8000
   ```

2. Push to GitHub and connect Render.com

---

## ⚠️ Notes

- Gemini embedding API limits input to 36,000 characters — chunking is applied to avoid errors.
- If a website blocks static requests, Selenium is used as fallback.
- Only text from `<p>` tags and `get_text()` is scraped — media, images, and scripts are ignored.
- Graphs are saved as JSON in `static/graphs/`.

---

## ✅ Example Live App

> https://your-render-url.onrender.com

---

## 📄 License

MIT — do anything, just give credit.