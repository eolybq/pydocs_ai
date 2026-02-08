import os
from argparse import ArgumentParser
from openai import OpenAI

from services.create_embeddings import get_embedding
from services.database import create_table

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
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

    status_table = create_table(doc_name)
    if status_table["status"] != "success":
        print(f"Failed to create table for {doc_name}: {status_table['error']}")
        return

    status_embedding = get_embedding(doc_name, client)
    if status_embedding["status"] == "completed":
        print(f"Embedding pipeline for {doc_name} completed successfully.")
        return
    else:
        print(
            f"Embedding pipeline for {doc_name} failed with error: {status_embedding['error']}"
        )
        return


if __name__ == "__main__":
    run_embedding_pipeline()
