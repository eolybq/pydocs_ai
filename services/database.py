from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")

DATABASE_URL = f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}?sslmode=require"
engine = create_engine(DATABASE_URL)


def save_bulk_embeddings(bulk_embedding_list, doc_name):
    """
    Uloží celý batch embeddingů do DB zaráz
    bulk_emmbedding_list: list slovníků s klíči:
        - main_title
        - chunk_title
        - content
        - embedding
    """
    if not bulk_embedding_list:
        return

    table_name = f"rag_docs.{doc_name}"

    # TODO zmenit tabulku na {table_name}  -> urcuje se v server.py tabulka
    sql = text(f"""
        INSERT INTO rag_docs.test (main_title, chunk_title, embedding, content)
        VALUES (:main_title, :chunk_title, :embedding, :content)
    """)

    with engine.begin() as conn:
        conn.execute(sql, bulk_embedding_list)


def search_similar(query_embedding, doc_name, k=5):
    table_name = f"rag_docs.{doc_name}"
    vec_string = "[" + ",".join(map(str, query_embedding)) + "]"

    sql = text(f"""
        SELECT
            main_title,
            chunk_title,
            content
        FROM {table_name}
        ORDER BY (embedding <-> :embedding) asc
        LIMIT :k;
    """)

    with engine.begin() as conn:
        rows = conn.execute(sql, {
            "embedding": vec_string,
            "k": k
        }).fetchall()

    rows_out = []
    for row in rows:
        row_dict = {
            "main_title": row[0],
            "chunk_title": row[1],
            "content": row[2]
        }
        rows_out.append(row_dict)

    return rows_out