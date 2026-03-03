from argparse import ArgumentParser

from loguru import logger
from openai import OpenAI
from sqlalchemy import create_engine

from src.core.clients.database_client import create_table
from src.core.config import DATABASE_URL, OPENAI_API_KEY
from src.services.ingest.embeddings import get_docs_embedding

client = OpenAI(api_key=OPENAI_API_KEY)


if not DATABASE_URL:
    logger.error("DB_URL is not set.")
    raise ValueError("DB_URL is not set. Please set the DB_URL environment variable.")

engine = create_engine(DATABASE_URL)


def run_embedding_pipeline() -> None:
    parser = ArgumentParser()
    parser.add_argument(
        "doc_name",
        type=str,
        default="",
        help="Name of desired documentation to process",
    )
    args = parser.parse_args()
    doc_name = args.doc_name

    try:
        create_table(engine, doc_name)
        logger.info(f"Table for {doc_name} created successfully.")
    except Exception:
        logger.exception(f"Error creating table for {doc_name}")
        return

    try:
        get_docs_embedding(engine, doc_name, client)
        logger.info(f"Embedding pipeline for {doc_name} completed successfully.")
    except Exception:
        logger.exception(f"Error during embedding pipeline for {doc_name}")
        return


if __name__ == "__main__":
    run_embedding_pipeline()
