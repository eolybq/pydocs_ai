from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")

DATABASE_URL = f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}?sslmode=require&options=-c statement_timeout=0"
engine = create_engine(DATABASE_URL)

def _chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


def save_bulk_embeddings(bulk_embedding_list, doc_name, db_batch_size=8):
    """
    Saves embedding to DB in smaller DB batches to avoid conn issuies
    bulk_emmbedding_list: list of dicts with keys:
        - main_title
        - chunk_title
        - content
        - embedding
    """
    if not bulk_embedding_list:
        return

    table_name = f"rag_docs.{doc_name}"

    sql = text(f"""
        INSERT INTO {table_name} (main_title, chunk_title, embedding, content)
        VALUES (:main_title, :chunk_title, :embedding, :content)
    """)

    with engine.begin() as conn:
        for batch in _chunks(bulk_embedding_list, db_batch_size):
            conn.execute(sql, batch)

    print("")


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