import os
import sys

from dotenv import load_dotenv
from loguru import logger
from pydantic import BaseModel

load_dotenv()


# ── Pydantic Models ──
class Chunk(BaseModel):
    main_title: str
    chunk_title: str
    content: str


class TableList(BaseModel):
    tables: list[str]


# ── Constants ──
save_eval_data = True
MAX_DB_ATTEMPTS = 3
SEARCH_K_EMBEDDINGS = 5
HISTORY_LEN = 6
EMBEDDING_MODEL = "text-embedding-3-large"
BATCH_SIZE = 8


# ── Environment Variables ──
DEPLOY_FE_URL = os.getenv("DEPLOY_FE_URL")
LOCAL_FE_URL = os.getenv("LOCAL_FE_URL", "http://localhost:8501")
DATABASE_URL = os.getenv("DB_URL")
DATABASE_EVAL_URL = os.getenv("DB_EVAL_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()


# ── Logging ──
def setup_logging() -> None:
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=LOG_LEVEL,
        enqueue=True,
    )
