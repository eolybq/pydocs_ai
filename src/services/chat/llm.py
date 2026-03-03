import textwrap
from collections.abc import Generator

from loguru import logger
from openai import APIConnectionError, APIError, OpenAI, RateLimitError
from openai.types.chat import ChatCompletionMessageParam

from src.core.config import Chunk


def format_error(message: str) -> str:
    return f"\n\n:red[**Error:**] {message}"


def get_llm_res(
    user_query: str,
    sim_embeddings: list[Chunk],
    history: list[ChatCompletionMessageParam],
    client: OpenAI,
) -> Generator[str, None, None]:
    context_str = "\n\n".join(
        f"<chunk>\nmain_title: {c.main_title}\nchunk_title: {c.chunk_title}\ncontent: {c.content}\n</chunk>"
        for c in sim_embeddings
    )

    system_prompt = textwrap.dedent("""
        You are a professional Python RAG assistant specialized in technical documentation.
        
        ### INSTRUCTIONS:
        1. **Source of Truth:** Base your answer PRIMARILY on the provided <context>.
        2. **Goal:** Provide concise and detailed explanation and answer to user needs. Explain everything clearly and professionally.
        2. **Handling Gaps:** - If the <context> completely lacks information to answer the query, state: "I cannot answer this based on the provided documentation."
           - If the query asks about a general concept (e.g., "Time Series") not explicitly defined but related, apply your relevant general knowledge to relevant parts of the <context> to construct an answer.
           - Do NOT fill in gaps with internal knowledge about specific library methods, parameters, or classes, as APIs may have changed.
        3. **Conflict Resolution:** If internal knowledge conflicts with <context>, the <context> WINS.
        4. **Code Examples:** Provide exact code examples in blocks if possible.
            - Ensure code is complete and syntactically correct.
        5. **Format:** Use Markdown (Headers, Bold, Code Blocks). ALWAYS specify the language in code blocks (e.g., ```python).
        - Don't explicitly mention keywords like <context> or similar runtime notes, as you are professional assistant in production.
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
            "I have reached the rate limit. Please wait a moment before trying again.",
        )
        return
    except APIConnectionError:
        logger.exception("Connection error")
        yield format_error("Could not connect to the AI server.")
        return
    except APIError:
        logger.exception("API error")
        yield format_error("An AI provider error occurred")
        return
    except Exception:
        logger.exception("Unexpected error during streaming response")
        yield format_error("Unexpected error occurred")
        return
