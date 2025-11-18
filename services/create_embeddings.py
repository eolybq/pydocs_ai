from openai import OpenAI
from dotenv import load_dotenv
import os
from tqdm import tqdm
import json

from services.preprocess import get_chunks_list
from services.database import save_bulk_embeddings

load_dotenv()
IPADRESS = os.getenv("ipadress")
client = OpenAI(base_url=IPADRESS, api_key="lm-studio")


BATCH_SIZE = 32
CHECKPOINT_FILE = "checkpoints.json"

def convert_embedding_batch(contents):
    """Vrátí seznam embeddingů pro celý batch textů"""
    response = client.embeddings.create(
        model="text-embedding-qwen3-embedding-8b",
        input=contents,
        # timeout=120
    )
    return [item.embedding for item in response.data]


def load_checkpoint(doc_name):
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, "r") as f:
            data = json.load(f)
        return data.get(doc_name, {"last_index": -1})
    return {"last_index": -1}

def save_checkpoint(doc_name, last_index):
    data = {}
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, "r") as f:
            data = json.load(f)
    data[doc_name] = {"last_index": last_index}
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump(data, f)


# Prevod kazdeho chunk na embedding
def get_embedding(doc_name):
    chunks_list = get_chunks_list(doc_name)  # flat list chunků

    checkpoint = load_checkpoint(doc_name)
    start_index = checkpoint["last_index"] + 1
    chunks_to_process = chunks_list[start_index:]

    for i in tqdm(range(0, len(chunks_to_process), BATCH_SIZE), desc="Batches"):
        batch = chunks_to_process[i:i+BATCH_SIZE]
        contents = [c["content"] for c in batch]

        embeddings = convert_embedding_batch(contents)

        bulk_data = []
        for c, emb in zip(batch, embeddings):
            # dim vektoru: (4096)
            bulk_data.append({
                "embedding": emb,
                "content": c["content"],
                "main_title": c["main_title"],
                "chunk_title": c["chunk_title"]
            })

        # bulk insert do DB
        save_bulk_embeddings(bulk_data, doc_name)

        # aktualizace checkpointu
        save_checkpoint(doc_name, start_index + i + len(batch) - 1)