from loguru import logger
from openai import OpenAI

from config import EMBEDDING_MODEL


def convert_embedding_batch(contents: list[str], client: OpenAI) -> list[list[float]]:
    logger.debug(
        f"CALL convert_embedding_batch, batch_size={len(contents)}, first_hash={hash(contents[0])}"
    )
    response = client.embeddings.create(
        model=EMBEDDING_MODEL, input=contents, timeout=7200
    )
    return [item.embedding for item in response.data]
