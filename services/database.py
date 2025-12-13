from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import json
import os
import time

load_dotenv()

USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")
HOST = os.getenv("HOST")
PORT = os.getenv("PORT")
DBNAME = os.getenv("DBNAME")

DATABASE_URL = f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}?sslmode=require"
engine = create_engine(DATABASE_URL)

CHECKPOINT_FILE = "checkpoints.json"


def create_table(doc_name):
    table_name = f"rag_docs.{doc_name}"

    sql = text(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id SERIAL PRIMARY KEY,
            main_title TEXT NOT NULL,
            chunk_title TEXT NOT NULL,
            content TEXT,
            embedding extensions.vector(1536)
        );
    """)

    try:
        with engine.begin() as conn:
            conn.execute(text("CREATE SCHEMA IF NOT EXISTS rag_docs;"))
            conn.execute(sql)
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "error": f"Error creating table {table_name}: {e}"}


def get_tables():
    sql = text(f"""
        SELECT
            table_name, table_type
        FROM
            information_schema.tables
        WHERE
            table_schema = 'rag_docs';
    """)

    try:
        with engine.begin() as conn:
            result = conn.execute(sql).fetchall()
            tables = [row['table_name'] for row in result]
    except Exception as e:
        print("Error getting tables: ", e)
        return {"status": "error", "error": str(e)}

    return {"status": "success", "tables": tables}




def _chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n], i

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

def save_bulk_embeddings(bulk_embedding_list, doc_name, start_index, db_batch_size=4, max_attempts=3):
    """
    Saves embedding to DB in smaller DB batches to avoid conn issuies
    bulk_emmbedding_list: list of dicts with keys:
        - main_title
        - chunk_title
        - content
        - embedding
    """
    if not bulk_embedding_list:
        return {"status": "error", "error": "Empty bulk_embedding_list"}

    table_name = f"rag_docs.{doc_name}"
    sql = text(f"""
        INSERT INTO {table_name} (main_title, chunk_title, embedding, content)
        VALUES (:main_title, :chunk_title, :embedding, :content)
    """)


    attempt = 0
    while attempt < max_attempts:
        try:
            with engine.begin() as conn:
                for batch, i in _chunks(bulk_embedding_list, db_batch_size):
                    conn.execute(sql, batch)
                    # aktualizace checkpointu
                    save_checkpoint(doc_name, start_index + i + len(batch) - 1)

            print(f"SAVED TO DB {table_name}: \n {[(x.get("main_title"), x.get("chunk_title")) for x in bulk_embedding_list]}")
            return {"status": "success"}

        except Exception as e:
            attempt += 1
            print(f"SAVING TO DB error (attempt {attempt}/{max_attempts}): {e}")
            if attempt < max_attempts:
                print("Waiting 60s before retrying...")
                time.sleep(60)
            else:
                print("Max retries reached")
                return {"status": "error", "error": str(e)}




def search_similar(query_embedding, doc_name, k=3):
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

    try:
        with engine.begin() as conn:
            rows = conn.execute(sql, {
                "embedding": vec_string,
                "k": k
            }).fetchall()
    except Exception as e:
        print(f"Error during search in {table_name}: {e}")
        return {"status": "error", "error": str(e), "results": []}

    rows_out = []
    for row in rows:
        rows_out.append({
            "main_title": row[0],
            "chunk_title": row[1],
            "content": row[2]
        })

    return {"status": "success", "results": rows_out}