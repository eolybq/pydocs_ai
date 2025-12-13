from openai import OpenAI
from dotenv import load_dotenv
import os
from tqdm import tqdm
import json
from math import ceil

from services.preprocess import get_chunks_list
from services.database import save_bulk_embeddings

load_dotenv()


BATCH_SIZE = 8
CHECKPOINT_FILE = "checkpoints.json"

def convert_embedding_batch(contents):
    """Vrátí seznam embeddingů pro celý batch textů"""
    API_KEY = os.getenv("OPENAI_API_KEY")
    em_model="text-embedding-3-small"

    client = OpenAI(api_key=API_KEY)


    print(f"CALL convert_embedding_batch, batch_size={len(contents)}, first_hash={hash(contents[0])}")
    response = client.embeddings.create(
        model=em_model,
        input=contents,
        timeout=7200
    )
    return [item.embedding for item in response.data]


def load_checkpoint(doc_name):
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, "r") as f:
            data = json.load(f)
        return data.get(doc_name, {"last_index": -1})
    else:
        print(f"No checkpoint found for {doc_name}")
        return {"last_index": -1}



# Prevod kazdeho chunk na embedding
def get_embedding(doc_name):
    chunks_list = get_chunks_list(doc_name)  # flat list chunků
    print(f"Total chunks for {doc_name}: {len(chunks_list)}")

    checkpoint = load_checkpoint(doc_name)
    start_index = checkpoint["last_index"] + 1
    print(f"Start index: {start_index}")

    chunks_to_process = chunks_list[start_index:]

    if not chunks_to_process:
        print(f"No chunks to process in {doc_name}, everything is already embedded")
        return {"status": "completed"}

    num_batches = ceil(len(chunks_to_process) / BATCH_SIZE)
    print(f"Expected batches: {num_batches}")

    for i in tqdm(range(0, len(chunks_to_process), BATCH_SIZE), desc="Batches"):
        batch = chunks_to_process[i:i+BATCH_SIZE]
        print(f"PYTHON BATCH index={i + start_index}, size={len(batch)}")
        # pridavam main title / chunk_title i do content ktery se prevede pak na embdedding aby byly titles i v nem
        contents = [c["main_title"] + c["chunk_title"] + c["content"] for c in batch]

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
        # TODO a vzit return funkce a poslat vys -> nakonec az userovi ve forme nejake hlasky
        status = save_bulk_embeddings(bulk_data, doc_name, start_index + i)

        if status["status"] != "success":
            return status

    return {"status": "completed"}