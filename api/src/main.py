import textwrap
from typing import Generator

import uvicorn
from config import (
    DEPLOY_FE_URL,
    LOCAL_FE_URL,
    OPENAI_API_KEY,
    SEARCH_K_EMBEDDINGS,
    Chunk,
    Query,
    TableList,
    setup_logging,
)
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, StreamingResponse
from loguru import logger
from openai import APIConnectionError, APIError, OpenAI, RateLimitError
from openai.types.chat import ChatCompletionMessageParam
from services.create_embeddings import convert_embedding_batch
from services.database import get_tables, search_similar

load_dotenv()
setup_logging()

origins = [DEPLOY_FE_URL, LOCAL_FE_URL]

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
        "OPENAI_API_KEY is not set. Please set the OPENAI_API_KEY environment variable."
    )
    raise ValueError("Could not connect to OpenAI API.")

client = OpenAI(api_key=OPENAI_API_KEY, max_retries=3, timeout=120)


def format_error(message: str) -> str:
    return f"\n\n:red[**Error:**] {message}"


def get_llm_res(
    user_query: str,
    sim_embeddings: list[Chunk],
    history: list[ChatCompletionMessageParam],
) -> Generator[str, None, None]:
    context_str = "\n\n".join(
        f"<chunk>\nmain_title: {c.main_title}\nchunk_title: {c.chunk_title}\ncontent: {c.content}\n</chunk>"
        for c in sim_embeddings
    )

    system_prompt = textwrap.dedent("""
        You are a professional Python RAG assistant specialized in technical documentation.
        
        ### INSTRUCTIONS:
        1. **Source of Truth:** Base your answer PRIMARILY on the provided <context>.
        2. **Handling Gaps:** - If the <context> completely lacks information to answer the query, state: "I cannot answer this based on the provided documentation."
           - If the query asks about a general concept (e.g., "Time Series") not explicitly defined but related, apply your relevant general knowledge to relevant parts of the <context> to construct an answer.
           - Do NOT fill in gaps with internal knowledge about specific library methods, parameters, or classes, as APIs may have changed.
        3. **Conflict Resolution:** If internal knowledge conflicts with <context>, the <context> WINS.
        4. **Tone:** Professional, technical, concise.
        5. **Code Examples:** Provide exact code examples in blocks if possible.
            - Ensure code is complete and syntactically correct.
        6. **Format:** Use Markdown (Headers, Bold, Code Blocks). ALWAYS specify the language in code blocks (e.g., ```python).
    """).strip()

    user_prompt = textwrap.dedent(f"""
    Please answer the query based on the context below:

    <context>
    {context_str}
    </context>

    <query>
    {user_query}
    </query>
    """).strip()

    try:
        stream = client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=[
                {"role": "system", "content": system_prompt},
                *history,
                {"role": "user", "content": user_prompt},
            ],
            stream=True,
            temperature=0.3,
        )

        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                logger.debug(content)
                yield content

    except RateLimitError:
        logger.exception("Rate limit exceeded")
        yield format_error(
            " I have reached the rate limit. Please wait a moment before trying again."
        )
        return
    except APIConnectionError:
        logger.exception("Connection error")
        yield format_error(" Could not connect to the AI server.")
        return
    except APIError:
        logger.exception("API error")
        yield format_error(" An AI provider error occurred")
        return
    except Exception:
        logger.exception("Unexpected error during streaming response")
        yield format_error(" Unexpected error occurred")
        return


@api.get("/")
def read_root():
    return RedirectResponse(url="/docs")


@api.get("/get_tables", response_model=TableList)
def get_all_tables():
    try:
        tables = get_tables()
        return TableList(tables=tables)
    except Exception:
        logger.exception("Unexpected error while fetching tables")
        return TableList(tables=[])


@api.post("/query", response_class=StreamingResponse)
def get_response(data: Query):
    user_query = data.prompt
    doc_name = data.doc_name
    context = data.context

    logger.debug(context)

    try:
        query_emb = convert_embedding_batch([user_query], client)[0]
    except Exception:
        logger.exception("Error during query embedding creation")
        return StreamingResponse(
            format_error("Could not create embedding for the query.")
        )

    try:
        sim_embeddings = search_similar(query_emb, doc_name, k=SEARCH_K_EMBEDDINGS)
    except Exception:
        logger.exception("Error during search for similar embeddings")
        return StreamingResponse(format_error("Could not find similar embeddings."))

    logger.debug(f"Similar embeddings: {sim_embeddings}")

    return StreamingResponse(
        get_llm_res(user_query, sim_embeddings, context), media_type="text/event-stream"
    )


if __name__ == "__main__":
    uvicorn.run("main:api", host="0.0.0.0", port=8000, reload=True)
