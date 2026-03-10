from math import ceil

from loguru import logger
from sqlalchemy import Engine
from tqdm import tqdm

from src.core.clients.database_client import save_bulk_embeddings
from src.core.clients.embedding_client import EmbeddingClient
from src.core.config import BATCH_SIZE
from src.services.ingest.checkpoints import load_checkpoint
from src.services.ingest.preprocess import get_chunks_list


def get_docs_embedding(engine: Engine, doc_name: str, client: EmbeddingClient) -> None:
    chunks_list = get_chunks_list(doc_name)  # flat list of chunks
    logger.info(f"Total chunks for {doc_name}: {len(chunks_list)}")

    checkpoint = load_checkpoint(doc_name)
    start_index = checkpoint["last_index"] + 1
    logger.info(f"Start index: {start_index}")

    chunks_to_process = chunks_list[start_index:]

    if not chunks_to_process:
        logger.info(
            f"No chunks to process in {doc_name}, everything is already embedded",
        )
        return

    num_batches = ceil(len(chunks_to_process) / BATCH_SIZE)
    logger.info(f"Expected batches: {num_batches}")

    for i in tqdm(range(0, len(chunks_to_process), BATCH_SIZE), desc="Batches"):
        batch = chunks_to_process[i : i + BATCH_SIZE]
        contents = [c.main_title + c.chunk_title + c.content for c in batch]
        embeddings = client.embed_batch(contents)
        bulk_data = []
        for c, emb in zip(batch, embeddings):
            bulk_data.append(
                {
                    "embedding": emb,
                    "content": c.content,
                    "main_title": c.main_title,
                    "chunk_title": c.chunk_title,
                },
            )
        save_bulk_embeddings(engine, bulk_data, doc_name, start_index + i)
