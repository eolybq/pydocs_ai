import os
from openai.types.chat import ChatCompletionMessageParam
import sys
from dotenv import load_dotenv
from pydantic import BaseModel
from loguru import logger
import json


load_dotenv()


# Pydantic models
class Chunk(BaseModel):
    main_title: str
    chunk_title: str
    content: str


class Query(BaseModel):
    prompt: str
    doc_name: str
    context: list[ChatCompletionMessageParam]


class TableList(BaseModel):
    tables: list[str]


# CONFIG VARS
SEARCH_K_EMBEDDINGS = 3
HISTORY_LEN = 6

BATCH_SIZE = 8
CHECKPOINT_FILE = "checkpoints.json"
EMBEDDING_MODEL = "text-embedding-3-large"


# ENV VARS
DEPLOY_FE_URL = os.getenv("DEPLOY_FE_URL")
LOCAL_FE_URL = os.getenv("LOCAL_FE_URL")

DATABASE_URL = os.getenv("DB_URL")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()


# CHECKPOINT FUNCTIONS
def save_checkpoint(doc_name, last_index):
    data = {}
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, "r") as f:
            data = json.load(f)
    else:
        print(f"No checkpoint found for {doc_name}")
    data[doc_name] = {"last_index": last_index}
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump(data, f)


def load_checkpoint(doc_name: str) -> dict[str, int]:
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, "r") as f:
            data = json.load(f)
        return data.get(doc_name, {"last_index": -1})
    else:
        logger.warning(f"No checkpoint found for {doc_name}")
        return {"last_index": -1}


# LOGGING
def setup_logging() -> None:
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=LOG_LEVEL,
        enqueue=True,
    )
