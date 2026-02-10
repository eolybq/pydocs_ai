from dotenv import load_dotenv
from loguru import logger
from openai import OpenAI
from tqdm import tqdm
from math import ceil

from services.preprocess import get_chunks_list
from services.database import save_bulk_embeddings
from config import EMBEDDING_MODEL, BATCH_SIZE, load_checkpoint

load_dotenv()


def convert_embedding_batch(contents: list[str], client: OpenAI) -> list[list[float]]:
    logger.debug(
        f"CALL convert_embedding_batch, batch_size={len(contents)}, first_hash={hash(contents[0])}"
    )
    response = client.embeddings.create(
        model=EMBEDDING_MODEL, input=contents, timeout=7200
    )
    return [item.embedding for item in response.data]


# Prevod kazdeho chunk na embedding
def get_docs_embedding(doc_name: str, client: OpenAI) -> None:
    chunks_list = get_chunks_list(doc_name)  # flat list chunků
    logger.info(f"Total chunks for {doc_name}: {len(chunks_list)}")

    checkpoint = load_checkpoint(doc_name)
    start_index = checkpoint["last_index"] + 1
    logger.info(f"Start index: {start_index}")

    chunks_to_process = chunks_list[start_index:]

    if not chunks_to_process:
        logger.info(
            f"No chunks to process in {doc_name}, everything is already embedded"
        )
        return

    num_batches = ceil(len(chunks_to_process) / BATCH_SIZE)
    logger.info(f"Expected batches: {num_batches}")

    for i in tqdm(range(0, len(chunks_to_process), BATCH_SIZE), desc="Batches"):
        batch = chunks_to_process[i : i + BATCH_SIZE]
        logger.debug(f"PYTHON BATCH index={i + start_index}, size={len(batch)}")
        # pridavam main title / chunk_title i do content ktery se prevede pak na embdedding aby byly titles i v nem
        contents = [c.main_title + c.chunk_title + c.content for c in batch]

        embeddings = convert_embedding_batch(contents, client)

        bulk_data = []
        for c, emb in zip(batch, embeddings):
            # dim vektoru: (4096)
            bulk_data.append(
                {
                    "embedding": emb,
                    "content": c.content,
                    "main_title": c.main_title,
                    "chunk_title": c.chunk_title,
                }
            )

        # bulk insert do DB
        save_bulk_embeddings(bulk_data, doc_name, start_index + i)
