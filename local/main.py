from argparse import ArgumentParser
from openai import OpenAI
from loguru import logger

from services.create_embeddings import get_docs_embedding
from services.database import create_table
from config import OPENAI_API_KEY

client = OpenAI(
    api_key=OPENAI_API_KEY,
)


def run_embedding_pipeline():
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
        create_table(doc_name)
        logger.info(f"Table for {doc_name} created successfully.")
    except Exception:
        logger.exception(f"Error creating table for {doc_name}")
        return

    try:
        get_docs_embedding(doc_name, client)
        logger.info(f"Embedding pipeline for {doc_name} completed successfully.")
    except Exception:
        logger.exception(f"Error during embedding pipeline for {doc_name}")
        return


if __name__ == "__main__":
    run_embedding_pipeline()
