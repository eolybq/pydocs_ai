from sqlalchemy import create_engine, text
import time
from loguru import logger

from config import DATABASE_URL, Chunk


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


def search_similar(query_embedding: list, doc_name: str, k: int) -> list[Chunk]:
    table_name = f"{doc_name}"
    vec_string = "[" + ",".join(map(str, query_embedding)) + "]"

    sql = text(f"""
        SELECT
            main_title,
            chunk_title,
            content
        FROM {table_name}
        ORDER BY (embedding <#> CAST(:embedding AS vector)) asc
        LIMIT :k;
    """)

    with engine.begin() as conn:
        rows = conn.execute(sql, {"embedding": vec_string, "k": k}).fetchall()

    rows_out = []
    for row in rows:
        rows_out.append(Chunk(main_title=row[0], chunk_title=row[1], content=row[2]))

    return rows_out
