import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_ROLE_KEY"))
TABLE = os.getenv("SUPABASE_TABLE")

def store_chunks(url, chunks, embeddings):

    # First, delete existing entries for this URL
    try:
        supabase.table(TABLE).delete().eq("url", url).execute()
        print(f"🗑️ Existing rows for URL '{url}' deleted.")
    except Exception as e:
        print(f"🚫 Error deleting old rows: {e}")

    # Now prepare new rows
    rows = []
    for chunk, embedding in zip(chunks, embeddings):
        if chunk and embedding:
            rows.append({
                "url": url,
                "chunk": chunk,
                "embedding": embedding
            })

    print("✅ Rows prepared for insertion.")  # for debugging

    if not rows:
        raise ValueError("🚫 No valid rows to insert into Supabase.")

    # Insert new rows
    supabase.table(TABLE).insert(rows).execute()
    print("✅ New rows inserted successfully.")

def query_top_chunks(query_vector, top_k=3):
    response = supabase.rpc(
        "match_vectors",
        {
            "query_embedding": query_vector,
            "match_count": top_k
        }
    ).execute()
    return [row["chunk"] for row in response.data]


