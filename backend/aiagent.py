import os
import re
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

chat_model = genai.GenerativeModel('gemini-2.0-flash-001')



def chunk_text(text, max_bytes=36000):
    """Split text into UTF-8 byte-safe chunks, preferably at sentence boundaries."""
    sentences = re.split(r'(?<=[.!?]) +', text)
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        test_chunk = (current_chunk + " " + sentence).strip()
        if len(test_chunk.encode("utf-8")) <= max_bytes:
            current_chunk = test_chunk
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            if len(sentence.encode("utf-8")) > max_bytes:
                words = sentence.split()
                buffer = ""
                for word in words:
                    if len((buffer + " " + word).encode("utf-8")) <= max_bytes:
                        buffer = (buffer + " " + word).strip()
                    else:
                        chunks.append(buffer)
                        buffer = word
                if buffer:
                    chunks.append(buffer)
                current_chunk = ""
            else:
                current_chunk = sentence

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


def embed_texts(texts):
    """Generate embeddings for each chunk of text using Gemini."""
    embeddings = []
    for text in texts:
        response = genai.embed_content(
            model="models/embedding-001",
            content=text,
            task_type="retrieval_document"
        )
        embeddings.append(response["embedding"])
    return embeddings