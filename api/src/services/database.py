from sqlalchemy import create_engine, text
import time
from loguru import logger

from config import DATABASE_URL, save_checkpoint, Chunk

if DATABASE_URL:
    try:
        engine = create_engine(DATABASE_URL)
    except Exception:
        logger.exception(
            f"Invalid DB_URL format. Length of DB_URL: {len(DATABASE_URL)}"
        )
        raise ValueError("Invalid DB_URL format. Please check your env variables.")
else:
    logger.error("DB_URL is not set. Database features will be disabled.")
    raise ValueError("DB_URL is not set. Please set the DB_URL environment variable.")


def create_table(doc_name: str, max_attempts: int = 3) -> None:
    table_name = f"{doc_name}"

    sql = text(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id SERIAL PRIMARY KEY,
            main_title TEXT NOT NULL,
            chunk_title TEXT NOT NULL,
            content TEXT,
            embedding extensions.vector(3072)
        );
    """)

    for attempt in range(max_attempts):
        try:
            with engine.begin() as conn:
                conn.execute(sql)
            logger.info(f"Table {table_name} created successfully.")
            return

        except Exception as e:
            logger.warning(f"Attempts:{attempt}\nError getting tables: {e}")
            time.sleep(2)

    raise RuntimeError(
        f"Error creating table {table_name} after {max_attempts} attempts"
    )


def get_tables(max_attempts: int = 3) -> list[str]:
    sql = text("""
        SELECT
            table_name
        FROM
            information_schema.tables
        WHERE
            table_schema = 'public';
    """)

    for attempt in range(max_attempts):
        try:
            with engine.begin() as conn:
                result = conn.execute(sql).fetchall()

            tables = [row[0] for row in result]
            return tables

        except Exception as e:
            logger.warning(f"Attempts:{attempt}\nError getting tables: {e}")
            time.sleep(2)

    raise RuntimeError(f"Error getting tables after {max_attempts} attempts")


def _chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i : i + n], i


def save_bulk_embeddings(
    bulk_embedding_list: list,
    doc_name: str,
    start_index: int,
    db_batch_size: int = 4,
    max_attempts: int = 3,
) -> None:
    if not bulk_embedding_list:
        raise ValueError("bulk_embedding_list cannot be empty")

    table_name = f"{doc_name}"
    sql = text(f"""
        INSERT INTO {table_name} (main_title, chunk_title, embedding, content)
        VALUES (:main_title, :chunk_title, :embedding, :content)
    """)

    for attempt in range(max_attempts):
        try:
            with engine.begin() as conn:
                for batch, i in _chunks(bulk_embedding_list, db_batch_size):
                    conn.execute(sql, batch)
                    # aktualizace checkpointu
                    save_checkpoint(doc_name, start_index + i + len(batch) - 1)

            logger.debug(
                f"SAVED TO DB {table_name}: \n {[(x.get('main_title'), x.get('chunk_title')) for x in bulk_embedding_list]}"
            )
            return

        except Exception as e:
            logger.warning(
                f"SAVING TO DB error (attempt {attempt}/{max_attempts}): {e}"
            )
            time.sleep(50)

    raise RuntimeError(f"Error saving to DB after {max_attempts}")


def search_similar(query_embedding: list, doc_name: str, k: int) -> list[Chunk]:
    table_name = f"{doc_name}"
    vec_string = "[" + ",".join(map(str, query_embedding)) + "]"

    sql = text(f"""
        SELECT
            main_title,
            chunk_title,
            content
        FROM {table_name}
        ORDER BY (embedding <-> CAST(:embedding AS vector)) asc
        LIMIT :k;
    """)

    with engine.begin() as conn:
        rows = conn.execute(sql, {"embedding": vec_string, "k": k}).fetchall()

    rows_out = []
    for row in rows:
        rows_out.append(Chunk(main_title=row[0], chunk_title=row[1], content=row[2]))

    return rows_out


if __name__ == "__main__":
    save_bulk_embeddings(
        [
            {
                "main_title": "Test Title",
                "chunk_title": "Test Chunk",
                "content": "This is some test content.",
                "embedding": [0.1] * 3072,
            }
        ],
        "pandas",
        1,
    )
