import time

from loguru import logger
from sqlalchemy import Engine, text

from src.core.config import MAX_DB_ATTEMPTS, Chunk
from src.services.ingest.checkpoints import save_checkpoint


def create_table(engine: Engine, doc_name: str, max_attempts: int = 3) -> None:
    sql = text(f"""CREATE TABLE IF NOT EXISTS {doc_name} (
        id SERIAL PRIMARY KEY,
        main_title TEXT NOT NULL,
        chunk_title TEXT NOT NULL,
        content TEXT,
        embedding extensions.vector(3072)
    );""")
    for attempt in range(max_attempts):
        try:
            with engine.begin() as conn:
                conn.execute(sql)
            return
        except Exception as e:
            logger.warning(f"Attempts:{attempt}\nError getting tables: {e}")
            time.sleep(2)
    raise RuntimeError(f"Error creating table {doc_name} after {max_attempts} attempts")


def _chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i : i + n], i


def save_bulk_embeddings(
    engine: Engine,
    bulk_embedding_list: list,
    doc_name: str,
    start_index: int,
    db_batch_size: int = 4,
    max_attempts: int = 3,
) -> None:
    if not bulk_embedding_list:
        raise ValueError("bulk_embedding_list cannot be empty")
    sql = text(f"""INSERT INTO {doc_name} (main_title, chunk_title, embedding, content)
        VALUES (:main_title, :chunk_title, :embedding, :content)""")
    for attempt in range(max_attempts):
        try:
            with engine.begin() as conn:
                for batch, i in _chunks(bulk_embedding_list, db_batch_size):
                    conn.execute(sql, batch)
                    save_checkpoint(doc_name, start_index + i + len(batch) - 1)
            return
        except Exception as e:
            logger.warning(
                f"SAVING TO DB error (attempt {attempt}/{max_attempts}): {e}",
            )
            time.sleep(50)
    raise RuntimeError(f"Error saving to DB after {max_attempts}")


def get_tables(engine: Engine) -> list[str]:
    sql = text(
        """SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';""",
    )
    for attempt in range(MAX_DB_ATTEMPTS):
        try:
            with engine.connect() as conn:
                result = conn.execute(sql)
            return [row[0] for row in result]
        except Exception as e:
            logger.warning(f"Attempts:{attempt}\nError getting tables: {e}")
            time.sleep(2)
    raise RuntimeError(f"Error getting tables after {MAX_DB_ATTEMPTS} attempts")


def search_similar(
    engine: Engine,
    query_embedding: list,
    doc_name: str,
    k: int,
) -> list[Chunk]:
    # TODO asi neni potreba?
    vec_string = "[" + ",".join(map(str, query_embedding)) + "]"

    sql_search = text(f"""
        SELECT main_title, chunk_title, content
        FROM {doc_name}
        ORDER BY (embedding <#> CAST(:embedding AS vector)) asc
        LIMIT :k;
    """)
    for attempt in range(MAX_DB_ATTEMPTS):
        try:
            with engine.connect() as conn:
                rows = conn.execute(sql_search, {"embedding": vec_string, "k": k})
            return [
                Chunk(main_title=r[0], chunk_title=r[1], content=r[2]) for r in rows
            ]
        except Exception as e:
            logger.warning(
                f"Attempts:{attempt}\nError searching similar embeddings: {e}",
            )
            time.sleep(2)
    raise RuntimeError(
        f"Error while searching similar embeddings after {MAX_DB_ATTEMPTS} attempts",
    )


def store_eval_data(
    eval_engine: Engine,
    user_query: str,
    rag_context: list[Chunk],
    agent_answer: str,
) -> None:
    context_string = "\n\n".join(
        f"Main title: {c.main_title}\nChunk title: {c.chunk_title}\nContent: {c.content}"
        for c in rag_context
    )
    sql_store = text(
        """INSERT INTO evaluation_data (user_query, rag_context, agent_answer) VALUES (:user_query, :rag_context, :agent_answer);""",
    )
    for attempt in range(MAX_DB_ATTEMPTS):
        try:
            with eval_engine.begin() as conn:
                conn.execute(
                    sql_store,
                    {
                        "user_query": user_query,
                        "rag_context": context_string,
                        "agent_answer": agent_answer,
                    },
                )
            logger.debug("Evaluation data stored successfully")
            return
        except Exception as e:
            logger.warning(f"Attempts:{attempt}\nError storing evaluation data: {e}")
            time.sleep(1)
    logger.warning(f"Error storing evaluation data after {MAX_DB_ATTEMPTS} attempts")
    return
