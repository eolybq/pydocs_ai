import os
from openai.types.chat import ChatCompletionMessageParam
import sys
from dotenv import load_dotenv
from pydantic import BaseModel
from loguru import logger


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

EMBEDDING_MODEL = "text-embedding-3-large"


# ENV VARS
DEPLOY_FE_URL = os.getenv("DEPLOY_FE_URL")
LOCAL_FE_URL = os.getenv("LOCAL_FE_URL", "http://localhost:8501")

DATABASE_URL = os.getenv("DB_URL")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()


# LOGGING
def setup_logging() -> None:
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=LOG_LEVEL,
        enqueue=True,
    )
