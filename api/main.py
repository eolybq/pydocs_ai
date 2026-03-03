import uvicorn
from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, StreamingResponse
from loguru import logger
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from pydantic import BaseModel
from sqlalchemy import create_engine

from src.core.clients.database_client import get_tables, search_similar, store_eval_data
from src.core.clients.openai_client import convert_embedding_batch
from src.core.config import (
    DATABASE_EVAL_URL,
    DATABASE_URL,
    DEPLOY_FE_URL,
    HISTORY_LEN,
    LOCAL_FE_URL,
    OPENAI_API_KEY,
    SEARCH_K_EMBEDDINGS,
    TableList,
    save_eval_data,
    setup_logging,
)
from src.services.chat.llm import format_error, get_llm_res


class Query(BaseModel):
    prompt: str
    doc_name: str
    context: list[ChatCompletionMessageParam]


setup_logging()
load_dotenv()

fe_url = DEPLOY_FE_URL or LOCAL_FE_URL
origins = [fe_url]

api = FastAPI()
api.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if not OPENAI_API_KEY:
    logger.error(
        "OPENAI_API_KEY is not set. Please set the OPENAI_API_KEY environment variable.",
    )
    raise ValueError("Could not connect to OpenAI API.")

client = OpenAI(api_key=OPENAI_API_KEY, max_retries=3, timeout=120)


if not DATABASE_URL:
    logger.error("DB_URL is not set.")
    raise ValueError("DB_URL is not set. Please set the DB_URL environment variable.")

engine = create_engine(DATABASE_URL)


if save_eval_data:
    if not DATABASE_EVAL_URL:
        logger.error(
            "DB_EVAL_URL is not set. Evaluation database features will be disabled.",
        )
        raise ValueError(
            "DB_EVAL_URL is not set. Please set the DB_EVAL_URL environment variable.",
        )

    eval_engine = create_engine(DATABASE_EVAL_URL)
else:
    logger.info("SAVE_EVAL_DATA is set to False. Evaluation data will not be stored.")


@api.get("/")
def read_root():
    return RedirectResponse(url="/docs")


@api.get("/get_tables", response_model=TableList)
def get_all_tables():
    try:
        tables = get_tables(engine)
        return TableList(tables=tables)
    except Exception:
        logger.exception("Unexpected error while fetching tables")
        return TableList(tables=[])


@api.post("/query", response_class=StreamingResponse)
def get_response(data: Query, background_tasks: BackgroundTasks):
    user_query = data.prompt
    doc_name = data.doc_name
    context = data.context[-HISTORY_LEN:]

    logger.debug(context)

    try:
        query_emb = convert_embedding_batch([user_query], client)[0]
    except Exception:
        logger.exception("Error during query embedding creation")
        return StreamingResponse(
            format_error("Could not create embedding for the query."),
        )

    try:
        sim_embeddings = search_similar(
            engine,
            query_emb,
            doc_name,
            k=SEARCH_K_EMBEDDINGS,
        )
    except Exception:
        logger.exception("Error during search for similar embeddings")
        return StreamingResponse(format_error("Could not find similar embeddings."))

    logger.debug(f"Similar embeddings: {sim_embeddings}")

    # EVALUATION
    def stream_and_collect():
        full_response = []
        for chunk in get_llm_res(user_query, sim_embeddings, context, client):
            full_response.append(chunk)
            yield chunk

        if save_eval_data:
            full_response = "".join(full_response)

            background_tasks.add_task(
                store_eval_data,
                eval_engine,
                user_query,
                sim_embeddings,
                full_response,
            )

    return StreamingResponse(stream_and_collect(), media_type="text/event-stream")


if __name__ == "__main__":
    uvicorn.run("api.main:api", host="0.0.0.0", port=8000, reload=True)
